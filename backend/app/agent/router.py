import re
from openai import AsyncOpenAI
from app.config import get_settings

openai_client = AsyncOpenAI(api_key=get_settings().openai_api_key)

_FOOTBALL_KEYWORDS = re.compile(
    r"trận|đấu|kết quả|tỉ số|tỷ số|bảng xếp hạng|lịch thi|world cup|wc|"
    r"bóng đá|đội bóng|cầu thủ|bàn thắng|vô địch|dự đoán|thắng|thua|hòa|"
    r"fifa|goal|match|score|standing|group|bảng|đội|vs|league",
    re.IGNORECASE,
)


def _is_clearly_football(question: str) -> bool:
    return bool(_FOOTBALL_KEYWORDS.search(question))

SYSTEM_PROMPT = """Bạn là bộ phân loại câu hỏi cho chatbot AI chuyên về bóng đá World Cup 2026.
Người dùng đang trò chuyện với chatbot bóng đá, vì vậy các câu hỏi ngắn như "hôm nay có trận nào?", "ai thắng?", "kết quả?", "bảng xếp hạng?" đều mặc định là hỏi về bóng đá.

Phân loại câu hỏi thành một trong 3 loại:
- "data_query": câu hỏi về thông tin thực tế (lịch thi đấu, tỉ số, kết quả, bảng xếp hạng, thống kê đội bóng, cầu thủ)
- "analysis_query": câu hỏi cần phân tích, dự đoán, so sánh, đánh giá về bóng đá
- "off_topic": câu hỏi RÕ RÀNG không liên quan gì đến bóng đá (ví dụ: nấu ăn, thời tiết, lập trình, v.v.)

Khi nghi ngờ, hãy chọn "data_query" hoặc "analysis_query" thay vì "off_topic".

Chỉ trả về đúng 1 trong 3 giá trị trên, không giải thích thêm."""


async def classify_query(question: str) -> str:
    if _is_clearly_football(question):
        return "data_query"

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        max_tokens=20,
        temperature=0,
    )
    result = response.choices[0].message.content.strip().lower()
    if result not in ("data_query", "analysis_query", "off_topic"):
        return "analysis_query"
    return result
