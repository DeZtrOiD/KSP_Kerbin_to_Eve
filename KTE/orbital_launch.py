
from time import sleep

import krpc

from KTE.notification import notify


def launch_into_orbit(conn : krpc.Client,
                    target_altitude = 260000.0,
                    turn_start_altitude = 3000.0,
                    turn_end_altitude = 120000.0) -> None:
    vessel = conn.space_center.active_vessel
    curr_altitude = conn.add_stream(getattr, vessel.flight(),
                                    "mean_altitude")
    #apoapsis of the vessel's orbit
    apoapsis = conn.add_stream(getattr, vessel.orbit,
                               "apoapsis_altitude")
    # amount of solid fuel remaining in the boosters
    solid_fuel_in_boosters = conn.add_stream(
        vessel.resources_in_decouple_stage(stage=5,
                                           cumulative=False).amount,
        "SolidFuel")

    # Pre-launch setup
    vessel.control.sas = False
    vessel.control.rcs = False
    # Activate the first stage
    vessel.control.activate_next_stage()
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.control.throttle = 1.0
    srbs_separated = False     # solid fuel boosters


    # launch into orbit loop
    while True:
        # Slow turn of the rocket
        if turn_start_altitude < curr_altitude() < turn_end_altitude:
            angle_increm = ((curr_altitude() - turn_start_altitude) /
                    (turn_end_altitude - turn_start_altitude))
            new_turn_angle = angle_increm * 90
            turn_angle = new_turn_angle
            if new_turn_angle < 90:
                vessel.auto_pilot.target_pitch_and_heading(
                    90 - turn_angle,
                    90)
            else:
                vessel.auto_pilot.target_pitch_and_heading(
                    0,
                    90)
        # Separate Solid Rocket Boosters when finished
        if not srbs_separated:
            if solid_fuel_in_boosters() < 0.1:
                notify(conn,
                       "Separating Solid Rocket Boosters")
                vessel.control.activate_next_stage()
                sleep(3)
                turn_end_altitude = 60000
                srbs_separated = True
        # Decrease throttle when approaching target apoapsis
        if apoapsis() > target_altitude * 0.9:
            break
    #slow engine shutdown
    vessel.control.throttle = 0.25
    while apoapsis() < target_altitude:
        sleep(1)
        pass
    vessel.control.throttle = 0.0
    vessel.auto_pilot.disengage()
    sleep(1)
