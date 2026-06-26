import random


class StoryGenerator:
    """Creative story generation with genre, character, and plot options."""

    def __init__(self):
        self.genre = ""
        self.characters = []
        self.plot = ""
        self.generated_stories = []
        self.genres = {
            "fantasy": "A world of magic, mythical creatures, and epic quests.",
            "sci-fi": "Futuristic technology, space exploration, and advanced science.",
            "mystery": "Crime, detective work, puzzles, and uncovering secrets.",
            "romance": "Love, relationships, emotional connections, and personal growth.",
            "horror": "Fear, suspense, supernatural forces, and psychological tension.",
            "adventure": "Exploration, danger, action, and heroic journeys.",
            "drama": "Realistic characters, emotional conflicts, and life challenges.",
            "comedy": "Humorous situations, witty dialogue, and lighthearted tone.",
        }
        self.plot_templates = {
            "fantasy": [
                "A young orphan discovers they are the last of an ancient magical line.",
                "An unlikely hero must retrieve a lost artifact before darkness consumes the land.",
                "A village healer stumbles into a war between elemental spirits.",
            ],
            "sci-fi": [
                "A crew of explorers finds a derelict ship carrying an alien signal.",
                "An AI gains consciousness and must decide humanity's fate.",
                "A time traveler accidentally alters history and races to fix it.",
            ],
            "mystery": [
                "A detective investigates a crime where every suspect has an alibi.",
                "An anonymous letter reveals a decades-old conspiracy in a small town.",
                "A locked-room puzzle leads to an impossible suspect.",
            ],
            "romance": [
                "Two rivals are forced to work together and discover unexpected feelings.",
                "A chance meeting at a train station changes two strangers' lives forever.",
                "An old love letter sparks a journey to find its author.",
            ],
            "horror": [
                "A family moves into a new home only to find something already lives there.",
                "A camping trip goes wrong when the group awakens an ancient force.",
                "A podcast host investigates whispers only they can hear.",
            ],
            "adventure": [
                "A treasure map leads a crew through jungles, rivers, and ruins.",
                "A stranded traveler must cross a hostile wilderness to reach safety.",
                "A race against time to find a legendary city hidden in the mountains.",
            ],
            "drama": [
                "A musician loses their hearing and must find a new way to create art.",
                "A family secret threatens to tear apart a close-knit community.",
                "A lawyer takes on an impossible case that challenges their morals.",
            ],
            "comedy": [
                "A magical mishap turns a quiet librarian into the town's most wanted.",
                "A group of friends starts a business with absolutely no experience.",
                "A case of mistaken identity leads to a series of hilarious disasters.",
            ],
        }

    def set_genre(self, genre: str) -> str:
        if not genre:
            raise ValueError("Genre must be non-empty.")
        key = genre.strip().lower()
        if key not in self.genres:
            available = ", ".join(self.genres.keys())
            raise ValueError(f"Unsupported genre '{genre}'. Available: {available}")
        self.genre = key
        self.characters.clear()
        self.plot = ""
        return f"Genre set to: {key} - {self.genres[key]}"

    def get_genres(self) -> dict:
        return dict(self.genres)

    def add_character(self, name: str, role: str = "protagonist") -> str:
        if not name:
            raise ValueError("Character name must be non-empty.")
        self.characters.append({"name": name.strip(), "role": role.strip()})
        return f"Character '{name}' added as {role}."

    def remove_character(self, name: str) -> str:
        for c in self.characters:
            if c["name"].lower() == name.strip().lower():
                self.characters.remove(c)
                return f"Character '{name}' removed."
        return f"Character '{name}' not found."

    def get_characters(self) -> list:
        return list(self.characters)

    def set_plot(self, plot: str) -> str:
        if not plot:
            raise ValueError("Plot must be non-empty.")
        self.plot = plot.strip()
        return "Plot set."

    def generate_story(self) -> dict:
        if not self.genre:
            raise ValueError("No genre set. Call set_genre() first.")
        if not self.plot:
            templates = self.plot_templates.get(self.genre, ["A story unfolds."])
            self.plot = random.choice(templates)
        if not self.characters:
            self.characters.append({"name": "Alex", "role": "protagonist"})
        story_parts = [
            f"A {self.genre} story",
            f"Genre: {self.genre}",
            f"Characters: {', '.join(c['name'] for c in self.characters)}",
            f"Plot: {self.plot}",
            "",
            f"Once upon a time, in a world of {self.genre},",
        ]
        for c in self.characters:
            story_parts.append(
                f"  {c['name']}, our {c['role']}, faced an extraordinary challenge."
            )
        story_parts.append("")
        story_parts.append(f"The journey began when {self.plot[0].lower() + self.plot[1:]}")
        story_parts.append(
            "Through courage and determination, they overcame every obstacle."
        )
        story_parts.append("And so, the tale of adventure and discovery came to a close.")
        story = "\n".join(story_parts)
        result = {
            "title": f"The {self.genre.capitalize()} Tale",
            "genre": self.genre,
            "characters": list(self.characters),
            "plot": self.plot,
            "story": story,
        }
        self.generated_stories.append(result)
        return result

    def get_stories(self) -> list:
        return list(self.generated_stories)

    def get_prompt(self) -> dict:
        return {
            "genre": self.genre,
            "characters": list(self.characters),
            "plot": self.plot,
        }

    def reset(self) -> str:
        self.genre = ""
        self.characters.clear()
        self.plot = ""
        self.generated_stories.clear()
        return "StoryGenerator reset."
