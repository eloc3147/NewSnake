require 'sinatra'
require 'json'
require 'pathing'
require 'ruby-prof'

debug_grid = false

START_SETTINGS = {
    "name": "Pankek_the_Snek",
    "color": "gold",
    "head_type": "tongue",
    "tail_type": "curled"
}

class Interface
    # gets an array of neighbors for the given node key
    # for this example, the node key is passed in as an array like so: [x, y]
    def neighbors_for(node_key)
        x, y = *node_key
        neighbors = []
        
        neighbors << [x-1, y] if coords_safe([x-1, y])
        neighbors << [x, y-1] if coords_safe([x, y-1])
        neighbors << [x+1, y] if coords_safe([x+1, y])
        neighbors << [x, y+1] if coords_safe([x, y+1])
        
        neighbors
    end

    # gets the cost for moving from node1 to node2
    def edge_cost_between(node1_key, node2_key)
        1
    end
end

get '/' do
    return START_SETTINGS.to_json
end

post '/start' do
    #requestBody = request.body.read
    #requestJson = requestBody ? JSON.parse(requestBody) : {}

    return START_SETTINGS.to_json
end

post '/move' do
    RubyProf.start
    requestBody = request.body.read
    requestJson = requestBody ? JSON.parse(requestBody) : {}
    puts requestBody

    $width = requestJson['width']
    $height = requestJson['height']
    $grid = Hash.new 0 # Creates a hash with a default value of 0, that we are going to pretend is a mutidimentional array
    snakes = requestJson['snakes']
    food = requestJson['food']
    snake = {}

    ### $grid values
    # 0: empty
    # 2: food
    # 10: this snake body
    # 11: this snake head
    # 20: enemy snake body
    # 21: enemy snake head
    
    # Propegate the $grid
    snakes.each do |s|
        you = false
        if s['id'] == requestJson['you']
            snake = s
            you = true
        end
        s['coords'].each_index do |i|
            coords = s['coords'][i]
            next unless $grid[coords] == 0 # Stops snake bodies from overwriting heads at the beginning
            # If this is the forst coordinate, it's the head
            if i == 0
                $grid[coords] = you ? 11 : 21
            else
                $grid[coords] = you ? 10 : 20
            end
        end
    end
    food.each do |coords|
        $grid[coords] = 2
    end
    
    head = snake['coords'][0]
    
    #Check if a given coordiante is safe
    def coords_safe(coords)
        return false unless $grid[coords] == 0 or $grid[coords] == 2 # Check if coordinate matches a snake body
        return false if coords[0] < 1 or coords[0] > $width # Check if coordinate is inside horizontal bounds
        return false if coords[1] < 1 or coords[1] > $height # Check if coordinate is inside vertical bounds
        return true
    end
    
    g = Pathing::Graph.new(Interface.new)
    path = g.path(head, food[0])
    puts path.to_json
    next_coord = path[0]
    
    if next_coord[1] < head[1]
        direction = "up"
    elsif next_coord[1] > head[1]
        direction = "down"
    elsif next_coord[0] > head[0]
        direction = "right"
    else
        direction = "left"
    end
    
    if debug_grid
        #print the $grid
        $height.times do |y|
            $width.times do |x|
                value = $grid[[x,y]]
                case value
                when 0
                    print "\u25FB"
                when 2
                    print "\u25C9"
                when 10
                    print "\u25C7"
                when 11
                    print "\u25B3"
                when 20
                    print "\u25C6"
                when 21
                    print "\u25B2"
                else
                    print value
                end
            end
            print "\n"
        end
        print "\n"
    end

    # Dummy response
    responseObject = {
        "move" => direction,
        "taunt" => "going north!",
    }
    
    result = RubyProf.stop
    printer = RubyProf::CallStackPrinter.new(result)
    File.open("profile_data.html", 'w') { |file| printer.print(file) }

    return responseObject.to_json
end

post '/end' do
    #requestBody = request.body.read
    #requestJson = requestBody ? JSON.parse(requestBody) : {}

    # No response required
    responseObject = {}

    return responseObject.to_json
end
