
import math
from time import sleep

import krpc
import krpc.services.spacecenter as krpc_s_s
from krpc.services.spacecenter import SASMode

from KTE.notification import notify


def planing_circularization_burn(vessel: krpc_s_s.Vessel) -> float:
    #Vis-viva equation
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2.0 / r) - (1.0 / a1)))
    v2 = math.sqrt(mu * ((2.0 / r) - (1.0 / a2)))
    return v2 - v1

def circularization_burn(conn: krpc.Client) -> None:
    vessel = conn.space_center.active_vessel
    ut = conn.add_stream(getattr, conn.space_center, "ut")
    delta_v = planing_circularization_burn(vessel)
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

    # Calculate burn time (using Tsiolkovsky rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.80665
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    # Orientate ship
    notify(conn,"Orienting ship for circularization burn")
    vessel.control.rcs = True
    vessel.control.sas = True
    sleep(1)
    # Using the code below once does not always
    # change the target for SAS, possibly due to in-game lag.
    vessel.control.sas_mode = SASMode.maneuver
    vessel.control.sas_mode = SASMode.maneuver
    sleep(19)

    # Wait until burn
    notify(conn, "Waiting until circularization burn")
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.0)
    lead_time = 3
    conn.space_center.warp_to(burn_ut - lead_time)
    sleep(lead_time)

    # Execute burn
    notify(conn,"Executing burn")
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit,
                                       "time_to_apoapsis")
    while time_to_apoapsis() - (burn_time / 2.0) > 0:
        pass
    vessel.control.throttle = 1.0
    sleep(burn_time - 0.01)
    vessel.control.sas_mode = SASMode.prograde
    vessel.control.sas_mode = SASMode.prograde
    vessel.control.throttle = 0.4
    apoapsis_alt = vessel.orbit.apoapsis_altitude
    while vessel.orbit.periapsis_altitude + 5_000 < apoapsis_alt:
        sleep(0.5)
        pass
    vessel.control.throttle = 0.0
    vessel.control.rcs = False
    vessel.control.sas = False
    node.remove()
    notify(conn,"Launch into Kerbin orbit complete")
