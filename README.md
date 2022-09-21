# Introduction
This blog is to detail my first experiences with AWS DeepRacer as somebody who knows very little about how AI works under the hood, and at first didn't fully understand the difference between Supervised Learning vs Unsupervised Learning vs Reinforcement Learning when I was writing my first Python code for the "reward_function".

![AWS DeepRacer Training](https://raw.githubusercontent.com/chiwaichan/blog-assets/main/images/aws-deepracer-pre-machine-learning-cert/aws-deepracer-training.jpg)

DeepRacer is a Reinforcement Learning based AWS Machine Learning Service that provides a quick and fun way to get into ML by letting you build and train an ML model that can be used to drive around on a virtual, as well as a physical race track.

I'm a racing fan in many ways whether it is watching Formula 1, racing my mates in go karting or having a hoon on the scooter, so once I found out about AWS DeepRacer service I've always wanted to dip my toes in it. More than 2 years later I found an excuse to play with it during my preparations for the AWS Certified Machine Learning Specialty exam, I am expecting a question or two on DeepRacer in the exam so what better way to learn about DeepRacer than to try it out by cutting some Python code. 

# Goal
Have a realistic one this time and keep it simple: produce an ML model that can drive a car around a few diferent virtual tracks for a few laps without going off the track.

# My Machine Learning background and relevant experience
 - Statistics, Calculus and Physics: was pretty good at these during high school and did ok in Statistics and Calculas during uni.
 - Python: have been writing some Python code in the past couple of years on and off, mainly in AWS Lambda functions.
 - Machine Learning: none
 - Writing code for mathematic: had a job that involved writing complex mathmatic equations and tree based algorithms in Ruby and Java for about 7 years


# Approach

Code a Python Reward Function to return a Reinforcement Reward value based on the state of the DeepRacer vehicle - the reward can be positive for good behaviour and also be negative to discourage the agent (vehicle) for a state that is not going to give us a good race pace. The state of the vehicle is a set of key/values shown below and is available to the Python Reward Function during runtime for us to use to calculate a reward value.


```
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
```

Based on this set of key/values we can get a pretty good idea of the state of the vehicle/agent and what it was getting up to on the track.

So using these key/values we calculate and return a value for the Reward Function in Python. For example, if the value for "is_offtrack" is "true" then this indicates the vehicle has come off the track so we can return a negative value for the Reward Function; also, we might want to amplify the negative reward if the vehicle was doing something else it should not be doing - like steering right into a left turn (steering_angle).

Conversely, we return a positive reward value for good behaviour such as steering straight on a long stretch of the track going as fast as possible within the center of the track.

My approach to coding the Reward Functions was pretty simple: calculate the reward value based on how I myself would physically drive on a go kart track; factor as much into the calculations as possible such as how the vehicle is hitting the apex, and is it hitting it from the outside of the track or the inside; is the vehicle in a good position to take the next turn or two. For each iteration of the code, I train a new model in AWS DeepRacer with it; I normally watch the video of the simulation to pay attention to what could be improved in the next iteration; then we do the whole process all over again.

Within the Reward Function I work out a bunch of sub-rewards such as:
- steering straight on a long stretch of the track as fast as possible within the center of the track
- is the vehicle in a good position to take the next turn or two
- is the vehicle was doing something else it should not be doing like steering right into a left turn

These are just some examples of sub-rewards I work out - and the list grows as I iterate and improve (or make it worse) with each version of the reward function, at the end of each function I calculate the net reward value based on the sum up of the weighted sub-rewards; each sub-reward could have a higher importance than another so I've taken a weighted approach to the calculation to allow a sub-reward to amplify the effect it has on the net reward value.


# Code

Here is the very first version of the Reward Function I coded:

```
MAX_SPEED = 4.0

def reward_function(params):
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = params['steering_angle']
    speed = params['speed']
    
    weighted_sub_rewards = []
    
    
    half_track_width = track_width / 2.0


    within_percentage_of_center_weight = 1.0
    steering_angle_weight = 1.0
    speed_weight = 0.5
    steering_angle_and_speed_weight = 1.0


    add_weighted_sub_reward(weighted_sub_rewards, "within_percentage_of_center_weight", within_percentage_of_center_weight, get_sub_reward_within_percentage_of_center(distance_from_center, track_width))
    add_weighted_sub_reward(weighted_sub_rewards, "steering_angle_weight", steering_angle_weight, get_sub_reward_steering_angle(steering_angle))
    add_weighted_sub_reward(weighted_sub_rewards, "speed_weight", speed_weight, get_sub_reward_speed(speed))
    add_weighted_sub_reward(weighted_sub_rewards, "steering_angle_and_speed_weight", steering_angle_and_speed_weight, get_sub_reward_steering_angle_and_speed_weight(steering_angle, speed))
    
    print(weighted_sub_rewards)

    weight_total = 0.0
    numerator = 0.0

    for weighted_sub_reward in weighted_sub_rewards:
        sub_reward = weighted_sub_reward["sub_reward"]
        weight = weighted_sub_reward["weight"]

        weight_total += weight
        numerator += sub_reward * weight

        print("sub numerator", weighted_sub_reward["sub_reward_name"], (sub_reward * weight))
    
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


def get_sub_reward_steering_angle_and_speed_weight(steering_angle, speed):
    abs_steering_angle = abs(steering_angle)
    percentage_of_max_speed = speed / MAX_SPEED * 100.0

    steering_angle_weight = 1.0
    speed_weight = 1.0

    steering_angle_reward = get_sub_reward_steering_angle(steering_angle)
    speed_reward = get_sub_reward_speed(speed)

    return (((steering_angle_reward * steering_angle_weight) + (speed_reward * speed_weight)) / (steering_angle_weight + speed_weight))
```

Here is a video of one of the simulation runs:

<iframe width="560" height="315" src="https://www.youtube.com/embed/-PeGCyBTzVc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


Here is a link to my Github repository where I have all of versions of reward functions I created: [https://github.com/chiwaichan/aws-deepracer/tree/main/models](https://github.com/chiwaichan/aws-deepracer/tree/main/models)

# Conclusion
After a few weeks of training and doing about 20 runs with each run using a different reward function, I did not meet the goal I set out to do - get the agent/vehicle to do 3 laps without coming off the track on a few different tracks. On average each model was only able to race the virtual car around each track for a little over a lap without crashing. It felt like at times I hit a bit of a wall and could not improve the results and in some instances the model got worse.
I need to take a break from this to think of a better approach, the way I am doing it is by improving areas without measuring the progress in each area and the amount of improvement made in each. 

# Next steps
 - Learn how to train a DeepRacer model in SageMaker Studio (outside of the DeepRacer Service) using a Jupyter notebook so I can have more control over how models are trained
 - Learn and perform HyperParameter Optimizations using some of the SageMaker features and services
 - Take a Data and Visualisation driven approach to derive insights into where improvements can be made to the next model iteration
 - Learn to optimise the training, e.g. stop the training early when the model is not performing well 
 - Sit the AWS Certified Machine Learning Specialty exam
