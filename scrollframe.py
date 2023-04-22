import platform
from tkinter import *


class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = Canvas(self, bd=0, width=600)
        self.viewPort = Frame(self.canvas)
        self.vsb = Scrollbar(self, command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vsb.set)
        self.vsb.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas_window = self.canvas.create_window(
            (4, 4), window=self.viewPort, anchor=NW, tags='self.viewPort'
        )
        self.viewPort.bind('<Configure>', self.on_frame_config)
        self.canvas.bind('<Configure>', self.on_canvas_config)
        self.viewPort.bind('<Enter>', self.on_enter)
        self.viewPort.bind('<Leave>', self.on_leave)
        self.on_frame_config(None)

    def on_frame_config(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox('all'))

    def on_canvas_config(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def on_mouse_wheel(self, event):
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), 'units')
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, 'units')
            elif event.num == 5:
                self.canvas.yview_scroll(1, 'units')

    def on_enter(self, event):
        if platform.system() == 'Linux':
            self.canvas.bind_all('<Button-4>', self.on_mouse_wheel)
            self.canvas.bind_all('<Button-5>', self.on_mouse_wheel)
        else:
            self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)

    def on_leave(self, event):
        if platform.system() == 'Linux':
            self.canvas.unbind_all('<Button-4>')
            self.canvas.unbind_all('<Button-5>')
        else:
            self.canvas.unbind_all('<MouseWheel>')
