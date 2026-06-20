import json
from typing import AsyncIterator
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.agent.react_agent import TOOLS_SCHEMA, TOOL_MAP

openai_client = AsyncOpenAI(api_key=get_settings().openai_api_key)

ANALYSIS_SYSTEM = """Bạn là chuyên gia phân tích bóng đá. Dùng tools để thu thập data,
sau đó đưa ra phân tích sâu, có lý luận rõ ràng. Trả lời bằng tiếng Việt."""

CRITIC_SYSTEM = """Bạn là critic review câu trả lời phân tích bóng đá.
Kiểm tra: có thiếu data quan trọng không? Có mâu thuẫn logic không?
Nếu cần bổ sung, nêu cụ thể. Nếu đã đủ, trả lời: "OK"."""


async def _collect_data(question: str, db: AsyncSession) -> tuple[list, str]:
    """Phase 1: Thu thập data qua tool calls."""
    messages = [
        {"role": "system", "content": ANALYSIS_SYSTEM},
        {"role": "user", "content": f"Thu thập data cần thiết để trả lời: {question}"},
    ]
    for _ in range(3):
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            stream=False,
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            break
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]})
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = await TOOL_MAP[tc.function.name](args, db)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    data_summary = "\n".join(
        m["content"] for m in messages if m["role"] == "tool"
    )
    return messages, data_summary


async def run_reflection_agent(question: str, db: AsyncSession) -> AsyncIterator[str]:
    messages, data_summary = await _collect_data(question, db)

    # Phase 2: Generate draft analysis
    messages.append({"role": "user", "content": f"Bây giờ hãy phân tích và trả lời: {question}"})
    draft_response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        stream=False,
    )
    draft = draft_response.choices[0].message.content

    # Phase 3: Self-critique
    critique_response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content": f"Câu hỏi: {question}\n\nData: {data_summary}\n\nCâu trả lời draft:\n{draft}"},
        ],
        temperature=0,
        stream=False,
    )
    critique = critique_response.choices[0].message.content.strip()

    # Phase 4: Refine nếu cần, stream kết quả cuối
    if critique.upper() == "OK":
        final_messages = messages + [{"role": "assistant", "content": draft}]
    else:
        final_messages = messages + [
            {"role": "assistant", "content": draft},
            {"role": "user", "content": f"Hãy cải thiện dựa trên nhận xét này: {critique}"},
        ]

    stream = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=final_messages,
        temperature=0.3,
        stream=True,
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""
