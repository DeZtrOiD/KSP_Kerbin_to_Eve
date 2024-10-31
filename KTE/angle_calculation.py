
import math
from time import sleep

from numpy.ma.core import arccos
import krpc


def angle_bt_vectors(a: tuple[float,float,float],
                     b: tuple[float, float, float]) -> float:

    tmp = a[0] * b[0] + a[1]*b[1] + a[2] * b[2]
    tmp /= math.sqrt(a[0] * a[0] + a[1]*a[1]+ a[2]*a[2]) * \
           math.sqrt(b[0] *b[0] + b[1]*b[1] + b[2]*b[2])
    return arccos(tmp)


def vect_dif(a1: tuple[float, float, float],
             a2: tuple[float, float, float]) \
        -> tuple[float, float, float]:
    return a1[0] - a2[0], a1[1] - a2[1], a1[2] - a2[2]


def time_shift_for_phase_angle(conn: krpc.Client,
                               phase_angle =
                               (54.13 + 1) / 180 * math.pi) -> float:
    eve = conn.space_center.bodies.get("Eve")
    kerbin = conn.space_center.bodies.get("Kerbin")

    ec = conn.add_stream(eve.position,
                         eve.orbit.body.reference_frame)
    kc = conn.add_stream(kerbin.position,
                         eve.orbit.body.reference_frame)
    #Angular velocities
    w_ep = 2 * math.pi / eve.orbit.period
    w_kp = 2 * math.pi / kerbin.orbit.period
    #Angular velocity of approach
    w_conv = w_ep - w_kp
    curr_angle = angle_bt_vectors(ec(), kc())
    sleep(10)
    d_ang = angle_bt_vectors(ec(), kc()) - curr_angle
    if d_ang > 0:
        curr_angle = - curr_angle - d_ang
    else:
        curr_angle = curr_angle - d_ang
    d_t = -(phase_angle - curr_angle) / w_conv
    if d_t < 0:
        d_t += 2 * math.pi / w_conv
    return  d_t


def time_shift_for_ejection_angle(conn: krpc.Client,
                                  ejection_angle =
                                  152.23 / 180 * math.pi) -> float:
    vessel = conn.space_center.active_vessel
    kerbin = conn.space_center.bodies.get("Kerbin")
    kp = conn.add_stream(kerbin.position,
                         kerbin.orbit.body.reference_frame)
    kv = conn.add_stream(kerbin.velocity,
                         kerbin.orbit.body.reference_frame)
    vp = conn.add_stream(vessel.position,
                         kerbin.orbit.body.reference_frame)

    curr_angle = angle_bt_vectors(vect_dif(vp(), kp()), kv())
    sleep(10)
    d_angle = angle_bt_vectors(vect_dif(vp(), kp()), kv()) - curr_angle
    if d_angle > 0:
        curr_angle = -curr_angle - d_angle
    else:
        curr_angle = curr_angle - d_angle

    d_t = (- (ejection_angle - curr_angle) /
           (2 * math.pi / vessel.orbit.period))

    if d_t < 0:
        d_t += vessel.orbit.period
    return  d_t
