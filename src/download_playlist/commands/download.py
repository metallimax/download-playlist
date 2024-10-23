import datetime
import json
import typer

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from typing_extensions import Annotated
from urllib.parse import urljoin

from download_playlist.models import Playlist, PlaylistSong
from download_playlist.services import DownloaderService


app = typer.Typer()

custom_theme = Theme({"key": "yellow", "value": "cyan"})
console = Console(theme=custom_theme)
err_console = Console(stderr=True)


def _get_playlist(playlist_path: Path) -> Playlist:
    with playlist_path.open("rb") as f:
        json_playlist = json.load(f)

    playlist: Playlist = Playlist(**json_playlist.get("results", {}))

    return playlist

def _url_builder(base_url: str, song: PlaylistSong) -> str:
    url = urljoin(base_url, f"artist/{song.artist_name}/song/{song.song_title}")
    return url

def _path_builder(destination: Path, extension: str, song: PlaylistSong, create_dir: bool = True) -> Path:
    path = destination / song.artist_name_filename / song.album_title_filename / f"{song.song_title_filename}.{extension}"

    if create_dir:
        path.parent.mkdir(parents=True, exist_ok=True)

    return path


@app.command()
def run(
    playlist_path: Annotated[
        Path,
        typer.Option(
            "-p",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="The path to the playlist JSON.",
        ),
    ],
    destination: Annotated[
        Path,
        typer.Option(
            "-d",
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
            help="Directory to put the content.",
        ),
    ] = Path(".downloads"),
    base_url: Annotated[
        str,
        typer.Option(
            "-u",
            help="Download service base URL.",
        ),
    ] = "http://some.url.to.dl",
):
    """
    Launch the download.
    """

    playlist = _get_playlist(playlist_path=playlist_path)
    downloader_service = DownloaderService(
        base_url=base_url,
        destination=destination,
        path_builder=_path_builder,
        url_builder=_url_builder,
        console=console,
        err_console=err_console,
    )

    downloader_service.download(songs=playlist.songs.data)


@app.command()
def dry_run(
    playlist_path: Annotated[
        Path,
        typer.Option(
            "-p",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
):
    """
    Display information about how the actual run would go.
    """

    playlist = _get_playlist(playlist_path=playlist_path)

    caption = f"""
Nb songs: {playlist.data.nb_song}
Duration: {str(datetime.timedelta(seconds=playlist.data.duration))}
"""

    table = Table(
        title=f"Playlist: {playlist.data.title}",
        title_justify="left",
        caption=caption,
        caption_justify="left",
    )
    table.add_column("Song title", style="cyan", no_wrap=True)
    table.add_column("Artist", style="magenta", no_wrap=True)
    table.add_column("Duration", justify="right", style="green")
    table.add_column("ISRC", justify="right")

    for song in sorted(playlist.songs.data, key=lambda x: x.artist_name):
        table.add_row(
            song.song_title,
            song.artist_name,
            str(datetime.timedelta(seconds=song.duration))[-5:],
            song.isrc,
        )

    console.print(table)
