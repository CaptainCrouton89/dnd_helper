import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

"""
Responsible for playing sweet tunes at exactly the right times

Goals
- Random song order
- Crossfade songs
- Super easy mood selection
"""

PLAYLIST = "playlist"
TRACK = "track"


class MusicPlayer():

    def __init__(self, playlists):
        self.playlists = playlists
        # Create OAuth Object
        with open("spotifykey.json") as f:
            key = json.load(f)

        oauth_object = spotipy.SpotifyOAuth(key["CID"], key["SECRET"], key["REDIRECT_URI"], scope=key["SCOPE"])
        # Create token
        token = oauth_object.get_access_token(as_dict=False)
        # Create Spotify Object
        self.sp = spotipy.Spotify(auth=token)
        self.user = self.sp.current_user()
        self.sp.shuffle(True)

        self.theme = "terror"
        self.intensity = 0
        self.playing = False
        self.repeating = False
        
    def _play(self, id, uri_type="playlist"):
        self.sp.start_playback(context_uri=f"spotify:{uri_type}:{id}")

    def refresh(self):
        self._play(self.playlists[self.theme][self.intensity][1])
       
    def pause_resume(self):
        if self.playing:
            self.sp.pause_playback()
            self.playing = False
        else:
            self.sp.start_playback()
            self.playing = True

    def skip(self):
        self.sp.next_track()

    def repeat(self):
        if self.repeating:
            self.repeating = False
            self.sp.repeat("context")
        else:
            self.repeating = True
            self.sp.repeat("track")

    def set_theme(self, theme, auto_refresh=True):
        self.theme = theme
        self.intensity = 0
        if auto_refresh:
            self.refresh()

    def change_intensity(self, delta, auto_refresh=True):
        self.intensity += delta
        if self.intensity >= len(self.playlists[self.theme]):
            self.intensity = 0
        elif self.intensity < 0:
            self.intensity = len(self.playlists[self.theme])-1

        if auto_refresh:
            self.refresh()

    def get_playlist(self):
        return self.playlists[self.theme][self.intensity][0]
        



if __name__ == '__main__':
    with open("playlists.json") as f:
        playlists = json.load(f)
    mp = MusicPlayer(playlists)
    mp.set_theme("terror")
    print(mp.get_playlist())

    while True:
        k = input()
        if k == "f":
            mp.change_intensity(1)
            print(mp.get_playlist())
        if k == "d":
            mp.change_intensity(-1)
            print(mp.get_playlist())