import math as m
import numpy as np
import scipy.optimize as o
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint 

### PARAM: Initial player or pearl position
s_x0 = 0
s_y0 = 4
s_z0 = 0
s_y0 = s_y0 + 1.62 - 0.1

### PARAM: Initial player velocity
v_px = 0
v_py = 0
v_pz = 0

### Component-wise initial velocity function given a pitch and axis. Yaw is kept constant to 360 degrees. 
def v_0(axis:str, pitch:float) -> float:
    pitch = m.radians(pitch)
    return {
        "x": 0,
        "y": -1.5 * m.sin(pitch),
        "z": 1.5 * m.cos(pitch)
    }[axis]


### Component-wise velocity function given a pitch and axis, initial pitch, and time. We keep yaw constant at 360 degrees
def v(t:int, axis:str, pitch:float) -> float:
    pitch = m.radians(pitch)
    return {
        "x": 0, 
        "y": v_0(axis, pitch)*0.99**m.floor(t) - 0.03*(100-100*0.99**m.floor(t)),
        "z": v_0(axis, pitch)*0.99**m.floor(t)
    }[axis]

### Component-wise position function given a pitch and axis. We keep yaw constant at 360 degrees (hence, zeroing every sin(yaw))
def s(t:int, axis:str, pitch:float) -> float:
    pitch = m.radians(pitch)
    return {
        "x": s_x0,
        "y": s_y0 - 3*t - (1.5*m.sin(pitch) - 3) * (100 - 100*0.99**t),
        "z": s_z0 + 1.5*m.cos(pitch) * (100 - 100*0.99**t)
    }[axis]

### Passed into root_scalar to find where the position function for y, ie s_y, intersects the even ground y=s_y0. This helper transforms the root found by root_scalar to be the solution to s_y = s_y0 (where s_y0 is adjusted for the 1.62 and -0.1 offsets applied its initialization). 
def helper_s_y(t:int, pitch:float) -> float:
    return s(t, "y", pitch) - (s_y0 - (1.62-0.1))


### Compute when the pearl hits the ground, ASSUMING the landing spot is level with the player's standing spot 
# upper bound seems to be at least 90 ticks, as produced by angle -89 to -84 (angle -83 produced 89 ticks). Hence, 300 as an upper bound on root-finding is more than enough.  
def compute_landing_time(pitch:float) -> float:
    return m.floor(o.root_scalar(helper_s_y, args=(pitch), bracket=[0, 300], method="bisect").root)

### Convert a given pitch to its significant angle equivalent
# I observed that the raw pitch always gets rounded up to the higher significant angle: -45 is exactly a signif angle, and you can test -45.00001 and -44.99999 -- the former achieves 51.425 and latter achieves 51.430. Crazy!
def convert_pitch(pitch:float) -> float:
    return m.ceil(pitch / (360/65536)) * 360/65536 

landing_times = {}
landing_distances = {}
desired_angles = np.arange(-50, -30+1)
for pitch in desired_angles:
    converted_pitch = convert_pitch(pitch)
    landing_times[pitch] = compute_landing_time(converted_pitch)
    landing_distances[pitch] = s(landing_times[pitch], "z", converted_pitch)

#pprint(landing_times)
pprint(landing_distances)
df = pd.DataFrame(landing_distances.items(), columns=['Angle', 'Distance'])
df.to_csv('C:/Users/vluon/Desktop/Math and Science/minecraft ender pearl simulations/output.csv', index=False)