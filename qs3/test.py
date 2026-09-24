import math
from scipy.optimize import minimize_scalar

# Given values
R = 5.0
omega = 0.40
T = 8.0


# Robot A position
def position_A(t):
    x_A = R * math.cos(omega * t)
    y_A = R * math.sin(omega * t)

    return x_A, y_A


# Robot B position
def position_B(t):
    s = (2 * math.pi / T) * t

    x_B = -(s + 3 * math.sin(s)) / math.sqrt(2)
    y_B = (s - 3 * math.sin(s)) / math.sqrt(2)

    return x_B, y_B


# Distance squared between A and B
def distance_squared(t):

    x_A, y_A = position_A(t)
    x_B, y_B = position_B(t)

    return (x_B - x_A)**2 + (y_B - y_A)**2


# Time for one complete revolution of Robot A
t_end = 2 * math.pi / omega

# Numerically minimize distance squared
result = minimize_scalar(
    distance_squared,
    bounds=(0, t_end),
    method='bounded'
)

# Time of minimum distance
t_min = result.x

# Minimum distance
d_min = math.sqrt(result.fun)

# Calculate positions at closest point
x_A, y_A = position_A(t_min)
x_B, y_B = position_B(t_min)

# Calculate s at that time
s_min = (2 * math.pi / T) * t_min


print("One revolution of A:", t_end, "seconds")
print("Time of closest approach:", t_min, "seconds")
print("Minimum distance:", d_min, "meters")
print("s at closest approach:", s_min)

print("\nRobot A position:")
print(x_A, y_A)

print("\nRobot B position:")
print(x_B, y_B)