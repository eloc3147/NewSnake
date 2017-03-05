import bottle
import os
import random
from collections import defaultdict
from pypaths import astar
import json

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data
    
    start_settings = {
        "name": "Leo isn't allowed to name things anymore",
        "color": "#807d8b",
        "secondary_color": "#d1ff02",
        "head_type": "shades",
        "taunt": "SEE YOU IN COURT!",
        "head_url": "http://i.imgur.com/peDooSu.gif",
        "tail_type": "regular"
    }

    return start_settings


@bottle.post('/move')
def move():
    data = bottle.request.json
    width = data['width']
    height = data['height']
    grid = [[0 for x in range(width)] for y in range(height)] 
    snakes = data['snakes']
    food = data['food']
    snake = {}
    
    for s in snakes:
        you = False
        if s['id'] == data['you']:
            snake = s
            you = True
        for idx, val in enumerate(s['coords']):
            x, y = val
            if grid[x][y] != 0:
                continue # Stops snake bodies from overwriting heads at the beginning
            # If this is the forst coordinate, it's the head
            if idx == 0:
                grid[x][y] = 11 if you else 21
            else:
                grid[x][y] = 10 if you else 20
    for coords in food:
        x, y = coords
        grid[x][y] = 2
        
    head = snake['coords'][0]
        
    # Simple macros for each direction
    c_north = [snake['coords'][0][0], snake['coords'][0][1] - 1]
    c_south = [snake['coords'][0][0], snake['coords'][0][1] + 1]
    c_east = [snake['coords'][0][0] + 1, snake['coords'][0][1]]
    c_west = [snake['coords'][0][0] - 1, snake['coords'][0][1]]
    
    #Check if a given coordiante is safe
    def coords_safe(coords):
        x, y = coords
        if x < 0 or x > width-1: return False # Check if coordinate is inside horizontal bounds
        if y < 0 or y > height-1: return False # Check if coordinate is inside vertical bounds
        if grid[x][y] not in [0,2]: return False # Check if coordinate matches a snake body
        return True
    
    def find_neighbours(coord):
        x, y = coord
        neighbors = []
        
        if coords_safe([x-1, y]): neighbors.append((x-1, y))
        if coords_safe([x, y-1]): neighbors.append((x, y-1))
        if coords_safe([x+1, y]): neighbors.append((x+1, y))
        if coords_safe([x, y+1]): neighbors.append((x, y+1))
        
        return neighbors
    
    finder = astar.pathfinder(neighbors=find_neighbours)
    path = finder( (head[0], head[1]), (food[0][0], food[0][1]) )[1]
    
    if len(path) < 2:
        if coords_safe(c_north):
            direction = "up"
        elif coords_safe(c_south):
            direction = "down"
        elif coords_safe(c_east):
            direction = "right"
        else:
            direction = "left"
    else:
        next_coord = path[1]
        if next_coord[1] < head[1]:
            direction = "up"
        elif next_coord[1] > head[1]:
            direction = "down"
        elif next_coord[0] > head[0]:
            direction = "right"
        else:
            direction = "left"

    return {
        'move': direction,
        'taunt': 'SEE YOU IN COURT!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
