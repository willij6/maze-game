# maze-game
This is a simple game written in Python using Tkinter.  The player
explores and escapes from a randomly-generated maze inhabited by
monsters.

The player starts at the bottom of the map.  There is one exit,
somewhere along the top edge.  The map is almost a tree, except that
one or two shortcuts have been added in (so it is not quite acyclic).

Once the player has come within a certain distance of a location, she
gains visibility of it for the rest of the game.  The monsters, on the
other hand, only see along direct unbroken lines of sight.  They are
also fairly stupid.

## Controls
Arrow keys move the player.  `ESC` restarts the game (creating a new
map).  `Space` pauses the game.