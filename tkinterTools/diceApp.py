import random
import tkinter as tk
import tkinterTools.templates as tp

class DiceApp(tp.AppTool):

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