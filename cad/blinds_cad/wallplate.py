"""Wall plate — screws into the window-recess reveal; the unit's cleat
hook drops onto its rail. Printable.

Local frame: x centred on plate width, y=0 at the FRONT face (plate
body extends -y toward the wall), z=0 at the plate bottom. 4× countersunk
screw holes for #8 + anchors; 2:1 cleat rail near the top edge.

View it: `just cad view blinds-plate`.
"""

from build123d import Box, Cylinder, Cone, Polygon, Pos, Rot, extrude

from .params import P

RAIL_TOP_LOCAL = P.cleat_rail_top - P.plate_z0  # 170 = unit z 185


def wallplate():
    w, h, t = P.plate_w, P.plate_h, P.plate_t

    body = Pos(0, -t / 2, h / 2) * Box(w, t, h)

    # cleat rail on the front face: 2:1 slope, hook slides down onto it.
    # CCW winding — CW polygons extrude along -Z and flip the axis map.
    rail = Polygon(
        (0, RAIL_TOP_LOCAL - P.cleat_h),
        (P.cleat_t, RAIL_TOP_LOCAL),
        (0, RAIL_TOP_LOCAL),
    )
    # length matches the shell's hook bar span (stops short of the
    # layshaft spur wheel, like the bar itself)
    rail_len = P.cleat_x1 - P.cleat_x0 - 1.0
    # Rot(0,90,90) is the cyclic axis map: sketch(x,y)+extrude(z) -> local(y,z,x)
    body += Pos(P.cleat_x0 + 0.5 - P.enc_w / 2, 0, 0) * (
        Rot(0, 90, 90) * extrude(rail, amount=rail_len)
    )

    # 4× countersunk screw holes
    ins = P.plate_screw_inset
    for x in (-w / 2 + ins, w / 2 - ins):
        for z in (ins, h - ins):
            body -= Pos(x, -t / 2, z) * (Rot(90, 0, 0) * Cylinder(P.plate_screw_d / 2, t + 2))
            sink_h = (P.plate_screw_head - P.plate_screw_d) / 2
            # Rot(90,0,0) sends cone bottom (-z) to +y: bottom radius =
            # head, landing flush on the front face, tapering wallward
            body -= Pos(x, -sink_h / 2, z) * (
                Rot(90, 0, 0)
                * Cone(P.plate_screw_head / 2, P.plate_screw_d / 2, sink_h)
            )
    return body


def scene():
    from splitflap_cad.viewer import Scene

    return Scene().add(wallplate(), "wallplate", color="lightsteelblue")
