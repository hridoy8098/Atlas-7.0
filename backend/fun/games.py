# backend/fun/games.py — Atlas 7.0 Games Engine
# In-memory game sessions: number guessing, hangman, tic-tac-toe, word scramble.

import random
from typing import Dict, Optional

HANGMAN_WORDS = [
    "BANGLADESH", "DHAKA", "SUNDARBAN", "TIGER", "RIVER", "MONSOON", "MANGO",
    "KITE", "BRIDGE", "POET", "LANGUAGE", "MOUNTAIN", "FOREST", "OCEAN",
    "ROCKET", "GARDEN", "LIBRARY", "MUSIC", "DANCING", "THUNDER",
]

SCRAMBLE_WORDS = [
    "PYTHON", "LAUNCH", "ORANGE", "WIZARD", "CASTLE", "JUNGLE", "PLANET",
    "ROCKET", "GUITAR", "MARBLE", "PIRATE", "TEMPLE", "VILLAGE", "WINTER",
]

MAX_WRONG_GUESSES = 6


class NumberGuessGame:
    """Computer picks a secret number; player guesses with higher/lower hints."""

    def __init__(self, low: int = 1, high: int = 100):
        self.low, self.high = low, high
        self.secret = random.randint(low, high)
        self.attempts = 0
        self.finished = False

    def guess(self, number: int) -> str:
        if self.finished:
            return "Game already finished | গেম আগেই শেষ হয়েছে"
        self.attempts += 1
        if number == self.secret:
            self.finished = True
            return (f"Correct! The number was {self.secret} in {self.attempts} "
                    f"attempts! | ঠিক হয়েছে! {self.attempts} বারে উত্তর!")
        hint = "higher | বড়" if number < self.secret else "lower | ছোট"
        return f"Wrong! Go {hint} ({self.low}-{self.high}) | ভুল! সংখ্যাটি {hint}"


class HangmanGame:
    def __init__(self, word: Optional[str] = None):
        self.word = (word or random.choice(HANGMAN_WORDS)).upper()
        self.guessed = set()
        self.wrong = set()
        self.max_wrong = MAX_WRONG_GUESSES

    @property
    def finished(self) -> bool:
        return self.lost or self.won

    @property
    def won(self) -> bool:
        return all(ch in self.guessed for ch in self.word if ch.isalpha())

    @property
    def lost(self) -> bool:
        return len(self.wrong) >= self.max_wrong

    def display(self) -> str:
        return " ".join(ch if ch in self.guessed else ("_" if ch.isalpha() else ch)
                        for ch in self.word)

    def guess(self, letter: str) -> str:
        letter = (letter or "").strip().upper()
        if self.finished:
            return f"Game over! Word was: {self.word} | খেলা শেষ! শব্দ: {self.word}"
        if not letter.isalpha() or len(letter) != 1:
            return "Enter a single letter | একটি অক্ষর লিখুন"
        if letter in self.guessed or letter in self.wrong:
            return f"Already tried '{letter}' | আগেই চেষ্টা করা হয়েছে"
        if letter in self.word:
            self.guessed.add(letter)
            if self.won:
                return f"You won! {self.word} | আপনি জিতেছেন! {self.word}"
            return f"Good! '{letter}' is in the word. {self.display()} | ভালো! অক্ষরটি আছে"
        self.wrong.add(letter)
        if self.lost:
            return f"Lost! The word was {self.word} | হেরে গেছেন! শব্দটি ছিল {self.word}"
        left = self.max_wrong - len(self.wrong)
        return f"No '{letter}'. {left} lives left | নেই। {left}বার বাকি। {self.display()}"


class TicTacToeGame:
    EMPTY, H, O = " ", "X", "O"
    WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

    def __init__(self):
        self.board = [self.EMPTY] * 9
        self.finished = False
        self.result: Optional[str] = None

    def _winner(self) -> Optional[str]:
        for a, b, c in self.WINS:
            if self.board[a] != self.EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def _ai_move(self) -> int:
        # win > block > center > corner > random
        for me in (self.O, self.H):
            for a, b, c in self.WINS:
                line = [self.board[a], self.board[b], self.board[c]]
                if line.count(me) == 2 and self.EMPTY in line:
                    return [a, b, c][line.index(self.EMPTY)]
        if self.board[4] == self.EMPTY:
            return 4
        corners = [i for i in (0, 2, 6, 8) if self.board[i] == self.EMPTY]
        if corners:
            return random.choice(corners)
        free = [i for i, v in enumerate(self.board) if v == self.EMPTY]
        return random.choice(free)

    def render(self) -> str:
        rows = ["".join(self.board[i:i+3]) for i in (0, 3, 6)]
        return "\n".join("|".join(r) for r in rows)

    def move(self, position: int) -> str:
        try:
            pos = int(position) - 1
        except (TypeError, ValueError):
            return "Give a position 1-9 | ১-৯ এর মধ্যে অবস্থান দিন"
        if self.finished:
            return f"Game over: {self.result} | খেলা শেষ"
        if not 0 <= pos < 9 or self.board[pos] != self.EMPTY:
            return "Invalid cell | অবৈধ ঘর"
        self.board[pos] = self.H
        if w := self._winner():
            self.finished, self.result = True, "You win! | আপনি জিতেছেন!"
            return f"{self.render()}\n{self.result}"
        if all(v != self.EMPTY for v in self.board):
            self.finished, self.result = True, "Draw! | অমীমাংসিত!"
            return f"{self.render()}\n{self.result}"
        ai = self._ai_move()
        self.board[ai] = self.O
        if w := self._winner():
            self.finished, self.result = True, "AI wins! | AI জিতেছে!"
            return f"{self.render()}\n{self.result}"
        return f"{self.render()}\nYour turn (1-9) | আপনার পালা"


class WordScrambleGame:
    def __init__(self, word: Optional[str] = None):
        self.word = (word or random.choice(SCRAMBLE_WORDS)).upper()
        letters = list(self.word)
        random.shuffle(letters)
        while "".join(letters) == self.word and len(letters) > 2:
            random.shuffle(letters)
        self.scrambled = "".join(letters)
        self.solved = False
        self.attempts = 0

    def solve(self, answer: str) -> str:
        self.attempts += 1
        if (answer or "").strip().upper() == self.word:
            self.solved = True
            return f"Solved in {self.attempts} tries! Correct: {self.word} | সমাধান হয়েছে!"
        return "Not quite, try again! | সঠিক নয়, আবার চেষ্টা করুন!"


class GameSessionManager:
    """Keeps active game sessions by game type."""

    _FACTORIES = {
        "number": NumberGuessGame, "guess_number": NumberGuessGame,
        "hangman": HangmanGame,
        "tic_tac_toe": TicTacToeGame, "tictactoe": TicTacToeGame,
        "scramble": WordScrambleGame, "word_scramble": WordScrambleGame,
    }

    def __init__(self):
        self.sessions: Dict[str, object] = {}

    def start(self, game_type: str) -> tuple:
        key = str(game_type or "").strip().lower()
        factory = self._FACTORIES.get(key)
        if factory is None:
            supported = ", ".join(sorted(set(self._FACTORIES)))
            raise ValueError(f"Unknown game '{game_type}'. Supported: {supported}")
        game = factory()
        self.sessions[key] = game
        return key, game

    def get(self, game_type: str):
        key = str(game_type or "").strip().lower()
        game = self.sessions.get(key)
        if game is None:
            raise ValueError(f"No active '{key}' game. Start one first! | কোনো গেম চালু নেই")
        return game

    def end(self, game_type: str) -> bool:
        return self.sessions.pop(str(game_type or "").strip().lower(), None) is not None


_manager: Optional[GameSessionManager] = None


def get_game_manager() -> GameSessionManager:
    global _manager
    if _manager is None:
        _manager = GameSessionManager()
    return _manager
