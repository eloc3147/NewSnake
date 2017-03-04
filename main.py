import bottle
import os
import random
from collections import defaultdict

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )
    
    start_settings = {
        "name": "leo isn't allowed to name things anymore",
        "color": "gold",
        "head_type": "tongue",
        "head_url": head_url,
        "tail_type": "curled"
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
        
    # Simple macros for each direction
    c_north = [snake['coords'][0][0], snake['coords'][0][1] - 1]
    c_south = [snake['coords'][0][0], snake['coords'][0][1] + 1]
    c_east = [snake['coords'][0][0] + 1, snake['coords'][0][1]]
    c_west = [snake['coords'][0][0] - 1, snake['coords'][0][1]]
    
    #Check if a given coordiante is safe
    def coords_safe(coords):
        x, y = coords
        if grid[x][y] not in [0,2]: return False # Check if coordinate matches a snake body
        if x < 0 or x > width-2: return False # Check if coordinate is inside horizontal bounds
        if y < 0 or y > height-2: return False # Check if coordinate is inside vertical bounds
        return True
        
    if coords_safe(c_north):
        direction = "up"
    elif coords_safe(c_south):
        direction = "down"
    elif coords_safe(c_east):
        direction = "right"
    else:
        direction = "left"

    return {
        'move': direction,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
