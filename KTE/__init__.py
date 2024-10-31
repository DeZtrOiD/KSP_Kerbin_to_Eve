"""
From 'Kerbin to Eve' set of function is essentially a set of useful
functions for implementing an autopilot and for some calculating the
flight from Kerbin to Eve.

Contains:

- angle_calculation.py,
    which helps calculate the time a spacecraft needs to wait in orbit
    to reach the launch window and ejection angle
- circularization.py,
    which helps to enter a circular orbit around Kerbin.
- correction_node.py
    Which helps to correct the Hohmann transition by brute force
- interorbital_flight.py,
    Which performs the Hohmann transition from Kerbin to Eve
- notification.py
    Which contains a simple function for notification in the console
     and in the game
- orbital_launch.py,
    Which performs the exit to the Kerbin orbit
- slowdown.py
    Which implements the transition from the Hohmann
     trajectory to the orbit around Eve
"""
