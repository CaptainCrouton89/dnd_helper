import os
import sys
import time
import webbrowser
import spotipy
import warnings
from spotipy.oauth2 import SpotifyClientCredentials
import tkmacosx as tkm
from functools import partial
import json
import random
import scripts.constants as c
from scripts.randGenerator import SettingGenerator
from scripts.musicPlayer import MusicPlayer
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfile

DATA_PATH = "data"
TEXT_PATH = "text"
PLAYLIST_PATH = "playlists"
CAMPAIGN_PATH = "campaigns"

default_mob = {
            "name": "",
            "vigor": 8,
            "hp": 40,
            "speed": 40,
            "ad": 0,
            "mig_die": 6,
            "mig_mod": 0,
            "agi_die": 6,
            "agi_mod": 0,
            "cun_die": 6,
            "cun_mod": 0,
            "def": 0,
            "notes": ""
}

vigor_scalar = [
    
]


def get_text(entry, output):
    output = entry.get()

class TemplateFrame(tk.Frame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        # self.columnconfigure(tuple(range(0, 100)), weight=0)
        # self.rowconfigure(tuple(range(0, 100)), weight=0)
        self.id = "template_frame"

    def get_id(self, id):
        if self.master.id == id:
            return self.master
        else:
            return self.master.get_id(id)


class TemplateNotebook(ttk.Notebook):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.id = "template_notebook"

    def get_id(self, id):
        if self.master.id == id:
            return self.master
        else:
            return self.master.get_id(id)


class BasicFrame(TemplateFrame):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, borderwidth=2, relief=tk.RAISED, *args, **kwargs)
        self.id = "basic_frame"


class AppTool(TemplateFrame):
    
    def __init__(self, root, name, takefocus=1):
        super().__init__(root, borderwidth=2, relief=tk.RAISED, 
                            takefocus=takefocus, highlightthickness=3, highlightcolor="OrangeRed4", highlightbackground="gray80")
        self.app_name = name
        self.id = "app"

    def get_config(self):
        return {}


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.vscrollbar.config(command=self.canvas.yview)
        
        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame(self.canvas, borderwidth=2, relief=tk.RAISED)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior,
                                           anchor=tk.NW)

        self.frame_height_ratio = .7
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)


    # track changes to the canvas and frame width and sync them,
    # also updating the scr
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())
        if  (self.get_ratio_to_parent() < self.frame_height_ratio):
            self.canvas.config(height=self.interior.winfo_reqheight())
        

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
            # canvas.itemconfigure(interior_id, height=canvas.winfo_height())
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-event.delta, "units")
        
    def get_ratio_to_parent(self):
        # Parent is entity collection
        central_content = self.master.master.master.master
        workspace, worldnotes = central_content.winfo_children()
        # print("workspace size:", workspace.winfo_height())
        # print("worldnotes size:", worldnotes.winfo_height())
        ratio = worldnotes.winfo_height() / workspace.winfo_height()
        return ratio


APP_BINDINGS = {
    "t": "tracker",
    "d": "dice",
    "p": "music",
    "g": "generator",
    "n": "session_notes",
    "e": "world_notes",
}


class App():

    def __init__(self, config=None):
        self.root = tk.Tk("D&D Helper")
        self.root.id = "root"
        self.root.app = self
        self.state = False

        self.root.bind("<Control-f>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)
        self.root.bind("<Command-s>", self.save_session)

        for binding, _ in APP_BINDINGS.items():
            self.root.bind(f"<Command-{binding}>", self.focus_on_app)

        self.load_campaign(config)
        

    def get_session_config(self) -> dict:
        return {
            "music": self.music.get_config(),
            "dice": self.dice.get_config(),
            "generator": self.generator.get_config(),
            "workspace": self.workspace.get_config(),
            "worldnotes": self.world_notes.get_config()
        }

    def initialize_dir(self, dir):
        os.makedirs(os.path.join(dir, "sessions"), exist_ok=True)
        os.makedirs(os.path.join(dir, "locations"), exist_ok=True)
        os.makedirs(os.path.join(dir, "encounters"), exist_ok=True)

    def load_campaign(self, config):
        if not config:
            self.campaign_dir = askdirectory(title="Open Campaign", initialdir="~/campaigns")
            self.initialize_dir(self.campaign_dir)

            sessions = os.listdir(os.path.join(self.campaign_dir, "sessions"))
            sessions = [session for session in sessions if ".DS_Store" not in session]
            max_session = [None, 0]
            for session in sessions:
                print(session)
                num = int(session.replace("session_", "").replace(".json", ""))
                if num > max_session[1]:
                    max_session[0] = session
                    max_session[1] = num

            if max_session[0] == None:
                with open(os.path.expanduser("~/campaigns/.new_campaign_config.json")) as f:
                    config = json.load(f)
            else:
                with open(os.path.join(self.campaign_dir, "sessions", max_session[0])) as f:
                    config = json.load(f)
        
        self.config = config
        if messagebox.askyesno(0, "Open new session?"):
            self.config["campaign_data"]["session_num"] += 1
        self.config["campaign_data"]["campaign_name"] = self.campaign_dir
        self.config["session_data"]["workspace"]["campaign_settings"]["directory"] = self.campaign_dir
        self.load_session()

    def load_session(self):
        print("Loading app")
        self.add_widgets(self.config["session_data"])

    def save_session(self, event=None):
        print("saving session")
        self.config["session_data"] = self.get_session_config()

        session_num = self.config["campaign_data"]["session_num"]
        save_path = os.path.join(self.campaign_dir, "sessions", f"session_{session_num}.json")
        
        with open(save_path, "w+") as f:
            json.dump(self.config, f)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.root.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.root.attributes("-fullscreen", False)
        return "break"

    def focus_on_app(self, event=None):
        k = event.keysym
        app_name = APP_BINDINGS[k]
        for app in self.all_apps:
            if app.app_name == app_name:
                app.focus_set()
        

    def add_widgets(self, config):
        # Set up overall grid
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)

        self.root.rowconfigure(0, weight=4)
        self.root.rowconfigure(1, weight=4)

        # Set up left_bar
        left_bar = TemplateFrame(self.root)
        left_bar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        # left_bar.pack(side=tk.LEFT, expand=True, fill="both")

        left_bar.rowconfigure((0, 1), weight=0)
        left_bar.rowconfigure(2, weight=4)

        self.music = MusicApp(left_bar, config["music"])
        self.music.grid(row=0, column=0, sticky="nsew")

        self.dice = DiceApp(left_bar, config["dice"])
        self.dice.grid(row=1, column=0, sticky="nsew")

        self.generator = GeneratorApp(left_bar, config["generator"])       
        self.generator.grid(row=2, column=0, sticky="nsew")

        # Set up central_content
        central_content = TemplateFrame(self.root)
        central_content.grid(row=0, column=1, rowspan=2, sticky="nsew")
        # central_content.pack(side=tk.LEFT, expand=True, fill="both")

        central_content.rowconfigure(0, weight=0)
        central_content.rowconfigure(1, weight=0)
        central_content.columnconfigure(0, weight=1)

        self.workspace = WorkspaceApp(central_content, config["workspace"])
        self.workspace.grid(row=0, column=0, sticky="nsew")

        self.world_notes = WorldNotesApp(central_content, config["worldnotes"])
        self.world_notes.grid(row=1, column=0, sticky="nsew")

        # All apps
        self.all_apps = [
            self.dice,
            self.music,
            self.generator,
            self.workspace,
            self.world_notes
        ]
       


class DiceApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "dice")
        self.root = master
        self.selected = None
        self.add_widgets(config)

        self.bind("<Key-4>", self.rollx)
        self.bind("<Key-6>", self.rollx)
        self.bind("<Key-8>", self.rollx)
        self.bind("<Key-0>", self.rollx)
        self.bind("<Key-@>", self.rollx)
        self.bind("<Key-)>", self.rollx)

        self.bind("<r>", self.reroll)
        self.bind("<R>", self.reset)

        self.current_roll = []

    def get_config(self):
        return {}

    def roll(self, num):
        result = random.randint(1, num)
        die_pair = [num, result]
        self.current_roll.append(die_pair)
        self.update_text()

    def reroll(self, event=None):
        last_rolls = self.current_roll
        self.current_roll = []
        [self.roll(r[0]) for r in last_rolls]

    def reset(self, event=None):
        self.current_roll = []
        self.update_text()

    def update_text(self):
        self.current_roll.sort(key = lambda x: x[0])
        self.dice_results.config(text = [f"{r[1]}/{r[0]}" for r in self.current_roll])
        self.dice_total.config(text = sum([r[1] for r in self.current_roll]))
        sorted_results = sorted([r[1] for r in self.current_roll])
        self.dice_advg.config(text = sum(sorted_results[-2:]))
        self.dice_dsvg.config(text = sum(sorted_results[:2]))

    def rollx(self, event=None):
        k = event.keysym
        if k == "4":
            self.roll(4)
        elif k == "6":
            self.roll(6)
        elif k == "8":
            self.roll(8)
        elif k == "0":
            self.roll(10)
        elif k == "at":
            self.roll(12)
        elif k == "parenright":
            self.roll(20)
    
    def add_widgets(self, config):
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=4)

        # Header
        header = tk.Frame(self)
        # header.grid(row=0, column=0, sticky="nsew")
        header.pack(side=tk.TOP)

        self.dice_results = tk.Label(header, fg="gray", text="")
        self.dice_results.pack(side=tk.TOP)

        # Dice Results
        results = tk.Frame(self)
        # results.grid(row=1, column=0, sticky="nsew")
        results.pack(side=tk.TOP)

        results.columnconfigure((0, 2), weight=2)
        results.columnconfigure(1, weight=5)

        self.dice_advg = tk.Label(results, text="0", fg="gray", font=("Callibri",24), justify="center")
        self.dice_advg.pack(side=tk.LEFT, expand=True, fill="both")
        # self.dice_total.grid(row=0, column=1, sticky="nsew")

        self.dice_total = tk.Label(results, text="0", font=("Callibri",48), justify="center")
        self.dice_total.pack(side=tk.LEFT, expand=True, fill="both")
        # self.dice_advg.grid(row=0, column=0, sticky="nsew")

        self.dice_dsvg = tk.Label(results, text="0", fg="gray", font=("Callibri",24), justify="center")
        # self.dice_dsvg.grid(row=0, column=2, sticky="nsew")
        self.dice_dsvg.pack(side=tk.LEFT, expand=True, fill="both")


class MusicApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "music")
        self.root = master
        self.selected = None
        self.playing_theme = True
        self.last_ambient_track = None
        self.last_amb_track_id = None

        with open(os.path.join(DATA_PATH, PLAYLIST_PATH, "moodPlaylists.json")) as f:
            moodPlaylists = json.load(f)

        with open(os.path.join(DATA_PATH, PLAYLIST_PATH, "ambiencePlaylists.json")) as f:
            ambiencePlaylists = json.load(f)

        self.music_player = MusicPlayer(moodPlaylists, ambiencePlaylists)

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
        current_info = BasicFrame(self)
        # current_info.grid(row=0, column=0, sticky="nsew")
        current_info.pack(side=tk.TOP, expand=True, fill="both")
        current_info.columnconfigure((0, 1, 2), weight=1)

        # Mood selection
        mood_selector = BasicFrame(self)
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

        ambience_selector = BasicFrame(self)
        # ambience_selector.grid(row=2, column=0, sticky="nsew")
        ambience_selector.pack(side=tk.TOP, expand=True, fill="both")

        self.ambience_category_selector = BasicFrame(ambience_selector)
        self.ambience_category_selector.pack(expand=True, fill="both")
        self.ambience_track_selector = BasicFrame(ambience_selector)

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


class SessionNotesApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "session_notes")
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def get_config(self):
        return {}
    
    def add_widgets(self, config):
        self.notes = tk.Text(self, height=4, wrap="word", takefocus=0, bg="white", fg="black")
        self.notes.pack(expand=True, fill="both")
        self.notes.insert(tk.INSERT, config["notes"])
        

class GeneratorApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "generator")
        self.root = master
        self.selected = None

        text_data_path = os.path.join(DATA_PATH, TEXT_PATH)

        with open(os.path.join(text_data_path, "config.json")) as f:
            config = json.load(f)

        self.location_generator = SettingGenerator(config["locations"], text_data_path, default_quantity=3)
        self.settlement_generator = SettingGenerator(config["settlements"], text_data_path)
        self.monster_generator = SettingGenerator(config["monsters"], text_data_path)
        self.character_generator = SettingGenerator(config["characters"], text_data_path, default_quantity=1)
        # self.name_generator = SettingGenerator(config["names"], text_data_path, default_quantity=2)

        self.add_widgets(config)

    def get_config(self):
        return {}

    def generate(self, generator):
        self.focus_set()
        text = generator.generate()
        text = "\n\n".join([str(elem) for elem in text])
        self.generated_text.delete("1.0","end")
        self.generated_text.insert(tk.INSERT, text)
    
    def add_widgets(self, config):
        self.generated_text = tk.Text(self, height=15, width=30, wrap="word", font=("Callibri", 14), takefocus=0, bg="white", fg="black")
        self.generated_text.pack(side=tk.TOP, expand=True, fill="both")

        generators = BasicFrame(self)
        generators.pack(side=tk.TOP, fill="x")
        generators.columnconfigure((0, 1), weight=1)

        # Generator buttons
        location = tkm.Button(generators, text="Location",
                                command=partial(self.generate, self.location_generator), takefocus=0)
        location.grid(row=0, column=0, sticky="nsew")

        settlement = tkm.Button(generators, text="Settlement",
                                command=partial(self.generate, self.settlement_generator), takefocus=0)
        settlement.grid(row=0, column=1, sticky="nsew")

        monster = tkm.Button(generators, text="Monster",
                                command=partial(self.generate, self.monster_generator), takefocus=0)
        monster.grid(row=1, column=0, sticky="nsew")

        character = tkm.Button(generators, text="Character",
                                command=partial(self.generate, self.character_generator), takefocus=0)
        character.grid(row=1, column=1, sticky="nsew")


class CampaignSettings(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "campaign_settings")
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def load_session(self, session_path):
        with open(os.path.join(self.config["directory"], "sessions", session_path)) as f:
            config = json.load(f)
        
        self.get_id("root").app.load_campaign(config)

    def get_config(self):
        return self.config

    def add_widgets(self, config):
        self.config = config

        session_selector = BasicFrame(self)
        session_selector.columnconfigure(0, weight=1)
        session_selector.rowconfigure(0, weight=1)
        session_selector.grid(row=0, column=0, sticky="new")

        l_sess_selector = tk.Label(session_selector, text="Select session to load")
        l_sess_selector.pack(side=tk.LEFT, fill="both")

        sessions = os.listdir(os.path.join(config["directory"], "sessions"))
        sessions = [session for session in sessions if ".DS_Store" not in session]
        for session in sessions:
            b_session = ttk.Button(session_selector, text=session.replace(".json", ""), command=partial(self.load_session, session))
            b_session.pack(side=tk.LEFT, fill="both")


class WorkspaceApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "world_notes")
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def get_config(self):
        tracker_config = self.tracker.get_config()
        session_notes_config = self.session_notes.get_config()
        campaign_settings_config = self.campaign_settings.get_config()
        return {"tracker": tracker_config, "session_notes": session_notes_config, "campaign_settings": campaign_settings_config}

    def add_widgets(self, config):
        contents = TemplateNotebook(self)
        contents.pack(expand=True, fill="both")

        self.tracker = TrackerApp(contents, config["tracker"])
        contents.add(self.tracker, text ='Tracker')

        self.session_notes = SessionNotes(contents, config["session_notes"])
        contents.add(self.session_notes, text ='Session Notes')

        self.campaign_settings = CampaignSettings(contents, config["campaign_settings"])
        contents.add(self.campaign_settings, text ='Campaign Setting')


class WorldNotesApp(AppTool):

    def __init__(self, master, config):
        super().__init__(master, "world_notes")
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def get_config(self):
        locations_config = self.locations.get_config()
        entities_config = self.entities.get_config()
        return {"locations": locations_config, "entities": entities_config}

    def add_widgets(self, config):
        contents = TemplateNotebook(self)
        contents.pack(expand=True, fill="both")

        self.locations = EntityCollection(contents, config["locations"])
        contents.add(self.locations, text ='Locations')

        self.entities = EntityCollection(contents, config["entities"])
        contents.add(self.entities, text ='Entities')


class EntityCollection(tk.Frame):

    def __init__(self, master, config):
        super().__init__(master)
        self.root = master
        self.selected = None
        self.entities = []
        self.columnconfigure(0, weight=1)
        self.add_widgets(config)

    def add_widgets(self, config):
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=0)
        # self.rowconfigure(1, weight=1)

        header = BasicFrame(self)
        header.grid(column=0, row=0, sticky="nsew")

        new_entity = tkm.Button(header, text="New",
                                command=partial(self.new_entity, None), takefocus=0)
        new_entity.pack(side=tk.RIGHT)

        self.body = VerticalScrolledFrame(self)
        self.body.grid(column=0, row=1, sticky="nsew")

        for entity in config:
            self.new_entity(entity)

    def get_config(self):
        all_entity_config = [entry.get_config() for entry in self.entities]
        return all_entity_config

    def new_entity(self, config):
        entry = WorldEntityEntry(self.body.interior, config)
        entry.pack(side=tk.TOP, expand=True, fill="x")
        entry.title.focus_set()
        self.entities.append(entry)


class WorldEntityEntry(BasicFrame):

    def __init__(self, master, config):
        super().__init__(master)
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def get_config(self):
        title = self.title.get()
        notes = self.notes.get("1.0",'end-1c')
        return {"title": title, "notes": notes}

    def add_widgets(self, config):
        header = BasicFrame(self)
        header.pack(side=tk.TOP, expand=True, fill="x")

        self.title = tk.Entry(header)
        self.title.pack(side=tk.LEFT)
        if config:
            print("config:", config)
            self.title.insert(tk.INSERT, config["title"])

        save = tkm.Button(header, text="X",
                                command=self.destroy, takefocus=0)
        save.pack(side=tk.RIGHT)
        save = tkm.Button(header, text="Save",
                                command=partial(print, "saving!"), takefocus=0)
        save.pack(side=tk.RIGHT)

        self.notes = tk.Text(self, height=4, wrap="word", takefocus=1, font=("Callibri", 14), bg="white", fg="black")
        self.notes.pack(side=tk.TOP, expand=True, fill="both")
        if config:
            self.notes.insert(tk.INSERT, config["notes"])


class SessionNotes(BasicFrame):

    def __init__(self, master, config):
        super().__init__(master)
        self.root = master
        self.selected = None
        self.add_widgets(config)

    def add_widgets(self, config):
        self.notes = tk.Text(self, height=30, wrap="word", takefocus=0, font=("Callibri", 14), bg="white", fg="black")
        self.notes.pack(side=tk.TOP, expand=True, fill="x")
        if config:
            self.notes.insert(tk.INSERT, config["notes"])

    def get_config(self):
        text = self.notes.get("1.0",'end-1c')
        return {"notes": text}


class TrackerApp(AppTool):
    # Tab through shelves
    # s/a/c to select stance
    # Command-R to roll: Result on right


    def __init__(self, master, config):
        super().__init__(master, "tracker")
        
        self.root = master

        self.bind("<Command-n>", self.new_shelf)
        self.bind("<Command-t>", self.next_turn)
        self.bind("<Command-Shift-BackSpace>", self.delete_all)
        self.bind("<Command-r>", self.roll)
        self.bind("<Command-v>", self.copy_selected)
        self.bind("<Command-s>", self.save_encounter)
        self.bind("<Command-o>", self.load_encounter)

        self.bind("<Control-n>", self.new_shelf)
        self.bind("<Control-t>", self.next_turn)
        self.bind("<Control-Shift-BackSpace>", self.delete_all)
        self.bind("<Control-r>", self.roll)
        self.bind("<Control-v>", self.copy_selected)
        self.bind("<Control-s>", self.save_encounter)
        self.bind("<Control-o>", self.load_encounter)

        # self.root.bind("<Command-/>", self._focus)

        self.shelves = []
        self.focus_index = 0

        self.add_widgets(config)
        self.new_shelf()

    def add_widgets(self, config):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)

        self.header = tk.Frame(self)
        self.header.grid(row=0, column=0)

        self.header.columnconfigure([0, 1, 2, 3, 4, 5, 6, 7], weight=1)

        self.turn_counter = UpDownButton(self.header, prefix="TURN: ", inverted=True)
        self.turn_counter.grid(row=0, column=6, sticky="e")

        open = tkm.Button(self.header, text="Open", command=self.load_encounter, takefocus=0)
        open.grid(row=0, column=0, sticky="w")

        save = tkm.Button(self.header, text="Save", command=self.save_encounter, takefocus=0)
        save.grid(row=0, column=1, sticky="w")

        keybinds = tkm.Button(self.header, text="Keybinds", command=self.open_keybinds, takefocus=0)
        keybinds.grid(row=0, column=2, sticky="w")

        self.content = tk.Frame(master=self)
        self.content.grid(row=1, column=0, sticky="ew")

    def open_keybinds(self, event=None):
        keybind_win = tk.Toplevel(self)
        keybind_win.title("Keybinds")
        text = tk.Label(keybind_win, anchor='w', justify=tk.LEFT, text=
            "\n\n\
            Command -> Control on Windows machines \n\n\
            ********* FILE COMMANDS *******************************     \n\n\
            save encounter          : <Command-s>                       \n\
            load encounter          : <Command-o>                       \n\
            \n\n\
            ********* SHELF COMMANDS ******************************     \n\n\
            next shelf              : <Tab>                             \n\
            new shelf               : <Alt-n>                           \n\
            duplicate shelf:        : <Command-v>                       \n\
            delete selected shelf   : <Command-BackSpace>               \n\
            delete all shelves      : <Command-Shift-BackSpace>         \n\
            \n\n\
            ********* GAMEPLAY ************************************     \n\n\
            next turn               : <Command-t>                       \n\
            choose might stance     : <m>                               \n\
            choose agility stance   : <a>                               \n\
            choose cunning stance   : <c>                               \n\
            choose defense stance   : <d>                               \n\
            apply weakened          : <Shift-m>                       \n\
            apply off-balanced      : <Shift-a>                       \n\
            apply dazed             : <Shift-c>                       \n\
            apply misc debuff       : <Shift-d>                       \n\
            \n\n\
            ********* MOB BUILDING ********************************     \n\n\
            decrease by 1           : <M1>                              \n\
            increase by 1           : <Shift-M1>                        \n\
            increase by 5           : <Command-M1>                      \n\
            decrease by 1           : <Command-Shift-M1>                \n\
            "
        )
        text.configure(font=("Menlo", 14))
        text.pack(side=tk.LEFT, fill="both")

    def _focus(self, event):
        widget = self.root.focus_get()
        print(widget, "has focus")

    def roll(self, event=None):
        for shelf in self.shelves:
            shelf.roll()

    def next_turn(self, event=None):
        for shelf in self.shelves:
            shelf.next_turn()
            shelf.reset_selection()
        self.set_focus_at(0)
        self.turn_counter.decrease()

    def pop(self, event=None):
        if self.shelves:
            self.shelves[-1].destroy()
        self.refresh()

    def new_shelf(self, event=None):
        self.add_shelf(default_mob)

    def add_shelf(self, config):
        shelf = MobShelf(self.content, self, config=config)
        shelf.pack(side=tk.TOP, fill='x', expand=True)
        self.set_focus_at()
        shelf.focus_set()

    def remove_shelf(self, shelf):
        i = self.shelves.index(shelf)
        shelf.destroy()
        self.set_focus_at(index=i)

    def set_focus_at(self, shelf=None, index=None):
        self.shelves = self.content.winfo_children()
        if shelf:
            index = self.shelves.index(shelf)
        if not index:
            index = 0
        if index >= len(self.shelves):
            index = len(self.shelves)-1
        if self.shelves:
            self.shelves[index].focus_set()

    def load_encounter(self, event=None):
        self.delete_all()
        in_file = askopenfile(title="Open Encounter", initialdir=".", filetypes=[("JSON", "*.json")])
        all_mobs = json.load(in_file)
        for mob_config in all_mobs:
            self.add_shelf(mob_config)

    def save_encounter(self, event=None):
        out_file = asksaveasfile(title="Save Encounter", defaultextension=".json")
        all_mobs = []
        for shelf in self.shelves:
            config = shelf.get_config()
            all_mobs.append(config)
        json.dump(all_mobs, out_file)

    def delete_all(self, event=None):
        self.turn_counter.val = 0
        for shelf in self.shelves:
            self.remove_shelf(shelf)

    def copy_selected(self, event=None):
        shelf = self.root.focus_get()
        shelf.copy()


class MobShelf(tk.Frame):

    def __init__(self, master, app, config=None, takefocus=1):
        super().__init__(master=master, height=140, width=2000, borderwidth=3, relief=tk.RAISED, 
                            takefocus=takefocus, highlightthickness=3, highlightcolor="OrangeRed4", highlightbackground="gray80")
        self.app = app
        self.selected = None
        self.core_stats = []
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)

        self.bind("<Command-BackSpace>", self.delete)
        self.bind("<Control-BackSpace>", self.delete)

        content = self.add_widgets()
        self.fill_content(content, config)

    def add_widgets(self):
        tailer = tk.Frame(master=self)
        bt_delete = tkm.Button(master=tailer, text="X", command=self.destroy, takefocus=0, width=30, bg="brown2")

        header = tk.Frame(master=self)
        self.name = tk.Entry(master=header, takefocus=0, width=10, bg="white", fg="black")
        bt_copy = tkm.Button(master=header, text="copy", command=self.copy, takefocus=0)

        content = tk.Frame(master=self, width=2000)

        header.grid(column=0, row=0, sticky="nsew")
        self.name.pack(fill='both', expand=True)
        bt_copy.pack(fill='both', expand=True)

        tailer.grid(column=2, row=0, sticky="nsew")
        bt_delete.pack(fill="both", expand=True)

        content.grid(column=1, row=0, sticky="nsew")

        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=0)
        content.columnconfigure(2, weight=0)
        content.columnconfigure(3, weight=1)
        return content

    def fill_content(self, content, config):
        # Health box
        self.name.insert(tk.END, config["name"])

        health = tk.Frame(master=content, borderwidth=3, relief=tk.GROOVE)
        health.grid(row=0, column=0, sticky="nsew")
        self.bt_hitpoints = UpDownButton(health, prefix="HP: ", value=config["hp"], width=2)
        wounds = tk.Frame(master=health)
        cb_wounds = [
            tk.Checkbutton(master=wounds, takefocus=0),
            tk.Checkbutton(master=wounds, takefocus=0),
            tk.Checkbutton(master=wounds, takefocus=0)
        ]
        for cb in cb_wounds:
            cb.pack(side=tk.LEFT)
        health.rowconfigure(0, weight=3)
        health.rowconfigure(1, weight=1)
        self.bt_hitpoints.grid(row=0, column=0, sticky="nsew")
        wounds.grid(row=1, column=0, sticky="nsew")

        # Vigor/Speed
        vigor_speed = tk.Frame(master=content, borderwidth=3, relief=tk.GROOVE)
        vigor_speed.grid(row=0, column=1, sticky="nsew")
        vigor_speed.rowconfigure(0, weight=3)
        vigor_speed.rowconfigure(1, weight=1)
        
        self.bt_vigor = DieButton(vigor_speed, value=config["vigor"], prefix="d")
        self.bt_vigor.configure(bg="RosyBrown1")
        self.bt_speed = UpDownButton(vigor_speed, value=config["speed"], mod=5, prefix="SPD: ", highlight_on_click=False)

        self.bt_vigor.grid(row=0, column=0, sticky="nsew")
        self.bt_speed.grid(row=1, column=0, sticky="nsew")

        # Core stats
        core_block = tk.Frame(master=content, borderwidth=3, relief=tk.GROOVE)
        core_block.grid(row=0, column=2, sticky="nsew")
        core_block.rowconfigure(0, weight=1)
        core_block.rowconfigure(1, weight=1)
        core_block.rowconfigure(1, weight=0)
        core_block.columnconfigure(0, weight=1)
        core_block.columnconfigure(1, weight=1)
        
        self.might = CoreStat(master=core_block, shelf=self, prefix="MIG: d", die=config["mig_die"], mod=config["mig_mod"], 
                                    sc=c.SELECTED_M, dc=c.UNSELECTED_M)
        self.agility = CoreStat(master=core_block, shelf=self, prefix="AGI: d", die=config["agi_die"], mod=config["agi_mod"], 
                                    sc=c.SELECTED_A, dc=c.UNSELECTED_A)
        self.cunning = CoreStat(master=core_block, shelf=self, prefix="CUN: d", die=config["cun_die"], mod=config["cun_mod"], 
                                    sc=c.SELECTED_C, dc=c.UNSELECTED_C)
        self.defense = Defense(master=core_block, shelf=self, mod=config["def"], bonus=config["ad"], 
                                    sc=c.SELECTED_D, dc=c.UNSELECTED_D)
        self.core_stats = [self.might, self.agility, self.cunning]

        self.might.configure(bg=c.SELECTED_M)
        self.agility.configure(bg=c.SELECTED_A)
        self.cunning.configure(bg=c.SELECTED_C)
        self.defense.configure(bg=c.SELECTED_D)   
        
        self.conditions = {
            "m": self.might.bt_pen,
            "w": self.agility.bt_pen,
            "o": self.cunning.bt_pen,
            "d": self.defense.bt_pen,
        }

        self.bind("<m>", self.might.bt_die.select)
        self.bind("<a>", self.agility.bt_die.select)
        self.bind("<c>", self.cunning.bt_die.select)
        self.bind("<d>", self.defense.bt_def.select)

        self.bind("<M>", self.might.bt_pen.increase)
        self.bind("<A>", self.agility.bt_pen.increase)
        self.bind("<C>", self.cunning.bt_pen.increase)
        self.bind("<D>", self.defense.bt_pen.increase)

        self.might.grid(row=0, column=0, sticky="nsew")
        self.agility.grid(row=0, column=1, sticky="nsew")
        self.cunning.grid(row=1, column=0, sticky="nsew")
        self.defense.grid(row=1, column=1, sticky="w")

        for stat in self.core_stats:
            if stat.bt_mod.val > 0:
                stat.bt_mod.select()
        
        # Notes
        notes_frame = tk.Frame(master=content, borderwidth=3, relief=tk.GROOVE)
        notes_frame.grid(row=0, column=3, sticky="nsew")
        self.notes = tk.Text(master=notes_frame, height=4, width=30, wrap="word", takefocus=0, bg="white", fg="black")
        self.notes.pack(fill="both", expand=True)
        self.notes.pack(fill='both', expand=True)
        self.notes.insert(tk.INSERT, config["notes"])
        self.notes.bind("<Command-Return>", self._take_focus)

    def _take_focus(self, event):
        self.focus()

    def get_config(self):
        config = {
            "name": self.name.get(),
            "vigor": self.bt_vigor.val,
            "hp": self.bt_hitpoints.val,
            "speed": self.bt_speed.val,
            "ad": self.defense.bt_ad.val,
            "mig_die": self.might.bt_die.val,
            "mig_mod": self.might.bt_mod.val,
            "agi_die": self.agility.bt_die.val,
            "agi_mod": self.agility.bt_mod.val,
            "cun_die": self.cunning.bt_die.val,
            "cun_mod": self.cunning.bt_mod.val,
            "def": self.defense.bt_def.val,
            "notes": self.notes.get("1.0", tk.END)
        }
        return config

    def copy(self):
        config = self.get_config()
        self.app.add_shelf(config)

    def delete(self, event=None):
        self.app.remove_shelf(self)

    def reset_selection(self):
        for stat in self.core_stats:
            stat.deselect_all()
        self.defense.deselect_all()

    def next_turn(self):
        for condition in self.conditions.values():
            condition.decrease()
            if condition.val == 0:
                condition.deselect()

    def highlight(self):
        pass    


class UpDownButton(tkm.Button):

    def __init__(self, master, command=None, value=0, mod=1, prefix="", width=None, inverted=False, sc=c.SELECTED, dc=c.UNSELECTED,
                    highlight_on_click=True):
        super().__init__(master, command=command, takefocus=0, width=width)
        self.sc = sc
        self.dc = dc
        self.prefix = prefix
        self.val = value
        self.mod = mod
        self.hoc = highlight_on_click
        self.selected = False
        if inverted:
            self.mod *= -1
        self.refresh()
        self.bind("<Button-1>", self.decrease)
        self.bind("<Shift-Button-1>", self.increase)
        self.bind("<Command-Shift-Button-1>", self.large_increase)
        self.bind("<Command-Button-1>", self.large_decrease)

        self.bind("<Button-1>", self.decrease)
        self.bind("<Shift-Button-1>", self.increase)
        self.bind("<Control-Shift-Button-1>", self.large_increase)
        self.bind("<Control-Button-1>", self.large_decrease)

    def refresh(self):
        self.configure(text=self.get_text())

    def get_text(self):
        return self.prefix + str(self.val)

    def increase(self, event=None):
        self.val += 1 * self.mod
        if not self.selected and self.hoc:
            self.select()
        self.refresh()

    def decrease(self, event=None):
        self.val -= 1 * self.mod
        if self.val < 1 * self.mod:
            self.val = 0
            self.deselect()
        self.refresh()

    def large_increase(self, event=None):
        self.val += 5 * self.mod
        if not self.selected:
            self.select()
        self.refresh()

    def large_decrease(self, event=None):
        self.val -= 5 * self.mod
        if self.val < 5 * self.mod:
            self.val = 0
            self.deselect()
        self.refresh()

    def select(self, event=None):
        if self.selected == False:
            self.configure(bg=self.sc)
            self.selected = True
        else:
            self.deselect()

    def deselect(self, event=None):
        self.selected = False
        self.configure(bg=self.dc)


class DieButton(UpDownButton):

    DIE_SIZES = [2, 4, 6, 8, 10, 12, 20]

    def __init__(self, master, command=None, value=4, prefix="", width=None, sc=c.SELECTED, dc=c.UNSELECTED):
        super().__init__(master, command=command, value=value, prefix=prefix, width=width, sc=sc, dc=dc)

    def roll(self):
        return random.randint(1, self.val)

    def increase(self, event=None):
        i = self.DIE_SIZES.index(self.val)
        if i != len(self.DIE_SIZES)-1:
            i+=1
        self.val = self.DIE_SIZES[i]
        self.refresh()

    def decrease(self, event=None):
        i = self.DIE_SIZES.index(self.val)
        if i != 0:
            i-=1
        self.val = self.DIE_SIZES[i]
        self.refresh()

    def large_increase(self, event=None):
        for i in range(3):
            self.increase()

    def large_decrease(self, event=None):
        for i in range(3):
            self.decrease()


class CoreStat(tk.Frame):

    def __init__(self, master, shelf, die, mod=0, penalty=0, prefix="d", pen_prfix="DA: ", mod_prefix="+ ", sc=c.SELECTED, dc=c.UNSELECTED):
        super().__init__(master=master, borderwidth=3, relief=tk.GROOVE)
        self.shelf = shelf

        self.bt_die = DieButton(self, prefix=prefix, value=die, sc=sc, dc=dc)
        self.bt_die.pack(side=tk.LEFT) 

        self.bt_mod = UpDownButton(self, prefix=mod_prefix, value=mod, sc=sc, dc=dc)
        self.bt_mod.pack(side=tk.LEFT) 

        self.bt_pen = UpDownButton(self, prefix=pen_prfix, value=penalty, sc=sc, dc=dc)
        self.bt_pen.pack(side=tk.LEFT)

    def deselect_all(self):
        self.bt_die.deselect()
        if self.bt_mod.val <= 0:
            self.bt_mod.deselect()
        if self.bt_pen.val <= 0:
            self.bt_pen.deselect()

    def get_die(self):
        return self.bt_die

    def get_da(self):
        return self.bt_pen


class Defense(tk.Frame):
    def __init__(self, master, shelf, mod, bonus=0, penalty=0, sc=c.SELECTED, dc=c.UNSELECTED):
        super().__init__(master=master, borderwidth=3, relief=tk.GROOVE)
        self.shelf = shelf
        
        self.bt_def = UpDownButton(self, prefix="DEF: ", value=mod, sc=sc, dc=dc)
        self.bt_def.pack(side=tk.LEFT)

        self.bt_ad = UpDownButton(self, prefix="AD: ", value=bonus)
        self.bt_ad.pack(side=tk.LEFT)

        self.bt_pen = UpDownButton(self, prefix="DA: ", value=penalty)
        self.bt_pen.pack(side=tk.RIGHT)

    def deselect_all(self):
        self.bt_def.deselect()
        if self.bt_ad.val <= 0:
            self.bt_ad.deselect()
        if self.bt_pen.val <= 0:
            self.bt_pen.deselect()

    def get_die(self):
        return False

    def roll(self):
        return self.bt_die.roll() + self.bt_mod.val   


def to_die(die: int) -> str:
    return "d" + str(die)


def load_config(path):
    with open("config.json") as f:
        config = json.load(f)
    return config

def main():
    # config = load_config("config.json")   
    config = None 
    app = App(config)
    app.root.mainloop()


if __name__ == '__main__':
    main()
