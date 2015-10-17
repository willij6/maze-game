#! /usr/bin/python3
'''The main program to run, launching the game'''

from tkinter import *
from math import sqrt
from box import *

from rules import build_world
from graphics import draw_world


# There are two utility classes: KeyBounceManager and TimerManager.
# Each of these manages something like a finite state machine or
# a coroutine that handles some interaction between timers
# and user events.


class KeyBounceManager:
    '''This class manages the arrow keys (and wasd).  For each key that
    should move the player, an instance of this will be created. Each
    instance takes the keyup and keydown events from Tkinter and, via
    timers, converts them into signals to send to the model of the
    game
    '''
    
    def __init__(self,root,direction):
        self.root = root
        self.direction = direction

        # which_game is a serial number which keeps track of
        # which game we're on (it gets incremented every time
        # the player starts a new game).
        # This is a cheap mechanism to kill all active timers
        self.which_game = root.which_game
        
        self.sleeping = False
        self.pressed = False


    # pseudocode of desired behavior:
    # while(True):
    #     wait for key press
    #     while(True):
    #         # do
    #         move the player
    #         wait 60 milliseconds
    #         if(not pressed):
    #             break

    # self.pressed will keep track of whether the key is up or down
    # self.sleeping will be True if we're waiting for the timer,
    # else False
        
    # goto the line labeled "# do stuff" in the pseudocode
    def _do_stuff(self):
        self.root.state["move"] = self.direction
        delay = self.root.settings["player_period"]
        self.root.after(delay,self._timer)
        self.sleeping = True
        
    def keyup(self,event):
        '''Called when key released'''
        self.pressed = False

    def keydown(self,event):
        '''Called when key pressed'''
        self.pressed = True
        if(self.sleeping == False):
            self._do_stuff()

    # timer callback
    def _timer(self):
        if(self.root.which_game != self.which_game):
            return # the game is over
        if(self.pressed):
            self._do_stuff()
        else:
            self.sleeping = False


        
        




class TimerManager:
    '''This class manages the timer that moves the monster.
    Matters are complicated by the occasional need to pause
    the timer.'''
    def __init__(self,root):
        self.root = root
        
        # which_game is a serial number which keeps track of
        # which game we're on (it gets incremented every time
        # the player starts a new game).
        # This is a cheap mechanism to kill all active timers
        self.which_game = root.which_game

        # keeps track of where we're waiting in the pseudocode below
        self.awaiting_unpause = False

        self.root.state.watch_key("paused",self._pause_watch)
        self._timer() # start the game

    # Pseudocode for desired behavior:
    # while(True):
    #     while(paused):
    #         pass
    #     # do stuff
    #     move monsters
    #     wait 120 milliseconds

    # go to line labeled "do stuff" in the pseudocode
    def _do_stuff(self):
        self.root.state["tick"] = True
        delay = self.root.settings["monster_period"]
        self.root.after(delay,self._timer)
        self.awaiting_unpause = False

    # called whenever state["paused"] changes
    # ...but we only care when the game *un*pauses AND
    # we're waiting for that to happen!
    def _pause_watch(self):
        if(self.awaiting_unpause and
           self.root.state["paused"] == False):
            self._do_stuff()
        
    # timer callback
    def _timer(self):
        if(self.root.which_game != self.which_game):
            return # the game is over
        if(self.root.state["paused"]):
            self.awaiting_unpause = True
            # and then wait.
        else:
            self._do_stuff()
            
        

class MazeGame(Tk):
    '''The main application'''
    def __init__(self):
        super().__init__()
        self.title("Maze Game")
        self.resizable(width=False, height=False) # resizing disallowed

        self.canvas = Canvas(self)
        # note: the dimensions and bg color of the canvas
        # are set in graphics.draw_world()

        # TODO: I've forgotten what's going on here
        self.canvas.grid(columnspan=2, sticky="NEWS")
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=0)
        self.columnconfigure(0,weight=0)
        self.columnconfigure(1,weight=1)

        # SERIAL NUMBER of the current game:
        # Every time a new game is started, which_game increases by 1
        # 
        # This is a cheap mechanism for killing off all the timers,
        # without maintaining a list of active ones.
        #
        # Each object that creates timers (each instance of
        # KeyBounceManager or of TimerManager) writes down what this
        # serial number is when it's created.  When timers fire, they
        # check whether the serial number has increased, and break
        # out of the loops in that case.
        self.which_game = 0
        
        self.setup_game()
        self.bind("<Escape>", self.esc_callback)

    def esc_callback(self,event):
        '''Callback called whenever the user presses ESC, to restart the game'''
        self.canvas.delete(ALL)
        self.which_game += 1
        self.setup_game()
        
        
    def setup_game(self):
        '''Called at the start of each game.  Creates the initial
        configuration, attaches all the listeners/observers to
        enforce rules, draws the initial world on the canvas, sets up
        the timers and keyboard callbacks.'''
        self.settings = {'cols':20, 'rows':20, 'loops':2,
                         'nmon':5, 'top':0.33, 'mid':0.33,
                         'guards':0.33, 'danger_radius':14,
                         'fog_radius':7,
                         'monster_period':150, 'player_period':60}
        # TODO: add a dialog to select settings
        
        self.state = build_world(self.settings)
        draw_world(self.settings,self.state,self.canvas)

        # Callback called when the user presses <space>,
        # to try and pause/unpause
        def space_bar(event):
            self.state['tilt'] = True
        self.bind("<space>", space_bar)

        # attach all the keys
        for j in [["Up","Left","Down","Right"],["w","a","s","d"]]:
            for i in range(4):
                textdir = j[i]
                vectdir = [(0,-1),(-1,0),(0,1),(1,0)][i]
                key_manager = KeyBounceManager(root=self,direction=vectdir)
                self.bind("<KeyPress-%s>" % textdir, key_manager.keydown)
                self.bind("<KeyRelease-%s>" % textdir, key_manager.keyup)

        # set up timer to move the monsters, and start the game
        TimerManager(self)



# create the program and run it
root = MazeGame()
root.mainloop()
