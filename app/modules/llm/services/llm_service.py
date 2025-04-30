import torch
from uuid import uuid4
from peft import PeftModel
from fastapi import HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer
from app.modules.llm.schemas.llm_schema import ChatMessageSchema
from app.modules.llm.config.chat_filter import MedicalChatFilter
from app.modules.llm.repositories.llm_repository import LLMRepository
from app.modules.llm.config.model_config import MODEL_PATH, ADAPTER_PATH, MAX_NEW_TOKENS, TEMPERATURE

class LLMService:
    def __init__(self):
        print(f"Loading base model from: {MODEL_PATH}")
        print(f"Loading adapter from: {ADAPTER_PATH}")
        self.filter = MedicalChatFilter()  
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

    def get_latest_session(self, user_id: str):
        try:
            session_id = LLMRepository.get_latest_session(user_id)
            if not session_id:
                # Trả về None nếu không tìm thấy session
                return None
            return session_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")
    

    def generate_response(self, user_prompt: str, session_id: str, user_id: str) -> str:
        filtered = self._filter_input(user_prompt)

        print(f"Filtered Output: {filtered}")
        self._save_message(session_id, user_id, "User", user_prompt)

        if not filtered["allow_model_response"]:
            return self._handle_filtered_input(session_id, user_id, filtered)
        
        chat_prompt = self._prepare_chat_prompt(session_id, user_prompt)

        inputs, prompt_length = self._tokenize_chat_prompt(chat_prompt)

        response = self._generate_from_model(inputs, prompt_length)

        self._save_message(session_id, user_id, "AI", response)
        
        return response

    def _filter_input(self, user_prompt: str):
        return self.filter.filter_input(user_prompt)

    def _save_message(self, session_id: str, user_id: str, sender: str, message: str):
        message_obj = ChatMessageSchema(
            session_id=session_id,
            user_id=user_id,
            sender=sender,
            message=message
        )
        LLMRepository.save_message(message_obj)

    def _handle_filtered_input(self, session_id: str, user_id: str, filtered: dict) -> str:

        self._save_message(session_id, user_id, "AI", filtered["response"])
        return filtered["response"]

    def _prepare_chat_prompt(self, session_id: str, user_prompt: str):
        history = LLMRepository.get_session_messages(session_id)
        
        # Start with the latest message and build backwards
        chat_prompt = [{"role": "user" if msg["sender"] == "User" else "assistant", "content": msg["message"]} for msg in reversed(history)]
        chat_prompt = chat_prompt[:30]  # Limit to last N messages first (arbitrary cutoff to avoid over-fetching)
        chat_prompt = list(reversed(chat_prompt))  # Restore original order
        chat_prompt.append({"role": "user", "content": user_prompt})

        # Now iteratively truncate until under token limit
        while True:
            inputs = self.tokenizer.apply_chat_template(
                chat_prompt, add_generation_prompt=True, return_tensors='pt'
            ).to('cuda')
            if inputs.shape[1] <= 2048:
                break
            if len(chat_prompt) > 1:
                chat_prompt.pop(0)  # Remove the oldest message
            else:
                break

        return chat_prompt

    def _tokenize_chat_prompt(self, chat_prompt: list):
        inputs = self.tokenizer.apply_chat_template(
            chat_prompt, add_generation_prompt=True, return_tensors='pt'
        ).to('cuda')

        prompt_length = inputs.shape[1]

        return inputs, prompt_length

    def _generate_from_model(self, inputs, prompt_length: int) -> str:
        with torch.inference_mode():
            tokens = self.model.generate(
                inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2
            )
        return self.tokenizer.decode(tokens[0][prompt_length:], skip_special_tokens=True)
    
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