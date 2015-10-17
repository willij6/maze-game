#! /usr/bin/python3
from tkinter import *
from math import sqrt
from box import *

from rules import build_world
from graphics import draw_world




# this class manages the arrow keys (and wasd).
# For each key that should move the player, an instance
# of this is created
#
# each manager takes the keyup and keydown events from Tkinter
# and, via timers, converts them into
# signals to send to the model of the game
class KeyBounceManager:

    # pseudocode:
    # while(True):
    #     wait for key press
    #     while(True):
    #         # move_etc
    #         move the player
    #         wait 60 milliseconds
    #         if(not pressed):
    #             break

    # self.pressed will keep track of whether the key's up or down
    # self.sleeping will be True if we're waiting for the timer,
    # else False


    
    def __init__(self,root,direction):
        self.root = root
        self.direction = direction
        self.which_game = root.which_game
        
        self.sleeping = False
        self.pressed = False

    # goto the line labeled "# move_etc" in the pseudocode
    def _move_etc(self):
        self.root.state["move"] = self.direction
        delay = self.root.settings["player_period"]
        self.root.after(delay,self.timer)
        self.sleeping = True
        
    # called whenever the key gets un-pressed
    def keyup(self,event):
        self.pressed = False

    # called whenever the key gets pressed
    def keydown(self,event):
        self.pressed = True
        if(self.sleeping == False):
            self._move_etc()

    # gets called after waiting 60 milliseconds
    def timer(self):
        if(self.root.which_game != self.which_game):
            return
        if(self.pressed):
            self._move_etc()
        else:
            self.sleeping = False


        
        


# this class manages the timer that controls the monster.
# Matters are complicated by the occasional need to pause the timer
#
# Pseudocode for desired behavior:
# while(True):
#     while(paused):
#         pass
#     move monsters
#     wait 120 milliseconds
class TimerManager:
    def __init__(self,root):
        self.root = root
        self.which_game = root.which_game
        self.awaiting_unpause = False # keeps track of where we're waiting
        self.root.state.watch_key("paused",self.pause_watch)

        self.timer() # start the game

    def _move(self):
        self.root.state["tick"] = True
        delay = self.root.settings["monster_period"]
        self.root.after(delay,self.timer)
        self.awaiting_unpause = False
        
    def pause_watch(self):
        if(self.awaiting_unpause and
           self.root.state["paused"] == False):
            self._move()
        

    def timer(self):
        if(self.root.which_game != self.which_game):
            return
        if(self.root.state["paused"]):
            self.awaiting_unpause = True
        else:
            self._move()
            
        

class MazeGame(Tk):
    def __init__(self):
        super().__init__()
        self.title("Maze Game")
        self.resizable(width=False, height=False)

        self.canvas = Canvas(self, bg="white", height=410, width=410)
        self.canvas.grid(columnspan=2, sticky="NEWS")

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=0)
        self.columnconfigure(0,weight=0)
        self.columnconfigure(1,weight=1)

        # TODO figure out what all that was about, and find a way for the
        # Canvas to resize itself at the right times

        self.which_game = 0
        self.setup_game()
        self.bind("<Escape>", self.esc_callback)

    def esc_callback(self,event):
        self.canvas.delete(ALL)
        self.which_game += 1
        self.setup_game()
        
        
    def setup_game(self):
        self.settings = {'cols':20, 'rows':20, 'loops':2,
                         'nmon':5, 'top':0.33, 'mid':0.33,
                         'guards':0.33, 'danger_radius':14,
                         'fog_radius':7,
                         'monster_period':150, 'player_period':60}
        # TODO: add a dialog to select settings
        self.state = build_world(self.settings)
        draw_world(self.settings,self.state,self.canvas)

        def space_bar(event):
            self.state['tilt'] = True
        self.bind("<space>", space_bar)

        for j in [["Up","Left","Down","Right"],["w","a","s","d"]]:
            for i in range(4):
                textdir = j[i]
                vectdir = [(0,-1),(-1,0),(0,1),(1,0)][i]
                key_manager = KeyBounceManager(root=self,direction=vectdir)
                self.bind("<KeyPress-%s>" % textdir, key_manager.keydown)
                self.bind("<KeyRelease-%s>" % textdir, key_manager.keyup)

        TimerManager(self)




root = MazeGame()
root.mainloop()
