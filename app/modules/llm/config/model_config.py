import os

# Define the base directory where config.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Correct the model path to reflect the intended directory structure and normalize the path
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "model_hub", "outputs", "checkpoint"))

# Other configuration settings
MAX_NEW_TOKENS = 128
TEMPERATURE = 0.7