import uuid
from datetime import datetime
from fastapi import HTTPException
from app.common.database.supabase import supabase
from app.modules.llm.schemas.llm_schema import ChatMessageSchema

class LLMRepository:
    @staticmethod
    def close_other_sessions(user_id: str, active_session_id: str):
        existing_sessions = supabase.table("chatSessions") \
            .select("sessionId") \
            .eq("userId", user_id) \
            .eq("status", "active") \
            .neq("sessionId", active_session_id) \
            .execute()

        for session in existing_sessions.data:
            supabase.table("chatSessions") \
                .update({"status": "closed"}) \
                .eq("sessionId", session["sessionId"]) \
                .execute()

    @staticmethod
    def create_session(user_id: str, session_name: str) -> str:
        session_id = str(uuid.uuid4())
        LLMRepository.close_other_sessions(user_id, session_id)

        supabase.table("chatSessions").insert({
            "sessionId": session_id,
            "userId": user_id,
            "sessionName": session_name,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }).execute()
        return session_id
    
    @staticmethod
    def get_user_sessions(user_id: str) -> str:
        sessions = supabase.table("chatSessions").select("*").eq("userId", user_id).order("created_at", desc=True).execute()
        return sessions
    
    @staticmethod
    def get_latest_session(user_id: str) -> str:
        response = (
            supabase
            .table("chatSessions")
            .select("sessionId")
            .eq("userId", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        data = response.data
        if data and len(data) > 0:
            return data[0]["sessionId"]
        raise ValueError("No sessions found for the given user.")


    @staticmethod
    def get_session_messages(session_id: str):
        result = supabase.table("chatMessages") \
            .select("*") \
            .eq("sessionId", session_id) \
            .order("timestamp", desc=False) \
            .execute()
        return result.data

    @staticmethod
    def save_message(message: ChatMessageSchema):
        supabase.table("chatMessages").insert({
            "messageId": str(uuid.uuid4()),
            "sessionId": message.session_id,
            "userId": message.user_id,
            "sender": message.sender,
            "message": message.message,
            "timestamp": datetime.now().isoformat()
        }).execute()

    @staticmethod
    def delete_session(session_id: str, user_id: str,):
        try:
            existing = supabase.table("chatSessions").select("*").eq("userId", user_id).eq("sessionId", session_id).execute()
            if not existing.data:
                raise HTTPException(status_code=404, detail="Chat session not found")
            response = supabase.table("chatSessions").delete().eq("userId", user_id).eq("sessionId", session_id).execute()  
            print(response)
        except Exception as e:
            print(e) 