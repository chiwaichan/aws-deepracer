import sys
# what are priorities
# steering direction
# track position
# speed







import math

MAX_SPEED = 1.0
DIRECTION_DIFF_WEIGHT = 5
LONG_DISTANCE_AHEAD_HEADING_WEIGHT = 10
IS_OFFTRACK_WEIGHT = 10
ALL_WHEELS_ON_TRACK_WEIGHT = 10
IS_REVERSED_WEIGHT = 10
SHORT_DISTANCE_AHEAD_STEERING_ANGLE_WEIGHT = 20
SHORT_DISTANCE_AHEAD_CENTER_WEIGHT = 20
MEDIUM_DISTANCE_AHEAD_STEERING_ANGLE_WEIGHT = 15
MEDIUM_DISTANCE_AHEAD_CENTER_WEIGHT = 15
LONG_DISTANCE_AHEAD_STEERING_ANGLE_WEIGHT = 10
LONG_DISTANCE_AHEAD_CENTER_WEIGHT = 10

def reward_function(params):
    # print(params)

    is_offtrack = params['is_offtrack']
    all_wheels_on_track = params['all_wheels_on_track']
    is_reversed = params['is_reversed']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = params['steering_angle']
    steering_angle_abs = abs(steering_angle)
    speed = params['speed']
    closest_waypoints = params['closest_waypoints'] 
    waypoints = params['waypoints'] 
    heading = params['heading']
    
    max_speed_percentage = get_max_speed_precentage(speed)

    if is_offtrack:      
        sub_reward_is_offtrack = -0.15

        if max_speed_percentage > 75.0:
            sub_reward_is_offtrack = -1.0
        elif max_speed_percentage > 50.0:
            sub_reward_is_offtrack = -0.4
        elif max_speed_percentage > 30.0:
            sub_reward_is_offtrack = -0.2

        return sub_reward_is_offtrack * IS_OFFTRACK_WEIGHT
    elif not all_wheels_on_track:
        sub_reward_all_wheels_on_track = -0.1

        if max_speed_percentage > 75.0:
            sub_reward_all_wheels_on_track = -0.8
        elif max_speed_percentage > 50.0:
            sub_reward_all_wheels_on_track = -0.3
        elif max_speed_percentage > 30.0:
            sub_reward_all_wheels_on_track = -0.15
        
        return sub_reward_all_wheels_on_track * ALL_WHEELS_ON_TRACK_WEIGHT
    elif is_reversed:
        sub_reward_is_reversed = -0.1

        if max_speed_percentage > 75.0:
            sub_reward_is_reversed = -0.70
        elif max_speed_percentage > 50.0:
            sub_reward_is_reversed = -0.25
        elif max_speed_percentage > 30.0:
            sub_reward_is_reversed = -0.15

        return sub_reward_is_reversed * IS_REVERSED_WEIGHT




    sub_rewards = []
    
    prev_point = closest_waypoints[0]
    next_point = closest_waypoints[1]

    half_track_width = track_width / 2.0

    waypoints_len = len(waypoints)

    # for heading in range(-180, 181):
    #     for prev_point in range(waypoints_len):
    

    
    track_direction = get_track_direction(waypoints, waypoints_len, prev_point)

    track_direction_ahead_1 = get_track_direction(waypoints, waypoints_len, next_point, 1)
    track_direction_ahead_2 = get_track_direction(waypoints, waypoints_len, next_point, 2)
    track_direction_ahead_3 = get_track_direction(waypoints, waypoints_len, next_point, 3)


    # diff cur current waypoints
    direction_heading_diff = track_direction - heading
    direction_heading_diff = get_normalised_angle(direction_heading_diff)

    heading_on_left_of_track_direction = direction_heading_diff < 0.0

    direction_heading_diff_abs = abs(direction_heading_diff)

    
    if direction_heading_diff_abs <= 1.0:
        sub_reward_direction_diff = 1.0
    elif direction_heading_diff_abs <= 3.0:
        sub_reward_direction_diff = 0.9
    elif direction_heading_diff_abs <= 5.0:
        sub_reward_direction_diff = 0.8
    elif direction_heading_diff_abs <= 15.0:
        sub_reward_direction_diff = 0.5
    elif direction_heading_diff_abs <= 25.0:
        sub_reward_direction_diff = 0.2
    elif direction_heading_diff_abs <= 35.0:
        sub_reward_direction_diff = 0.05
    else:
        sub_reward_direction_diff = 0.001

    sub_rewards.append(sub_reward_direction_diff * DIRECTION_DIFF_WEIGHT)




    # diff for 2 waypoints ahead
    direction_heading_diff_ahead_1 = track_direction_ahead_1 - heading
    direction_heading_diff_ahead_1 = get_normalised_angle(direction_heading_diff_ahead_1)
    direction_heading_diff_ahead_2 = track_direction_ahead_2 - heading
    direction_heading_diff_ahead_2 = get_normalised_angle(direction_heading_diff_ahead_2)
    direction_heading_diff_ahead_3 = track_direction_ahead_3 - heading
    direction_heading_diff_ahead_3 = get_normalised_angle(direction_heading_diff_ahead_3)

    direction_heading_diff_ahead_1_abs = abs(direction_heading_diff_ahead_1)
    direction_heading_diff_ahead_2_abs = abs(direction_heading_diff_ahead_2)
    direction_heading_diff_ahead_3_abs = abs(direction_heading_diff_ahead_3)

    # # is the track straight relative to the current waypoints
    # track_direction_variation_ahead_1 = track_direction_ahead_1 - track_direction
    # track_direction_variation_ahead_2 = track_direction_ahead_2 - track_direction
    # track_direction_variation_ahead_3 = track_direction_ahead_3 - track_direction

    sub_reward_long_distance_ahead_heading = 0.0

    # Is the long distance ahead straight
    if direction_heading_diff_ahead_3_abs < 6.0:
        if max_speed_percentage > 90.0:
            sub_reward_long_distance_ahead_heading = 1.0
        elif max_speed_percentage > 70.0:
            sub_reward_long_distance_ahead_heading = 0.8
        elif max_speed_percentage > 50.0:
            sub_reward_long_distance_ahead_heading = 0.5
        else:
            sub_reward_long_distance_ahead_heading = 0.1
    elif direction_heading_diff_ahead_3_abs < 10.0:
        if max_speed_percentage > 90.0:
            sub_reward_long_distance_ahead_heading = 0.6
        elif max_speed_percentage > 70.0:
            sub_reward_long_distance_ahead_heading = 0.3
        elif max_speed_percentage > 50.0:
            sub_reward_long_distance_ahead_heading = 0.1
            

    sub_rewards.append(sub_reward_long_distance_ahead_heading * LONG_DISTANCE_AHEAD_HEADING_WEIGHT)





    # sub_reward_long_distance_ahead_steering_angle = 0.0

    # if direction_heading_diff_ahead_3_abs < 5.0:
    #     if steering_angle_abs < 7.0:
    #         sub_reward_long_distance_ahead_steering_angle = 1.0
    #     elif steering_angle_abs < 10.0:
    #         sub_reward_long_distance_ahead_steering_angle = 0.5
    #     elif steering_angle_abs >= 15.0:
    #         sub_reward_long_distance_ahead_steering_angle = -1.0
    #     elif steering_angle_abs >= 10.0:
    #         sub_reward_long_distance_ahead_steering_angle = -0.5

    # sub_rewards.append(sub_reward_long_distance_ahead_steering_angle * LONG_DISTANCE_AHEAD_STEERING_ANGLE_WEIGHT)





    percentage_within_of_center = get_percentage_within_of_center(distance_from_center, track_width)



    sub_reward_short_distance_ahead_center = 0.0
    short_distance_ahead_center_weight_nested = SHORT_DISTANCE_AHEAD_CENTER_WEIGHT

    if direction_heading_diff_ahead_1_abs < 5.0:
        short_distance_ahead_center_weight_nested *= 2

        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 1.0
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.9
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = 0.7
        elif percentage_within_of_center < 70.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 85.0:
            sub_reward_short_distance_ahead_center = -0.3
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.0
    elif direction_heading_diff_ahead_1_abs < 10.0:
        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.8
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.7
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = 0.6
        elif percentage_within_of_center < 65.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 80.0:
            sub_reward_short_distance_ahead_center = -0.35
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.0
    elif direction_heading_diff_ahead_1_abs >= 10.0:
        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.6
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.5
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = 0.4
        elif percentage_within_of_center < 60.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 75.0:
            sub_reward_short_distance_ahead_center = -0.35
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.1
    elif direction_heading_diff_ahead_1_abs >= 15.0:
        short_distance_ahead_center_weight_nested *= 2

        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.4
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.3
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = 0.1
        elif percentage_within_of_center < 60.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 75.0:
            sub_reward_short_distance_ahead_center = -0.4
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.2
    elif direction_heading_diff_ahead_1_abs >= 20.0:
        short_distance_ahead_center_weight_nested *= 3

        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.2
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.1
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 60.0:
            sub_reward_short_distance_ahead_center = -0.3
        elif percentage_within_of_center < 75.0:
            sub_reward_short_distance_ahead_center = -0.6
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.3
    elif direction_heading_diff_ahead_1_abs >= 25.0:
        short_distance_ahead_center_weight_nested *= 3.5

        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.1
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = -0.1
        elif percentage_within_of_center < 60.0:
            sub_reward_short_distance_ahead_center = -0.5
        elif percentage_within_of_center < 75.0:
            sub_reward_short_distance_ahead_center = -0.8
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -1.5
    elif direction_heading_diff_ahead_1_abs >= 30.0:
        short_distance_ahead_center_weight_nested *= 4

        if percentage_within_of_center < 10.0:
            sub_reward_short_distance_ahead_center = 0.05
        elif percentage_within_of_center < 20.0:
            sub_reward_short_distance_ahead_center = 0.0
        elif percentage_within_of_center < 40.0:
            sub_reward_short_distance_ahead_center = -0.3
        elif percentage_within_of_center < 60.0:
            sub_reward_short_distance_ahead_center = -0.7
        elif percentage_within_of_center < 75.0:
            sub_reward_short_distance_ahead_center = -1.0
        elif percentage_within_of_center < 100.0:
            sub_reward_short_distance_ahead_center = -2.0

    sub_rewards.append(sub_reward_short_distance_ahead_center * short_distance_ahead_center_weight_nested)       





    sub_reward_long_distance_ahead_center = 0.0
    long_distance_ahead_center_weight_nested = LONG_DISTANCE_AHEAD_CENTER_WEIGHT

    if direction_heading_diff_ahead_3_abs < 5.0:
        long_distance_ahead_center_weight_nested *= 2

        if percentage_within_of_center < 10.0:
            sub_reward_long_distance_ahead_center = 1.0
        elif percentage_within_of_center < 20.0:
            sub_reward_long_distance_ahead_center = 0.9
        elif percentage_within_of_center < 40.0:
            sub_reward_long_distance_ahead_center = 0.7
        elif percentage_within_of_center < 70.0:
            sub_reward_long_distance_ahead_center = 0.0
        elif percentage_within_of_center < 85.0:
            sub_reward_long_distance_ahead_center = -0.3
        elif percentage_within_of_center < 100.0:
            sub_reward_long_distance_ahead_center = -1.0
    elif direction_heading_diff_ahead_3_abs < 10.0:
        if percentage_within_of_center < 10.0:
            sub_reward_long_distance_ahead_center = 1.0
        elif percentage_within_of_center < 20.0:
            sub_reward_long_distance_ahead_center = 0.9
        elif percentage_within_of_center < 40.0:
            sub_reward_long_distance_ahead_center = 0.7
        elif percentage_within_of_center < 70.0:
            sub_reward_long_distance_ahead_center = 0.0
        elif percentage_within_of_center < 85.0:
            sub_reward_long_distance_ahead_center = -0.3
        elif percentage_within_of_center < 100.0:
            sub_reward_long_distance_ahead_center = -1.0

    sub_rewards.append(sub_reward_long_distance_ahead_center * long_distance_ahead_center_weight_nested)       






            # under_steer = True
            # over_steer = True

            # if track_direction_variation_ahead_1 > 70.0:
            #     print("")
            #     print("track_direction", track_direction, "heading", heading, "direction_heading_diff", direction_heading_diff, "heading_on_left_of_track_direction", heading_on_left_of_track_direction)
            #     print("track_direction_variation_ahead", track_direction_variation_ahead_1, track_direction_variation_ahead_2, track_direction_variation_ahead_3)
            

    # print(sub_rewards)
    # print(sum(sub_rewards))

    return sum(sub_rewards)

def get_normalised_angle(angle):
    if angle < -180.0:
        angle += 360.0
        
    if angle > 180.0:
        angle -= 360.0

    return angle

def get_track_direction(waypoints, waypoints_len, prev_point_idx, points_after=1):
    prev_point = waypoints[prev_point_idx]
    next_point_idx = (prev_point_idx + points_after) % waypoints_len

    next_point = waypoints[next_point_idx]

    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    # Convert to degree
    track_direction = math.degrees(track_direction)

    # print(prev_point_idx, "->", next_point_idx, track_direction)

    return track_direction

def get_percentage_within_of_center(distance_from_center, track_width):
    half_track_width = track_width / 2.0
    return (distance_from_center / half_track_width * 100.0)

def get_max_speed_precentage(speed):
    percentage_of_max_speed = speed / MAX_SPEED * 100.0

    return percentage_of_max_speed



