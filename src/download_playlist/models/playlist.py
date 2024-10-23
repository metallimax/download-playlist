import re

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    computed_field,
)
from typing import List


RE_FILENAME_SANITIZE = re.compile(r"[^\w\s-]")


class PlaylistData(BaseModel):
    nb_song: int = Field(validation_alias=AliasChoices("NB_SONG"))
    duration: int = Field(validation_alias=AliasChoices("DURATION"))
    title: str = Field(validation_alias=AliasChoices("TITLE"))

class PlaylistSong(BaseModel):
    song_title: str = Field(validation_alias=AliasChoices("SNG_TITLE"))
    artist_name: str = Field(validation_alias=AliasChoices("ART_NAME"))
    duration: int = Field(validation_alias=AliasChoices("DURATION"))
    isrc: str = Field(validation_alias=AliasChoices("ISRC"))
    album_title: str = Field(validation_alias=AliasChoices("ALB_TITLE"))
    
    @computed_field
    @property
    def artist_name_filename(self) -> str:
        return RE_FILENAME_SANITIZE.sub("", self.artist_name).strip()
    
    @computed_field
    @property
    def song_title_filename(self) -> str:
        return RE_FILENAME_SANITIZE.sub("", self.song_title).strip()
    
    @computed_field
    @property
    def album_title_filename(self) -> str:
        return RE_FILENAME_SANITIZE.sub("", self.album_title).strip()

class PlaylistSongs(BaseModel):
    data: List[PlaylistSong]
    total: int

class Playlist(BaseModel):
    data: PlaylistData = Field(validation_alias=AliasChoices("DATA"))
    songs: PlaylistSongs = Field(validation_alias=AliasChoices("SONGS"))
