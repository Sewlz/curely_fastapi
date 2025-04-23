import re

class MedicalChatFilter:
    def __init__(self):
        self.greeting_keywords = {"hi", "hello", "hey", "good morning", "good evening"}
        self.small_talk_keywords = {"how are you", "what's up", "are you real", "tell me a joke"}
        self.sensitive_keywords = {
            "suicide", "self harm", "kill myself", "hurting", "abuse", "overdose", "rape"
        }
        self.non_medical_keywords = {
            "weather", "movie", "celebrity", "game", "news", "recipe", "travel"
        }

    def detect_intent(self, text: str) -> str:
        cleaned = text.lower().strip()

        if any(kw in cleaned for kw in self.sensitive_keywords):
            return "emergency"

        if any(kw in cleaned for kw in self.non_medical_keywords):
            return "off_topic"

        if any(greet in cleaned for greet in self.greeting_keywords):
            return "greeting"

        if any(talk in cleaned for talk in self.small_talk_keywords):
            return "small_talk"

        if re.search(r'\b(who are you|what can you do)\b', cleaned):
            return "identity"

        if re.search(r'\b(symptom|pain|headache|fever|medication|dose|allergy|prescription|side effect|disease|treatment)\b', cleaned):
            return "medical_query"

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
                "I'm a medical assistant chatbot, so I'm best at answering health-related questions. "
                "How can I assist you today?"
            )
            should_continue = False

        elif intent == "medical_query":
            response = "" 
            should_continue = True

        elif intent == "unknown":
            response = (
                "I'm not sure I understood your question. Could you please rephrase it in a health-related context?"
            )
            should_continue = False

        return {
            "intent": intent,
            "response": response,
            "allow_model_response": should_continue
        }
