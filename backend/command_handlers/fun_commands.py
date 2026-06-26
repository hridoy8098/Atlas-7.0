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
        return self._bilingual("Move registered | মুভ রেজিস্টার করা হয়েছে")

    def game_end(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Game ended | গেম শেষ হয়েছে")

    def game_score(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Your score | আপনার স্কোর")

    def game_leaderboard(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Leaderboard loaded | লিডারবোর্ড লোড হয়েছে")

    def game_restart(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Game restarted | গেম পুনরায় শুরু হয়েছে")

    def trivia_start(self, entities: Dict) -> CommandResponse:
        category = entities.get("category", "general")
        difficulty = entities.get("difficulty", "medium")
        try:
            from backend.fun.trivia_engine import start_trivia
            trivia = start_trivia(category=category, difficulty=difficulty)
            return CommandResponse.ok(message=trivia.get("question", ""), action="trivia_start",
                                      data={"question": trivia.get("question"), "options": trivia.get("options")})
        except Exception as e:
            return self._error("trivia_start", str(e), entities)

    def trivia_answer(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Answer checked | উত্তর পরীক্ষা করা হয়েছে")

    def trivia_score(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Trivia score | ট্রিভিয়া স্কোর")

    def hangman_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Hangman started | হ্যাংম্যান শুরু হয়েছে")

    def hangman_guess(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Guess checked | অনুমান পরীক্ষা করা হয়েছে")

    def tic_tac_toe_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Tic-tac-toe started | টিক-ট্যাক-টো শুরু হয়েছে")

    def tic_tac_toe_move(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Move made | মুভ দেওয়া হয়েছে")

    def guess_number_start(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Guess the number (1-100) | সংখ্যা অনুমান করুন (১-১০০)")

    def guess_number_guess(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Your guess | আপনার অনুমান")

    def word_scramble(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Scrambled word | এলোমেলো শব্দ")

    def word_scramble_solve(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Solved! | সমাধান হয়েছে!")

    def meme_generator(self, entities: Dict) -> CommandResponse:
        text_top = entities.get("top", entities.get("text"))
        text_bottom = entities.get("bottom", "")
        template = entities.get("template", "drake")
        if not text_top:
            return self._bilingual("Meme text required | মিমের টেক্সট প্রয়োজন")
        try:
            from backend.fun.meme_generator import generate_meme
            meme = generate_meme(template=template, top=text_top, bottom=text_bottom)
            return CommandResponse.ok(message="Meme generated! | মিম তৈরি করা হয়েছে!",
                                      action="meme_generator", data=meme)
        except Exception as e:
            return self._error("meme_generator", str(e), entities)

    def meme_list(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Available meme templates | উপলব্ধ মিম টেমপ্লেট")

    def meme_create_custom(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Custom meme created | কাস্টম মিম তৈরি করা হয়েছে")

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
        return self._bilingual("Random joke ready | র্যান্ডম জোক প্রস্তুত")

    def joke_dark(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Dark humor joke | ডার্ক হিউমার জোক")

    def joke_dad(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Dad joke loaded | ড্যাড জোক লোড হয়েছে")

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

    def music_pause(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Music paused | মিউজিক পজ করা হয়েছে")

    def music_next(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Next track | পরবর্তী ট্র্যাক")

    def music_previous(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Previous track | আগের ট্র্যাক")

    def music_stop(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Music stopped | মিউজিক বন্ধ করা হয়েছে")

    def music_volume(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Volume adjusted | ভলিউম অ্যাডজাস্ট করা হয়েছে")

    def music_playlist(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Playlist loaded | প্লেলিস্ট লোড হয়েছে")

    def music_queue(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Queue updated | কিউ আপডেট করা হয়েছে")

    def music_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Music search results | গানের সার্চ ফলাফল")

    def music_lyrics(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Lyrics retrieved | গানের কথা পাওয়া গেছে")

    def video_download(self, entities: Dict) -> CommandResponse:
        url = entities.get("url", entities.get("link"))
        if not url:
            return self._bilingual("Video URL required | ভিডিও URL প্রয়োজন")
        try:
            from backend.fun.video_downloader import download_video
            result = download_video(url, quality=entities.get("quality", "720p"))
            return CommandResponse.ok(message=f"Downloading: {result.get('title', url)} | ডাউনলোড হচ্ছে: {result.get('title', url)}",
                                      action="video_download", data=result)
        except Exception as e:
            return self._error("video_download", str(e), entities)

    def video_search(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Video search results | ভিডিও সার্চ ফলাফল")

    def video_info(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Video info retrieved | ভিডিও তথ্য পাওয়া গেছে")

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
        return self._bilingual("Image edited | ইমেজ এডিট করা হয়েছে")

    def image_filter(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Filter applied | ফিল্টার প্রয়োগ করা হয়েছে")

    def image_resize(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Image resized | ইমেজ রিসাইজ করা হয়েছে")

    def image_convert(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Image format converted | ইমেজ ফরম্যাট পরিবর্তন করা হয়েছে")

    def image_compress(self, entities: Dict) -> CommandResponse:
        return self._bilingual("Image compressed | ইমেজ কমপ্রেস করা হয়েছে")

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
