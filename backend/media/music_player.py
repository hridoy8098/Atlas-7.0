import os
import random
import logging
from pathlib import Path
from collections import deque
from threading import Thread, Event
from typing import Optional

logger = logging.getLogger(__name__)


class MusicPlayer:
    def __init__(self, playlist: list = None):
        self._playlist = deque(playlist or [])
        self._queue = deque()
        self._current_track: Optional[dict] = None
        self._is_playing = False
        self._is_paused = False
        self._stop_event = Event()
        self._volume = 0.7
        self._loop_mode = "off"
        self._thread: Optional[Thread] = None

    def add_to_playlist(self, track: dict) -> None:
        self._playlist.append(track)
        logger.info("Added '%s' to playlist", track.get("title", "untitled"))

    def add_to_queue(self, track: dict) -> None:
        self._queue.append(track)
        logger.info("Added '%s' to queue", track.get("title", "untitled"))

    def play(self) -> Optional[dict]:
        if self._is_paused:
            self._is_paused = False
            self._is_playing = True
            logger.info("Resumed playback")
            return self._current_track
        if self._queue:
            self._current_track = self._queue.popleft()
        elif self._playlist:
            self._current_track = self._playlist[0]
            if self._loop_mode == "one":
                pass
            elif self._loop_mode == "all":
                self._playlist.rotate(-1)
            elif self._loop_mode == "shuffle":
                random.shuffle(self._playlist)
                self._current_track = self._playlist[0]
                self._playlist.rotate(-1)
            else:
                self._playlist.popleft()
        else:
            logger.warning("No tracks to play")
            return None
        self._is_playing = True
        self._is_paused = False
        logger.info("Now playing '%s'", self._current_track.get("title", "untitled"))
        return self._current_track

    def pause(self) -> bool:
        if not self._is_playing:
            return False
        self._is_paused = True
        self._is_playing = False
        logger.info("Paused")
        return True

    def next_track(self) -> Optional[dict]:
        if not self._queue and not self._playlist:
            return None
        if self._queue:
            self._current_track = self._queue.popleft()
        elif self._playlist:
            self._current_track = self._playlist.popleft()
            if self._loop_mode == "all":
                self._playlist.append(self._current_track)
        else:
            return None
        self._is_playing = True
        self._is_paused = False
        logger.info("Skipped to '%s'", self._current_track.get("title", "untitled"))
        return self._current_track

    def previous_track(self) -> Optional[dict]:
        if not self._playlist and not self._current_track:
            return None
        if self._playlist:
            self._playlist.rotate(1)
            self._current_track = self._playlist[0]
            self._is_playing = True
            self._is_paused = False
            return self._current_track
        return None

    def stop(self) -> None:
        self._is_playing = False
        self._is_paused = False
        self._stop_event.set()
        logger.info("Stopped")

    def get_current_track(self) -> Optional[dict]:
        return self._current_track

    def get_playlist(self) -> list:
        return list(self._playlist)

    def get_queue(self) -> list:
        return list(self._queue)

    def set_volume(self, volume: float) -> None:
        if not 0 <= volume <= 1:
            raise ValueError("Volume must be between 0 and 1")
        self._volume = volume
        logger.info("Volume set to %.2f", volume)

    def get_volume(self) -> float:
        return self._volume

    def set_loop_mode(self, mode: str) -> None:
        if mode not in ("off", "one", "all", "shuffle"):
            raise ValueError("Loop mode must be one of: off, one, all, shuffle")
        self._loop_mode = mode
        logger.info("Loop mode set to '%s'", mode)

    def get_loop_mode(self) -> str:
        return self._loop_mode

    def clear_playlist(self) -> None:
        self._playlist.clear()
        self._queue.clear()
        self._current_track = None
        logger.info("Playlist cleared")

    def load_playlist_from_dir(self, directory: str, extensions: tuple = (".mp3", ".wav", ".flac", ".aac", ".ogg")) -> int:
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Not a directory: {directory}")
        count = 0
        for f in sorted(Path(directory).iterdir()):
            if f.suffix.lower() in extensions:
                self._playlist.append({"title": f.stem, "path": str(f), "ext": f.suffix})
                count += 1
        logger.info("Loaded %d tracks from %s", count, directory)
        return count

    def is_playing(self) -> bool:
        return self._is_playing

    def is_paused(self) -> bool:
        return self._is_paused
