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


root = Tk()
root.title("Maze Game")
root.resizable(width=False, height=False)

canv = Canvas(root, bg="white", height=bigrows*10, width=bigcols*10)
canv.grid(columnspan=2, sticky="NEWS")

root.rowconfigure(0,weight=1)
root.rowconfigure(1,weight=0)
root.columnconfigure(0,weight=0)
root.columnconfigure(1,weight=1)


def neighbors(loc, randomize=True):
    retval = []
    retval.append((loc[0],loc[1]-1))
    retval.append((loc[0],loc[1]+1))
    retval.append((loc[0]-1,loc[1]))
    retval.append((loc[0]+1,loc[1]))
    if randomize:
        random.shuffle(retval)
    return retval

def makemaze(nrows, ncols):
    bigr = 2*nrows+1
    bigc = 2*ncols+1
    open_loc = set() # eventual return value

    x = 2*random.randint(1,ncols)-1
    y = 2*random.randint(1,nrows)-1
    open_loc.add((x,y))
    found = 1
    steps = 0
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
        
    if ncols > 5 and nrows > 5 and True:
        for j in range(2):
            bestscore = -1
            for i in range(30):
                while True:
                    z = random.randint(0,1)
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
                score = distance((ax,ay),(bx,by),open_loc)
                if score > bestscore:
                    bestscore = score
                    best = (x,y)
            open_loc.add(best)
    open_loc.add((2*random.randint(1,ncols)-1,0))
    return open_loc


# this global data exists because in one case, after
# running the distance function, we need the data of the optimal
# path between the two points
#
distancedata = {}

def distance(start,end, open_loc):
    global distancedata
    frontier = {start}
    distancedata = {start:start}
    old = set()
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

                

                     
class monster:
    def __init__(self,home,loc):
        self.home = home
        self.loc = loc
        self.prevloc = False
        self.hunting = False

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
        if((dx == 0) != (dy == 0)):
            (x,y) = self.loc
            while(True):
                x += dx
                y += dy
                if((x,y) not in self.home.maze):
                    break
                elif (x,y) == self.home.player:
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
            self.hunting = False
        # okay, just move randomly
        nbhr = neighbors(self.loc)
        nbhr = [x for x in nbhr if (x != self.prevloc and x in self.home.maze)]
        if len(nbhr) == 0:
            t = self.loc
            self.loc = self.prevloc
            self.prevloc = t
            return
        else:
            self.prevloc = self.loc
            self.loc = nbhr[0]
            return

class model:
    def __init__(self,nrows,ncols):
        self.maze = makemaze(nrows,ncols)
        self.player = (random.randint(1,ncols)*2-1,nrows*2-1)
        self.nrows = nrows
        self.ncols = ncols
        self.running = 0

        self.visibility = set()
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
                if(abs(x - self.player[0]) > ncols*2//3):
                    break
            self.monsters.append(monster(self,(x,(nrows//2)*2-1)))


        x = 0
        while((x,0) not in self.maze):
            x += 1 # find the exit
        d = distance(self.player,(x,0), self.maze)
        delta = d//2//mid + 1
        loc = (x,0)
        for i in range(mid):
            for j in range(delta):
                loc = distancedata[loc]
            self.monsters.append(monster(self,loc))
            
        

    # call(i,j) to indicate that (i,j) has become visible
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

    # callback(x,y,b) means monster b has moved to location (x,y)
    def moveMonsters(self,callback = False):
        if self.running != 0:
            return
        for b in self.monsters:
            b.move()
            if b.loc == self.player:
                self.running = -1
            if(callback):
                callback(b.loc[0],b.loc[1],b)

    # viscall(i,j) means that (i,j) has become visible
    def attemptPlayerMove(self,dx,dy,viscall = False):
        if self.running != 0:
            return False
        n = (self.player[0]+dx,self.player[1]+dy)
        if n not in self.maze:
            return False
        self.player = n
        self.updateVis(viscall)
        for b in self.monsters:
            if self.player == b.loc:
                self.running = -1
        if(self.player[1] == 0):
            self.running = 1
            for g in grays:
                canv.coords(grays[g], -10, -10, 0, 0)
        return True

ms_delay = 150 # timing for when the monsters move
ms_player = 60 # timing for when the player moves
    
aft_canc = False

# this function mostly sets up the graphics
# though it also creates the maze
# setup() gets called when the game (re)starts
def setup(nrows,ncols):
    canv.delete(ALL)
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
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.maze):
                canv.create_rectangle(i*10,j*10,i*10+10,j*10+10,fill="black")

    (i,j) = mod.player
    green = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="blue")
    for b in mod.monsters:
        (i,j) = b.loc
        oranges[b] = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="orange")
    word = "gray" # change this to "" to make the whole maze be visible
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.visibility):
                grays[(i,j)] = canv.create_rectangle(i*10,j*10,
                                                     i*10+10,j*10+10,
                                                     fill=word, outline=word)
            else:
                grays[(i,j)] = canv.create_rectangle(-10,-10,0,0,fill=word, outline=word)
    # red "radar" circle showing distance to nearest monster
    # it starts off the map, to be invisible (probably better ways to do this)
    monster_circ = canv.create_oval(-10,-10,0,0,fill="",outline="red",width="1.5")
    bc_vis = False
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

paused = False

# this function gets called when the monsters need to be moved
def timecall():
    if(mod.running != 0):
        return
    global aft_canc
    aft_canc = root.after(ms_delay,timecall)
    if(paused):
        return
    mod.moveMonsters(lambda i, j, b: canv.coords(oranges[b], i*10, j*10, i*10+10, j*10+10))
    update_monster_circ()
    root.update_idletasks()

def update_monster_circ():
    global monster_circ, bc_vis
    best_dist = 2000
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
        canv.coords(monster_circ,-10,-10,0,0)
        bc_vis = False

setup(numrows,numcols)

def kill(e):
    if(aft_canc != False):
        root.after_cancel(aft_canc)
    setup(numrows,numcols)

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
