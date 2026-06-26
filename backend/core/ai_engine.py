# backend/core/ai_engine.py — Atlas 6.0 AI Engine
# Groq multi-key + model routing + fallback system

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

try:
    from groq import Groq, RateLimitError, APIError
except ImportError:
    print("⚠️ pip install groq")
    Groq = None
    RateLimitError = Exception
    APIError = Exception

# Gemini optional - না থাকলেও চলবে
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False
    print("⚠️ pip install google-generativeai (optional, vision features এর জন্য)")

import config


class MultiKeyManager:
    """Multiple API keys manage করে - rotate, rate limit track, auto-switch"""
    
    def __init__(self, keys: List[str], rpm_limit: int, rpd_limit: int, strategy: str = "round_robin"):
        self.keys = keys
        self.rpm_limit = rpm_limit
        self.rpd_limit = rpd_limit
        self.strategy = strategy
        self.current_index = 0
        self.key_stats = {}
        
        for i, key in enumerate(keys):
            if key and "তোমার" not in key and "your" not in key.lower():
                self.key_stats[i] = {
                    "key": key,
                    "rpm_used": 0,
                    "rpd_used": 0,
                    "total_requests": 0,
                    "rate_limited": False,
                    "limited_until": None,
                    "last_used": None,
                    "last_reset_rpm": time.time(),
                    "last_reset_rpd": datetime.now().date()
                }
    
    @property
    def active_keys_count(self):
        return len([k for k in self.key_stats.values() if not k["rate_limited"]])
    
    def get_next_key(self) -> Tuple[int, str]:
        """পরবর্তী available key return করে"""
        if not self.key_stats:
            return None, None
        
        self._reset_counters_if_needed()
        
        if self.strategy == "round_robin":
            return self._round_robin()
        elif self.strategy == "least_used":
            return self._least_used()
        elif self.strategy == "random":
            return self._random()
        else:
            return self._round_robin()
    
    def _round_robin(self) -> Tuple[int, str]:
        attempts = 0
        while attempts < len(self.key_stats):
            idx = self.current_index % len(self.key_stats)
            self.current_index += 1
            
            if idx in self.key_stats:
                stat = self.key_stats[idx]
                if not stat["rate_limited"] and stat["rpm_used"] < self.rpm_limit:
                    return idx, stat["key"]
            
            attempts += 1
        
        return self._wait_for_available_key()
    
    def _least_used(self) -> Tuple[int, str]:
        available = [(i, s) for i, s in self.key_stats.items() 
                     if not s["rate_limited"] and s["rpm_used"] < self.rpm_limit]
        if not available:
            return self._wait_for_available_key()
        
        available.sort(key=lambda x: x[1]["total_requests"])
        idx, stat = available[0]
        return idx, stat["key"]
    
    def _random(self) -> Tuple[int, str]:
        import random
        available = [(i, s) for i, s in self.key_stats.items() 
                     if not s["rate_limited"] and s["rpm_used"] < self.rpm_limit]
        if not available:
            return self._wait_for_available_key()
        
        idx, stat = random.choice(available)
        return idx, stat["key"]
    
    def _wait_for_available_key(self) -> Tuple[int, str]:
        now = time.time()
        for i, stat in self.key_stats.items():
            if stat["rate_limited"] and stat["limited_until"]:
                if now >= stat["limited_until"]:
                    stat["rate_limited"] = False
                    stat["limited_until"] = None
                    stat["rpm_used"] = 0
                    return i, stat["key"]
        
        return None, None
    
    def mark_used(self, key_index: int):
        if key_index in self.key_stats:
            stat = self.key_stats[key_index]
            stat["rpm_used"] += 1
            stat["rpd_used"] += 1
            stat["total_requests"] += 1
            stat["last_used"] = time.time()
    
    def mark_rate_limited(self, key_index: int, cooldown_seconds: int = 65):
        if key_index in self.key_stats:
            stat = self.key_stats[key_index]
            stat["rate_limited"] = True
            stat["limited_until"] = time.time() + cooldown_seconds
            print(f"⏳ Key {key_index} rate limited for {cooldown_seconds}s")
    
    def _reset_counters_if_needed(self):
        now = time.time()
        today = datetime.now().date()
        
        for stat in self.key_stats.values():
            if now - stat["last_reset_rpm"] >= 60:
                stat["rpm_used"] = 0
                stat["last_reset_rpm"] = now
            
            if today != stat["last_reset_rpd"]:
                stat["rpd_used"] = 0
                stat["last_reset_rpd"] = today
            
            if stat["rate_limited"] and stat["limited_until"]:
                if now >= stat["limited_until"]:
                    stat["rate_limited"] = False
                    stat["limited_until"] = None
                    stat["rpm_used"] = 0
    
    def get_status(self) -> List[Dict]:
        self._reset_counters_if_needed()
        status_list = []
        for i, stat in self.key_stats.items():
            status_list.append({
                "index": i,
                "rpm_used": stat["rpm_used"],
                "rpm_left": self.rpm_limit - stat["rpm_used"],
                "day_used": stat["rpd_used"],
                "limited": stat["rate_limited"],
                "total": stat["total_requests"]
            })
        return status_list


class AtlasAI:
    """Atlas 6.0 AI Engine - Main class"""
    
    def __init__(self):
        # Groq setup
        self.groq_key_manager = None
        self.groq_clients = {}
        
        if Groq:
            valid_keys = [k for k in config.GROQ_API_KEYS if k and "তোমার" not in k]
            if valid_keys:
                self.groq_key_manager = MultiKeyManager(
                    keys=valid_keys,
                    rpm_limit=config.GROQ_RPM_LIMIT,
                    rpd_limit=config.GROQ_RPD_LIMIT,
                    strategy=config.GROQ_KEY_STRATEGY
                )
                for i, key in self.groq_key_manager.key_stats.items():
                    try:
                        self.groq_clients[i] = Groq(api_key=key["key"])
                    except Exception as e:
                        print(f"❌ Groq client {i} init failed: {e}")
        
        # ✅ FIX: Gemini setup — config.GEMINI_API_KEYS (list) use করছে
        # আগে config.GEMINI_API_KEYS ছিল না → AttributeError হতো
        self.gemini_key_manager = None
        self.gemini_clients = {}
        
        if GENAI_AVAILABLE:
            # ✅ FIX: getattr দিয়ে safe access — পুরনো config হলেও crash হবে না
            gemini_keys_list = getattr(config, "GEMINI_API_KEYS", [])
            
            # fallback: পুরনো single key থাকলেও কাজ করবে
            if not gemini_keys_list:
                single_key = getattr(config, "GEMINI_API_KEY", "")
                if single_key and "your" not in single_key.lower() and "xxxxxxx" not in single_key.lower():
                    gemini_keys_list = [single_key]
            
            valid_keys = [k for k in gemini_keys_list if k and "তোমার" not in k and "your" not in k.lower()]
            
            if valid_keys:
                self.gemini_key_manager = MultiKeyManager(
                    keys=valid_keys,
                    rpm_limit=config.GEMINI_RPM_LIMIT,
                    rpd_limit=config.GEMINI_RPD_LIMIT,
                    strategy=config.GEMINI_KEY_STRATEGY
                )
                for i, key_info in self.gemini_key_manager.key_stats.items():
                    try:
                        genai.configure(api_key=key_info["key"])
                        self.gemini_clients[i] = genai.GenerativeModel(config.VISION_MODEL)
                    except Exception as e:
                        print(f"❌ Gemini client {i} init failed: {e}")
            else:
                print("⚠️ No valid Gemini keys found - vision features disabled")
        else:
            print("ℹ️ Gemini not installed - vision features disabled")
            print("   Install: pip install google-generativeai")
        
        # Conversation history
        self.conversation_history = []
        self.max_history = config.SHORT_TERM_MEMORY_SIZE
        
        # Stats
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Print status
        groq_count = self.groq_key_manager.active_keys_count if self.groq_key_manager else 0
        gemini_count = self.gemini_key_manager.active_keys_count if self.gemini_key_manager else 0
        print(f"✅ Atlas AI Engine initialized")
        print(f"   Groq keys:   {groq_count}")
        print(f"   Gemini keys: {gemini_count}")
    
    def chat(self, message: str, model: str = None, system_prompt: str = None, use_history: bool = True) -> str:
        """Main chat function - Groq দিয়ে text generation"""
        if self.groq_key_manager is None:
            return self._fallback_response(message)

        # ✅ FIX: config.DEFAULT_MODEL — আগে এই variable ছিল না → AttributeError হতো
        # getattr দিয়ে safe fallback রাখা হয়েছে
        default_model = getattr(config, "DEFAULT_MODEL", None) or getattr(config, "GROQ_MODEL", "llama3-70b-8192")
        model = model or default_model

        key_index, api_key = self.groq_key_manager.get_next_key()

        if key_index is None:
            print("❌ No available Groq keys")
            return self._fallback_response(message)

        try:
            client = self.groq_clients.get(key_index)
            if not client:
                return self._fallback_response(message)

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if use_history:
                for entry in self.conversation_history[-self.max_history:]:
                    messages.append(entry)

            messages.append({"role": "user", "content": message})

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )

            response = completion.choices[0].message.content

            self.groq_key_manager.mark_used(key_index)
            self.total_requests += 1
            self.successful_requests += 1

            if use_history:
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": response})

                if len(self.conversation_history) > self.max_history * 2:
                    self.conversation_history = self.conversation_history[-self.max_history * 2:]

            return response
            
        except RateLimitError:
            print(f"⚠️ Groq key {key_index} rate limited")
            self.groq_key_manager.mark_rate_limited(key_index, config.KEY_COOLDOWN_TIME)
            self.failed_requests += 1
            # Retry once with a different key — avoid infinite recursion
            if self.groq_key_manager.active_keys_count > 0:
                key_index2, api_key2 = self.groq_key_manager.get_next_key()
                if key_index2 is not None and key_index2 != key_index:
                    return self.chat(message, model, system_prompt)
            return self._fallback_response(message)
            
        except APIError as e:
            print(f"❌ Groq API error: {e}")
            self.failed_requests += 1
            return self._fallback_response(message)
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.failed_requests += 1
            return self._fallback_response(message)
    
    def chat_vision(self, image_data, prompt: str = "What do you see in this image?") -> str:
        """Gemini দিয়ে image analysis"""
        if not GENAI_AVAILABLE or self.gemini_key_manager is None:
            return "Vision features not available. Install: pip install google-generativeai"
        
        key_index, api_key = self.gemini_key_manager.get_next_key()
        
        if key_index is None:
            return "All Gemini keys are rate limited. Try again later."
        
        try:
            # ✅ Per-request configure — correct key নিশ্চিত করে
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(config.VISION_MODEL)
            
            response = model.generate_content([prompt, image_data])
            
            self.gemini_key_manager.mark_used(key_index)
            self.total_requests += 1
            self.successful_requests += 1
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini error: {error_msg}")
            if "429" in error_msg or "quota" in error_msg.lower():
                self.gemini_key_manager.mark_rate_limited(key_index)
                # ✅ Recursive retry — key শেষ হলে graceful exit
                if self.gemini_key_manager.active_keys_count > 0:
                    return self.chat_vision(image_data, prompt)
                return "All Gemini keys exhausted. Try again later."
            self.failed_requests += 1
            return f"Vision analysis failed: {error_msg}"
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Groq Whisper দিয়ে STT"""
        if self.groq_key_manager is None:
            return None
        
        key_index, api_key = self.groq_key_manager.get_next_key()
        
        if key_index is None:
            return None
        
        try:
            client = self.groq_clients.get(key_index)
            if not client:
                return None
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            with open(temp_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model=config.GROQ_WHISPER_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            import os
            os.unlink(temp_path)
            
            self.groq_key_manager.mark_used(key_index)
            return transcription
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def _fallback_response(self, message: str) -> str:
        """Fallback যখন API unavailable"""
        import random
        responses = [
            "I'm processing your request... 🤔",
            "Let me think about that...",
            "Interesting! Let me analyze...",
            "One moment please...",
        ]
        return random.choice(responses)
    
    def get_key_status(self) -> Dict:
        """Frontend এর জন্য key status"""
        return {
            "groq": self.groq_key_manager.get_status() if self.groq_key_manager else [],
            "gemini": self.gemini_key_manager.get_status() if self.gemini_key_manager else [],
            "total_requests": self.total_requests,
            "success_rate": f"{(self.successful_requests / max(1, self.total_requests) * 100):.1f}%"
        }
    
    def clear_history(self):
        self.conversation_history = []
        print("🗑️ Conversation history cleared")
    
    def get_history(self) -> List[Dict]:
        return self.conversation_history


# ===== Singleton =====
ai_engine = AtlasAI()