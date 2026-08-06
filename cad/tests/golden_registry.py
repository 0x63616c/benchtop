"""Registry of parts under golden-geometry guard (see test_geometry.py).

Every part is BREP + fingerprint: exact geometry committed to golden/,
XOR-diffable. The FINGERPRINT_ONLY tier existed for the two full units,
which used to carry verbatim vendor STEP fins we couldn't commit; the
fins are parametric now, so both are guarded like everything else. The
tier stays as an empty dict for whenever third-party geometry shows up
again.

Builders are lazy; importing this module builds nothing.
"""

GOLDEN_DIR_NAME = "golden"
FINGERPRINTS_NAME = "fingerprints.json"

# relative tolerance for volume/area, absolute mm for bbox/COM coords
REL_TOL = 1e-6
ABS_TOL = 1e-4
# residual mm^3 allowed in each direction of the XOR test
XOR_TOL = 1e-3


def _flap():
    from splitflap_cad.flap import flap

    return flap()


def _holder():
    from splitflap_cad.holder import holder

    return holder()


def _drum_outer():
    from splitflap_cad.drum import drum_outer

    return drum_outer()


def _drum_inner():
    from splitflap_cad.drum import drum_inner

    return drum_inner()


def _drum_inner_nema():
    from splitflap_cad.drum import drum_inner_nema

    return drum_inner_nema()


def _motor_byj():
    from splitflap_cad.stepper28byj import stepper28byj

    return stepper28byj()


def _hall_pcb():
    from splitflap_cad.assembly import posed_hall_pcb

    return posed_hall_pcb()


def _unit_plate():
    from splitflap_cad.unit import unit_plate

    return unit_plate()


def _full_unit():
    from splitflap_cad.unit import full_unit

    return full_unit()


def _nema_plate():
    from splitflap_cad.unitnema import nema_plate

    return nema_plate()


def _nema_bridge():
    from splitflap_cad.unitnema import nema_bridge

    return nema_bridge()


def _full_unit_nema():
    from splitflap_cad.unitnema import full_unit_nema

    return full_unit_nema()


def _ipad_body():
    from splitflap_cad.ipadwall import bracket_body

    return bracket_body()


def _ipad_lid():
    from splitflap_cad.ipadwall import bracket_lid

    return bracket_lid()


def _grommet_usb():
    from splitflap_cad.grommet import grommet_usb

    return grommet_usb()


def _grommet_bathroom():
    from splitflap_cad.grommet import grommet_bathroom

    return grommet_bathroom()


def _poop_bucket():
    from splitflap_cad.poopbucket import poop_bucket

    return poop_bucket()


def _mirror_spacer_straight():
    from splitflap_cad.mirrorlight import spacer_straight

    return spacer_straight()


def _mirror_spacer_arch():
    from splitflap_cad.mirrorlight import spacer_arch

    return spacer_arch()


def _mirror_spacer_corner():
    from splitflap_cad.mirrorlight import spacer_corner

    return spacer_corner()


def _blinds_sprocket():
    from blinds_cad.sprocket import sprocket_print

    return sprocket_print()


def _blinds_sprocket_bevel():
    from blinds_cad.sprocket import sprocket_bevel_print

    return sprocket_bevel_print()


def _blinds_sprocket_spacer():
    from blinds_cad.drivecassette import sprocket_spacer_print

    return sprocket_spacer_print()


def _blinds_frame():
    from blinds_cad.enclosure import frame

    return frame()


def _blinds_cassette_lid():
    from blinds_cad.drivecassette import cassette_lid_print

    return cassette_lid_print()


def _blinds_sleeve():
    from blinds_cad.cover import sleeve

    return sleeve()


def _blinds_cap_rear():
    from blinds_cad.cover import cap_rear

    return cap_rear()


def _blinds_cap_front():
    from blinds_cad.cover import cap_front

    return cap_front()


def _blinds_motor():
    from blinds_cad.jgb37 import jgb37

    return jgb37()


def _blinds_pinion():
    from blinds_cad.gears import pinion_print

    return pinion_print()


def _blinds_layshaft_spur():
    from blinds_cad.gears import spur_gear_print

    return spur_gear_print()


def _blinds_layshaft_bevel():
    from blinds_cad.gears import bevel_gear_print

    return bevel_gear_print()


def _blinds_drive_cassette():
    from blinds_cad.drivecassette import drive_cassette

    return drive_cassette()


def _blinds_drive_spacers():
    from blinds_cad.drivecassette import spacers_print

    return spacers_print()


def _gearbox_housing():
    from splitflap_cad.gearbox import housing

    return housing()


def _gearbox_lid():
    from splitflap_cad.gearbox import lid

    return lid()


def _gearbox_input_gear():
    from splitflap_cad.gearbox import input_gear

    return input_gear()


def _gearbox_output_gear():
    from splitflap_cad.gearbox import output_gear

    return output_gear()


def _gearbox_input_spacer():
    from splitflap_cad.gearbox import input_spacer

    return input_spacer()


def _gearbox_output_spacer():
    from splitflap_cad.gearbox import output_spacer

    return output_spacer()


def _gearbox_test_bushings():
    from splitflap_cad.gearbox import test_bushings

    return test_bushings()


def _gearbox_mesh_jig():
    from splitflap_cad.gearbox import mesh_jig

    return mesh_jig()


def _gearbox_motor_housing():
    from splitflap_cad.motorbevel import housing

    return housing()


def _gearbox_motor_lid():
    from splitflap_cad.motorbevel import lid_print

    return lid_print()


def _gearbox_motor_input_spacer():
    from splitflap_cad.motorbevel import input_spacer

    return input_spacer()


def _gearbox_motor_output_spacer():
    from splitflap_cad.motorbevel import output_spacer

    return output_spacer()


def _nas_hdd():
    from nas_cad.hdd import hdd_envelope

    return hdd_envelope()


def _nas_caddy():
    from nas_cad.bay import caddy

    return caddy()


def _nas_door():
    from nas_cad.bay import door

    return door()


def _nas_bay_frame():
    from nas_cad.bay import bay_frame

    return bay_frame()


def _flatbed_calibration_kit():
    from flatbed_cad.calibration import calibration_kit

    return calibration_kit()


def _flatbed_insert_test():
    from flatbed_cad.insert_test import insert_test_plate

    return insert_test_plate()


def _flatbed_speedbox_motor():
    from flatbed_cad.motor_reference import motor_reference

    return motor_reference()


def _flatbed_speedbox_bottom():
    from flatbed_cad.speedbox_panels import bottom_panel

    return bottom_panel()


def _flatbed_speedbox_top():
    from flatbed_cad.speedbox_panels import top_panel

    return top_panel()


def _flatbed_speedbox_left():
    from flatbed_cad.speedbox_panels import left_panel

    return left_panel()


def _flatbed_speedbox_right():
    from flatbed_cad.speedbox_panels import right_panel

    return right_panel()


def _flatbed_speedbox_front():
    from flatbed_cad.speedbox_panels import front_panel

    return front_panel()


def _flatbed_speedbox_rear():
    from flatbed_cad.speedbox_panels import rear_panel

    return rear_panel()


def _flatbed_speedbox_bulkhead():
    from flatbed_cad.speedbox_panels import motor_bulkhead

    return motor_bulkhead()


def _flatbed_speedbox_input_gear():
    from flatbed_cad.speedbox import input_gear

    return input_gear()


def _flatbed_speedbox_input_spacer():
    from flatbed_cad.speedbox import input_spacer

    return input_spacer()


def _flatbed_speedbox_output_gear():
    from flatbed_cad.speedbox import output_gear

    return output_gear()


def _flatbed_speedbox_output_spacer():
    from flatbed_cad.speedbox import output_spacer

    return output_spacer()


# name -> builder. All in their own local frames.
BREP_PARTS = {
    "flap": _flap,
    "holder": _holder,
    "drum-outer": _drum_outer,
    "drum-inner-byj": _drum_inner,
    "drum-inner-nema": _drum_inner_nema,
    "motor-byj": _motor_byj,
    "hall-pcb": _hall_pcb,
    "unit-plate": _unit_plate,
    "unit-nema-plate": _nema_plate,
    "bridge-nema": _nema_bridge,
    "ipad-body": _ipad_body,
    "ipad-lid": _ipad_lid,
    "grommet-usb": _grommet_usb,
    "grommet-bathroom": _grommet_bathroom,
    "poop-bucket": _poop_bucket,
    "mirror-spacer-straight": _mirror_spacer_straight,
    "mirror-spacer-arch": _mirror_spacer_arch,
    "mirror-spacer-corner": _mirror_spacer_corner,
    "unit-full": _full_unit,
    "unit-nema-full": _full_unit_nema,
    "blinds-sprocket": _blinds_sprocket,
    "blinds-sprocket-bevel": _blinds_sprocket_bevel,
    "blinds-sprocket-spacer": _blinds_sprocket_spacer,
    "blinds-frame": _blinds_frame,
    "blinds-cassette-lid": _blinds_cassette_lid,
    "blinds-sleeve": _blinds_sleeve,
    "blinds-cap-rear": _blinds_cap_rear,
    "blinds-cap-front": _blinds_cap_front,
    "blinds-motor": _blinds_motor,
    "blinds-pinion": _blinds_pinion,
    "blinds-layshaft-spur": _blinds_layshaft_spur,
    "blinds-layshaft-bevel": _blinds_layshaft_bevel,
    "blinds-drive-cassette": _blinds_drive_cassette,
    "blinds-drive-spacers": _blinds_drive_spacers,
    "gear-box-housing": _gearbox_housing,
    "gear-box-lid": _gearbox_lid,
    "gear-box-input-gear": _gearbox_input_gear,
    "gear-box-output-gear": _gearbox_output_gear,
    "gear-box-input-spacer": _gearbox_input_spacer,
    "gear-box-output-spacer": _gearbox_output_spacer,
    "gear-box-test-bushings": _gearbox_test_bushings,
    "gear-box-mesh-jig": _gearbox_mesh_jig,
    "gear-box-motor-housing": _gearbox_motor_housing,
    "gear-box-motor-lid": _gearbox_motor_lid,
    "gear-box-motor-input-spacer": _gearbox_motor_input_spacer,
    "gear-box-motor-output-spacer": _gearbox_motor_output_spacer,
    "nas-hdd": _nas_hdd,
    "nas-caddy": _nas_caddy,
    "nas-door": _nas_door,
    "nas-bay-frame": _nas_bay_frame,
    "flatbed-calibration-kit": _flatbed_calibration_kit,
    "flatbed-insert-test": _flatbed_insert_test,
    "flatbed-speedbox-motor": _flatbed_speedbox_motor,
    "flatbed-speedbox-bottom": _flatbed_speedbox_bottom,
    "flatbed-speedbox-top": _flatbed_speedbox_top,
    "flatbed-speedbox-left": _flatbed_speedbox_left,
    "flatbed-speedbox-right": _flatbed_speedbox_right,
    "flatbed-speedbox-front": _flatbed_speedbox_front,
    "flatbed-speedbox-rear": _flatbed_speedbox_rear,
    "flatbed-speedbox-bulkhead": _flatbed_speedbox_bulkhead,
    "flatbed-speedbox-input-gear": _flatbed_speedbox_input_gear,
    "flatbed-speedbox-input-spacer": _flatbed_speedbox_input_spacer,
    "flatbed-speedbox-output-gear": _flatbed_speedbox_output_gear,
    "flatbed-speedbox-output-spacer": _flatbed_speedbox_output_spacer,
}

FINGERPRINT_ONLY = {}

ALL_PARTS = {**BREP_PARTS, **FINGERPRINT_ONLY}


def fingerprint(part) -> dict:
    """Geometry invariants: cheap to compare, catch ~all accidents."""
    bb = part.bounding_box()
    com = part.center()
    return {
        "volume": part.volume,
        "area": part.area,
        "bbox_min": [bb.min.X, bb.min.Y, bb.min.Z],
        "bbox_max": [bb.max.X, bb.max.Y, bb.max.Z],
        "com": [com.X, com.Y, com.Z],
    }
