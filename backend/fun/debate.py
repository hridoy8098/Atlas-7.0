import random


class DebateEngine:
    """AI-powered debate engine for generating pro/con arguments on any topic."""

    def __init__(self):
        self.topic = ""
        self.pro_arguments = []
        self.con_arguments = []
        self.history = []

    def set_topic(self, topic: str) -> str:
        if not topic or not isinstance(topic, str):
            raise ValueError("Topic must be a non-empty string.")
        self.topic = topic.strip()
        self.pro_arguments.clear()
        self.con_arguments.clear()
        entry = {"action": "set_topic", "topic": self.topic}
        self.history.append(entry)
        return f"Debate topic set to: {self.topic}"

    def add_argument(self, side: str, argument: str) -> str:
        if not argument or not isinstance(argument, str):
            raise ValueError("Argument must be a non-empty string.")
        side = side.lower()
        if side not in ("pro", "con"):
            raise ValueError("Side must be 'pro' or 'con'.")
        entry = {"side": side, "argument": argument}
        if side == "pro":
            self.pro_arguments.append(entry)
        else:
            self.con_arguments.append(entry)
        self.history.append({"action": "add_argument", **entry})
        return f"Added {side} argument: {argument[:60]}..."

    def get_pro_arguments(self) -> list:
        return list(self.pro_arguments)

    def get_con_arguments(self) -> list:
        return list(self.con_arguments)

    def generate_counterargument(self, argument: str) -> str:
        rebuttals = [
            "While that point has merit, it overlooks the broader context.",
            "This argument assumes a premise that may not hold in all cases.",
            "An opposing viewpoint suggests the opposite is more likely.",
            "Evidence for this claim is mixed, and alternative interpretations exist.",
            "This argument can be turned on its head when considering long-term effects.",
        ]
        return random.choice(rebuttals)

    def summarize(self) -> dict:
        return {
            "topic": self.topic,
            "pro_count": len(self.pro_arguments),
            "con_count": len(self.con_arguments),
            "pro_arguments": [a["argument"] for a in self.pro_arguments],
            "con_arguments": [a["argument"] for a in self.con_arguments],
        }

    def get_history(self) -> list:
        return list(self.history)

    def reset(self) -> str:
        self.topic = ""
        self.pro_arguments.clear()
        self.con_arguments.clear()
        self.history.clear()
        return "Debate engine has been reset."
