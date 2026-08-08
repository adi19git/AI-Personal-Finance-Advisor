from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import chat_with_agent

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Send a message to the AI finance advisor and receive a response.
    """
    try:
        reply, session_id, tool_calls = chat_with_agent(
            db=db,
            user_id=current_user.id,
            user_message=req.message,
            session_id=req.session_id or "",
        )
        return ChatResponse(reply=reply, session_id=session_id, tool_calls=tool_calls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
