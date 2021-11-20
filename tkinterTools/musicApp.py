import os
import json
from functools import partial
import tkinter as tk
import tkmacosx as tkm
import tkinterTools.templates as tp
import scripts.musicPlayer as mp


class MusicApp(tp.AppTool):

    def __init__(self, master, config, playlist_path):
        super().__init__(master, "music")
        self.root = master
        self.selected = None
        self.playing_theme = True
        self.last_ambient_track = None
        self.last_amb_track_id = None

        with open(os.path.join(playlist_path, "moodPlaylists.json")) as f:
            moodPlaylists = json.load(f)

        with open(os.path.join(playlist_path, "ambiencePlaylists.json")) as f:
            ambiencePlaylists = json.load(f)

        self.music_player = mp.MusicPlayer(moodPlaylists, ambiencePlaylists)

        self.current_track = tk.StringVar()
        self.current_track.set("<no song>")
        self.next_track = tk.StringVar()
        self.next_track.set("<no song>")
        self.prev_track = tk.StringVar()
        self.prev_track.set("<no song>")
        self.amb_track_text = tk.StringVar()
        self.amb_track_text.set("<last ambient>")

        self.add_widgets(config)

        self.bind("<C>", self.set_bound_theme)
        self.bind("<J>", self.set_bound_theme)
        self.bind("<L>", self.set_bound_theme)
        self.bind("<T>", self.set_bound_theme)

        self.bind("<h>", self.hide_ambient_tracks)
        self.bind("<a>", self.play_last_ambient)
        
        self.bind("<Up>", self.decrease_intensity)
        self.bind("<Down>", self.increase_intensity)
        self.bind("<Right>", self.skip)
        self.bind("<Command-Right>", self.middle)
        self.bind("<Left>", self.repeat)
        self.bind("<BackSpace>", self.pause_resume)
        # self.bind("<?>", self.get_current_track)

    def get_config(self):
        return {}

    def set_bound_theme(self, event=None):
        k = event.keysym
        if k == "C":
            self.set_theme("Curiousity>Horror")
        if k == "J":
            self.set_theme("Joy>Sad")
        if k == "L":
            self.set_theme("Locations")
        if k == "T":
            self.set_theme("Tension>Conflict")
    
    def set_theme(self, mood):
        self.playing_theme = True
        self.focus_set()
        self.music_player.set_theme(mood)
        self.update_current()

    def set_ambient_track(self, track_id, track_name):
        self.playing_theme = False
        self.last_ambient_track = track_name
        self.last_amb_track_id = track_id
        self.force_repeat()
        self.hide_ambient_tracks()
        self.focus_set()
        self.music_player.set_ambient_track(track_id)
        self.update_current()

    def show_ambient_tracks(self, ambient_category):
        self.focus_set()
        self.ambience_track_selector.pack(expand=True, fill="both")
        self.ambience_category_selector.pack_forget()
        tracks = self.music_player.get_tracks_from_playlist(ambient_category)
        for i, (track_name, track_id) in enumerate(tracks.items()):
            button = tkm.Button(self.ambience_track_selector, text=track_name, 
                                command=partial(self.set_ambient_track, track_id, track_name), takefocus=0)
            button.grid(row=i, column=0, sticky="ew")

    def increase_intensity(self, event=None):
        self.music_player.change_intensity(1)
        print(self.music_player.get_playlist())
        self.update_current()

    def decrease_intensity(self, event=None):
        self.music_player.change_intensity(-1)
        print(self.music_player.get_playlist())
        self.update_current()

    def skip(self, event=None):
        self.music_player.skip()
        self.update_current()

    def middle(self, event=None):
        self.music_player.middle()

    def pause_resume(self, event=None):
        self.music_player.pause_resume()

    def play_last_ambient(self, event=None):
        if self.last_amb_track_id:
            self.set_ambient_track(self.last_amb_track_id, self.last_ambient_track)

    def repeat(self, event=None):
        self.music_player.repeat()
        self.update_current()

    def force_repeat(self):
        self.music_player.repeat(force_on=True)
        self.update_current()

    def update_current(self):
        if self.playing_theme:
            self.current_track.set(self.music_player.get_playlist())
            self.next_track.set(self.music_player.get_playlist(-1))
            self.prev_track.set(self.music_player.get_playlist(1))
        else:
            self.current_track.set(self.music_player.get_current_track())
            self.prev_track.set("")
            if self.music_player.repeating:
                self.next_track.set("R")
            else:
                self.next_track.set("")
            self.amb_track_text.set(self.last_ambient_track)

    def hide_ambient_tracks(self, event=None):
        self.ambience_category_selector.pack(expand=True, fill="both")
        self.ambience_track_selector.pack_forget()
    
    def add_widgets(self, config):
        current_info = tp.BasicFrame(self)
        # current_info.grid(row=0, column=0, sticky="nsew")
        current_info.pack(side=tk.TOP, expand=True, fill="both")
        current_info.columnconfigure((0, 1, 2), weight=1)

        # Mood selection
        mood_selector = tp.BasicFrame(self)
        # mood_selector.grid(row=1, column=0, sticky="nsew")
        mood_selector.pack(side=tk.TOP, expand=True, fill="both")
        mood_selector.columnconfigure((0, 1), weight=1)

        all_moods = []
        mood_plists = self.music_player.get_mood_plists()
        for i, mood_plist in enumerate(mood_plists):
            button = tkm.Button(mood_selector, text=mood_plist,
                                command=partial(self.set_theme, mood_plist), takefocus=0)
            button.grid(row=i//2, column=i%2, sticky="ew")
            all_moods.append(button)

        ambience_selector = tp.BasicFrame(self)
        # ambience_selector.grid(row=2, column=0, sticky="nsew")
        ambience_selector.pack(side=tk.TOP, expand=True, fill="both")

        self.ambience_category_selector = tp.BasicFrame(ambience_selector)
        self.ambience_category_selector.pack(expand=True, fill="both")
        self.ambience_track_selector = tp.BasicFrame(ambience_selector)

        all_ambience = []
        ambience_plists = self.music_player.get_ambient_plists()
        for i, ambience_plist in enumerate(ambience_plists):
            button = tkm.Button(self.ambience_category_selector, text=ambience_plist, 
                                command=partial(self.show_ambient_tracks, ambience_plist), takefocus=0)
            button.grid(row=i, column=0, sticky="ew")
            all_ambience.append(button)

        self.current_track_text = tk.Label(current_info, textvariable=self.current_track, font=("Callibri",14), justify="center")
        self.current_track_text.grid(row=0, column=1, sticky="nsew")
        self.next_track_text = tk.Label(current_info, textvariable=self.next_track, fg="gray", justify="center")
        self.next_track_text.grid(row=0, column=0, sticky="nsew")
        self.prev_track_text = tk.Label(current_info, textvariable=self.prev_track, fg="gray", justify="center")
        self.prev_track_text.grid(row=0, column=2, sticky="nsew")

        self.ambient_last_track_text = tk.Label(current_info, textvariable=self.amb_track_text, fg="gray", justify="center")
        self.ambient_last_track_text.grid(row=1, column=1, sticky="nsew")