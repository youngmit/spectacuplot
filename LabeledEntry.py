from tkinter import *

# This is a little GUI widget that has a text box for user input and a label,
# indicating the purpose of the text box. The widget can be enabled and disabled
# programatically
class LabeledEntry(Frame):
    def __init__(self, master, textvariable=None, text='', width=None,
                 disabled=False):
        Frame.__init__(self, master)

        self.disabled = False

        self.label = Label(self, text=text)
        self.label.pack(side=LEFT)

        self.entry = Entry(self, textvariable=textvariable, width=width)
        self.entry.pack(side=LEFT)

        if disabled:
            self.disable()

    def enable(self):
        self.disabled = False
        self.entry.config(state=NORMAL, fg='#000')
        self.label.config(fg='#000')

    def disable(self):
        self.disabled = True
        self.entry.config(state=DISABLED, fg='#888')
        self.label.config(fg='#888')