
from time import sleep
import math
import enum

import krpc
from krpc.services.spacecenter import SASMode
from krpc.services.spacecenter import CelestialBody
from krpc.services.spacecenter import Node
from krpc.stream import Stream

from KTE.angle_calculation import vect_dif
from KTE.notification import notify


#Direction of correction
class DirectionCorr(enum.Enum):
    co_directed = 1
    counter_directed = -1

class NodeAttr(enum.Enum):
    prograde = "prograde"
    normal = "normal"
    radial = "radial"


def measure(a: tuple[float, float, float]) -> float:
    return math.sqrt(a[0]*a[0] + a[1]* a[1] + a[2]*a[2])


def brute_force_corr(eve: CelestialBody,
                     ut: krpc.stream.Stream,
                     node: Node,
                     t_hohmann: float,
                     atr_name: NodeAttr,
                     direction: DirectionCorr) -> float:

    ref_frame = eve.orbit.body.reference_frame
    eve_pos = eve.orbit.position_at(ut() + t_hohmann, ref_frame)
    ves_pos = node.orbit.position_at(ut() + t_hohmann, ref_frame)
    #Difference between positions
    d_position = measure(vect_dif(ves_pos, eve_pos))

    setattr(node, atr_name.value,
            getattr(node, atr_name.value) + 1 * direction.value)

    eve_pos = eve.orbit.position_at(ut() + t_hohmann, ref_frame)
    ves_pos = node.orbit.position_at(ut() + t_hohmann, ref_frame)

    while d_position > measure(vect_dif(ves_pos, eve_pos)):
        d_position = measure(vect_dif(ves_pos, eve_pos))
        setattr(node, atr_name.value,
                getattr(node, atr_name.value) + 1 * direction.value)
        eve_pos = eve.orbit.position_at(ut() + t_hohmann, ref_frame)
        ves_pos = node.orbit.position_at(ut() + t_hohmann, ref_frame)

    setattr(node, atr_name.value,
            getattr(node, atr_name.value) - 1 * direction.value)

    return d_position

def correction_of_trajectory(conn: krpc.Client) -> None:
    vessel = conn.space_center.active_vessel

    ut = conn.add_stream(getattr, conn.space_center, "ut")
    node = vessel.control.add_node(ut() + 180)
    eve = conn.space_center.bodies.get("Eve")
    kerbin = conn.space_center.bodies.get("Kerbin")
    sun = eve.orbit.body
    ref_frame = sun.reference_frame

    r_k = kerbin.orbit.semi_major_axis
    r_e = eve.orbit.semi_major_axis

    #time*1.14 'cause the 2nd type of Hohmann trajectory
    t_hohmann = 1.14 * math.pi * math.sqrt(
        math.pow(r_k + r_e, 3.0) /
        (sun.gravitational_parameter * 8.0)
    )

    eve_pos = eve.orbit.position_at(ut() + t_hohmann,
                               ref_frame)
    ves_pos = node.orbit.position_at(ut() + t_hohmann,
                                           ref_frame)

    #Difference between positions
    d_position = measure(vect_dif(ves_pos, eve_pos))

    # Finding a correction maneuver by brute force
    while d_position > eve.sphere_of_influence/2:
        #prograde
        brute_force_corr(eve, ut, node, t_hohmann, NodeAttr.prograde,
                         DirectionCorr.co_directed)
        #retrograde
        brute_force_corr(eve, ut, node, t_hohmann, NodeAttr.prograde,
                         DirectionCorr.counter_directed)
        #normal
        brute_force_corr(eve, ut, node, t_hohmann, NodeAttr.normal,
                         DirectionCorr.co_directed)
        #anti-normal
        brute_force_corr(eve, ut, node, t_hohmann, NodeAttr.normal,
                         DirectionCorr.counter_directed)
        #Radial
        brute_force_corr(eve, ut, node, t_hohmann, NodeAttr.radial,
                         DirectionCorr.co_directed)
        #radial out
        d_position = brute_force_corr(eve, ut, node, t_hohmann,
                                      NodeAttr.radial,
                                      DirectionCorr.counter_directed)

    # Calculate burn time (using Tsiolkovsky rocket equation)
    d_v = node.remaining_delta_v
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.80665
    m0 = vessel.mass
    m1 = m0 / math.exp(d_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    burn_ut = ut() + node.time_to - burn_time / 2.0

    lead_time = 21 #Delay for SAS
    conn.space_center.warp_to(burn_ut - lead_time)
    vessel.control.sas = True
    vessel.control.rcs = True
    sleep(1)
    # Using the code below once does not always
    # change the target for SAS, possibly due to in-game lag.
    vessel.control.sas_mode = SASMode.maneuver
    vessel.control.sas_mode = SASMode.maneuver
    vessel.control.sas_mode = SASMode.maneuver
    sleep(lead_time - 1)

    notify(conn, "Execute burn for corretion.")
    vessel.control.throttle = 1.0
    sleep(burn_time - 0.1)

    vessel.control.throttle = 0.1
    vessel.control.sas = False
    vessel.auto_pilot.reference_frame = ref_frame
    vessel.auto_pilot.target_direction = vessel.direction(ref_frame)
    vessel.auto_pilot.engage()

    while (vessel.orbit.next_orbit is None or
           vessel.orbit.next_orbit.body.name != eve.name or
           vessel.orbit.next_orbit.periapsis_altitude >
           eve.sphere_of_influence / 1.5):
        sleep(0.1)
        pass

    vessel.control.throttle = 0.0
    vessel.auto_pilot.disengage()
    vessel.control.rcs = False
    node.remove()
