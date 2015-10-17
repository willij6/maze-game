#! /usr/bin/python3
'''This module has the logic for drawing the world on a Tkinter
canvas.'''


from tkinter import *
from math import sqrt
from box import *

# convert maze coordinates to canvas coordinates
def times_ten(x,y):
    return (x*10,y*10,(x+1)*10,(y+1)*10)

# to make things invisible, send them here
def siberia():
    return (-10,-10,0,0)

# calculate distance between two points
def dist(p1,p2):
    (x,y) = p1
    (xx,yy) = p2
    return sqrt((x-xx)**2+(y-yy)**2)



def draw_world(settings,state,canv):
    '''(1) draw the state on the canvas, and (2) attach listeners to
       the state that will draw all future changes in the state.'''

    rows = settings['rows']
    cols = settings['cols']
    nmon = settings['nmon']
    bigc = 2*cols+1
    bigr = 2*rows+1

    canv.config(width=10*bigc,height=10*bigr, bg="white")

    # the order in which things are drawn determines what's on top
    # (there's apparently no way to change this after the fact)
    # So, things must be drawn in this order:
    # 1. the maze
    # 2. the player character
    # 3. monsters
    # 4. fog
    # 5. radar circle
    
    # 1. the maze
    for i in range(bigc):
        for j in range(bigr):
            if not state['open'][(i,j)]:
                canv.create_rectangle(*(times_ten(i,j)), fill="black")
    

    # 2. the player character
    ploc = state['player']
    player = canv.create_oval(*(times_ten(*ploc)), fill="blue")
    # also need a callback to update this as the player moves
    def player_relocator():
        ploc = state['player']
        canv.coords(player,*(times_ten(*ploc)))
    state.watch_key('player',player_relocator)



    # 3. the monsters
    monsters = {}
    for i in range(nmon):
        mloc = state['monsters'][i]
        monsters[i] = canv.create_oval(*(times_ten(*mloc)), fill="orange")

    def monster_relocator(which):
        mloc = state['monsters'][which]
        canv.coords(monsters[which],*(times_ten(*mloc)))
    state['monsters'].watch(monster_relocator)



    # 4. the fog
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
    # some of the fog should be initially cleared
    for i in range(bigc):
        for j in range(bigr):
            fog_helper((i,j))
    state['fog'].watch(fog_helper)

    # 5. the radar circle
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

    # perhaps the player starts near monsters
    radar_update()

    # rather than updating that circle after each individual
    # monster moves, we instead update it after each signal
    # is sent from the UI to the rules
    state.watch_key('tick',radar_update)
    state.watch_key('move',radar_update)
    state.watch_key('tilt',radar_update)    
    # TODO: this is problematic; we're relying on the fact
    # that listeners are notified in the order registered
    # Is that robust?
