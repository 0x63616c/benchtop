"""Public contract for the removable 2S3P battery assembly.

The bought parts are two Bistook three-slot 21700 holders.  Each holder
mounts directly to the wall frame through its three moulded 4.2 mm holes;
there is no structural carrier PCB.
"""

import pytest


def test_two_owned_holders_match_the_supplied_plastic_envelope():
    from blinds_cad.cells21700 import holder_stack

    bounds = holder_stack().bounding_box()

    assert bounds.size.X == pytest.approx(83.00)
    assert bounds.size.Y == pytest.approx(14.51)
    assert bounds.size.Z == pytest.approx(136.18)
