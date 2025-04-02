from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from app.modules.llm.config.model_config import MODEL_PATH, MAX_NEW_TOKENS, TEMPERATURE

class TinyLlamaService:
    def __init__(self):
        print(f"Loading model from: {MODEL_PATH}")  # Debugging log
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True, repo_type="local")
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map="auto")

    def generate_response(self, prompt: str) -> str:
        chat_prompt = [{'role': 'user', 'content': prompt}]
        inputs = self.tokenizer.apply_chat_template(
            chat_prompt, add_generation_prompt=False, return_tensors='pt'
        )

        prompt_length = inputs.shape[1]
        inputs = inputs.to(self.model.device)

        with torch.no_grad():
            tokens = self.model.generate(
                inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True
            )

        response = self.tokenizer.decode(tokens[0][prompt_length:], skip_special_tokens=True)
        return response
