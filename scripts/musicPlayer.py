import logging
import json
import os
import subprocess
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

SPOTIFY_PATH = "/Applications/Spotify.app"

def is_runnning(app):
    count = int(subprocess.check_output(["osascript",
                "-e", "tell application \"System Events\"",
                "-e", "count (every process whose name is \"" + app + "\")",
                "-e", "end tell"]).strip())
    return count > 0


class MusicPlayer():

    def __init__(self, moodPlaylists, ambiencePlaylists):
        self.moodPlaylists = moodPlaylists
        self.ambiencePlaylists = ambiencePlaylists   

        logging.info("Initializing music player")

        if not is_runnning("Spotify"):
            os.system(f"open {SPOTIFY_PATH}")
            print("Opening spotify, please wait...") 

        if not self.connect():
            exit(1)

        # self.sp.shuffle(True, self.device)

        self.theme = "terror"
        self.intensity = 0

        self.ambience_track = None

        self.playing = False
        self.repeating = False
        
    def connect(self):
        print("Connecting to Spotify")
        with open("spotifykey.json") as f:
            key = json.load(f)
        oauth_object = spotipy.SpotifyOAuth(key["CID"], key["SECRET"], key["REDIRECT_URI"], scope=key["SCOPE"])
        token = oauth_object.get_access_token(as_dict=False)
        self.sp = spotipy.Spotify(auth=token)
        print("Connected")
        self.user = self.sp.current_user()
        
        try:
            print(self.sp.devices())
            self.device = self.sp.devices()["devices"][0]["id"]
            print("Hiding spotify")
            try:
                os.system("osascript -e \'tell application \"Finder\"\' -e \'set visible of process \"Spotify\" to false\' -e \'end tell\'")
            except:
                pass
            return True
        except:
            print("Could not find device.")
            return False
        print("Found device")
    
    def _play(self, id, uri_type):
        try:
            if uri_type == "playlist":
                uri = f"spotify:{uri_type}:{id}"
                self.sp.start_playback(context_uri=uri)
            elif uri_type == "track":
                uris = f"spotify:{uri_type}:{id}"
                self.sp.start_playback(uris=[uris])
            return True
        except:
            return False
    
    def play(self, id, uri_type):
        success = self._play(id, uri_type)
        if not success:
            self.connect()
            success = self._play(id, uri_type)
        if not success:
            os.system(f"open {SPOTIFY_PATH}")
            print("Reopen spotify, play something from a different playlist.")
            exit()

    def refresh(self, refresh_type):
        if refresh_type == "theme":
            self.play(self.moodPlaylists[self.theme][self.intensity][1], uri_type="playlist")
        elif refresh_type == "ambience":
            self.play(self.ambience_track, uri_type="track")
       
    def pause_resume(self):
        if self.playing:
            self.sp.pause_playback()
            self.playing = False
        else:
            try:
                self.sp.start_playback()
                self.playing = True
            except:
                self.sp.pause_playback()
                self.playing = False

    def skip(self):
        self.sp.next_track()

    def middle(self):
        self.sp.seek_track(40000)

    def repeat(self, force_on=False):            
        if not self.repeating or force_on:
            self.repeating = True
            self.sp.repeat("track")
        else:
            self.repeating = False
            self.sp.repeat("context")

    def set_ambient_track(self, id):
        self.ambience_track = id
        self.refresh("ambience")

    def set_theme(self, theme):
        self.theme = theme
        self.intensity = 0
        self.refresh("theme")

    def change_intensity(self, delta):
        self.intensity += delta
        if self.intensity >= len(self.moodPlaylists[self.theme]):
            self.intensity = 0
        elif self.intensity < 0:
            self.intensity = len(self.moodPlaylists[self.theme])-1
        self.refresh("theme")

    def get_tracks_from_playlist(self, name) -> dict:
        id = self.ambiencePlaylists[name]
        playlist = self.sp.playlist(f"spotify:playlist:{id}")
        tracks = {}
        for track in playlist["tracks"]["items"]:
            tracks[track["track"]["name"]] = track["track"]["id"]
        return tracks

    def get_playlist(self, offset=0):
        if self.intensity+offset >= len(self.moodPlaylists[self.theme]):
            offset = -len(self.moodPlaylists[self.theme])+1
        return self.moodPlaylists[self.theme][self.intensity+offset][0]

    def get_current_track(self):
        info = self.sp.current_playback()
        return info["item"]["name"]

    def get_theme(self):
        return self.theme

    def get_mood_plists(self):
        return self.moodPlaylists.keys()

    def get_ambient_plists(self):
        return self.ambiencePlaylists.keys()


if __name__ == '__main__':
    with open("moodPlaylists.json") as f:
        m_list = json.load(f)
    with open("ambiencePlaylists.json") as g:
        a_list = json.load(g)
    mp = MusicPlayer(m_list, a_list)

    mp.get_tracks_from_ambience(a_list["Desert"])

    while True:
        k = input()
        if k == "f":
            mp.get_tracks_from_ambience()
        if k == "d":
            pass