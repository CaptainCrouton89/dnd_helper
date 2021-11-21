import os
import json
import random
import tkinter as tk
from tkinter import ttk 
import tkmacosx as tkm
import tkinterTools.templates as tp
import tkinterTools.constants as c
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfile

KEYBIND_TEXT = \
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
            apply weakened          : <Shift-m>                         \n\
            apply off-balanced      : <Shift-a>                         \n\
            apply dazed             : <Shift-c>                         \n\
            apply misc debuff       : <Shift-d>                         \n\
            \n\n\
            ********* MOB BUILDING ********************************     \n\n\
            decrease by 1           : <M1>                              \n\
            increase by 1           : <Shift-M1>                        \n\
            increase by 5           : <Command-M1>                      \n\
            decrease by 1           : <Command-Shift-M1>                \n\
            "

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

class TrackerApp(tp.AppTool):
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
        self.bind("<Command-o>", self.open_encounter)

        self.shelves = []
        self.focus_index = 0

        self.add_widgets(config)
        self.load_encounter(config)

    def add_widgets(self, config):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)

        self.header = tk.Frame(self)
        self.header.grid(row=0, column=0)

        # self.header.columnconfigure(weight=1)

        self.title = tk.Entry(self.header)
        self.title.grid(row=0, column=0, sticky="ew")
        if config:
            self.title.insert(tk.INSERT, config["title"])


        new = tkm.Button(self.header, text="New Mob", command=self.add_shelf, takefocus=0)
        new.grid(row=0, column=1, sticky="w")

        open = tkm.Button(self.header, text="Open", command=self.open_encounter, takefocus=0)
        open.grid(row=0, column=2, sticky="w")

        save = tkm.Button(self.header, text="Save", command=self.save_encounter, takefocus=0)
        save.grid(row=0, column=3, sticky="w")

        keybinds = tkm.Button(self.header, text="Keybinds", command=self.open_keybinds, takefocus=0)
        keybinds.grid(row=0, column=4, sticky="w")

        self.turn_counter = UpDownButton(self.header, prefix="TURN: ", inverted=True)
        self.turn_counter.grid(row=0, column=5, sticky="e")

        self.content = tk.Frame(master=self)
        self.content.grid(row=1, column=0, sticky="ew")

    def open_keybinds(self, event=None):
        keybind_win = tk.Toplevel(self)
        keybind_win.title("Keybinds")
        text = tk.Label(keybind_win, anchor='w', justify=tk.LEFT, text=
            KEYBIND_TEXT
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

    def add_shelf(self, config=default_mob):
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

    def open_encounter(self, event=None):
        self.delete_all()
        in_file = askopenfile(title="Open Encounter", initialdir=os.path.join(self.get_dir(), "encounters"), filetypes=[("JSON", "*.json")])
        if not in_file:
            return
        config = json.load(in_file)
        self.load_encounter(config)
        
    def load_encounter(self, config):
        for mob_config in config["mobs"]:
            self.add_shelf(mob_config)
        self.title.delete(0, 'end')
        self.title.insert(tk.INSERT, config["title"])

    def save_encounter(self, event=None):
        print(self.title.get())
        save_path = os.path.join(self.get_dir(), "encounters", self.title.get() + ".json")
        # out_file = asksaveasfile(title="Save Encounter", initialdir=save_path, defaultextension=".json")
        config = self.get_config()        
        json.dump(config, open(save_path, "w"))

    def get_config(self):
        all_mobs = []
        for shelf in self.shelves:
            config = shelf.get_config()
            all_mobs.append(config)
        return {"title": self.title.get(), "mobs": all_mobs}

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

        self.add_widgets(config)

    def add_widgets(self, config):
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

