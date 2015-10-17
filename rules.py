#! /usr/bin/python3
'''Governs the non-UI rules.

The one important function here is build_world, which takes settings
and produces a nested dictionary that contains the state of the world,
and has callbacks attached to enforce all the rules of the game'''

from box import *
import random
from random import randint


# utility functions for manipulating vectors
def plus(p1,p2):
    return (p1[0]+p2[0],p1[1]+p2[1])
    
def minus(p1,p2):
    return (p1[0]-p2[0],p1[1]-p2[1])
    
def sq_dist(p1,p2):
    d = minus(p1,p2)
    return d[0]**2+d[1]**2


directions = [(1,0),(0,1),(-1,0),(0,-1)]

             
def make_maze(settings):
    '''Returns a dictionary whose (i,j)th entry specifies whether
    location (i,j) is open.  The dimensions are (2r+1) by (2c+1),
    where r and c are settings['rows'] and settings['cols'].'''
    cols = settings['cols']
    rows = settings['rows']
    bigc = 2*cols+1 # actual number of columns
    bigr = 2*rows+1 # actual number of rows
    maze = {} # eventual return value

    # the maze generation algorithm is the following:
    # do a random walk.  When going from location a to location b
    # add the edge from a to b if this is the first time we've reached b

    # we're thinking of a graph whose vertices are the positions (i,j)
    # with i and j both odd, and whose edges are the positions (i,j)
    # with exactly one of i and j odd.

    # positions with i and j both even will never be hollowed out

    # To start, block off every location
    for i in range(bigc):
        for j in range(bigr):
            maze[(i,j)] = False
    # Find the starting location of the random walk
    loc = (2*randint(1,cols)-1, 2*randint(1,rows)-1)
    # hollow it out
    maze[loc] = True
    found = 1 # counts number of visited vertices
    while(found < cols*rows):
        d = random.choice(directions) # choose random direction to move
        gate = plus(loc,d) # the 'edge' we're moving along
        next_loc = plus(gate,d) # the next 'vertex'
        if(next_loc not in maze):
            continue # off the edge of the map; try a different direction
        if(maze[next_loc] == False): # visiting a new location?
            maze[next_loc] = True
            maze[gate] = True
            found += 1
        loc = next_loc


    # now we have a maze
    #
    # However, we're going to modify it a little, by knocking out
    # a few more walls.  This introduces loops into the maze,
    # and makes the game easier and more interesting
    shortcuts = settings['loops']
    walls = (cols-1)*rows + cols*(rows-1) # how many walls between cells existed
    walls -= (cols*rows - 1) # how many walls were removed to make the maze
    # don't try and remove more walls than possible
    shortcuts = min(shortcuts,walls) 

    for j in range(shortcuts):
        add_shortcut(maze,cols,rows)


    return maze



def add_shortcut(maze,cols,rows):
    '''add a shortcut to the maze, by knocking out a wall,
    preferably one that produces a large-ish loop in the maze'''

    # we don't want to just knock out a random wall,
    # because this has good odds of producing a
    # short and boring loop (like a loop of length 8,
    # not very helpful for the player)
    #
    # So instead, we try 30 random walls, and choose the
    # one which creates the biggest loop
    bestscore = -1
    for i in range(30):

        # the while(True) loop finds a wall (x,y) and
        # points a and b on either sides
        while True:
            # coin toss decides between vertical and horizontal walls
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
            # exit the loop if we found a solid wall
            if not maze[(x,y)]:
                break
        # alright, we found a potential wall
        score = distance(maze,a,b)
        if score > bestscore:
            bestscore = score
            best = (x,y)
    maze[best] = True




def distance(maze,start,end,path=False):
    '''Use breadth first search to find the shortest distance
    in the maze from start to end.
    If path=False, return the distance (or -1 if no path exists)
    If path=True, return a path from end to start, or None if no path exists'''
    # TODO: use A* rather than breadth first search


    
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
    '''Test the make_maze function, and display graphical output'''
    settings = {'cols':5, 'rows':5, 'loops':2}
    maz = make_maze(settings)
    for i in range(2*5+1):
        c = ''
        for j in range(2*5+1):
            c += (' ' if maz[(j,i)] else '@')
        print(c)




def starting_configuration(settings):
    '''Build the starting configuration, but attach no observers.
    Return a nested box, in the format described in state.txt.

    This sets open,fog, player, and monsters, but not
    win, paused, or danger'''
    
    rows = settings['rows']
    cols = settings['cols']

    state = box() # <- the box that we'll return
    # the rest of this function fills in state

    # STEP 1: MAKE THE MAZE AND THE FOG
    
    maze = make_maze(settings)

    # add exit at the northern end of the map
    northgate = (2*randint(1,cols)-1,0)
    maze[northgate] = True
    
    state['open'] = box()
    state['fog'] = box()
    for (i,j) in maze:
        state['open'][(i,j)] = maze[(i,j)]
        state['fog'][(i,j)] = True

    # STEP 2: PLACE THE PLAYER IN THE MAZE
        
    # put the player in a random place along the bottom row
    state['player'] = (randint(1,cols)*2-1,rows*2-1)

    # STEP 3: PLACE THE MONSTERS
    
    # 3a: how many monsters?
    
    nmon = settings['nmon']
    # allocate nmon monsters among three categories
    # roughly following the percentages
    tmg = [settings[s] for s in ['top','mid','guards']]
    tmg = [int(nmon*percent) for percent in tmg]
    while(sum(tmg) < nmon):
        tmg[randint(0,2)] += 1
    (top,mid,guards) = tmg
    
    monster_coords = [] # running list of monster locations

    # top monsters
    for i in range(top):
        monster_coords.append((randint(1,cols)*2-1,1))

    # middle monsters
    halfway = (rows//2)*2+1
    for i in range(mid):
        monster_coords.append((randint(1,cols)*2-1,halfway))
        # TODO: previously, we checked for these guys being too close
        # to the player's initial position

    # guard monsters
    #
    # These stand directly between the player and the exit
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



# also set the initial values of win, paused, and danger
def animate(settings, state):
    '''Bring the world to life

    Attaches observers and sets the initial values of win, paused,
    danger'''

    state['danger'] = False # but this might get updated below
    state['win'] = 0
    state['paused'] = False

    nmon = settings['nmon']
    danger_rad = settings['danger_radius']
    cols = settings['cols']
    rows = settings['rows']

    # The following code enforces the main mechanics of
    # the game.
    #
    # Each mechanic needs to be enforced in response to
    # certain changes in the "state" variable.  So, for
    # each mechanic we write some code in an inline function
    # and attach this function as an observer to the state.
    # Often we also run the inline function right now,
    # to make the state be consistent.



    # "danger" happens if the player's too close to the monsters
    # (this makes the radar circle appear, and prevents pausing)
    #
    # If the player runs into the monster, the game is over
    
    def proximity_check(dummy_var = 0):
        # watch and watch_key require proximity_check
        # to have varying arity, hence "dummy_var"

        if(nmon == 0):
            state['danger'] = False
            return
        p = state['player']
        # make a list of the squared distances to the monsters
        dists = [sq_dist(p,state['monsters'][i]) for i in range(nmon)]
        closest = min(dists)
        if(closest == 0):
            state['win'] = -1 # YOU LOSE
        state['danger'] = (closest <= danger_rad**2)

    # we need to run proximity_check when the player or monsters move
    state['monsters'].watch(proximity_check)
    state.watch_key('player',proximity_check)
    
    proximity_check() # also let's run it at the beginning


    # winning the game
    
    def win_check():
        # check if player reached the northern edge of the map
        if(state['player'][1] == 0):
            state['win'] = 1

    state.watch_key('player',win_check)

    win_check()

    # the game pauses when it ends

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
                # if(sq_dist((i,j),p) > fog_rad**2):
                #     continue
                if(state['fog'][(i,j)]):
                    state['fog'][(i,j)] = False
                # TODO: clear a circle, not a square

    state.watch_key('player',fog_clear)
    fog_clear() # the game should start with some fog cleared!

    
    # # random fog removal
    
    # def random_fog():
    #     for q in range(5):
    #         i = randint(0,2*cols+1-1)
    #         j = randint(0,2*rows)
    #         state['fog'][(i,j)] = False
    # state.watch_key('tick',random_fog)
    
    # TODO:
    # a lot of places are contingent on the domains of certain dictionaries
    # e.g. we use (i,j) in state['fog'] rather than doing range checks on
    # i and j.  Is this a good idea?


    # when the player tries to pause, the game pauses
    
    def try_pause():
        if(state['win'] != 0):
            state['paused'] = True # for robustness?
            return
        if(state['paused']):
            state['paused'] = False
        elif(not state['danger']):
            state['paused'] = True

    state.watch_key('tilt', try_pause)

    animate_player(settings,state)
    animate_monsters(settings,state)



    

def animate_player(settings,state):
    '''Add the rules for player movement'''
    maze = state['open']
    # try_move will be called whenever the player tries to move
    def try_move():
        if(state['win'] != 0 or state['paused']):
            return # don't move if the game is over or the game's paused
        direction = state['move']
        ploc = state['player']
        newloc = plus(ploc,direction)
        # check for legal move
        if(newloc in maze and maze[newloc]):
            state['player'] = newloc

    state.watch_key('move',try_move)






def animate_monsters(settings,state):
    '''Add the rules for monster movement'''
    nmon = settings['nmon']
    
    # monsters have some internal memory: if a monster sees the player,
    # it moves towards the player, and if the player goes out of sight,
    # it continues to move towards the last location it saw the player
    #
    # Also the monster remembers where it last was, to avoid doubling
    # back during random-walk mode.
    #
    # Rather than storing this in a struct/class, we'll use closures!
    # For fun, and because I got tired of typing "self." everywhere


    def closure_factory(i):
        '''Returns the function that moves the ith monster'''
        
        # state variables---these functions as the fields of a struct
        # managing the ith monster's memory
        prev_loc = state['monsters'][i]
        hunting = False # or d, if we're going in direction d
        destination = state['monsters'][i]
        

        def look_one_way(d):
            '''Is the player visible in direction d?'''
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
            '''If player's visible, set hunting and destination'''
            nonlocal hunting, destination
            for d in directions:
                if(look_one_way(d)):
                    hunting = d
                    destination = state['player']
                    return

        def do_it():
            '''Move the ith monster'''
            nonlocal prev_loc, hunting, destination
            loc = state['monsters'][i]
            look_for_player()
            if(hunting):
                next_loc = plus(loc,hunting)
            else:
                # take all immediate neighbors
                exits = [plus(loc,d) for d in directions]
                # only look at ones that are accessible
                exits = [x for x in exits
                         if x in state['open'] and state['open'][x]]
                # don't double back on yourself...
                if(prev_loc in exits):
                    exits.remove(prev_loc)
                # ...unless necessary
                if(len(exits) == 0):
                    next_loc = prev_loc
                else:
                    next_loc = random.choice(exits)
            # check if we reached the last place we saw the player
            if(hunting and next_loc == destination):
                hunting = False
            prev_loc = loc
            state['monsters'][i] = next_loc

        return do_it

    for i in range(nmon):
        state.watch_key('tick',closure_factory(i))


def build_world(settings):
    '''The only outward facing method of this module

    Return a world built using settings, with observers attached to
    enforce the rules
    '''
    state = starting_configuration(settings)
    animate(settings,state)
    return state
    


# testing data.  These are NOT the default settings for the main game!
def default_settings():
    return {'cols':7, 'rows':5, 'loops':1,
            'nmon':1, 'top':0.33, 'mid':0.33, 'guards':0.33,
            'danger_radius':2, 'fog_radius':4}

# testing function: print a text representation to the console
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

# a basic test: see whether the world can be created
def basic_test():
    s = default_settings()
    state = build_world(s)
    display(s,state)



# play a small game using console i/o
def fun_test():
    s = default_settings()
    state = build_world(s)
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


