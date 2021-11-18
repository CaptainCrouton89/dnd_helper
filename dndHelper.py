import os
import time
import webbrowser
import spotipy
import warnings
from spotipy.oauth2 import SpotifyClientCredentials
import tkmacosx as tkm
from functools import partial
import json
import random
import constants as c
from randGenerator import SettingGenerator
from musicPlayer import MusicPlayer
from session import Campaign, Session, save_game
import tkinter as tk
from tkinter import ttk 
from tkinter.filedialog import askopenfile, asksaveasfile

DATA_PATH = "data"
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


class AppTool(tk.Frame):
    
    def __init__(self, root, name, takefocus=1):
        super().__init__(root, borderwidth=2, relief=tk.RAISED, 
                            takefocus=takefocus, highlightthickness=2, highlightcolor="OrangeRed4", highlightbackground="gray80")
        self.app_name = name


class BasicFrame(tk.Frame):

    def __init__(self, root):
        super().__init__(root, borderwidth=2, relief=tk.RAISED)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


APP_BINDINGS = {
    "t": "tracker",
    "d": "dice",
    "m": "music",
    "g":  "generator",
    "s": "session_notes",
    "w": "world_notes",
}


class App():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title = "D&D Helper"
        self.state = False

        self.root.bind("<Control-f>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

        for binding, _ in APP_BINDINGS.items():
            self.root.bind(f"<{binding}>", self.focus_on_app)

        self.add_widgets()

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
        

    def add_widgets(self):
        # Set up overall grid
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=0)

        self.root.rowconfigure(0, weight=4)
        self.root.rowconfigure(1, weight=4)

        # Set up left_bar
        left_bar = tk.Frame(self.root)
        left_bar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        # left_bar.pack(side=tk.LEFT, expand=True, fill="both")

        left_bar.rowconfigure((0, 1), weight=0)
        left_bar.rowconfigure(2, weight=4)

        self.music = MusicApp(left_bar)
        self.music.grid(row=0, column=0, sticky="nsew")

        self.dice = DiceApp(left_bar)
        self.dice.grid(row=1, column=0, sticky="nsew")

        self.generator = GeneratorApp(left_bar)       
        self.generator.grid(row=2, column=0, sticky="nsew")

        # Set up central_content
        central_content = tk.Frame(self.root)
        central_content.grid(row=0, column=1, rowspan=2, sticky="nsew")
        # central_content.pack(side=tk.LEFT, expand=True, fill="both")

        central_content.rowconfigure(0, weight=1)
        central_content.rowconfigure(1, weight=1)

        # central_content_tabs = ttk.Notebook(central_content)
        # # central_content_tabs.grid(row=0, column=0, sticky="nsew")

        # self.tracker = TrackerApp(central_content_tabs)
        # central_content_tabs.add(self.tracker, text ='Combat')
        
        # self.session_notes = SessionNotesApp(central_content_tabs)
        # central_content_tabs.add(self.session_notes, text ='Notes')

        self.workspace = WorkspaceApp(central_content)
        self.workspace.grid(row=0, column=0, sticky="nsew")

        self.world_notes = WorldNotesApp(central_content)
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

    def __init__(self, master):
        super().__init__(master, "dice")
        self.root = master
        self.selected = None
        self.add_widgets()

        self.bind("<Key-4>", self.rollx)
        self.bind("<Key-6>", self.rollx)
        self.bind("<Key-8>", self.rollx)
        self.bind("<Key-0>", self.rollx)
        self.bind("<Key-@>", self.rollx)
        self.bind("<Key-)>", self.rollx)

        self.bind("<r>", self.reroll)
        self.bind("<R>", self.reset)

        self.current_roll = []

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
    
    def add_widgets(self):
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

    def __init__(self, master):
        super().__init__(master, "music")
        self.root = master
        self.selected = None
        self.playing_theme = True
        self.last_ambient_track = None
        self.last_amb_track_id = None

        with open("moodPlaylists.json") as f:
            moodPlaylists = json.load(f)

        with open("ambiencePlaylists.json") as f:
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

        self.add_widgets()

        self.bind("<C>", self.set_bound_theme)
        self.bind("<J>", self.set_bound_theme)
        self.bind("<L>", self.set_bound_theme)
        self.bind("<T>", self.set_bound_theme)

        self.bind("<h>", self.hide_ambient_tracks)
        self.bind("<a>", self.play_last_ambient)
        
        self.bind("<Up>", self.decrease_intensity)
        self.bind("<Down>", self.increase_intensity)
        self.bind("<Right>", self.skip)
        self.bind("<Left>", self.repeat)
        self.bind("<BackSpace>", self.pause_resume)
        # self.bind("<?>", self.get_current_track)

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

    def pause_resume(self, event=None):
        self.music_player.pause_resume()

    def play_last_ambient(self, event=None):
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
    
    def add_widgets(self):
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

        self.current_track_text = tk.Label(current_info, textvariable=self.current_track, font=("Helvetica",14), justify="center")
        self.current_track_text.grid(row=0, column=1, sticky="nsew")
        self.next_track_text = tk.Label(current_info, textvariable=self.next_track, fg="gray", justify="center")
        self.next_track_text.grid(row=0, column=0, sticky="nsew")
        self.prev_track_text = tk.Label(current_info, textvariable=self.prev_track, fg="gray", justify="center")
        self.prev_track_text.grid(row=0, column=2, sticky="nsew")

        self.ambient_last_track_text = tk.Label(current_info, textvariable=self.amb_track_text, fg="gray", justify="center")
        self.ambient_last_track_text.grid(row=1, column=1, sticky="nsew")


class SessionNotesApp(AppTool):

    def __init__(self, master):
        super().__init__(master, "session_notes")
        self.root = master
        self.selected = None
        self.add_widgets()
    
    def add_widgets(self):
        self.notes = tk.Text(self, height=4, wrap="word", takefocus=0, bg="white", fg="black")
        self.notes.pack(expand=True, fill="both")


class GeneratorApp(AppTool):

    def __init__(self, master):
        super().__init__(master, "generator")
        self.root = master
        self.selected = None

        with open(os.path.join(DATA_PATH, "config.json")) as f:
            config = json.load(f)

        self.location_generator = SettingGenerator(config["locations"], default_quantity=3)
        self.settlement_generator = SettingGenerator(config["settlements"])
        self.monster_generator = SettingGenerator(config["monsters"])

        self.add_widgets()

    def generate(self, generator):
        self.focus_set()
        text = generator.generate()
        text = "\n\n".join([str(elem) for elem in text])
        self.generated_text.delete("1.0","end")
        self.generated_text.insert(tk.INSERT, text)
    
    def add_widgets(self):
        self.generated_text = tk.Text(self, height=15, width=30, wrap="word", takefocus=0, bg="white", fg="black")
        self.generated_text.pack(side=tk.TOP, expand=True, fill="both")

        generators = BasicFrame(self)
        generators.pack(side=tk.TOP, fill="x")

        # Generator buttons
        location = tkm.Button(generators, text="Location",
                                command=partial(self.generate, self.location_generator), takefocus=0)
        location.pack(side=tk.LEFT, expand=True, fill="both")

        settlement = tkm.Button(generators, text="Settlement",
                                command=partial(self.generate, self.settlement_generator), takefocus=0)
        settlement.pack(side=tk.LEFT, expand=True, fill="both")

        monster = tkm.Button(generators, text="Monster",
                                command=partial(self.generate, self.monster_generator), takefocus=0)
        monster.pack(side=tk.LEFT, expand=True, fill="both")


class WorkspaceApp(AppTool):

    def __init__(self, master):
        super().__init__(master, "world_notes")
        self.root = master
        self.selected = None
        self.add_widgets()

    def add_widgets(self):
        contents = ttk.Notebook(self)
        contents.pack(expand=True, fill="both")

        tracker = TrackerApp(contents)
        contents.add(tracker, text ='Tracker')

        session_notes = EntityCollection(contents)
        contents.add(session_notes, text ='Session Notes')


class WorldNotesApp(AppTool):

    def __init__(self, master):
        super().__init__(master, "world_notes")
        self.root = master
        self.selected = None
        self.add_widgets()

    def add_widgets(self):
        contents = ttk.Notebook(self)
        contents.pack(expand=True, fill="both")

        locations = EntityCollection(contents)
        contents.add(locations, text ='Locations')

        entities = EntityCollection(contents)
        contents.add(entities, text ='Entities')


class EntityCollection(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.root = master
        self.selected = None
        self.add_widgets()

    def add_widgets(self):
        entry = WorldEntityEntry(self)
        entry.pack(side=tk.TOP, expand=True, fill="x")


class WorldEntityEntry(BasicFrame):

    def __init__(self, master):
        super().__init__(master)
        self.root = master
        self.selected = None
        self.add_widgets()

    def add_widgets(self):
        header = tk.Frame(self)
        header.pack(side=tk.TOP, expand=True, fill="x")

        self.title = tk.Entry(header)
        self.title.pack(side=tk.LEFT)

        self.notes = tk.Text(self, height=4, wrap="word", takefocus=0, bg="white", fg="black")
        self.notes.pack(side=tk.TOP, expand=True, fill="both")


class TrackerApp(AppTool):
    # Tab through shelves
    # s/a/c to select stance
    # Command-R to roll: Result on right


    def __init__(self, master):
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

        self.add_widgets()
        self.new_shelf()

    def add_widgets(self):
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
        self.content.grid(row=1, column=0, sticky="w")

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
        self.columnconfigure(1, weight=10)
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

        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=2)
        content.columnconfigure(2, weight=4)
        content.columnconfigure(3, weight=8)
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
        self.notes = tk.Text(master=notes_frame, height=4, wrap="word", takefocus=0, bg="white", fg="black")
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


def main():
    app = App()
    app.root.mainloop()


if __name__ == '__main__':
    main()
