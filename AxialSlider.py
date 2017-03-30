from tkinter import *

class AxialSlider(Frame):
    def __init__(self, master, command=None):
        Frame.__init__(self, master)

        self.slider = Scale(self, from_=1, to=1, orient=HORIZONTAL,
                            command=command)
        self.disable()

        self.slider.pack(expand=1, fill=BOTH)

    def update(self, from_, to):
        self.slider.config(from_=from_, to=to, state=NORMAL)

        if to > 1:
            self.enable()
        else:
            self.disable()

    def get(self):
        return self.slider.get()

    def enable(self):
        self.slider.config(state=NORMAL, fg='#000', sliderrelief=RAISED)

    def disable(self):
        self.slider.config(state=DISABLED, fg='#888', sliderrelief=FLAT)