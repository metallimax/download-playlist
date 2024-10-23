import json

from pathlib import Path
from rich.console import Console
from typing import Callable, List, Tuple

from download_playlist.models import PlaylistSong

class DownloaderService():

    def __init__(
            self,
            base_url: str,
            url_builder: Callable[[str, PlaylistSong], str],
            destination: Path,
            path_builder: Callable[[Path, str, PlaylistSong], Path],
            console: Console = None,
            err_console: Console = None,
        ):
        self.base_url: str = base_url
        self.url_builder: Callable[[str, PlaylistSong], str] = url_builder
        self.destination: Path = destination
        self.path_builder: Callable[[Path, str, PlaylistSong], Path] = path_builder
        self.console: Console = console
        self.err_console: Console = err_console
    
    def _print(self, message):
        if self.console:
            self.console.print(message)
    
    def _err(self, message):
        if self.err_console:
            self.err_console.print(message, style="red")
    
    def _download_song(self, url: str) -> Tuple[bytes, str]:
        self._print(f"Downloading song at: {url}")
        # TODO Finish this
        content = b""
        extension = "flacc"
        return content, extension
    
    def _save_content(self, path: Path, content: bytes):
        self._print(f"Saving song content at: {path.as_posix()}")
        with path.open("wb") as f:
            f.write(content)

    
    def download(self, songs: List[PlaylistSong]):
        references_path = self.destination / "references.json"

        try:
            with references_path.open("r") as f:
                older_references = json.load(f)
        except FileNotFoundError:
            older_references = {}
            pass
        
        references = {}
        error_count = 0

        for song in songs:
            refs: List[str] = references.setdefault(song.isrc, [])
            url = self.url_builder(base_url=self.base_url, song=song)

            # TODO check in older references if content exists

            try:
                content, extension = self._download_song(url=url)
            except Exception as ex: # TODO Targer specific errors
                error_count += 1
                self._err(f"An error occured while downloading the content at: {url}")
                self._err(str(ex))
                continue

            path: Path = self.path_builder(destination=self.destination, extension=extension, song=song)

            try:
                self._save_content(path=path, content=content)
                refs.append(path.as_posix())
            except FileNotFoundError as err:
                error_count += 1
                self._err(f"An error occured while saving the content at: {path.as_posix()}")
                self._err(str(err))
                continue
        
        self._err(f"Error count: {error_count}")

        with references_path.open("w") as f:
            json.dump(references, f, indent=2)

