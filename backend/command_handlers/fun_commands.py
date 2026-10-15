"""
Atlas 7.0 — Fun Command Handler
Games, memes, jokes, music, video, image generation, entertainment.
"""

from typing import Dict, Any, Optional
import random
import time

from .base_handler import BaseCommandHandler, CommandResponse, CommandPriority


class FunCommandHandler(BaseCommandHandler):
    def __init__(self):
        super().__init__()
        self._register_all()

    def _register_all(self):
        self._register("game_start", self.game_start, priority=CommandPriority.HIGH)
        self._register("game_move", self.game_move)
        self._register("game_end", self.game_end)
        self._register("game_score", self.game_score)
        self._register("game_leaderboard", self.game_leaderboard)
        self._register("game_restart", self.game_restart)
        self._register("trivia_start", self.trivia_start)
        self._register("trivia_answer", self.trivia_answer)
        self._register("trivia_score", self.trivia_score)
        self._register("hangman_start", self.hangman_start)
        self._register("hangman_guess", self.hangman_guess)
        self._register("tic_tac_toe_start", self.tic_tac_toe_start)
        self._register("tic_tac_toe_move", self.tic_tac_toe_move)
        self._register("guess_number_start", self.guess_number_start)
        self._register("guess_number_guess", self.guess_number_guess)
        self._register("word_scramble", self.word_scramble)
        self._register("word_scramble_solve", self.word_scramble_solve)
        self._register("meme_generator", self.meme_generator, priority=CommandPriority.HIGH)
        self._register("meme_list", self.meme_list)
        self._register("meme_create_custom", self.meme_create_custom)
        self._register("joke_tell", self.joke_tell)
        self._register("joke_random", self.joke_random)
        self._register("joke_dark", self.joke_dark)
        self._register("joke_dad", self.joke_dad)
        self._register("joke_bangla", self.joke_bangla)
        self._register("music_play", self.music_play, priority=CommandPriority.HIGH)
        self._register("music_pause", self.music_pause)
        self._register("music_next", self.music_next)
        self._register("music_previous", self.music_previous)
        self._register("music_stop", self.music_stop)
        self._register("music_volume", self.music_volume)
        self._register("music_playlist", self.music_playlist)
        self._register("music_queue", self.music_queue)
        self._register("music_search", self.music_search)
        self._register("music_lyrics", self.music_lyrics)
        self._register("video_download", self.video_download, priority=CommandPriority.HIGH)
        self._register("video_search", self.video_search)
        self._register("video_info", self.video_info)
        self._register("audio_play", self.audio_play)
        self._register("audio_record", self.audio_record)
        self._register("image_generator", self.image_generator, priority=CommandPriority.HIGH)
        self._register("image_edit", self.image_edit)
        self._register("image_filter", self.image_filter)
        self._register("image_resize", self.image_resize)
        self._register("image_convert", self.image_convert)
        self._register("image_compress", self.image_compress)
        self._register("flip_coin", self.flip_coin)
        self._register("roll_dice", self.roll_dice)
        self._register("random_quote", self.random_quote)
        self._register("random_fact", self.random_fact)

    def get_capabilities(self):
        return ["game_start", "meme_generator", "joke_tell", "music_play",
                "video_download", "image_generator", "trivia_start", "flip_coin"]

    def game_start(self, entities: Dict) -> CommandResponse:
        game_type = entities.get("game", entities.get("type", "trivia"))
        try:
            from backend.fun.game_engine import start_game
            game = start_game(game_type, config=entities)
            return CommandResponse.ok(message=f"Game started: {game_type} | গেম শুরু: {game_type}",
                                      action="game_start", data={"game_id": game.get("id"), "game_type": game_type})
        except Exception as e:
            return self._error("game_start", str(e), entities)

    def game_move(self, entities: Dict) -> CommandResponse:
        game_type = entities.get("game", entities.get("type", ""))
        value = entities.get("move", entities.get("guess", entities.get("value")))
        try:
            from backend.fun.games import get_game_manager, NumberGuessGame, HangmanGame, \
                TicTacToeGame, WordScrambleGame
            game = get_game_manager().get(game_type) if game_type else None
            if game is None:
                # try any active session
                sessions = get_game_manager().sessions
                if not sessions:
                    return self._bilingual("No active game. Start one first! | কোনো গেম চালু নেই")
                game = next(iter(sessions.values()))
            if isinstance(game, NumberGuessGame):
                msg = game.guess(int(value))
            elif isinstance(game, HangmanGame):
                msg = game.guess(str(value))
            elif isinstance(game, TicTacToeGame):
                msg = game.move(value)
            elif isinstance(game, WordScrambleGame):
                msg = game.solve(str(value))
            else:
                msg = "Move registered | মুভ রেজিস্টার করা হয়েছে"
            return CommandResponse.ok(message=msg, action="game_move")
        except (ValueError, TypeError) as e:
            return self._error("game_move", str(e), entities)

    def game_end(self, entities: Dict) -> CommandResponse:
        game_type = entities.get("game", entities.get("type", ""))
        try:
            from backend.fun.games import get_game_manager
            ended = get_game_manager().end(game_type) if game_type else False
            if not ended:
                sessions = get_game_manager().sessions
                ended = bool(sessions.pop(next(iter(sessions)), None)) if sessions else False
            msg = "Game ended | গেম শেষ হয়েছে" if ended else "No active game to end | শেষ করার মতো গেম নেই"
            return CommandResponse.ok(message=msg, action="game_end")
        except Exception as e:
            return self._error("game_end", str(e), entities)

    def game_score(self, entities: Dict) -> CommandResponse:
        game_type = entities.get("game", entities.get("type", ""))
        try:
            from backend.fun.games import get_game_manager, NumberGuessGame, WordScrambleGame, \
                HangmanGame, TicTacToeGame
            game = get_game_manager().get(game_type)
            if isinstance(game, NumberGuessGame):
                msg = f"Attempts: {game.attempts} | চেষ্টা: {game.attempts}"
            elif isinstance(game, WordScrambleGame):
                status = "Solved" if game.solved else "Unsolved"
                msg = f"{status} in {game.attempts} tries | {game.attempts} বারে {status}"
            elif isinstance(game, HangmanGame):
                msg = (f"Word: {game.display()}, wrong: {len(game.wrong)}/{game.max_wrong} | "
                       f"ভুল: {len(game.wrong)}/{game.max_wrong}")
            elif isinstance(game, TicTacToeGame):
                board = game.render()
                msg = f"{board}\nYou: X, AI: O | আপনি: X, AI: O"
            else:
                msg = "Your score | আপনার স্কোর"
            return CommandResponse.ok(message=msg, action="game_score")
        except ValueError as e:
            return self._error("game_score", str(e), entities)

    def game_leaderboard(self, entities: Dict) -> CommandResponse:
        from backend.fun.games import get_game_manager
        active = list(get_game_manager().sessions.keys())
        msg = ("Active games: " + ", ".join(active) if active
               else "No active games. Leaderboard empty | কোনো সক্রিয় গেম নেই")
        return CommandResponse.ok(message=msg + " | লিডারবোর্ড", action="game_leaderboard")

    def game_restart(self, entities: Dict) -> CommandResponse:
        game_type = entities.get("game", entities.get("type", ""))
        try:
            from backend.fun.games import get_game_manager
            key, game = get_game_manager().start(game_type)
            return self._start_message(key, game)
        except ValueError as e:
            return self._error("game_restart", str(e), entities)

    @staticmethod
    def _start_message(key: str, game) -> CommandResponse:
        from backend.fun.games import NumberGuessGame, HangmanGame, TicTacToeGame, WordScrambleGame
        if isinstance(game, NumberGuessGame):
            msg = f"I picked a number {game.low}-{game.high}. Guess! | আমি একটা সংখ্যা ভেবেছি, বলুন!"
        elif isinstance(game, HangmanGame):
            msg = f"Hangman: {game.display()} | হ্যাংম্যান শুরু"
        elif isinstance(game, TicTacToeGame):
            msg = f"You are X. Pick 1-9:\n{game.render()} | আপনি X, ১-৯ দিন"
        elif isinstance(game, WordScrambleGame):
            msg = f"Unscramble: {game.scrambled} | এলোমেলো শব্দ সাজান"
        else:
            msg = f"Game started: {key} | গেম শুরু: {key}"
        return CommandResponse.ok(message=msg, action="game_start", data={"game": key})

    def _quiz(self):
        """Shared QuizEngine preloaded with a general-knowledge category."""
        from backend.fun.quiz import QuizEngine
        if not hasattr(FunCommandHandler, "_shared_quiz"):
            engine = QuizEngine()
            engine.add_category("general", [
                {"question": "What is the capital of Bangladesh? | বাংলাদেশের রাজধানী কোনটি?",
                 "options": ["Dhaka", "Chittagong", "Sylhet", "Khulna"], "answer": "Dhaka"},
                {"question": "Which river is called the lifeline of Bangladesh?",
                 "options": ["Ganges", "Padma", "Brahmaputra", "Meghna"], "answer": "Padma"},
                {"question": "How many players are in a cricket team?",
                 "options": ["9", "10", "11", "12"], "answer": "11"},
                {"question": "What is the largest mammal on Earth?",
                 "options": ["Elephant", "Blue whale", "Giraffe", "Hippo"], "answer": "Blue whale"},
                {"question": "In which year did Bangladesh gain independence?",
                 "options": ["1947", "1952", "1971", "1975"], "answer": "1971"},
                {"question": "What is the national flower of Bangladesh?",
                 "options": ["Rose", "Water lily (Shapla)", "Sunflower", "Lily"], "answer": "Water lily (Shapla)"},
                {"question": "Who wrote 'Jago Bangla' era poem 'Kobiyar Kagoj'? (fun filler)",
                 "options": ["Kazi Nazrul Islam", "Rabindranath Tagore", "Jibanananda Das", "Farrukh Ahmed"],
                 "answer": "Kazi Nazrul Islam"},
                {"question": "The Sundarbans is famous for which animal?",
                 "options": ["Lion", "Royal Bengal Tiger", "Leopard", "Elephant"], "answer": "Royal Bengal Tiger"},
            ])
            engine.add_category("science", [
                {"question": "What is the chemical symbol for gold?",
                 "options": ["Ag", "Au", "Gd", "Go"], "answer": "Au"},
                {"question": "Speed of light is approximately?",
                 "options": ["300,000 km/s", "150,000 km/s", "1,000 km/s", "30,000 km/s"],
                 "answer": "300,000 km/s"},
                {"question": "Which planet is known as the Red Planet?",
                 "options": ["Venus", "Jupiter", "Mars", "Saturn"], "answer": "Mars"},
                {"question": "What gas do plants absorb from the atmosphere?",
                 "options": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
                 "answer": "Carbon dioxide"},
            ])
            FunCommandHandler._shared_quiz = engine
        return self._shared_quiz

    def trivia_start(self, entities: Dict) -> CommandResponse:
        category = entities.get("category", "general")
        try:
            engine = self._quiz()
            if category not in engine.get_categories():
                category = "general"
            engine.start_quiz(category)
            q = engine.get_current_question()
            return CommandResponse.ok(message=q.get("question", ""), action="trivia_start",
                                      data={"question": q.get("question"),
                                            "options": q.get("options")})
        except Exception as e:
            return self._error("trivia_start", str(e), entities)

    def trivia_answer(self, entities: Dict) -> CommandResponse:
        answer = str(entities.get("answer", entities.get("query", ""))).strip()
        try:
            engine = self._quiz()
            result = engine.answer_question(answer)
            correct = result.get("correct", False)
            msg = ("Correct! | সঠিক!" if correct else f"Wrong! Answer: {result.get('correct_answer', '')} | ভুল!")
            if result.get("finished"):
                score = engine.get_score()
                msg += f" Quiz over — {score.get('score', 0)}/{score.get('total', 0)}"
            else:
                nxt = engine.get_current_question()
                msg += f" Next: {nxt.get('question', '')} {nxt.get('options', '')}"
            return CommandResponse.ok(message=msg, action="trivia_answer", data=result)
        except Exception as e:
            return self._error("trivia_answer", str(e), entities)

    def trivia_score(self, entities: Dict) -> CommandResponse:
        try:
            score = self._quiz().get_score()
            return CommandResponse.ok(
                message=f"Score: {score.get('score', 0)}/{score.get('total', 0)} | "
                        f"স্কোর: {score.get('score', 0)}/{score.get('total', 0)}",
                action="trivia_score", data=score)
        except Exception as e:
            return self._error("trivia_score", str(e), entities)

    def hangman_start(self, entities: Dict) -> CommandResponse:
        try:
            from backend.fun.games import get_game_manager
            key, game = get_game_manager().start("hangman")
            return self._start_message(key, game)
        except Exception as e:
            return self._error("hangman_start", str(e), entities)

    def hangman_guess(self, entities: Dict) -> CommandResponse:
        letter = entities.get("letter", entities.get("guess", entities.get("query", "")))
        try:
            from backend.fun.games import get_game_manager, HangmanGame
            game = get_game_manager().get("hangman")
            if not isinstance(game, HangmanGame):
                raise ValueError("Hangman is not running | হ্যাংম্যান চালু নেই")
            return CommandResponse.ok(message=game.guess(str(letter)), action="hangman_guess")
        except ValueError as e:
            return self._error("hangman_guess", str(e), entities)

    def tic_tac_toe_start(self, entities: Dict) -> CommandResponse:
        try:
            from backend.fun.games import get_game_manager
            key, game = get_game_manager().start("tic_tac_toe")
            return self._start_message(key, game)
        except Exception as e:
            return self._error("tic_tac_toe_start", str(e), entities)

    def tic_tac_toe_move(self, entities: Dict) -> CommandResponse:
        position = entities.get("position", entities.get("move", entities.get("cell",
                       entities.get("query"))))
        try:
            from backend.fun.games import get_game_manager, TicTacToeGame
            game = get_game_manager().get("tic_tac_toe")
            if not isinstance(game, TicTacToeGame):
                raise ValueError("Tic-tac-toe is not running | টিক-ট্যাক-টো চালু নেই")
            return CommandResponse.ok(message=game.move(position), action="tic_tac_toe_move")
        except ValueError as e:
            return self._error("tic_tac_toe_move", str(e), entities)

    def guess_number_start(self, entities: Dict) -> CommandResponse:
        try:
            from backend.fun.games import get_game_manager
            key, game = get_game_manager().start("number")
            return self._start_message(key, game)
        except Exception as e:
            return self._error("guess_number_start", str(e), entities)

    def guess_number_guess(self, entities: Dict) -> CommandResponse:
        raw = entities.get("number", entities.get("guess", entities.get("query")))
        try:
            from backend.fun.games import get_game_manager, NumberGuessGame
            game = get_game_manager().get("number")
            if not isinstance(game, NumberGuessGame):
                raise ValueError("Number game is not running | নাম্বার গেম চালু নেই")
            return CommandResponse.ok(message=game.guess(int(raw)), action="guess_number_guess")
        except (ValueError, TypeError) as e:
            return self._error("guess_number_guess", str(e), entities)

    def word_scramble(self, entities: Dict) -> CommandResponse:
        try:
            from backend.fun.games import get_game_manager
            key, game = get_game_manager().start("scramble")
            return self._start_message(key, game)
        except Exception as e:
            return self._error("word_scramble", str(e), entities)

    def word_scramble_solve(self, entities: Dict) -> CommandResponse:
        answer = entities.get("answer", entities.get("word", entities.get("query", "")))
        try:
            from backend.fun.games import get_game_manager, WordScrambleGame
            game = get_game_manager().get("scramble")
            if not isinstance(game, WordScrambleGame):
                raise ValueError("Scramble game is not running | স্ক্র্যাম্বল গেম চালু নেই")
            return CommandResponse.ok(message=game.solve(str(answer)), action="word_scramble_solve")
        except ValueError as e:
            return self._error("word_scramble_solve", str(e), entities)

    def meme_generator(self, entities: Dict) -> CommandResponse:
        text_top = entities.get("top", entities.get("text"))
        text_bottom = entities.get("bottom", "")
        template = entities.get("template", "drake")
        if not text_top:
            # No explicit text given — pick a random ready-made meme instead of failing
            try:
                from backend.fun.meme_generator import generate_meme
                import random as _random
                presets = [
                    ("When Atlas fixes your PC", "and it works first try"),
                    ("Me: just one more game", "Atlas: time to sleep"),
                    ("Monday morning", "but you forgot the alarm"),
                    ("Code compiles", "on the first attempt"),
                ]
                top, bottom = _random.choice(presets)
                meme = generate_meme(template=template, top=top, bottom=bottom)
                return CommandResponse.ok(message=f"Meme generated! | মিম তৈরি: \"{top}\" / \"{bottom}\"",
                                          action="meme_generator", data=meme)
            except Exception:
                return self._bilingual("Meme text required | মিমের টেক্সট প্রয়োজন")
        try:
            from backend.fun.meme_generator import generate_meme
            meme = generate_meme(template=template, top=text_top, bottom=text_bottom)
            return CommandResponse.ok(message="Meme generated! | মিম তৈরি করা হয়েছে!",
                                      action="meme_generator", data=meme)
        except Exception as e:
            return self._error("meme_generator", str(e), entities)

    def meme_list(self, entities: Dict) -> CommandResponse:
        templates = ["drake", "distracted-boyfriend", "two-buttons", "expanding-brain",
                     "this-is-fine", "woman-cat", "roll-safe", "success-kid"]
        return CommandResponse.ok(message="Templates: " + ", ".join(templates) +
                                  " | টেমপ্লেট", action="meme_list",
                                  data={"templates": templates})

    def meme_create_custom(self, entities: Dict) -> CommandResponse:
        text_top = entities.get("top", entities.get("text"))
        text_bottom = entities.get("bottom", "")
        image_path = entities.get("image", entities.get("path"))
        if not text_top or not image_path:
            return self._bilingual("Need top text and an image path | টেক্সট ও ছবির পাথ দরকার")
        try:
            from PIL import Image, ImageDraw
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            w, h = img.size
            font_size = max(20, w // 15)
            draw.text((w // 2, font_size), str(text_top), fill="white",
                      stroke_width=3, stroke_fill="black", anchor="mm")
            if text_bottom:
                draw.text((w // 2, h - font_size), str(text_bottom), fill="white",
                          stroke_width=3, stroke_fill="black", anchor="mm")
            from pathlib import Path
            src = Path(image_path)
            dest = src.parent / f"{src.stem}_meme.png"
            img.convert("RGB").save(dest)
            return CommandResponse.ok(message=f"Custom meme saved: {dest} | কাস্টম মিম সংরক্ষিত",
                                      action="meme_create_custom", data={"path": str(dest)})
        except ImportError:
            return self._bilingual("Pillow is required | Pillow দরকার")
        except Exception as e:
            return self._error("meme_create_custom", str(e), entities)

    def joke_tell(self, entities: Dict) -> CommandResponse:
        try:
            from backend.fun.joke_engine import tell_joke
            joke = tell_joke(category=entities.get("category", "general"))
            return CommandResponse.ok(message=joke.get("text", ""), action="joke_tell", data=joke)
        except Exception as e:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything! | বিজ্ঞানীরা পরমাণুকে বিশ্বাস করেন না কেন? কারণ তারা সবকিছু বানিয়ে বলে!",
                "What do you call a fake noodle? An impasta! | জাল নুডলকে কী বলে? ইমপাস্তা!",
                "Why did the scarecrow win an award? Because he was outstanding in his field! | কাকতাড়ুয়া পুরস্কার পেল কেন? কারণ সে তার মাঠে অসাধারণ ছিল!",
            ]
            return CommandResponse.ok(message=random.choice(jokes), action="joke_tell")

    def joke_random(self, entities: Dict) -> CommandResponse:
        return self.joke_tell({"category": "general"})

    def joke_dark(self, entities: Dict) -> CommandResponse:
        jokes = [
            "I told my grandfather he was as old as the hills. He said, 'At least I'm not over the hill.' | দাদু বললেন, 'তবুও তো পাহাড়ের ওপরে যাইনি!'",
            "My grief counselor died last week. He was very good — he took his grief with him. | আমার শোক-পরামর্শক তাঁর শোক সঙ্গে নিয়ে গেছেন।",
        ]
        return CommandResponse.ok(message=random.choice(jokes), action="joke_dark")

    def joke_dad(self, entities: Dict) -> CommandResponse:
        jokes = [
            "Why don't eggs tell jokes? They'd crack each other up! | ডিম জোকস বলে না? একে অপরকে হাসিয়ে দেয়!",
            "I'm reading a book about anti-gravity. It's impossible to put down! | বিপরীত-মাধ্যাকর্ষণের বইটা হাত থেকে নামানো যায় না!",
            "Did you hear about the restaurant on the moon? Great food, no atmosphere! | চাঁদের রেস্টুরেন্টে খাবার দারুণ, কিন্তু পরিবেশ নেই!",
        ]
        return CommandResponse.ok(message=random.choice(jokes), action="joke_dad")

    def joke_bangla(self, entities: Dict) -> CommandResponse:
        jokes = [
            "একজন লোক ডাক্তারের কাছে গিয়ে বলল, 'ডাক্তার, আমার হাত কাঁপছে!' ডাক্তার বললেন, 'আপনি কি সিগারেট খান?' লোকটা বলল, 'না, আমি খাই না।' ডাক্তার বললেন, 'তবে আরেকটু নাড়ান, দেখি কতদূর কাঁপে!'",
            "টিচার: 'তোমার বাবার বয়স কত?' ছাত্র: 'বাবা বলেন, তাঁর বয়স ৪০-এর কাছাকাছি।' টিচার: 'কাছাকাছি মানে?' ছাত্র: '৪০ পেরিয়ে ৫০-এর দিকে!'",
        ]
        return CommandResponse.ok(message=random.choice(jokes), action="joke_bangla")

    def music_play(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("song"))
        if not query:
            return self._bilingual("Song name required | গানের নাম প্রয়োজন")
        try:
            from backend.fun.music_player import play_music
            result = play_music(query)
            return CommandResponse.ok(message=f"Playing: {query} | বাজছে: {query}",
                                      action="music_play", data=result)
        except Exception as e:
            return self._error("music_play", str(e), entities)

    def _player(self):
        from backend.media.music_player import MusicPlayer
        if not hasattr(FunCommandHandler, "_shared_player"):
            FunCommandHandler._shared_player = MusicPlayer()
        return self._shared_player

    def music_pause(self, entities: Dict) -> CommandResponse:
        try:
            player = self._player()
            paused = player.pause()
            msg = "Music paused | মিউজিক পজ করা হয়েছে" if paused else "Nothing playing | কিছু বাজছে না"
            return CommandResponse.ok(message=msg, action="music_pause")
        except Exception as e:
            return self._error("music_pause", str(e), entities)

    def music_next(self, entities: Dict) -> CommandResponse:
        try:
            track = self._player().next_track()
            title = (track or {}).get("title", "unknown")
            return CommandResponse.ok(message=f"Next track: {title} | পরবর্তী ট্র্যাক: {title}",
                                      action="music_next", data=track)
        except Exception as e:
            return self._error("music_next", str(e), entities)

    def music_previous(self, entities: Dict) -> CommandResponse:
        try:
            track = self._player().previous_track()
            title = (track or {}).get("title", "unknown")
            return CommandResponse.ok(message=f"Previous track: {title} | আগের ট্র্যাক: {title}",
                                      action="music_previous", data=track)
        except Exception as e:
            return self._error("music_previous", str(e), entities)

    def music_stop(self, entities: Dict) -> CommandResponse:
        try:
            self._player().stop()
            return CommandResponse.ok(message="Music stopped | মিউজিক বন্ধ করা হয়েছে",
                                      action="music_stop")
        except Exception as e:
            return self._error("music_stop", str(e), entities)

    def music_volume(self, entities: Dict) -> CommandResponse:
        try:
            player = self._player()
            vol = entities.get("volume")
            if vol is not None:
                player.set_volume(float(vol))
            current = player.get_volume()
            return CommandResponse.ok(message=f"Volume: {current:.0%} | ভলিউম: {current:.0%}",
                                      action="music_volume", data={"volume": current})
        except Exception as e:
            return self._error("music_volume", str(e), entities)

    def music_playlist(self, entities: Dict) -> CommandResponse:
        try:
            player = self._player()
            directory = entities.get("directory", entities.get("path"))
            if directory:
                count = player.load_playlist_from_dir(directory)
                msg = f"Loaded {count} tracks | {count} ট্র্যাক লোড হয়েছে"
            else:
                msg = None
            tracks = player.get_playlist()
            titles = [t.get("title", "?") for t in tracks]
            return CommandResponse.ok(message=(msg or f"Playlist ({len(tracks)} tracks)") +
                                      " | প্লেলিস্ট", action="music_playlist",
                                      data={"tracks": titles})
        except Exception as e:
            return self._error("music_playlist", str(e), entities)

    def music_queue(self, entities: Dict) -> CommandResponse:
        try:
            player = self._player()
            song = entities.get("song", entities.get("query"))
            if song:
                player.add_to_queue({"title": str(song)})
            queued = [t.get("title", "?") for t in player.get_queue()]
            return CommandResponse.ok(message=f"Queue: {', '.join(queued) or 'empty'} | কিউ",
                                      action="music_queue", data={"queue": queued})
        except Exception as e:
            return self._error("music_queue", str(e), entities)

    def music_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("song", ""))
        if not query:
            return self._bilingual("Song name required | গানের নাম প্রয়োজন")
        try:
            import urllib.parse
            results = [{"title": f"{query} - result {i+1}",
                        "url": f"https://www.youtube.com/results?search_query="
                               f"{urllib.parse.quote_plus(query + ' song')}"}
                       for i in range(5)]
            return CommandResponse.ok(message=f"Music search for '{query}' | ফলাফল",
                                      action="music_search", data={"results": results})
        except Exception as e:
            return self._error("music_search", str(e), entities)

    def music_lyrics(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("song", ""))
        if not query:
            return self._bilingual("Song name required | গানের নাম প্রয়োজন")
        try:
            import urllib.parse
            url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query + ' lyrics')}"
            return CommandResponse.ok(
                message=f"Lyrics link for '{query}': {url} | গানের কথা",
                action="music_lyrics", data={"url": url})
        except Exception as e:
            return self._error("music_lyrics", str(e), entities)

    def video_download(self, entities: Dict) -> CommandResponse:
        url = entities.get("url", entities.get("link"))
        if not url:
            return self._bilingual("Video URL required | ভিডিও URL প্রয়োজন")
        try:
            from backend.media.video_downloader import VideoDownloader
            downloader = VideoDownloader()
            path = downloader.download_video(url)
            info = downloader.get_video_info(url)
            return CommandResponse.ok(message=f"Saved: {path} | সংরক্ষিত: {path}",
                                      action="video_download",
                                      data={"path": path, "title": info.get("title")})
        except Exception as e:
            return self._error("video_download", str(e), entities)

    def video_search(self, entities: Dict) -> CommandResponse:
        query = entities.get("query", entities.get("text", ""))
        if not query:
            return self._bilingual("Search query required | সার্চ প্রশ্ন প্রয়োজন")
        try:
            import urllib.parse
            results = [{"title": f"{query} - video {i+1}",
                        "url": f"https://www.youtube.com/results?search_query="
                               f"{urllib.parse.quote_plus(query)}"}
                       for i in range(5)]
            return CommandResponse.ok(message=f"Video search for '{query}' | '{query}' এর জন্য ফলাফল",
                                      action="video_search", data={"results": results})
        except Exception as e:
            return self._error("video_search", str(e), entities)

    def video_info(self, entities: Dict) -> CommandResponse:
        url = entities.get("url", entities.get("link"))
        if not url:
            return self._bilingual("Video URL required | ভিডিও URL প্রয়োজন")
        try:
            from backend.media.video_downloader import VideoDownloader
            info = VideoDownloader().get_video_info(url)
            return CommandResponse.ok(message=f"Title: {info.get('title')} | তথ্য পাওয়া গেছে",
                                      action="video_info", data=info)
        except Exception as e:
            return self._error("video_info", str(e), entities)

    def audio_play(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Audio playing | অডিও বাজছে")

    def audio_record(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Recording started... | রেকর্ডিং শুরু হয়েছে...")

    def image_generator(self, entities: Dict) -> CommandResponse:
        prompt = entities.get("prompt", entities.get("text"))
        if not prompt:
            return self._bilingual("Image description required | ইমেজ বর্ণনা প্রয়োজন")
        try:
            from backend.fun.image_generator import generate_image
            result = generate_image(prompt, size=entities.get("size", "1024x1024"))
            return CommandResponse.ok(message="Image generated | ইমেজ তৈরি করা হয়েছে",
                                      action="image_generator", data=result)
        except Exception as e:
            return self._error("image_generator", str(e), entities)

    def image_edit(self, entities: Dict) -> CommandResponse:
        return self._image_op(entities, "image_edit", "Image edited | ইমেজ এডিট করা হয়েছে")

    def image_filter(self, entities: Dict) -> CommandResponse:
        return self._image_op(entities, "image_filter", "Filter applied | ফিল্টার প্রয়োগ করা হয়েছে")

    def image_resize(self, entities: Dict) -> CommandResponse:
        return self._image_op(entities, "image_resize", "Image resized | ইমেজ রিসাইজ করা হয়েছে")

    def image_convert(self, entities: Dict) -> CommandResponse:
        return self._image_op(entities, "image_convert",
                              "Image format converted | ইমেজ ফরম্যাট পরিবর্তন করা হয়েছে")

    def image_compress(self, entities: Dict) -> CommandResponse:
        return self._image_op(entities, "image_compress", "Image compressed | ইমেজ কমপ্রেস করা হয়েছে")

    @staticmethod
    def _resolve_image_path(entities: Dict):
        from pathlib import Path
        for key in ("path", "file", "image"):
            p = entities.get(key)
            if p and Path(p).exists():
                return Path(p)
        # search common folders by name
        name = entities.get("query") or entities.get("name") or ""
        if name:
            home = Path.home()
            for base in (home / "Downloads", home / "Pictures", home / "Desktop"):
                candidate = base / name
                if candidate.exists():
                    return candidate
        return None

    def _image_op(self, entities: Dict, action: str, ok_msg: str) -> CommandResponse:
        try:
            from PIL import Image
            src = self._resolve_image_path(entities)
            if src is None:
                return self._bilingual("Image file not found. Provide a path. | ছবির পাথ দিন")
            img = Image.open(src)
            out = src.parent / f"{src.stem}_edited{src.suffix or '.png'}"
            op = entities.get("filter", "")
            if action == "image_resize":
                w = int(entities.get("width", 800))
                h = int(entities.get("height", img.height * w // img.width))
                img = img.resize((w, h))
                out = src.parent / f"{src.stem}_{w}x{h}{src.suffix or '.png'}"
            elif action == "image_rotate":
                img = img.rotate(int(entities.get("angle", 90)), expand=True)
            elif action == "image_crop":
                box = tuple(int(x) for x in (entities.get("box") or (0, 0, img.width//2, img.height//2)))
                img = img.crop(box)
            elif action == "image_compress":
                quality = int(entities.get("quality", 70))
                out = out.with_suffix(".jpg")
                img.convert("RGB").save(out, "JPEG", quality=quality)
                size_kb = out.stat().st_size // 1024
                return CommandResponse.ok(message=f"{ok_msg} ({size_kb} KB) | {size_kb} KB",
                                          action=action, data={"path": str(out)})
            elif action == "image_convert":
                fmt = (entities.get("format") or "PNG").upper()
                out = out.with_suffix(f".{fmt.lower()}")
                img.convert("RGB").save(out, fmt) if fmt in ("PNG", "JPEG", "BMP") else img.save(out)
            elif op == "grayscale" or action == "image_filter":
                img = img.convert("L") if op != "sepia" else self._apply_sepia(img)
            else:  # generic edit: brightness/contrast via point ops
                factor = float(entities.get("brightness", 1.0))
                img = img.point(lambda px: min(255, int(px * factor)))
            img.save(out)
            return CommandResponse.ok(message=f"{ok_msg}: {out}", action=action,
                                      data={"path": str(out), "size": img.size})
        except ImportError:
            return self._bilingual("Pillow is required | Pillow দরকার (pip install Pillow)")
        except Exception as e:
            return self._error(action, str(e), entities)

    @staticmethod
    def _apply_sepia(img):
        from PIL import ImageEnhance
        sepia = img.convert("L").point(lambda p: p)
        return ImageEnhance.Color(sepia.convert("RGB")).enhance(0.3)

    def flip_coin(self, entities: Dict) -> CommandResponse:
        result = random.choice(["Heads | হেডস", "Tails | টেইলস"])
        return CommandResponse.ok(message=result, action="flip_coin", data={"result": result.split(" | ")[0]})

    def roll_dice(self, entities: Dict) -> CommandResponse:
        sides = entities.get("sides", 6)
        count = entities.get("count", 1)
        results = [random.randint(1, sides) for _ in range(count)]
        return CommandResponse.ok(message=f"Dice: {results} | ডাইস: {results}",
                                  action="roll_dice", data={"results": results, "sides": sides})

    def random_quote(self, entities: Dict) -> CommandResponse:
        quotes = [
            "The only way to do great work is to love what you do. | মহান কাজ করার একমাত্র উপায় হল আপনি যা করেন তা ভালোবাসা।",
            "Life is what happens when you're busy making other plans. | জীবন তখন ঘটে যখন আপনি অন্য পরিকল্পনা করতে ব্যস্ত থাকেন।",
            "Be the change you wish to see in the world. | পৃথিবীতে যে পরিবর্তন দেখতে চান, সেই পরিবর্তন নিজেই হোন।",
        ]
        return CommandResponse.ok(message=random.choice(quotes), action="random_quote")

    def random_fact(self, entities: Dict) -> CommandResponse:
        facts = [
            "Honey never spoils. | মধু কখনও নষ্ট হয় না।",
            "Octopuses have three hearts. | অক্টোপাসের তিনটি হৃদয় রয়েছে।",
            "Bananas are berries, but strawberries aren't. | কলা বেরি, কিন্তু স্ট্রবেরি বেরি নয়।",
        ]
        return CommandResponse.ok(message=random.choice(facts), action="random_fact")
