
import math
from time import sleep

import krpc
from krpc.services.spacecenter import SASMode

from KTE.notification import notify


def slowdown_near_eve(conn: krpc.Client) -> None:
    vessel = conn.space_center.active_vessel
    ut = conn.add_stream(getattr, conn.space_center, "ut")
    #Vis-viva equation
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.periapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2.0 / r) - (1.0 / a1)))
    v2 = math.sqrt(mu * ((2.0 / r) - (1.0 / a2)))
    d_v_prograde = v2-v1
    node = vessel.control.add_node(ut() +
                                   vessel.orbit.time_to_periapsis,
                                   prograde=d_v_prograde)

    # Calculate burn time (using Tsiolkovsky rocket equation)
    d_v_prograde = abs(d_v_prograde)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.80665
    m0 = vessel.mass
    m1 = m0 / math.exp(d_v_prograde / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    burn_ut = ut() + vessel.orbit.time_to_periapsis - (burn_time / 2.0)
    lead_time = 21
    notify(conn,"Wait maneuver time")
    conn.space_center.warp_to(burn_ut - lead_time)
    vessel.control.rcs = True
    vessel.control.sas = True
    sleep(1)
    # Using the code below once does not always
    # change the target for SAS, possibly due to in-game lag.
    vessel.control.sas_mode = SASMode.maneuver
    vessel.control.sas_mode = SASMode.maneuver
    sleep(lead_time - 1)

    time_to_periapsis = conn.add_stream(getattr, vessel.orbit,
                                       "time_to_periapsis")
    while time_to_periapsis() - (burn_time / 2.0) > 0:
        pass
    notify(conn,"Executing a slowdown")
    vessel.control.throttle = 1.0
    sleep(burn_time - 0.1)
    vessel.control.throttle = 0.2
    while node.remaining_delta_v > 10:
        sleep(0.2)
        pass
    vessel.control.throttle = 0.0
    vessel.control.rcs = False
    vessel.control.sas = False
    node.remove()
    sleep(1)
