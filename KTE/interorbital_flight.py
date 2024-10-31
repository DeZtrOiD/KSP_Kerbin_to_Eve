
import math
from time import sleep

import krpc
from krpc.services.spacecenter import SASMode

from KTE.angle_calculation import time_shift_for_ejection_angle
from KTE.notification import notify


def interorbital_burn(conn: krpc.Client,
                      ejection_angle = 152.23 / 180 * math.pi,
                      d_v_prograde = 950.0) -> None:
    ut = conn.add_stream(getattr, conn.space_center, "ut")
    vessel = conn.space_center.active_vessel
    delta_t = time_shift_for_ejection_angle(conn, ejection_angle)
    if delta_t < 60:
        delta_t += vessel.orbit.period
    eve = conn.space_center.bodies.get("Eve")
    sun = eve.orbit.body

    node = vessel.control.add_node(ut() + delta_t,
                                   prograde=d_v_prograde)

    # The cycle is necessary to avoid
    # collisions with Kerbin's moons.
    while (node.orbit.next_orbit.body.name != sun.name
           and node.orbit.next_orbit.body.name != eve.name):
        node.ut += vessel.orbit.period

    # Calculate burn time (using Tsiolkovsky rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.80665
    m0 = vessel.mass
    m1 = m0 / math.exp(d_v_prograde / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    # Wait until burn
    burn_ut = ut() + node.time_to - burn_time/2.0
    lead_time = 26
    conn.space_center.warp_to(burn_ut - lead_time)
    vessel.control.sas = True
    vessel.control.rcs = True
    sleep(1)
    # Using the code below once does not always
    # change the target for SAS, possibly due to in-game lag.
    vessel.control.sas_mode = SASMode.maneuver
    vessel.control.sas_mode = SASMode.maneuver
    sleep(lead_time - 1)
    # Execute burn
    notify(conn,"Execute burn.")
    vessel.control.throttle = 1.0
    sleep(burn_time - 0.2)
    vessel.control.throttle = 0.2
    while node.remaining_delta_v > 10:
        sleep(0.2)
        pass
    vessel.control.throttle = 0.0
    vessel.control.sas = False
    vessel.control.rcs = False
    node.remove()
