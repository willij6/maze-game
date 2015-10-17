#! /usr/bin/python3
from tkinter import *
from math import sqrt
from box import *

from rules import build_world

default_settings = {'cols':20, 'rows':20, 'loops':2,
            'nmon':5, 'top':0.33, 'mid':0.33, 'guards':0.33,
            'danger_radius':14, 'fog_radius':7}
# TODO: add a settings menu



root = Tk()
root.title("Maze Game")
root.resizable(width=False, height=False)

canv = Canvas(root, bg="white", height=410, width=410)
canv.grid(columnspan=2, sticky="NEWS")

root.rowconfigure(0,weight=1)
root.rowconfigure(1,weight=0)
root.columnconfigure(0,weight=0)
root.columnconfigure(1,weight=1)

# TODO figure out what all that was about, and find a way for the
# Canvas to resize itself at the right times


def times_ten(x,y):
    return (x*10,y*10,(x+1)*10,(y+1)*10)

# to make things invisible, send them here
def siberia():
    return (-10,-10,0,0)

def dist(p1,p2):
    (x,y) = p1
    (xx,yy) = p2
    return sqrt((x-xx)**2+(y-yy)**2)


# draw it, and attach all the hooks except for restart
# return a callback for cleanup
def draw_world(settings,state):
    rows = settings['rows']
    cols = settings['cols']
    nmon = settings['nmon']
    bigc = 2*cols+1
    bigr = 2*rows+1

    canv.delete(ALL)
    
    # the draw order matters :-/
    # fog needs to cover the maze
    for i in range(bigc):
        for j in range(bigr):
            if not state['open'][(i,j)]:
                canv.create_rectangle(*(times_ten(i,j)), fill="black")
    
    # now things get tricky...
    monsters = {}
    for i in range(nmon):
        mloc = state['monsters'][i]
        monsters[i] = canv.create_oval(*(times_ten(*mloc)), fill="orange")

    def monster_relocator(which):
        mloc = state['monsters'][which]
        canv.coords(monsters[which],*(times_ten(*mloc)))
    state['monsters'].watch(monster_relocator)

    # well, that was easy

    ploc = state['player']
    player = canv.create_oval(*(times_ten(*ploc)), fill="blue")
    
    def player_relocator():
        ploc = state['player']
        canv.coords(player,*(times_ten(*ploc)))
    state.watch_key('player',player_relocator)


    # the fog
    fog = {}
    for i in range(bigc):
        for j in range(bigr):
            fog[(i,j)] = canv.create_rectangle(*(times_ten(i,j)),
                                               fill="gray",outline="gray")
    def fog_helper(p):
        if(state['fog'][p]):
            canv.coords(fog[p],*(times_ten(*p)))
        else:
            canv.coords(fog[p],*(siberia()))
    for i in range(bigc):
        for j in range(bigr):
            fog_helper((i,j))
    state['fog'].watch(fog_helper)

    # the radar circle
    radar = canv.create_oval(*(siberia()), fill="", outline="red", width="1.5")

    def radar_update():
        if(state['danger'] == False):
            canv.coords(radar,*(siberia()))
            return
        p = state['player']
        dists = [dist(p,state['monsters'][i]) for i in range(nmon)]
        radius = min(dists)*10
        p = (p[0]*10+5,p[1]*10+5)
        canv.coords(radar,p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius)

    # DON'T register this, because it would be updated too many times!
    radar_update()


    # okay, now everything is drawn
    # register callbacks

    def space_bar(event):
        state['tilt'] = 1337
    root.bind("<space>", space_bar)





    ms_delay = 150 # TODO MAKE IT A SETTING
    ms_player = 60 # timing for when the player moves

    monster_timer = False
    
    key_timers = {}

    def cleanup():
        if(monster_timer):
            root.after_cancel(monster_timer)
        for k in key_timers:
            root.after_cancel(k)
            

    awaiting_unpause = False
    def timecall():
        nonlocal awaiting_unpause
        if(not state['paused']):
            state['tick'] = 1337
            radar_update()
            monster_timer = root.after(ms_delay,timecall)
        else:
            awaiting_unpause = True

    def unpause_watcher():
        nonlocal awaiting_unpause
        if(awaiting_unpause and not state['paused']):
            state['tick'] = 1337
            radar_update()
            awaiting_unpause = False
            monster_timer = root.after(ms_delay,timecall)
    state.watch_key('paused',unpause_watcher)

    def bind_key(textdir, vectdir):
        pressed = False
        def keyup(event):
            nonlocal pressed
            pressed = False
            
        def keydown(event):
            nonlocal pressed
            pressed = True
            if(textdir in key_timers):
                return
            state['move'] = vectdir
            radar_update()
            key_timers[textdir] = root.after(ms_player,time_callback)

        def time_callback():
            if(not pressed):
                del key_timers[textdir]
                return # don't reregister
            state['move'] = vectdir
            radar_update()
            key_timers[textdir] = root.after(ms_player,time_callback)
        root.bind("<KeyPress-%s>" % textdir, keydown)
        root.bind("<KeyRelease-%s>" % textdir, keyup)
    for j in [["Up","Left","Down","Right"],["w","a","s","d"]]:
        for i in range(4):
            textdir = j[i]
            vectdir = [(0,-1),(-1,0),(0,1),(1,0)][i]
            bind_key(textdir, vectdir)

    timecall() # start the game
    return cleanup



def esc_callback(event):
    cleanup_callback()
    do_a_game()

def do_a_game():
    global cleanup_callback
    settings = default_settings
    state = build_world(settings)
    cleanup_callback = draw_world(settings,state)
    

do_a_game()
root.bind("<Escape>", esc_callback)
root.mainloop()

# TODO: unbind things when necessary?

