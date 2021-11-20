from functools import partial
import tkinter as tk
import tkmacosx as tkm
import tkinterTools.templates as tp

class WorldNotesApp(tp.AppTool):

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
        contents = tp.TemplateNotebook(self)
        contents.pack(expand=True, fill="both")

        self.locations = EntityCollection(contents, config["locations"])
        contents.add(self.locations, text ='Locations')

        self.entities = EntityCollection(contents, config["entities"])
        contents.add(self.entities, text ='Entities')


class SessionNotes(tp.BasicFrame):

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

        header = tp.BasicFrame(self)
        header.grid(column=0, row=0, sticky="nsew")

        new_entity = tkm.Button(header, text="New",
                                command=partial(self.new_entity, None), takefocus=0)
        new_entity.pack(side=tk.RIGHT)

        self.body = tp.VerticalScrolledFrame(self)
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


class WorldEntityEntry(tp.BasicFrame):

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
        header = tp.BasicFrame(self)
        header.pack(side=tk.TOP, expand=True, fill="x")

        self.title = tk.Entry(header)
        self.title.pack(side=tk.LEFT)
        if config:
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