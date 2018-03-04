import bottle
import os
import random
from collections import defaultdict
from pypaths import astar
import json

FOOD = 2
YOU_HEAD = 21
YOU_BODY = 20
SNAKE_HEAD = 11
SNAKE_BODY = 10
HEALTH_CUTOFF = 50

TAUNTS = [
    "Bing is better with Microsoft Edge",
    "Microsoft Edge is the faster, safer browser on Windows 10 and it is already installed on your PC",
    "20.9%!",
    "Bing it on!",
    "I know Bing is great! I googled it! ",
    "You’re missing Silverlight. Install it to run this content.",
    "These updates help protect you in an online world",
    "Formerly called Live Search!",
    "STEVE BALLMER IS A GOD IN OUR MODERN SOCIETY",
    "Try our little brother, Yahoo!"

]


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = dict(bottle.request.json)

    return {
        "color": "#008272",
        "secondary_color": "#ffb900",
        "head_type": "sand-worm",
        "head_url": "https://i.imgur.com/ksMI3rJ.gif",
        "tail_type": "freckled"
    }


@bottle.post('/move')
def move():
    data = dict(bottle.request.json)
    width = data['width']
    height = data['height']
    grid = [[0 for x in range(width)] for y in range(height)]
    snakes = data['snakes']['data']
    food = [ptoc(x) for x in data['food']['data']]
    snake = data['you']

    # Add this snake to grid
    for idx, point in enumerate(snake['body']['data']):
        x = point['x']
        y = point['y']
        if grid[x][y] != 0:
            # Stops snake bodies from overwriting heads at the beginning
            continue
        # If this is the forst coordinate, it's the head
        if idx == 0:
            grid[x][y] = YOU_HEAD
        else:
            grid[x][y] = YOU_BODY
    # Add other snakes to grid
    for s in snakes:
        # Skip snake if dead
        if(s['health'] < 1):
            continue
        for idx, point in enumerate(s['body']['data']):
            x = point['x']
            y = point['y']
            if grid[x][y] != 0:
                # Stops snake bodies from overwriting heads at the beginning
                continue
            # If this is the forst coordinate, it's the head
            if idx == 0:
                grid[x][y] = SNAKE_HEAD
            else:
                grid[x][y] = SNAKE_BODY
    for c in food:
        x, y = c
        grid[x][y] = FOOD

    head = ptoc(snake['body']['data'][0])

    # Simple macros for each direction
    c_north = [head[0], head[1] - 1]
    c_south = [head[0], head[1] + 1]
    c_east = [head[0] + 1, head[1]]
    c_west = [head[0] - 1, head[1]]

    def find_neighbours(coord):
        x, y = coord
        neighbors = []

        if coords_safe([x-1, y], width, height, grid):
            neighbors.append((x-1, y))
        if coords_safe([x, y-1], width, height, grid):
            neighbors.append((x, y-1))
        if coords_safe([x+1, y], width, height, grid):
            neighbors.append((x+1, y))
        if coords_safe([x, y+1], width, height, grid):
            neighbors.append((x, y+1))

        return neighbors

    finder = astar.pathfinder(neighbors=find_neighbours)

    # Find nearest food
    closest_food = None
    for f in food:
        # Skip food if it's too close to the wall, unless we're desperate
        if(snake['health'] >= HEALTH_CUTOFF and (
           f[0] == 0 or
           f[0] == width - 1 or
           f[1] == 0 or
           f[1] == height - 1)):
            continue
        p = finder((head[0], head[1]), (f[0], f[1]))
        # Skip if no path to food
        if(p[0] is None):
            continue
        # Update best path if this path is better
        if(p and (closest_food is None or p[0] < len(closest_food))):
            closest_food = p[1]

    path = closest_food

    direction = ""

    if(path is not None and len(path) > 1):
        next_coord = path[1]
        if next_coord[1] < head[1]:
            direction = "up"
        elif next_coord[1] > head[1]:
            direction = "down"
        elif next_coord[0] > head[0]:
            direction = "right"
        else:
            direction = "left"

    # Fallback to safe execution
    if(not direction):
        if coords_safe(c_north, width, height, grid):
            direction = "up"
        elif coords_safe(c_south, width, height, grid):
            direction = "down"
        elif coords_safe(c_east, width, height, grid):
            direction = "right"
        else:
            direction = "left"

    result = {
        'move': direction,
        'taunt': random.choice(TAUNTS)
    }
    return result


# Check if a given coordiante is safe
def coords_safe(coords, width, height, grid):
    x, y = coords
    # Check if coordinate is inside horizontal bounds
    if(x < 0 or x > width-1):
        return False
    # Check if coordinate is inside vertical bounds
    if(y < 0 or y > height-1):
        return False
    # Check if coordinate matches a snake body
    if(grid[x][y] not in [0, 2]):
        return False
    return True


def ptoc(point):
    return [point['x'], point['y']]

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'),
               port=os.getenv('PORT', '8080'))
