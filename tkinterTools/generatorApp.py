import os
import json
from functools import partial
import tkinter as tk
import tkmacosx as tkm
import tkinterTools.templates as tp
import tkinterTools.constants as c
from scripts.randGenerator import SettingGenerator



class GeneratorApp(tp.AppTool):

    def __init__(self, master, config, text_data_path):
        super().__init__(master, "generator")
        self.root = master
        self.selected = None

        with open(os.path.join(text_data_path, "config.json")) as f:
            config = json.load(f)

        self.location_generator = SettingGenerator(config["locations"], text_data_path, default_quantity=3)
        self.settlement_generator = SettingGenerator(config["settlements"], text_data_path)
        self.monster_generator = SettingGenerator(config["monsters"], text_data_path)
        self.character_generator = SettingGenerator(config["characters"], text_data_path, default_quantity=1)
        self.thing_generator = SettingGenerator(config["things"], text_data_path, default_quantity=1)
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

        generators = tp.BasicFrame(self)
        generators.pack(side=tk.TOP, fill="x")
        generators.columnconfigure((0, 1), weight=1)

        # Generator buttons
        location = tkm.Button(generators, text="Location",
                                command=partial(self.generate, self.location_generator), takefocus=0)
        location.grid(row=0, column=0, sticky="nsew")

        thing = tkm.Button(generators, text="Thing",
                                command=partial(self.generate, self.thing_generator), takefocus=0)
        thing.grid(row=0, column=1, sticky="nsew")

        monster = tkm.Button(generators, text="Monster",
                                command=partial(self.generate, self.monster_generator), takefocus=0)
        monster.grid(row=1, column=0, sticky="nsew")

        character = tkm.Button(generators, text="Character",
                                command=partial(self.generate, self.character_generator), takefocus=0)
        character.grid(row=1, column=1, sticky="nsew")
        
        settlement = tkm.Button(generators, text="Settlement",
                                command=partial(self.generate, self.settlement_generator), takefocus=0)
        settlement.grid(row=2, column=0, sticky="nsew")