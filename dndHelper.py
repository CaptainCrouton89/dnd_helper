import os
from functools import partial
import json
from tkinterTools import musicApp, diceApp, generatorApp, trackerApp, noteKeeperApp
import tkinterTools.templates as tp
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox
from tkinter.filedialog import askdirectory

DATA_PATH = "data"
TEXT_PATH = "text"
PLAYLIST_PATH = "playlists"
CAMPAIGN_PATH = "campaigns"

def get_text(entry, output):
    output = entry.get()


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
        self.state = not self.state
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
        left_bar = tp.TemplateFrame(self.root)
        left_bar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        left_bar.rowconfigure((0, 1), weight=0)
        left_bar.rowconfigure(2, weight=4)

        self.music = musicApp.MusicApp(left_bar, config["music"], os.path.join(DATA_PATH, PLAYLIST_PATH))
        self.music.grid(row=0, column=0, sticky="nsew")

        self.dice = diceApp.DiceApp(left_bar, config["dice"])
        self.dice.grid(row=1, column=0, sticky="nsew")

        self.generator = generatorApp.GeneratorApp(left_bar, config["generator"], os.path.join(DATA_PATH, TEXT_PATH))       
        self.generator.grid(row=2, column=0, sticky="nsew")

        # Set up central_content
        central_content = tp.TemplateFrame(self.root)
        central_content.grid(row=0, column=1, rowspan=2, sticky="nsew")

        central_content.rowconfigure(0, weight=0)
        central_content.rowconfigure(1, weight=0)
        central_content.columnconfigure(0, weight=1)

        self.workspace = WorkspaceApp(central_content, config["workspace"])
        self.workspace.grid(row=0, column=0, sticky="nsew")

        self.world_notes = noteKeeperApp.WorldNotesApp(central_content, config["worldnotes"])
        self.world_notes.grid(row=1, column=0, sticky="nsew")

        # All apps
        self.all_apps = [
            self.dice,
            self.music,
            self.generator,
            self.workspace,
            self.world_notes
        ]        


class CampaignSettings(tp.AppTool):

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

        session_selector = tp.BasicFrame(self)
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


class WorkspaceApp(tp.AppTool):

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
        contents = tp.TemplateNotebook(self)
        contents.pack(expand=True, fill="both")

        self.tracker = trackerApp.TrackerApp(contents, config["tracker"])
        contents.add(self.tracker, text ='Tracker')

        self.session_notes = noteKeeperApp.SessionNotes(contents, config["session_notes"])
        contents.add(self.session_notes, text ='Session Notes')

        self.campaign_settings = CampaignSettings(contents, config["campaign_settings"])
        contents.add(self.campaign_settings, text ='Campaign Setting')


def main():
    config = None 
    app = App(config)
    app.root.mainloop()


if __name__ == '__main__':
    main()
