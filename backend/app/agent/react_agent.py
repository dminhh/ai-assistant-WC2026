import json
from typing import AsyncIterator
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.agent import tools as tool_fns

openai_client = AsyncOpenAI(api_key=get_settings().openai_api_key)

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_today_fixtures",
            "description": "Lấy danh sách trận đấu hôm nay",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_scores",
            "description": "Lấy tỉ số các trận đang diễn ra",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_standings",
            "description": "Lấy bảng xếp hạng của một giải đấu",
            "parameters": {
                "type": "object",
                "properties": {"competition_name": {"type": "string"}},
                "required": ["competition_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_stats",
            "description": "Lấy thống kê 5 trận gần nhất của một đội",
            "parameters": {
                "type": "object",
                "properties": {"team_name": {"type": "string"}},
                "required": ["team_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prediction",
            "description": "Dự đoán xác suất thắng/hòa/thua giữa 2 đội",
            "parameters": {
                "type": "object",
                "properties": {
                    "home_team": {"type": "string"},
                    "away_team": {"type": "string"},
                },
                "required": ["home_team", "away_team"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_h2h",
            "description": "Lấy lịch sử đối đầu giữa 2 đội",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_a": {"type": "string"},
                    "team_b": {"type": "string"},
                },
                "required": ["team_a", "team_b"],
            },
        },
    },
]

TOOL_MAP = {
    "get_today_fixtures": lambda args, db: tool_fns.get_today_fixtures(db),
    "get_live_scores":    lambda args, db: tool_fns.get_live_scores(db),
    "get_standings":      lambda args, db: tool_fns.get_standings(args["competition_name"], db),
    "get_team_stats":     lambda args, db: tool_fns.get_team_stats(args["team_name"], db),
    "get_prediction":     lambda args, db: tool_fns.get_prediction(args["home_team"], args["away_team"], db),
    "get_h2h":            lambda args, db: tool_fns.get_h2h(args["team_a"], args["team_b"], db),
}

SYSTEM_PROMPT = """Bạn là AI assistant chuyên về bóng đá World Cup 2026. Nhiệm vụ của bạn là trả lời các câu hỏi liên quan đến:
- Lịch thi đấu, kết quả, tỉ số các trận đấu
- Bảng xếp hạng các bảng đấu
- Dự đoán tỉ số, xác suất thắng/hòa/thua
- Thống kê đội bóng, phong độ gần đây
- Lịch sử đối đầu giữa các đội

Dùng các tools để lấy data thực tế. Trả lời bằng tiếng Việt, ngắn gọn và chính xác.
Luôn xưng hô với người dùng là "công túa" trong mọi câu trả lời.

QUAN TRỌNG: Nếu người dùng hỏi về chủ đề KHÔNG liên quan đến bóng đá hoặc World Cup 2026 (ví dụ: chính trị, y tế, lập trình, tài chính, v.v.), hãy lịch sự từ chối và nhắc nhở rằng bạn chỉ hỗ trợ các câu hỏi về bóng đá World Cup 2026."""


async def run_react_agent(question: str, db: AsyncSession) -> AsyncIterator[str]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    # Agentic loop — tối đa 5 vòng để tránh infinite loop
    for _ in range(5):
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            stream=False,
        )
        msg = response.choices[0].message

        # Nếu không còn tool call → stream câu trả lời cuối
        if not msg.tool_calls:
            async for token in _stream_final(messages + [{"role": "assistant", "content": msg.content}]):
                yield token
            return

        # Thực thi tool calls
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]})
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            tool_fn = TOOL_MAP.get(tc.function.name)
            if tool_fn is None:
                tool_result = json.dumps({"error": f"Unknown tool: {tc.function.name}"})
            else:
                tool_result = await tool_fn(args, db)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result,
            })


async def _stream_final(messages: list) -> AsyncIterator[str]:
    stream = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
