from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from fastapi import HTTPException
from uuid import uuid4
from app.modules.llm.config.model_config import MODEL_PATH, MAX_NEW_TOKENS, TEMPERATURE
from app.modules.llm.repositories.llm_repository import LLMRepository
from app.modules.llm.schemas.llm_schema import ChatMessageSchema

class LLMService:
    def __init__(self):
        print(f"Loading model from: {MODEL_PATH}")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16).to('cuda')

    def create_session(user_id: str, session_name: str):
        try:
            session_id = LLMRepository.create_session(user_id, session_name)
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
        user_messages = [msg for msg in messages if msg.get("userId") == user_id]
        return user_messages