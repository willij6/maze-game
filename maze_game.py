#! /usr/bin/python3
from tkinter import *
from collections import deque
from math import sqrt
import random
import time


numrows = 20
numcols = 20
bigrows = 2*numrows+1
bigcols = 2*numcols+1

# here's the start of setting up the UI

root = Tk()
root.title("Maze Game")
root.resizable(width=False, height=False)

canv = Canvas(root, bg="white", height=bigrows*10, width=bigcols*10)
canv.grid(columnspan=2, sticky="NEWS")

# some packing

root.rowconfigure(0,weight=1)
root.rowconfigure(1,weight=0)
root.columnconfigure(0,weight=0)
root.columnconfigure(1,weight=1)

# this gets the four immediate neighbors
# of the tuple 'loc', possibly in a random order
def neighbors(loc, randomize=True):
    retval = []
    retval.append((loc[0],loc[1]-1))
    retval.append((loc[0],loc[1]+1))
    retval.append((loc[0]-1,loc[1]))
    retval.append((loc[0]+1,loc[1]))
    if randomize:
        random.shuffle(retval)
    return retval

# this makes an (nrows*2+1)x(ncols*2+1) maze
# it returns a set containing all the open locations in the maze
# as pairs (i,j) where i is the column and j is the row
def makemaze(nrows, ncols):
    bigr = 2*nrows+1 # the actual number of rows
    bigc = 2*ncols+1 # the actual number of columns
    open_loc = set() # eventual return value

    # the maze generation algorithm is the following:
    # do a random walk.  When going from location a to location b
    # add the edge from a to b if this is the first time we've reached b

    # we're thinking of a graph whose vertices are the positions (i,j)
    # with i and j both odd, and whose edges are the positions (i,j)
    # with exactly one of i and j odd.

    # positions with i and j both even will never be hollowed out

    # find the starting location
    x = 2*random.randint(1,ncols)-1
    y = 2*random.randint(1,nrows)-1
    open_loc.add((x,y)) # add it to the maze

    found = 1 # variable to keep track of how many vertices we've reached
    steps = 0 # keep track of the number of steps, for debugging purposes
    while(found < ncols*nrows):
        steps += 1
        gate = neighbors((x,y))[0]
        second = (2*gate[0]-x,2*gate[1]-y)
        if(second[0] < 0 or second[0] > 2*ncols):
            continue
        if(second[1] < 0 or second[1] > 2*nrows):
            continue
        if(second not in open_loc):
            open_loc.add(gate)
            open_loc.add(second)
            found += 1
        (x,y) = second
        

    # now we have a maze
    #
    # However, we're going to modify it a little, by knocking out
    # a few more walls.  This introduces loops into the maze,
    # and makes the game easier and more interesting

    # we'll try to add in two loops
    # if the board is too small, this might be impossible
    # requiring that it has at least 10 rows and 10 columns should be
    # good enough...
    if ncols > 5 and nrows > 5 and True:
        
        # add in two shortcuts
        for j in range(2):

            # we don't want to just knock out a random wall,
            # because this has good odds of producing a
            # short and boring loop (like a loop of length 8,
            # not very helpful for the player)
            #
            # So instead, we try 30 random walls, and choose the
            # one which creates the biggest loop
            bestscore = -1
            for i in range(30):
                while True:
                    # loop until we find a wall
                    z = random.randint(0,1) # vertical vs horizontal wall
                    if z == 0:
                        x = 2*random.randint(1,ncols-1)
                        y = 2*random.randint(1,nrows)-1
                        ax = x - 1
                        bx = x+1
                        ay = by = y
                    else:
                        x = 2*random.randint(1,ncols)-1
                        y = 2*random.randint(1,nrows-1)
                        ax = bx = x
                        ay = y - 1
                        by = y + 1
                    if (x,y) not in open_loc:
                        break
                # now (x,y) is the location of a wall
                #   (ax,ay) and (bx,by) are the open spaces on either side
                score = distance((ax,ay),(bx,by),open_loc)
                if score > bestscore:
                    bestscore = score
                    best = (x,y)
            open_loc.add(best)
    open_loc.add((2*random.randint(1,ncols)-1,0))
    return open_loc



# distancedata is a dictionary which sends x -> y if the minimal
# path from start to x ends with y -> x
# (so distancedata lets you work backwards from end to start and
#  and recover the minimal path)

distancedata = {}

# this is a global variable because in one case, after
# running the distance function, we need the data of the optimal
# path between the two points


# open_loc: a set of pairs (i,j) that are the vertices of a graph,
# with (i,j) and (ii,jj) neighboring if separated by (manhattan) distance 1
#
# returns distance from start to end, which had better be in open_loc
def distance(start,end, open_loc):
    global distancedata
    frontier = {start}
    distancedata = {start:start}
    old = set()
    # the set of nodes considered so far is
    # the union of old and frontier
    #
    # At the beginning of step d, frontier is exactly the set of
    # nodes of distance d from start
    d = 0
    while True:
        nextfrontier = set()
        while len(frontier) > 0:
            curr = frontier.pop()
            old.add(curr)
            if curr == end:
                return d
            for c2 in neighbors(curr,False):
                if c2 not in open_loc:
                    continue
                if c2 in old or c2 in frontier:
                    continue
                nextfrontier.add(c2)
                distancedata[c2] = curr
        frontier = nextfrontier
        d += 1

                

# this class governs the internal state and behavior of the monsters
class monster:
    def __init__(self,home,loc):
        self.home = home
        self.loc = loc

        # remember where we were last round, to avoid backtracking
        self.prevloc = False
        # are we chasing down the player?
        self.hunting = False
        # if self.hunting isn't False, then self.hunting will be the tuple
        # where we last saw the player

    def normalize(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0
    
    def move(self):
        # first check visibility of the player
        dx = monster.normalize(self.home.player[0] - self.loc[0])
        dy = monster.normalize(self.home.player[1] - self.loc[1])
        if((dx == 0) != (dy == 0)): # is the player in an orthogonal direction?
            (x,y) = self.loc
            # look at consecutive positions in that direction till we find
            # the player...
            while(True):
                x += dx
                y += dy
                if((x,y) not in self.home.maze):
                    break
                elif (x,y) == self.home.player:
                    # remember where we last saw the player
                    self.hunting = self.home.player
                    break
        # okay, now we know whether we're hunting
        if(self.hunting):
            dx = monster.normalize(self.hunting[0] - self.loc[0])
            dy = monster.normalize(self.hunting[1] - self.loc[1])
            if(dx != 0 or dy != 0):
                self.prevloc = self.loc
                self.loc = (self.loc[0]+dx,self.loc[1]+dy)
                return
            # else:
            #     we've reached the place we last saw the player
            #     guess he lost us
            self.hunting = False
        # okay, just move randomly
        nbhr = neighbors(self.loc) # these'll be randomized
        nbhr = [x for x in nbhr if (x != self.prevloc and x in self.home.maze)]
        if len(nbhr) == 0:
            # we're in a dead end and must turn around
            t = self.loc
            self.loc = self.prevloc
            self.prevloc = t
            return
        else: 
            self.prevloc = self.loc
            self.loc = nbhr[0]
            return

# this class is supposed to represent the state of the game,
# as opposed to the UI
#
# It's a mess, and this is a big part of why the next commit
# will essentially have everything rewritten from scratch
class model:
    def __init__(self,nrows,ncols):
        self.maze = makemaze(nrows,ncols)
        self.player = (random.randint(1,ncols)*2-1,nrows*2-1)
        self.nrows = nrows
        self.ncols = ncols
        self.running = 0 # 1 means victory, -1 means loss

        # the set of places that have been explored
        self.visibility = set()
        # ensure initial area around player is revealed
        self.updateVis()

        
        self.monsters = []
        top = 2 # two monsters start along the top of the map
        bot = 1 # 1 monster starts along the bottom
                # oops halfway between the top and the bottom
        mid = 3 # 3 monsters start out spaced evenly along the
                # shortest path between the player and the exit
        for i in range(top):
            self.monsters.append(monster(self,(random.randint(1,ncols)*2-1,1)))
        for j in range(bot):
            while(True):
                x = random.randint(1,ncols)*2-1
                # [check whether this location is too close to the player
                if(abs(x - self.player[0]) > ncols*2//3):
                    # it's okay
                    break
                # it's not okay, repeat the loop.]

            self.monsters.append(monster(self,(x,(nrows//2)*2-1)))


        x = 0
        while((x,0) not in self.maze):
            x += 1 # find the exit
        # (x,0) is the exit at the top of the maze
        d = distance(self.player,(x,0), self.maze)
        # rather than spacing out evenly, space along the first half
        # of the path (the half closer to the maze's exit)...
        delta = d//2//mid + 1 # ...hence the "//2" here
        loc = (x,0)
        for i in range(mid):
            for j in range(delta):
                loc = distancedata[loc]
            self.monsters.append(monster(self,loc))
            
        
    # this updates the explored areas based on the current player location
    # revealing all the nearby areas
    #
    # Once the game is running, we'd also need to change the graphical
    # representation of the game, so there's an optional callback parameter
    # that will be called on each location that needs to be revealed
    def updateVis(self,call = False):
        for i in range(self.player[0]-7,self.player[0]+7):
            if i < 0 or i >= 2*self.ncols+1:
                continue
            for j in range(self.player[1]-7,self.player[1]+7):
                if j < 0 or j >= 2*self.nrows+1:
                    continue
                self.visibility.add((i,j))
                if(call):
                    call(i,j)

    # update the monsters
    # again, we need to provide an optional callback for graphics, later
    # if monster #b moves to (x,y), then callback(x,y,b) will be called
    def moveMonsters(self,callback = False):
        if self.running != 0:
            return
        for b in self.monsters:
            b.move() # tell each monster to move itself
            if b.loc == self.player:
                self.running = -1 # you lose!
            if(callback):
                callback(b.loc[0],b.loc[1],b)

    # this tries to move the player in direciton dx, dy
    # again, there's a graphics callback optional parameter
    # viscall(i,j) will be called if position (i,j) is explored/revealed
    # For some reason there ISN'T a callback to move the player, though
    #
    # return True if the move was successful, else False
    def attemptPlayerMove(self,dx,dy,viscall = False):
        if self.running != 0: 
            return False # you can't move if the game is over
        n = (self.player[0]+dx,self.player[1]+dy)
        if n not in self.maze:
            return False # player tried to move into a wall
        self.player = n
        self.updateVis(viscall)
        for b in self.monsters:
            if self.player == b.loc:
                # player walked straight into a monster
                self.running = -1
        if(self.player[1] == 0):
            # player escaped the maze
            self.running = 1
            for g in grays:
                canv.coords(grays[g], -10, -10, 0, 0)
        return True

ms_delay = 150 # timing for when the monsters move
ms_player = 60 # timing for when the player moves
    
aft_canc = False
# when not False, this is a handle to the timer
# for managing the clock that moves the monsters


# setup() gets called when the game (re)starts
# 
# this function mostly sets up the graphics
# though it also creates the maze
def setup(nrows,ncols):
    canv.delete(ALL) # clear the canvas
    global mod
    mod = model(nrows, ncols) # this creates the maze and monsters

    global bc_vis # global variable to keep track of whether
                  # monsters are in range, i.e., whether pause is allowed

    # here are some graphics objects
    global grays, oranges, green, monster_circ
    # grays are the squares blocking visibility
    # oranges are the monsters
    # green is the player
    # monster_circ is a red circle showing how close nearest monster is
    
    grays = {}
    oranges = {}

    # draw the walls
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.maze):
                canv.create_rectangle(i*10,j*10,i*10+10,j*10+10,fill="black")

    # draw the player
    (i,j) = mod.player
    green = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="blue")

    # draw the monsters
    for b in mod.monsters:
        (i,j) = b.loc
        oranges[b] = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="orange")
        
    # draw the gray area obscuring the maze
    word = "gray" # change this to "" to make the whole maze be visible
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.visibility):
                grays[(i,j)] = canv.create_rectangle(i*10,j*10,
                                                     i*10+10,j*10+10,
                                                     fill=word, outline=word)
            else:
                # we want grays[(i,j)] to always be defined, so create a
                # rectangle off-screen
                grays[(i,j)] = canv.create_rectangle(-10,-10,0,0,fill=word, outline=word)
    # red "radar" circle showing distance to nearest monster
    # it starts off the map, to be invisible (probably better ways to do this)
    monster_circ = canv.create_oval(-10,-10,0,0,fill="",outline="red",width="1.5")
    bc_vis = False
    # in case some monsters start close to home
    update_monster_circ()

    # register the callbacks for the windowing system
    global aft_canc
    aft_canc = root.after(ms_delay,timecall)
    global keymanagers
    keymanagers = {}
    for j in [["Up","Left","Down","Right"],["w","a","s","d"]]:
        for i in range(4):
            textdir = j[i]
            vectdir = [(0,-1),(-1,0),(0,1),(1,0)][i]
            (keydown,keyup) = keyfactory(textdir, vectdir)
            root.bind("<KeyPress-" + textdir + ">", keydown)
            root.bind("<KeyRelease-" + textdir + ">", keyup)


    
# what follows is
# a horrible mess caused by problems with key bounces
# if you hold down the arrow key, tkinter thinks that
# after some point, the user is releasing and pressing the key repeatedly
# This happens on Linux Mint but not on Windows

# the current setup might be equivalent to something much simpler


def keyfactory(textdir, vectdir):
    def keydown(event):
        # print("down")
        global keymanagers
        if textdir not in keymanagers:
            keymanagers[textdir] = keymanager(vectdir)
        else:
            keymanagers[textdir].uncancel()
    def keyup(event):
        # print("up")
        global keymanagers
        if textdir in keymanagers:
            keymanagers[textdir].cancel()
    return (keydown, keyup)
    
class keymanager:
    def __init__(self, dir):
        self.canceled = False
        self.dir = dir
        self.doit()
    def doit(self):
        if(self.canceled or mod.running != 0):
            global keymanagers
            t = False
            for txt in keymanagers:
                if keymanagers[txt] == self:
                    t = txt
                    break
            if(t):
                del keymanagers[t]
            return
        root.after(ms_player, self.doit)
        if(paused):
            return
        mod.attemptPlayerMove(self.dir[0],self.dir[1],
                              lambda i,j: canv.coords(grays[(i,j)], -10, -10, 0, 0))

        (i,j) = mod.player
        canv.coords(green,i*10,j*10,i*10+10,j*10+10)
        update_monster_circ()
        root.update_idletasks()




    def cancel(self):
        self.canceled = True
    def uncancel(self):
        self.canceled = False


# Analysis of what's going on here...
# consider the 'w' key, which should trigger moving north
#
# there's basically a finite state machine
# state 1: keymanagers['w'] doesn't exist
# state 2: keymanagers['w'].canceled = True
# state 3: keymanagers['w'].canceled = False
#
# States 1-2 mean that the 'w' key is up, and state 3 means it's down
# A timer is registered in states 2 and 3, but not state 1
#
# In state 1, when the key is pressed, we try and move the player, and
# start a timer, and go to state 3
#
# In state 2 or 3, when the key is pressed or raised, we go to state 3 or 2
# 
# In state 3, when the timer fires, we try and move the player, and
# reregister the timer (remaining in state 3)
#
# In state 2, when the timer fires, we
#   don't move the player
#   don't reregister the timer
#   move to state 1


# global variable to track whether the game is paused
paused = False

# this function gets called (by Tkinter) when the monsters need to be moved
def timecall():
    if(mod.running != 0):
        # game is over, don't keep moving the monsters
        # though, it might be fun to keep moving them after a defeat
        return
    global aft_canc
    aft_canc = root.after(ms_delay,timecall) # reregister the timer
    if(paused):
        # oh wait, don't do anything
        return
    mod.moveMonsters(lambda i, j, b: canv.coords(oranges[b], i*10, j*10, i*10+10, j*10+10))
    update_monster_circ()
    root.update_idletasks()

# this function updates the red circle indicating closest monster
# as well as the variable bc_vis that determines whether the game is pausable
def update_monster_circ():
    global monster_circ, bc_vis
    best_dist = 2000 # the closest monster will be closer than 2000 units!
    (px,py) = mod.player
    for b in mod.monsters:
        (bx,by) = b.loc
        d = (bx-px)*(bx-px) + (by-py)*(by-py)
        d = sqrt(d)
        if d < best_dist:
            best_dist = d
    d = best_dist
    if(d < 7*2):
        d *= 10
        px *= 10
        py *= 10
        px += 5
        py += 5
        canv.coords(monster_circ,px-d,py-d,px+d,py+d)
        bc_vis = True
    else:
        # move the red circle off-camera
        canv.coords(monster_circ,-10,-10,0,0)
        bc_vis = False

setup(numrows,numcols)

# called when the user presses Escape, to start a new game
def kill(e):
    if(aft_canc != False):
        root.after_cancel(aft_canc)
    setup(numrows,numcols)

# called when the user presses Space, to try pausing or unpausing
def pause(e):
    global paused
    if(bc_vis and not paused):
        return
    paused = not paused

root.bind("<Escape>", kill)
root.bind("<space>", pause)

root.mainloop()



# TODO list
#
# Refactor the code into three pieces, so that the logic governing the rules
# of the game can be as independent as possible from the code to draw the
# current game state
#
# Clean up and encapsulate the code for monitoring key states and
# solving key bounce issues
#
# Add tests
#
# Add command line flags for logging, and for varying the settings
# 
# Add a settings menu which species the size of the map and number of monsters
# as well as which algorithm to use for generating the maze
#
# Solve the timing problem in Windows
