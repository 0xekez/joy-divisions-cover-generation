import numpy as np
from params import params


def add_noise(amps, mean):
    '''
    adds noise and connecting lines to data
    IN: data, mean of data
    OUT: data combined with connecting lines and noise
    '''
    noise_len = len(amps)//params['noise_frac']
    start = amps[0]
    end = amps[-1]

    start_slope = (amps[1]-start)/2
    end_slope = (amps[-2]-end)/2

    # BUILD START LINE
    start_line = get_connecting_line(mean, start, start_slope, params['min_ticks'])
    start_line = [mean for i in range(noise_len-len(start_line))] + start_line

    # BUILD END LINE
    end_line = get_connecting_line(end, mean, end_slope, params['min_ticks'])
    end_line = end_line + [mean for i in range(noise_len - len(end_line))]

    # ADD RANDOM NOISE AND RETURN
    combined = add_random_noise(start_line, params['random_noise_range']) + amps + add_random_noise(end_line, params['random_noise_range'])
    return combined


def get_connecting_line(start, end, target_slope, min_ticks):
    '''
    calculates the values for a connecting line
    IN: where the line should start, where the line should end, ideal slope,
        the minimum amount of ticks to get to the end
    OUT: list of amplitude values for connecting line
    '''
    # handle case where start and end are functionally the same:
    if(int(start) == int(end)):
        return []

    if int(target_slope) == 0:
        return []

    connecting_line = []

    delta_y = end-start
    min_slope = delta_y/min_ticks

    # if the sign of target_slope and min_slope are diff
    # change target slope to same as min slope
    if (target_slope*min_slope < 0):
        target_slope = target_slope*(-1)

    # whichever has the smallest diff from 0 has slowest slope
    if abs(target_slope) >= abs(min_slope):
        slope = target_slope
    else:
        slope = min_slope

    num_ticks = int(delta_y/slope)
    for i in range(num_ticks):
        connecting_line.append(start + len(connecting_line)*slope)

    return add_random_noise(connecting_line, params['connecting_line_range'])


def add_random_noise(list, range):
    '''
    adds random noise to list of amplitudes
    IN: amplitude data, how much range does the noise have
    OUT: data with noise added
    TODD: casting between np.array and list takes lots of time, probably faster
          alt that involves python random lib
    '''
    min = 0-range/2
    max = 0+range/2
    a = np.array(list)
    noise = np.random.normal(min, max, a.size)
    a = a+noise
    return a.tolist()
