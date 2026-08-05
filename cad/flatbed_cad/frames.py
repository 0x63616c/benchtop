"""Flatbed local-to-assembly poses."""

from build123d import Plane, Pos, Rot

from .params import P


# Upright local Y becomes assembly +Z. Its seating edge lands on the base top
# while the two tabs occupy the base thickness and finish flush underneath.
UPRIGHT_ON_BASE = Pos(0, P.panel_t / 2, P.panel_t) * Rot(90, 0, 0)


# Enclosed gearbox panel frames. Each local part is modeled in its flat print
# orientation with local +Z growing away from the bed. For wall panels +Z is
# deliberately mapped inward so bearing reinforcements stay inside the box.
FG_BOTTOM_IN_BOX = Pos(P.fg_box_w / 2, P.fg_box_d / 2, 0)
FG_TOP_IN_BOX = Pos(P.fg_box_w / 2, P.fg_box_d / 2, P.fg_box_h) * Rot(180, 0, 0)

FG_LEFT_IN_BOX = Plane(
    origin=(0, P.fg_box_d / 2, P.fg_box_h / 2),
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0),
).location
FG_RIGHT_IN_BOX = Plane(
    origin=(P.fg_box_w, P.fg_box_d / 2, P.fg_box_h / 2),
    x_dir=(0, 1, 0),
    z_dir=(-1, 0, 0),
).location

FG_REAR_IN_BOX = Plane(
    origin=(P.fg_box_w / 2, 0, P.fg_box_h / 2),
    x_dir=(-1, 0, 0),
    z_dir=(0, 1, 0),
).location
FG_FRONT_IN_BOX = Plane(
    origin=(P.fg_box_w / 2, P.fg_box_d, P.fg_box_h / 2),
    x_dir=(1, 0, 0),
    z_dir=(0, -1, 0),
).location

FG_BULKHEAD_IN_BOX = Plane(
    origin=(P.fg_box_w / 2, P.fg_motor_face_y, P.fg_box_h / 2),
    x_dir=(-1, 0, 0),
    z_dir=(0, 1, 0),
).location
FG_MOTOR_IN_BOX = Pos(P.fg_motor_axis_x, P.fg_motor_face_y, P.fg_shaft_z)
