import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "app", "model_hub", "outputs", "checkpoint")
MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7