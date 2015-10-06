#! /usr/bin/python3

from box import *
import random
from random import randint


def plus(p1,p2):
    return (p1[0]+p2[0],p1[1]+p2[1])
    
def minus(p1,p2):
    return (p1[0]-p2[0],p1[1]-p2[1])
    
def sq_dist(p1,p2):
    d = minus(p1,p2)
    return d[0]**2+d[1]**2


directions = [(1,0),(0,1),(-1,0),(0,-1)]

             
def make_maze(settings):
    cols = settings['cols']
    rows = settings['rows']
    bigc = 2*cols+1
    bigr = 2*rows+1
    maze = {}
    for i in range(bigc):
        for j in range(bigr):
            maze[(i,j)] = False
    loc = (2*randint(1,cols)-1, 2*randint(1,rows)-1)
    maze[loc] = True
    found = 1
    while(found < cols*rows):
        d = random.choice(directions)
        gate = plus(loc,d)
        next_loc = plus(gate,d)
        if(next_loc not in maze):
            continue
        if(maze[next_loc] == False):
            maze[next_loc] = True
            maze[gate] = True
            found += 1
        loc = next_loc


    # now, add in the shortcuts
    shortcuts = settings['loops']
    walls = (cols-1)*rows + cols*(rows-1) # how many walls between cells existed
    walls -= (cols*rows - 1) # how many walls were removed to make the maze
    # don't try and remove more walls than possible
    shortcuts = min(shortcuts,walls) 

    for j in range(shortcuts):
        add_shortcut(maze,cols,rows)


    return maze



# choose a random wall to knock out, and see how big of a loop
# it creates...
# repeat 30 times total, and choose one that creates a really big loop
def add_shortcut(maze,cols,rows):
    bestscore = -1
    for i in range(30):

        # the next loop finds a wall (x,y) and
        # points a and b on either sides
        while True:
            if(randint(0,1) == 0):
                x = 2*randint(1,cols-1)
                y = 2*randint(1,rows)-1
                a = (x-1,y)
                b = (x+1,y)
            else:
                x = 2*randint(1,cols)-1
                y = 2*randint(1,rows-1)
                a=(x,y-1)
                b=(x,y+1)
            if not maze[(x,y)]:
                break
        # alright, we found a potential wall
        score = distance(maze,a,b)
        if score > bestscore:
            bestscore = score
            best = (x,y)
    maze[best] = True




# use breadth first search to find the shortest distance
# from start to end
#
# maze[(i,j)] is true iff (i,j) is an open position
#
# returns the distance, or -1 if no path exists
# OR, if path is True
# returns a path from end to start (a list of pairs), or None if none exists
#
# TODO: use A* rather than breadth first search?
#
def distance(maze,start,end,path=False):
    # we'll have two dictionaries
    #    distances and crumbs
    #
    # distances[p] = d means dist(p,start) is *exactly* d (not a bound)
    # crumbs[p] is a neighbor of p on a minimal path back to start
    #
    # distances and crumbs should have the same keys
    #
    # the variable 'd' keeps track of what step we're on
    # 'current' = { p | dist(p,start) = d }
    # 'frontier' \subset { p | dist(p,start) = d+1 }
    # frontier = { p | distances[p] = d+1 }

    # distances = {start:0}
    crumbs = {start:None}
    current = {start}
    frontier = set()
    done = False
    d = 0
    while(not done):
        # at this point, current contains ALL points that are exactly
        # distance d from start
        for c in current:
            if(c == end):
                if not path:
                    return d
                retval = [end]
                while(crumbs[end]):
                    end = crumbs[end]
                    retval.append(end)
                return retval
            # iterate over c's neighbors
            for i in range(4):
                nbhr = plus(c,directions[i])
                if not maze[nbhr] or nbhr in crumbs: # in distances:
                    continue
                # distances[nbhr] = d+1
                crumbs[nbhr] = c
                frontier.add(nbhr)                    

        # now frontier = {p | dist(p,start) = d}

        d += 1
        current = frontier
        frontier = set()
        if(len(current) == 0):
            done = True
    return None




def test():
    settings = {'cols':5, 'rows':5, 'loops':2}
    maz = make_maze(settings)
    for i in range(2*5+1):
        c = ''
        for j in range(2*5+1):
            c += (' ' if maz[(j,i)] else '@')
        print(c)



# build the starting configuration, but attach no observers
# returns a nested box, in the format described in state.txt
# this sets open,fog, player, and monsters, but not
# win, paused, or danger
def starting_configuration(settings):
    rows = settings['rows']
    cols = settings['cols']

    state = box() # <- the box that we'll return

    maze = make_maze(settings)

    # add exit at the northern end of the map
    northgate = (2*randint(1,cols)-1,0)
    maze[northgate] = True
    
    state['open'] = box()
    state['fog'] = box()
    for (i,j) in maze:
        state['open'][(i,j)] = maze[(i,j)]
        state['fog'][(i,j)] = True
    
    state['player'] = (randint(1,cols)*2-1,rows*2-1)

    # where should the monsters go?
    nmon = settings['nmon']
    tmg = [settings[s] for s in ['top','mid','guards']]
    tmg = [int(nmon*percent) for percent in tmg]
    while(sum(tmg) < nmon):
        tmg[randint(0,2)] += 1
    (top,mid,guards) = tmg
    
    monster_coords = []
    for i in range(top):
        monster_coords.append((randint(1,cols)*2-1,1))
    halfway = (rows//2)*2+1
    for i in range(mid):
        monster_coords.append((randint(1,cols)*2-1,halfway))
        # TODO: previous we checked for these guys being too close
        # to the player's initial position

    if(guards > 0):
        path = distance(maze,state['player'],northgate,path=True)
        # now path is a path from the exit to the player


        delta = len(path)//guards//2
        # why the //2? it turns out that
        #     spacing the guards evenly
        #     along the path between the player and the exit
        # yields guards that are too close to the player, and the game's too hard
        # this way, they're spaced closest to the exit, not the player
        if((delta+1)*(guards-1) < len(path)):
            delta += 1
        for i in range(guards):
            monster_coords.append(path[i*delta])
        # TODO: check the math on that, for possible edge cases

    state['monsters'] = box()
    for i in range(len(monster_coords)):
        state['monsters'][i] = monster_coords[i]

    return state


# attach all the observers!
# also set the initial values of win, paused, and danger
def animate(settings, state):


    state['danger'] = False # but this might get updated below
    state['win'] = 0
    state['paused'] = False

    nmon = settings['nmon']
    danger_rad = settings['danger_radius']
    cols = settings['cols']
    rows = settings['rows']

    # danger and losing the game


    # check whether we're in danger, and end the game if we hit a monster
    def danger_check():
        if(nmon == 0):
            state['danger'] = False
        p = state['player']
        dists = [sq_dist(p,state['monsters'][i]) for i in range(nmon)]
        closest = min(dists)
        if(closest == 0):
            state['win'] = -1
        state['danger'] = (closest <= danger_rad**2)

    # we need to run danger_check when the player or monsters move
    state['monsters'].watch(lambda k : danger_check())
    state.watch_key('player',danger_check)
    
    danger_check() # also let's run it at the beginning


    # winning the game
    
    def win_check():
        if(state['player'][1] == 0):
            state['win'] = 1

    state.watch_key('player',win_check)

    win_check()

    # the game should pause when it ends

    def pause_on_end():
        if(state['win'] != 0):
            state['paused'] = True
    state.watch_key('win',pause_on_end)

    pause_on_end()
    
    # fog clears when the maze is escaped

    def revelation():
        if(state['win'] != 1):
            return
        for loc in state['fog']:
            state['fog'][loc] = False
    state.watch_key('win',revelation)
    revelation()
    

    # fog clears as the player explores

    fog_rad = settings['fog_radius']
    def fog_clear():
        p = state['player']
        for i in range(p[0]-fog_rad,p[0]+fog_rad):
            for j in range(p[1]-fog_rad,p[1]+fog_rad):
                if((i,j) not in state['fog']):
                    continue
                state['fog'][(i,j)] = False
                # TODO: clear a circle, not a square

    state.watch_key('player',fog_clear)
    fog_clear() # the game should start with some fog cleared!

    '''
    # random fog removal
    def random_fog():
        if(False):
            return
        i = randint(0,2*cols+1-1)
        j = randint(0,2*rows)
        state['fog'][(i,j)] = False
    state.watch_key('tick',random_fog)
    '''
    # TODO:
    # a lot of places are contingent on the domains of certain dictionaries
    # e.g. we use (i,j) in state['fog'] rather than doing range checks on
    # i and j.  Is this a good idea?


    # when the player tries to pause, the game pauses
    def try_pause():
        if(state['win'] != 0):
            state['paused'] = True # for robustness?
            return # nice try
        # otherwise...
        if(state['paused']):
            state['paused'] = False
        elif(not state['danger']):
            state['paused'] = True

    state.watch_key('tilt', try_pause)

    animate_player(settings,state)
    animate_monsters(settings,state)


def animate_player(settings,state):
    maze = state['open']
    def try_move():
        if(state['win'] != 0 or state['paused']):
            return # nice try
        direction = state['move']
        ploc = state['player']
        newloc = plus(ploc,direction)
        if(newloc in maze and maze[newloc]):
            state['player'] = newloc

        # whoah, that was easy!

    state.watch_key('move',try_move)






def animate_monsters(settings,state):
    nmon = settings['nmon']
    
    # monsters have some internal memory
    #
    # rather than storing this in a struct/class
    # we'll use closures!
    # for fun, and because I got tired of typing "self." everywhere


    # this returns the program to run for the ith monster
    def closure_factory(i):
        prev_loc = state['monsters'][i]
        hunting = False # or d, if we're going in direction d
        destination = state['monsters'][i]
        
        # prev_loc, hunting, and destination
        # function as the fields of a struct

        def look_one_way(d):
            loc = state['monsters'][i]
            player = state['player']
            while(True):
                loc = plus(loc,d)                
                if(loc in state['open'] and state['open'][loc]):
                    if(loc == player):
                        return True
                else:
                    return False
                
        def look_for_player():
            nonlocal hunting, destination
            current_loc = state['monsters'][i]
            for d in directions:
                if(look_one_way(d)):
                    hunting = d
                    destination = state['player']
                    return

        def do_it():
            nonlocal prev_loc, hunting, destination
            loc = state['monsters'][i]
            look_for_player()
            if(hunting):
                next_loc = plus(loc,hunting)
            else:
                exits = [plus(loc,d) for d in directions]
                exits = [x for x in exits
                         if x in state['open'] and state['open'][x]]
                if(prev_loc in exits):
                    exits.remove(prev_loc)
                if(len(exits) == 0):
                    next_loc = prev_loc
                else:
                    next_loc = random.choice(exits)
            if(hunting and next_loc == destination):
                hunting = False
            prev_loc = loc
            state['monsters'][i] = next_loc

        return do_it

    for i in range(nmon):
        state.watch_key('tick',closure_factory(i))


# the following method is the only outward facing method of this
# module
def build_world(settings):
    state = starting_configuration(settings)
    animate(settings,state)
    return state
    



def default_settings():
    return {'cols':7, 'rows':5, 'loops':1,
            'nmon':1, 'top':0.33, 'mid':0.33, 'guards':0.33,
            'danger_radius':2, 'fog_radius':4}


def display(settings,state):
    cols = settings['cols']
    rows = settings['rows']
    nmon = settings['nmon']
    charrep = {}
    for i in range(2*cols+1):
        for j in range(2*rows+1):
            p = (i,j)
            charrep[p] = ' ' if state['open'][p] else '#'
            if(state['fog'][p]):
                charrep[p] = '?'
    for i in range(nmon):
        charrep[state['monsters'][i]] = 'M'
    charrep[state['player']] = '!'
    for j in range(2*rows+1):
        s = ''
        for i in range(2*cols+1):
            s += charrep[(i,j)]
        print(s)


def basic_test():
    s = default_settings()
    state = starting_configuration(s)
    animate(s,state)
    display(s,state)




def fun_test():
    s = default_settings()
    state = starting_configuration(s)
    animate(s,state)
    count = 0
    while(state['win'] == 0):
        display(s,state)
        x = input(">")
        if(x in 'dsaw'):
            state['move'] = directions['dsaw'.index(x)]
            count += 1
            if(count > 1):
                state['tick'] = 1337
                count = 0
        elif(x == ' '):
            state['tilt'] = 1337
    display(s,state)
    if(state['win'] == 1):
        print("you won!")
    else:
        print("you lost!")


