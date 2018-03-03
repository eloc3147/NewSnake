# Memsnek AI for Battlesnake 2018
Bingsnek is a snake AI built for Battlesnake 2018

How Bingsnek works:
Bingsnek uses a pathfinding algorithm called astar. At the start of the game Bingsnek uses astar to pathfind to the nearest food
When the closest food is completley obstructed Bingsnek will go to the second closest food.
When all food is obstructed Bingsnek will default to the spot on the map that is farthest away from all obstacles.
When the selected piece of food is 1 block away from a wall Bingsnek will not pathfind to it unless Bingsnek is under 50% health.
Bingsnek will not pathfind within 1 block of all snake heads.
