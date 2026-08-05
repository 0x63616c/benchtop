# Flatbed calibration print

The first Flatbed model is a palm-scale calibration kit, not a box. It tests
the two interfaces that constrain the later motor-mount enclosure:

- three cross-lap pairs with **0.10, 0.20, and 0.30 mm total slot clearance**;
- M3 clearance holes at **3.2, 3.4, and 3.6 mm**;
- broad-face heat-set insert bores at **4.0, 4.2, and 4.4 mm**.

The variants run left-to-right or bottom-to-top from smallest to largest.
One, two, and three tiny witness holes identify the corresponding variant.

Print `flatbed-calibration-kit.stl` flat, with the same material, nozzle,
layer height, wall count, and slicer compensation intended for the motor
mount. Supports are not required. Before fitting an insert, measure its body
diameter and length: this coupon assumes a short M3 insert installed into a
broad face. Do not heat-set a near-4 mm insert into the edge of a 5 mm panel;
there is too little material around it for a dependable structural joint.

Record which lap pair pushes together firmly by hand without splitting, which
clearance hole admits the chosen M3 bolt, and which bore holds the insert
without bulging. Those three measured choices become named Flatbed parameters
before modeling the four-panel box.
