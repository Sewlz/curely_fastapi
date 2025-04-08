import os

# Define the base directory where config.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "model_hub", "tiny_llama", "TinyLlama-1.1B-Chat-v1.0"))
ADAPTER_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "model_hub", "tinyllama-medical-sft"))

MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7
