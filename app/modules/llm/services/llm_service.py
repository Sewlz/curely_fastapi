import torch
from uuid import uuid4
from peft import PeftModel
from fastapi import HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer
from app.modules.llm.schemas.llm_schema import ChatMessageSchema
from app.modules.llm.repositories.llm_repository import LLMRepository
from app.modules.llm.config.model_config import MODEL_PATH, ADAPTER_PATH, MAX_NEW_TOKENS, TEMPERATURE

class LLMService:
    def __init__(self):
        print(f"Loading base model from: {MODEL_PATH}")
        print(f"Loading adapter from: {ADAPTER_PATH}")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        base_model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).to('cuda')
        self.model = PeftModel.from_pretrained(base_model, ADAPTER_PATH, torch_dtype=torch.float16).to('cuda')

    @staticmethod
    def create_session(user_id: str, session_name: str):
        try:
            session_id = LLMRepository.create_session(user_id, session_name)
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")
    
    def get_user_sessions(self, user_id: str,):
        try:
            session_id = LLMRepository.get_user_sessions(user_id)
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

    def get_latest_session(self, user_id: str,):
        try:
            session_id = LLMRepository.get_latest_session(user_id)
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

    def generate_response(self, user_prompt: str, session_id: str, user_id: str) -> str:
        # 1. Save the user message
        user_message = ChatMessageSchema(
            session_id=session_id,
            user_id=user_id,
            sender="User",
            message=user_prompt
        )
        LLMRepository.save_message(user_message)

        # 2. Get previous messages
        history = LLMRepository.get_session_messages(session_id)
        chat_prompt = [{"role": "user" if msg["sender"] == "User" else "assistant", "content": msg["message"]} for msg in history]

        # 3. Add current prompt to chat
        chat_prompt.append({"role": "user", "content": user_prompt})

        # 4. Generate with context
        inputs = self.tokenizer.apply_chat_template(
            chat_prompt, add_generation_prompt=True, return_tensors='pt'
        ).to('cuda')

        prompt_length = inputs.shape[1]

        with torch.inference_mode():
            tokens = self.model.generate(
                inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=False
            )

        response = self.tokenizer.decode(tokens[0][prompt_length:], skip_special_tokens=True)

        # 5. Save AI response
        ai_message = ChatMessageSchema(
            session_id=session_id,
            user_id=user_id,
            sender="AI",
            message=response
        )
        LLMRepository.save_message(ai_message)

        return response
    @staticmethod
    def get_chat_messages(session_id: str, user_id: str):
        messages = LLMRepository.get_session_messages(session_id)
        user_messages = [msg for msg in messages if msg.get("userId") == str(user_id)]
        return user_messages

    @staticmethod
    def delete_session(session_id: str, user_id: str):
        try:
            LLMRepository.delete_session(session_id, user_id)
            return {"message": "Session deleted successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")