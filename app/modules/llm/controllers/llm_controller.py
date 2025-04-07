from fastapi import APIRouter, Depends, HTTPException, Form
from app.modules.llm.schemas.llm_schema import InputData, OutputData, ChatSessionCreate
from app.modules.llm.services.llm_service import LLMService
from app.common.security.auth import auth_guard
router = APIRouter()
model_service = LLMService()

@router.post("/generate", response_model=OutputData)
async def generate(input_data: InputData, service: 
                   LLMService = Depends(lambda: model_service),
                   user_id: str = Depends(auth_guard)):
    try:
        response = service.generate_response(input_data.prompt, input_data.session_id, user_id)
        return OutputData(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/create_session")
async def create_session(session: ChatSessionCreate,user_id: str = Depends(auth_guard) ):
    try:
        session_id = model_service.create_session(
            user_id,
            session.session_name
        )
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str, user_id: str = Depends(auth_guard)):
    try:
        messages = model_service.get_chat_messages(session_id, user_id)
        return {"sessionId": session_id, "userId": user_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")