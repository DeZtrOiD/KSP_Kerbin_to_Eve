
import math
from time import sleep

import krpc

from KTE.correction_node import correction_of_trajectory
from KTE.interorbital_flight import interorbital_burn
from KTE.orbital_launch import launch_into_orbit
from KTE.angle_calculation import time_shift_for_phase_angle
from KTE.circularization import circularization_burn
from KTE.slowdown import slowdown_near_eve
from KTE.notification import notify


#connection to server, setting up base variables
conn = krpc.connect(name="Control connection")
vessel = conn.space_center.active_vessel
ut = conn.add_stream(getattr, conn.space_center, "ut")

target_altitude = 260000.0
turn_start_altitude = 3000.0
turn_end_altitude = 120000.0

#Taken from https://ksp.olex.biz/
phase_angle = 55/180 * math.pi
ejection_angle = 152.23 / 180 * math.pi
d_v_hohmann = 950.0

preparation_time = 60*60*4


sleep(1)
notify(conn, "Waiting for the launch window.")
#Hibernation to save energy
vessel.parts.root.modules[0].set_field_bool_by_id("hibernation", True)
#Calculating the launch window and waiting for it
d_t = time_shift_for_phase_angle(conn, phase_angle) - preparation_time
conn.space_center.warp_to(ut() + d_t)
vessel.parts.root.modules[0].set_field_bool_by_id("hibernation", False)
sleep(2)


#Start of launch
notify(conn, "Launch!")
launch_into_orbit(conn, target_altitude, turn_start_altitude,
                  turn_end_altitude)

vessel.control.activate_next_stage() # Opening of the cargo bay
vessel.control.activate_next_stage() # Separation of the booster stage
vessel.control.activate_next_stage() # Activation of the second stage


#Entering a cyclic orbit
circularization_burn(conn)

#Deployment of solar panels and antennas
sol_panels = vessel.parts.solar_panels
for i in sol_panels:
    i.deployed = True
ves_antennas = vessel.parts.antennas
for i in range(1, 3):
    ves_antennas[i].deployed = True


#Hohmann transfer
interorbital_burn(conn, ejection_angle, d_v_hohmann)


#wait leaving Kerbin SOI
notify(conn, "Leave Kerbin")
conn.space_center.warp_to(ut() + vessel.orbit.time_to_soi_change)
sleep(2)


# correction transfer
notify(conn, "Correction")
correction_of_trajectory(conn)
sleep(2)


# Waiting to approach Eve
notify(conn, "Waiting to approach Eve.")
conn.space_center.warp_to(ut() + vessel.orbit.time_to_soi_change)
sleep(2)


#Slowdown near Eva
slowdown_near_eve(conn)
sleep(2)


# Separation of the old stage
vessel.control.activate_next_stage()
vessel.control.activate_next_stage()

#Turning on the girodin
girodin = vessel.parts.with_name("advSasModule")[0].modules[0]
girodin.trigger_event(girodin.events[0])

notify(conn, "Launch into Eve orbit complete")
