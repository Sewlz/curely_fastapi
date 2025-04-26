import re
from app.modules.llm.config.keywords import *
class MedicalChatFilter:
    def __init__(self):
        self.greeting_keywords = greeting_keywords
        self.small_talk_keywords = small_talk_keywords
        self.sensitive_keywords = sensitive_keywords
        self.non_medical_keywords = non_medical_keywords
        self.medical_keywords = medical_keywords
        self.identity_keywords = identity_keywords

    def detect_intent(self, text: str) -> str:
        cleaned = text.lower().strip()

        if any(kw in cleaned for kw in self.sensitive_keywords):
            return "emergency"

        if any(kw in cleaned for kw in self.non_medical_keywords):
            return "off_topic"

        if any(re.fullmatch(r'\b' + re.escape(kw) + r'\b', cleaned, re.IGNORECASE) for kw in greeting_keywords):
            return "greeting"

        if any(kw in cleaned for kw in self.small_talk_keywords):
            return "small_talk"
        
        if any(kw in cleaned for kw in self.medical_keywords):
            return "medical_query"

        if any(kw in cleaned for kw in self.identity_keywords):
            return "identity"

        return "unknown"

    def filter_input(self, user_input: str) -> dict:
        intent = self.detect_intent(user_input)
        response = ""
        should_continue = True

        if intent == "emergency":
            response = (
                "I'm really sorry you're feeling this way. Please talk to someone immediately — "
                "you can contact a doctor or call your local emergency services or mental health hotline."
            )
            should_continue = False

        elif intent == "off_topic":
            response = (
                "I'm here to help with medical questions. Could you please rephrase your query "
                "to be more health-related?"
            )
            should_continue = False

        elif intent == "greeting":
            response = "Hello! I'm here to help with medical questions. What would you like to know?"
            should_continue = False

        elif intent == "small_talk":
            response = (
                "I'm a medical assistant chatbot, so I'm best at answering health-related questions. "
                "How can I assist you today?"
            )
            should_continue = False

        elif intent == "identity":
            response = (
                "I am a medical-assisted chatbot, developed using the Tiny-Llama model by Team Atomic. "
                "My purpose is to provide accurate and reliable answers to your questions. "
                "What would you like to know today?"
            )
            should_continue = False

        elif intent == "medical_query":
            response = "Thanks for your question. Here's the answer to your medical query:"
            should_continue = True

        elif intent == "unknown":
            response = "I will try my best to answer your question. Here's the answer:"
            should_continue = True

        return {
            "intent": intent,
            "response": response,
            "allow_model_response": should_continue
        }
