import sys

    # "all_wheels_on_track": Boolean,        # flag to indicate if the agent is on the track
    # "x": float,                            # agent's x-coordinate in meters
    # "y": float,                            # agent's y-coordinate in meters
    # "closest_objects": [int, int],         # zero-based indices of the two closest objects to the agent's current position of (x, y).
    # "closest_waypoints": [int, int],       # indices of the two nearest waypoints.
    # "distance_from_center": float,         # distance in meters from the track center 
    # "is_crashed": Boolean,                 # Boolean flag to indicate whether the agent has crashed.
    # "is_left_of_center": Boolean,          # Flag to indicate if the agent is on the left side to the track center or not. 
    # "is_offtrack": Boolean,                # Boolean flag to indicate whether the agent has gone off track.
    # "is_reversed": Boolean,                # flag to indicate if the agent is driving clockwise (True) or counter clockwise (False).
    # "heading": float,                      # agent's yaw in degrees
    # "objects_distance": [float, ],         # list of the objects' distances in meters between 0 and track_length in relation to the starting line.
    # "objects_heading": [float, ],          # list of the objects' headings in degrees between -180 and 180.
    # "objects_left_of_center": [Boolean, ], # list of Boolean flags indicating whether elements' objects are left of the center (True) or not (False).
    # "objects_location": [(float, float),], # list of object locations [(x,y), ...].
    # "objects_speed": [float, ],            # list of the objects' speeds in meters per second.
    # "progress": float,                     # percentage of track completed
    # "speed": float,                        # agent's speed in meters per second (m/s)
    # "steering_angle": float,               # agent's steering angle in degrees
    # "steps": int,                          # number steps completed
    # "track_length": float,                 # track length in meters.
    # "track_width": float,                  # width of the track
    # "waypoints": [(float, float), ]        # list of (x,y) as milestones along the track center


MAX_SPEED = 4.0

def reward_function(params):
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = params['steering_angle']
    speed = params['speed']
    is_offtrack = params['is_offtrack']
    
    weighted_sub_rewards = []
    
    
    half_track_width = track_width / 2.0


    within_percentage_of_center_weight = 1.0
    steering_angle_weight = 1.0
    speed_weight = 0.5
    steering_angle_and_speed_weight = 1.0


    add_weighted_sub_reward(weighted_sub_rewards, "within_percentage_of_center_weight", within_percentage_of_center_weight, get_sub_reward_within_percentage_of_center(distance_from_center, track_width))
    add_weighted_sub_reward(weighted_sub_rewards, "steering_angle_weight", steering_angle_weight, get_sub_reward_steering_angle(steering_angle))
    add_weighted_sub_reward(weighted_sub_rewards, "speed_weight", speed_weight, get_sub_reward_speed(speed))
    add_weighted_sub_reward(weighted_sub_rewards, "steering_angle_and_speed_weight", steering_angle_and_speed_weight, get_sub_reward_steering_angle_and_speed(steering_angle, speed))
    
    if is_offtrack:      
        add_weighted_sub_reward(weighted_sub_rewards, "is_offtrack_weight", 80.0, 1e-3)
    else:
        add_weighted_sub_reward(weighted_sub_rewards, "is_offtrack_weight", 1.0, 1.0)
    
    print(weighted_sub_rewards)

    weight_total = 0.0
    numerator = 0.0

    for weighted_sub_reward in weighted_sub_rewards:
        sub_reward = weighted_sub_reward["sub_reward"]
        weight = weighted_sub_reward["weight"]

        weight_total += weight
        numerator += sub_reward * weight

        print("sub numerator", weighted_sub_reward["sub_reward_name"], sub_reward, weight, (sub_reward * weight))
    
    print(numerator)
    print(weight_total)
    print(numerator / weight_total)
    
    return numerator / weight_total



def add_weighted_sub_reward(weighted_sub_rewards, sub_reward_name, weight, sub_reward):
    weighted_sub_rewards.append({"sub_reward_name": sub_reward_name, "sub_reward": sub_reward, "weight": weight})

def get_sub_reward_within_percentage_of_center(distance_from_center, track_width):
    half_track_width = track_width / 2.0
    percentage_from_center = (distance_from_center / half_track_width * 100.0)

    if percentage_from_center <= 10.0:
        return 1.0
    elif percentage_from_center <= 20.0:
        return 0.8
    elif percentage_from_center <= 40.0:
        return 0.5
    elif percentage_from_center <= 50.0:
        return 0.4
    elif percentage_from_center <= 70.0:
        return 0.15
    else:
       return 1e-3

# The reward is better if going straight
# steering_angle of -30.0 is max right
def get_sub_reward_steering_angle(steering_angle):
    is_left_turn = True if steering_angle > 0.0 else False
    abs_steering_angle = abs(steering_angle)

    print("abs_steering_angle", abs_steering_angle)

    if abs_steering_angle <= 3.0:
        return 1.0
    elif abs_steering_angle <= 5.0:
        return 0.9
    elif abs_steering_angle <= 8.0:
        return 0.75
    elif abs_steering_angle <= 10.0:
        return 0.7
    elif abs_steering_angle <= 15.0:
        return 0.5
    elif abs_steering_angle <= 23.0:
        return 0.35
    elif abs_steering_angle <= 27.0:
        return 0.2
    else:
       return 1e-3


def get_sub_reward_speed(speed):
    percentage_of_max_speed = speed / MAX_SPEED * 100.0

    print("percentage_of_max_speed", percentage_of_max_speed)

    if percentage_of_max_speed >= 90.0:
        return 0.7
    elif percentage_of_max_speed >= 65.0:
        return 0.8
    elif percentage_of_max_speed >= 50.0:
        return 0.9
    else:
       return 1.0


def get_sub_reward_steering_angle_and_speed(steering_angle, speed):
    abs_steering_angle = abs(steering_angle)
    percentage_of_max_speed = speed / MAX_SPEED * 100.0

    steering_angle_weight = 1.0
    speed_weight = 1.0

    steering_angle_reward = get_sub_reward_steering_angle(steering_angle)
    speed_reward = get_sub_reward_speed(speed)

    return (((steering_angle_reward * steering_angle_weight) + (speed_reward * speed_weight)) / (steering_angle_weight + speed_weight))





def test1():
    reward_function({'track_width': 10.0, 
                        'distance_from_center': 2.5, 
                        "steering_angle": -23.0, 
                        "speed": 3.0,
                        "is_offtrack": True})


if __name__ == '__main__':
    globals()[sys.argv[1]]()