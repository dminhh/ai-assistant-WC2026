from openai import AsyncOpenAI
from app.config import get_settings

openai_client = AsyncOpenAI(api_key=get_settings().openai_api_key)

SYSTEM_PROMPT = """Phân loại câu hỏi thành một trong 2 loại:
- "data_query": câu hỏi về thông tin thực tế (lịch thi đấu, tỉ số, bảng xếp hạng, thống kê)
- "analysis_query": câu hỏi cần phân tích, dự đoán, so sánh, giải thích

Chỉ trả về đúng 1 trong 2 giá trị trên, không giải thích thêm."""


async def classify_query(question: str) -> str:
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
    if result not in ("data_query", "analysis_query"):
        return "analysis_query"
    return result
