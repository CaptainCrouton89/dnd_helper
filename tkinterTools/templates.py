import tkinter as tk
from tkinter import ttk 

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

    def get_root_config(self):
        return self.get_id("root").app.config

    def get_dir(self):
        return self.get_root_config()["session_data"]["workspace"]["campaign_settings"]["directory"]

    def add_widgets(self, config):
        pass


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


class Canvas(tk.Canvas):

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.id = "canvas"

    def get_id(self, id):
        if self.master.id == id:
            return self.master
        else:
            return self.master.get_id(id)


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.id = "SrollFrame"   

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.vscrollbar.config(command=self.canvas.yview)
        
        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = TemplateFrame(self.canvas, borderwidth=2, relief=tk.RAISED)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior,
                                           anchor=tk.NW)

        self.frame_height_ratio = .7
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def get_id(self, id):
        if self.master.id == id:
            return self.master
        else:
            return self.master.get_id(id)

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