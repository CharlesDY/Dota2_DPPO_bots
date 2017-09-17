from tkinter import *
from .Config import Config
from .simulator import DotaSimulator

master = Tk()
canvas = None
_engine = None
def visualize():
    global canvas,_engine,master
    canvas = Canvas(master,width = Config.windows_size, height = Config.windows_size)
    eng = DotaSimulator(Config.dire_init_pos,canvas = canvas)
    canvas.pack()
    _engine = eng
    master.after(0,loop)
    master.mainloop()

def loop():
    global canvas,_engine,master
    _engine.loop()
    _engine.draw()
    _engine.tick_tick()
    canvas.update_idletasks()
    master.after(1,loop)