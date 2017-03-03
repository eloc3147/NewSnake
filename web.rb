require 'sinatra'
require 'json'

START_SETTINGS = {
        "name": "leo isn't allowed to name things anymore",
        "color": "gold",
        "head_type": "tongue",
        "tail_type": "curled"
    }

get '/' do
    return START_SETTINGS.to_json
end

post '/start' do
    #requestBody = request.body.read
    #requestJson = requestBody ? JSON.parse(requestBody) : {}

    return START_SETTINGS.to_json
end

post '/move' do
    requestBody = request.body.read
    requestJson = requestBody ? JSON.parse(requestBody) : {}

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
    
    # Simple macros for each direction
    c_north = [snake['coords'][0][0], snake['coords'][0][1] - 1]
    c_south = [snake['coords'][0][0], snake['coords'][0][1] + 1]
    c_east = [snake['coords'][0][0] + 1, snake['coords'][0][1]]
    c_west = [snake['coords'][0][0] - 1, snake['coords'][0][1]]
    
    #Check if a given coordiante is safe
    def coords_safe(coords)
        puts coords.to_json
        return false unless $grid[coords] == 0 or $grid[coords] == 2 # Check if coordinate matches a snake body
        return false if coords[0] < 1 or coords[0] > $width # Check if coordinate is inside horizontal bounds
        return false if coords[1] < 1 or coords[1] > $height # Check if coordinate is inside vertical bounds
        return true
    end
    
    if coords_safe(c_north)
        direction = "up"
    elsif coords_safe(c_south)
        direction = "down"
    elsif coords_safe(c_east)
        direction = "right"
    else
        direction = "left"
    end
    
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
    
    puts "North: #{coords_safe(c_north)}, South: #{coords_safe(c_south)}, East: #{coords_safe(c_east)}, West: #{coords_safe(c_west)}"
    

    # Dummy response
    responseObject = {
        "move" => direction,
        "taunt" => "going north!",
    }

    return responseObject.to_json
end

post '/end' do
    #requestBody = request.body.read
    #requestJson = requestBody ? JSON.parse(requestBody) : {}

    # No response required
    responseObject = {}

    return responseObject.to_json
end
