#! /usr/bin/python3
from tkinter import *
from collections import deque
from math import sqrt
import random
import time

root = Tk()

canv = Canvas(root, bg="white", height=410, width=410)
canv.grid(columnspan=2, sticky="NEWS")
# label = Label(root, text="Settings:")
# label.grid(sticky=E)
# txt = Entry(root)
# txt.grid(row=1,column=1,sticky="EW")




root.rowconfigure(0,weight=1)
root.rowconfigure(1,weight=0)
root.columnconfigure(0,weight=0)
root.columnconfigure(1,weight=1)



class direction:
    pass

def neighbors(loc, randomize=True):
    retval = []
    retval.append((loc[0],loc[1]-1))
    retval.append((loc[0],loc[1]+1))
    retval.append((loc[0]-1,loc[1]))
    retval.append((loc[0]+1,loc[1]))
    if randomize:
        random.shuffle(retval)
    return retval

def makemaze(nrows, ncols, breadthfirst):
    bigr = 2*nrows+1
    bigc = 2*ncols+1
    q = []
    open_loc = set()

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
        # if(random.randint(1,100) == 1):
        #     print(found)
    print(steps)
        
    # def handle_loc(loc):
    #     open_loc.add(loc)
    #     nbhrs = neighbors(loc)
    #     for i in range(4):
    #         d = direction()
    #         d.start = loc
    #         d.gate = nbhrs[i]
    #         q.append(d)
    # startx = 2*random.randint(1,ncols)-1
    # starty = 2*random.randint(1,nrows)-1
    # handle_loc((startx,starty))
    # haha = 0
    # print("starting at (%d,%d)" % (startx,starty))
    # while(len(q) > 0):
    #     # if(random.randint(1,300) == 1):
    #     #     print("haha!")
    #     #     breadthfirst = not breadthfirst
    #     haha += 1
    #     if(breadthfirst and haha > 60): # ncols*nrows/2):
    #         breadthfirst = False
    #         haha = 0
    #         print("haha1")
    #     elif(not breadthfirst and haha > 60): # ncols*nrows/2):
    #         breadthfirst = True
    #         haha = 0
    #         print("haha2")
    #     if(breadthfirst):
    #         d = q.pop(random.randint(1,len(q))-1)
    #     else:
    #         if(len(q) > 10 and random.randint(1,2) == 1 and False):
    #             d = q.pop(len(q) - 10)
    #         else:
    #             d = q.pop()
    #     start = d.start
    #     # breadthfirst = ((start[0] % 4) != (start[1] % 4))
    #     gate = d.gate
    #     delta = (gate[0]-start[0],gate[1]-start[1])
    #     target = (gate[0]+delta[0],gate[1]+delta[1])
    #     if(target[0] < 0 or target[0] >= bigc):
    #         continue
    #     if(target[1] < 0 or target[1] >= bigr):
    #         continue
    #     if(target in open_loc):
    #         continue
    #     open_loc.add(gate)
    #     handle_loc(target)
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
                score = dijkstra((ax,ay),(bx,by),open_loc)
                if score > bestscore:
                    bestscore = score
                    best = (x,y)
            open_loc.add(best)
    open_loc.add((2*random.randint(1,ncols)-1,0))
    return open_loc

dijkstradata = {}

def dijkstra(start,end, open_loc):
    global dijkstradata
    frontier = {start}
    dijkstradata = {start:start}
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
                dijkstradata[c2] = curr
        frontier = nextfrontier
        d += 1

                

                     
class boss:
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
        dx = boss.normalize(self.home.player[0] - self.loc[0])
        dy = boss.normalize(self.home.player[1] - self.loc[1])
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
            dx = boss.normalize(self.hunting[0] - self.loc[0])
            dy = boss.normalize(self.hunting[1] - self.loc[1])
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
    def __init__(self,nrows,ncols,boohoo,enemies):
        self.maze = makemaze(nrows,ncols,boohoo)
        self.player = (random.randint(1,ncols)*2-1,nrows*2-1)
        self.nrows = nrows
        self.ncols = ncols
        self.running = 0

        self.visibility = set()
        self.updateVis()

        
        self.bosses = []
        # for i in range(enemies):
        #     self.bosses.append(boss(self))
        top = 2 # enemies//2
        bot = 1 # 0 # actually middle
        mid = 3 # enemies - top - bot
        for i in range(top):
            self.bosses.append(boss(self,(random.randint(1,ncols)*2-1,1)))
        for j in range(bot):
            while(True):
                x = random.randint(1,ncols)*2-1
                if(abs(x - self.player[0]) > ncols*2//3):
                    break
            self.bosses.append(boss(self,(x,(nrows//2)*2-1)))

            # x = (self.player[0] + 1)//2
            
            # x = random.randint(ncols//4,ncols//2 + ncols//4)
            # print("Modifier is %d" % x)
            # x += (self.player[0]+1)//2
            # print("Putting it at %d" % x)
            # x %= ncols
            # print("JK actually %d" % x)
            # self.bosses.append(boss(self,(x*2+1,nrows*2-3)))
        # find the exit
        x = 0
        while((x,0) not in self.maze):
            x += 1
        d = dijkstra(self.player,(x,0), self.maze)
        delta = d//2//mid + 1
        loc = (x,0)
        for i in range(mid):
            for j in range(delta):
                loc = dijkstradata[loc]
            self.bosses.append(boss(self,loc))
            
        

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

    # callback(x,y,b) means boss b has moved to location (x,y)
    def moveBosses(self,callback = False):
        if self.running != 0:
            return
        for b in self.bosses:
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
        for b in self.bosses:
            if self.player == b.loc:
                self.running = -1
        if(self.player[1] == 0):
            self.running = 1
            for g in grays:
                canv.coords(grays[g], -10, -10, 0, 0)
        return True

ms_delay = 150
ms_player = 60
    
aft_canc = False

def setup(nrows,ncols,boohoo):
    canv.delete(ALL)
    global mod
    mod = model(nrows, ncols, boohoo, 5)
    global grays, oranges, green, boss_circ, bc_vis
    grays = {}
    oranges = {}
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.maze):
                canv.create_rectangle(i*10,j*10,i*10+10,j*10+10,fill="black")
            # elif (i,j) in dijkstradata:
            #     (ii,jj) = dijkstradata[(i,j)]
            #     if(abs(ii-i) + abs(jj -j) != 1):
            #         print("(%d,%d) points to (%d,%d)" % (i,j,ii,jj))
            #     canv.create_line(i*10+5,j*10+5,(i+ii)*5+5,(j+jj)*5+5, fill="blue")
    (i,j) = mod.player
    green = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="blue")
    for b in mod.bosses:
        (i,j) = b.loc
        oranges[b] = canv.create_oval(i*10,j*10,i*10+10,j*10+10,fill="orange")
    word = "gray"
    for i in range(2*ncols+1):
        for j in range(2*nrows+1):
            if((i,j) not in mod.visibility):  # and False:
                grays[(i,j)] = canv.create_rectangle(i*10,j*10,
                                                     i*10+10,j*10+10,
                                                     fill=word, outline=word) # "gray"
            else:
                grays[(i,j)] = canv.create_rectangle(-10,-10,0,0,fill=word, outline=word) # "gray"
    boss_circ = canv.create_oval(-10,-10,0,0,fill="",outline="red",width="1.5")
    bc_vis = False
    update_boss_circ()

    # register the callbacks for the windowing system
    global aft_canc
    aft_canc = root.after(ms_delay,timecall)
    global thingies
    thingies = {}
    for j in [["Up","Left","Down","Right"],["w","a","s","d"]]:
        for i in range(4):
            textdir = j[i]
            vectdir = [(0,-1),(-1,0),(0,1),(1,0)][i]
            (keydown,keyup) = keyfactory(textdir, vectdir)
            root.bind("<KeyPress-" + textdir + ">", keydown)
            root.bind("<KeyRelease-" + textdir + ">", keyup)
    

def keyfactory(textdir, vectdir):
    def keydown(event):
        # print("down")
        global thingies
        if textdir not in thingies:
            thingies[textdir] = thingy(vectdir)
        else:
            thingies[textdir].uncancel()
    def keyup(event):
        # print("up")
        global thingies
        if textdir in thingies:
            thingies[textdir].cancel()
            # del thingies[textdir]
    return (keydown, keyup)

        
    
    

class thingy:
    def __init__(self, dir):
        self.canceled = False
        self.dir = dir
        self.doit()
    def doit(self):
        # print("gogogo!" + str(mod.running))
        if(self.canceled or mod.running != 0):
            global thingies
            t = False
            for txt in thingies:
                if thingies[txt] == self:
                    t = txt
                    break
            if(t):
                del thingies[t]
            return
        root.after(ms_player, self.doit)
        # t = time.clock()
        if(paused):
            return
        s = mod.attemptPlayerMove(self.dir[0],self.dir[1],
                              lambda i,j: canv.coords(grays[(i,j)], -10, -10, 0, 0))
        # if(not s):
        #     print("Player silly")
        # else:
        #     print("Player moves")
        # print("Player" + str(time.clock() - t))
        (i,j) = mod.player
        canv.coords(green,i*10,j*10,i*10+10,j*10+10)
        update_boss_circ()
        root.update_idletasks()

        # print("rereg")


    def cancel(self):
        self.canceled = True
    def uncancel(self):
        self.canceled = False

paused = False

def timecall():
    if(mod.running != 0):
        return
    global aft_canc
    aft_canc = root.after(ms_delay,timecall)
    if(paused):
        return
    mod.moveBosses(lambda i, j, b: canv.coords(oranges[b], i*10, j*10, i*10+10, j*10+10))
    # print("Bosses move")
    # print("Monsters" + str(time.clock() - t))
    update_boss_circ()
    root.update_idletasks()

def update_boss_circ():
    global boss_circ, bc_vis
    best_dist = 2000
    (px,py) = mod.player
    for b in mod.bosses:
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
        canv.coords(boss_circ,px-d,py-d,px+d,py+d)
        bc_vis = True
    else:
        canv.coords(boss_circ,-10,-10,0,0)
        bc_vis = False

setup(20,20,random.randint(1,2)==1)

def kill(e):
    if(aft_canc != False):
        root.after_cancel(aft_canc)
    setup(20,20,random.randint(1,2)==1)

def pause(e):
    global paused
    if(bc_vis and not paused):
        return
    paused = not paused

root.bind("<Escape>", kill)
root.bind("<space>", pause)

root.mainloop()



# def rightclick(event):
#     if(startx != -1):
#         x = canv.canvasx(event.x)
#         y = canv.canvasy(event.y)
#         x = int(x/10)
#         y = int(y/10)
#         if((x,y) not in maz):
#             return
#         print(dijkstra((startx,starty),(x,y),maz))
    
# def leftclick(event):
#     x = canv.canvasx(event.x)
#     y = canv.canvasy(event.y)
#     x = int(x/10)
#     y = int(y/10)
#     if((x,y) not in maz):
#         return
#     global startx, starty, blah
#     startx = x
#     starty = y
#     if(blah == -1):
#         blah = canv.create_oval(x*10,y*10,x*10+10,y*10+10,fill="orange")
#     else:
#         canv.coords(blah, x*10, y*10, x*10+10, y*10+10)
    

# def mousedown(event):
#     global curr
#     curr = n
#     add_point(canv.canvasx(event.x),canv.canvasy(event.y))
#     root.update_idletasks()
              
# def mouseup(event):
#     global curr
#     curr = -1

# def mousemove(event):
#     global x, y
#     if(curr != -1):
#         x[curr] = canv.canvasx(event.x)
#         y[curr] = canv.canvasy(event.y)
#         draw_ith(curr)
#         root.update_idletasks()
        
    


# canv.bind("<Button-1>", leftclick)
# canv.bind("<Button-3>", rightclick)
# canv.bind("<B1-Motion>", mousemove)
# canv.bind("<ButtonRelease-1>", mouseup)



