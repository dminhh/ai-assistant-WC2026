# app/routers/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.agent.router import classify_query
from app.agent.react_agent import run_react_agent
from app.agent.reflection_agent import run_reflection_agent

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    async def event_stream():
        query_type = await classify_query(body.message)

        if query_type == "data_query":
            agent_gen = run_react_agent(body.message, db)
        else:
            agent_gen = run_reflection_agent(body.message, db)

        async for token in agent_gen:
            yield f"data: {token}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
