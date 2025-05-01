from fastapi import APIRouter, Depends, HTTPException
from app.common.security.auth import auth_guard
from app.modules.llm.services.llm_service import LLMService
from app.modules.llm.schemas.llm_schema import InputData, OutputData, ChatSessionCreate

router = APIRouter()
model_service = LLMService()

@router.post("/generate", response_model=OutputData)
async def generate(input_data: InputData, service: LLMService = Depends(lambda: model_service), user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        response = service.generate_response(input_data.prompt, input_data.session_id, user_id)
        return OutputData(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/create_session")
async def create_session(session: ChatSessionCreate, user=Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        session_id = model_service.create_session(user_id, session.session_name)
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str, user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        messages = model_service.get_chat_messages(session_id, user_id)
        return {"sessionId": session_id, "userId": user_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@router.get("/user/session/")
async def get_user_sessions(user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        sessions = model_service.get_user_sessions(user_id)
        return {"userId": user_id, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user sessions: {str(e)}")
    
@router.get("/user/latest_session/")
async def get_latest_session(user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        session_id = model_service.get_latest_session(user_id)
        if not session_id:
            return {"sessionId": None}
        
        return {"sessionId": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest session: {str(e)}")
    
@router.delete("/session/{session_id}")
async def delete_session(session_id: str, user = Depends(auth_guard)):
    try:
        user_id = user.get("uid")
        model_service.delete_session(session_id, user_id)
        return {"message": f"Session: {session_id} from user: {user_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")