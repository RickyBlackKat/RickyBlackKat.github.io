# KAT-5 stability and structure check

Mass properties come from the actual CAD meshes (rechecked after the arm, canopy and feet changes). Each printed part was exported in its assembled position, and its volume, centre of gravity and inertia were integrated at its printed density (PETG at 92% fill for the arms and plates). Bought parts and hardware use their published weights at their mounted positions. The script is `tools/stab.py`; drawing sheet 9 summarises the results.

## Weight (setup B, rechecked)

Every printed part was re-exported from the current CAD in its assembled position. Each one matched its print-ready STL to within 0.05 cm³. Bought parts use published weights; bolt heads, nuts and wiring are placed where they actually sit. Positions are measured from the frame centre: y is positive forward, and z is height above the arm underside (the ground is 8 mm lower, under the feet).

| Item | Type | Mass (g) | y (mm) | z (mm) | Source |
|---|---|---|---|---|---|
| Battery 6S 1200 (Tattu R-Line V5) | bought | 197.0 | +7 | 62 | retailer spec 197 g ±20 |
| Motor XING2 2207 | bought | 126.4 | +0 | 15 | retailer spec 31.6 g incl. wires |
| Arms (4), PETG | printed | 78.8 | +0 | 4 | CAD volume × print density |
| ESC SpeedyBee BLS 55A | bought | 23.5 | +0 | 13 | retailer spec 23.5 g |
| Canopy, PETG | printed | 20.7 | +3 | 26 | CAD volume × print density |
| Centre plate, PETG | printed | 16.0 | +0 | 6 | CAD volume × print density |
| Top plate, PETG | printed | 15.4 | -7 | 42 | CAD volume × print density |
| Prop Gemfan 51433 | bought | 15.2 | +0 | 28 | retailer spec 3.8 g |
| Battery straps x2 (Lumenier 20x250) | hardware | 15.0 | +7 | 62 | retailer spec 7.5 g each |
| FC SpeedyBee F405 V4 | bought | 10.5 | +0 | 22 | retailer spec 10.5 g |
| Arm bolts M3x12 + nylock | hardware | 10.4 | -0 | 1 | steel, ~1.3 g each |
| Stack bolt M3x35 + nylock | hardware | 9.2 | -0 | 16 | steel, ~2.3 g |
| Motor screws M3x8 (4) | hardware | 8.8 | +0 | -0 | steel, ~0.55 g each |
| Landing feet (4), TPU | printed | 8.5 | -0 | -3 | CAD volume × print density |
| GPS Matek M10Q-5883 | bought | 8.0 | -69 | 74 | retailer spec 8 g |
| XT60 + 12AWG pigtail | bought | 8.0 | -76 | 49 | estimate |
| VTX antenna (SMA) + MMCX pigtail | bought | 8.0 | -55 | 28 | estimate |
| GPS/XT60 tower, PETG | printed | 7.4 | -69 | 56 | CAD volume × print density |
| Wires, solder, heat-shrink, ties | hardware | 7.0 | +0 | 16 | estimate |
| Foot bolt M3x20 + nylock | hardware | 6.2 | +0 | 6 | steel, ~1.55 g |
| Prop nut M5 | hardware | 6.0 | +0 | 32 | estimate |
| Camera Caddx Ratel 2 | bought | 5.9 | +37 | 22 | retailer spec 5.9 g |
| VTX SpeedyBee TX800 | bought | 5.6 | +0 | 35 | retailer spec 5.6 g |
| Capacitor 35V 1000uF | bought | 5.0 | -28 | 12 | estimate |
| Standoff M3x30 | hardware | 5.0 | +0 | 25 | retailer spec 1.25 g |
| Standoff screws M3x8 (2) | hardware | 4.4 | +0 | 24 | steel, ~0.55 g each |
| Grommets + camera M2 screws | hardware | 3.0 | +0 | 18 | estimate |
| Battery pad | hardware | 3.0 | +7 | 44 | estimate |
| Tower bolts M3x10 + nylock | hardware | 2.3 | -58 | 45 | steel |
| Antenna mount, TPU | printed | 2.2 | -46 | 16 | CAD volume × print density |
| Receiver RP1 | bought | 2.2 | -30 | 20 | manufacturer 2.2 g incl. antenna |
| VTX plate, PETG | printed | 2.1 | -0 | 30 | CAD volume × print density |
| Camera mount, TPU | printed | 1.5 | +37 | 15 | CAD volume × print density |
| **Total** | | **648** | | | printed 153 g · bought 415 g · hardware 80 g |

**Uncertainty.**
- **Battery:** the 6S 1200 pack is listed at 197 g ±20 g, which moves the CG by less than 0.3 mm.
- **Printed parts:** these are ±10% depending on your infill and walls, about ±15 g in total.

## Balance

The thrust centre is the geometric centre of the four motors (the middle of the stack). The tip-over angle is how far the quad can tilt on its feet before it falls over.

| Setup | All-up weight | CG fore/aft (+ = forward) | CG height above ground | Motor-load imbalance | Tip-over angle |
|---|---|---|---|---|---|
| A: as drawn (battery at rear, GoPro mount fitted, no camera) | 651 g | -8.1 mm | 40.1 mm | ±9.9% | 56° |
| **B: no action camera, GoPro mount removed, battery front edge flush with the top plate** | 648 g | -1.3 mm | 40.0 mm | ±1.5% | 59° |
| C: full-size GoPro HERO (154 g) on the mount, battery at rear | 805 g | +1.1 mm | 50.6 mm | ±1.4% | 53° |
| D: stripped "naked" GoPro (30 g), battery at rear | 681 g | -6.0 mm | 42.5 mm | ±7.3% | 56° |
| B + Remote ID (15 g, assumed) on the GPS tower | 663 g | -2.8 mm | 40.6 mm | ±3.4% | 58° |
| **B + Remote ID (15 g, assumed) strapped on the front of the battery** | 663 g | -0.6 mm | 41.1 mm | ±0.7% | 59° |

**What to do:**
- **No action camera (setup B).** Leave the GoPro mount off and slide the battery forward until its front edge is flush with the front of the top plate. That puts the CG 1.3 mm behind centre, a 1.5% imbalance. For a perfect balance, let the pack overhang the front edge by about 4 mm: every 10 mm you move the battery shifts the CG by 3 mm.
- **Remote ID (required in the US).** Strap the module on top of the front of the battery, under the same straps. That brings the CG to 0.6 mm (0.7% imbalance) and gives the module's GPS a clear sky view. Mounted at the back on the GPS tower instead, it pulls the CG back to 2.8 mm (3.4%).
- **Full-size GoPro (setup C).** Keep the battery at the rear; the camera balances it (1.4%).
- **Naked GoPro (setup D).** The rear motors work 7% harder. ArduPilot copes, but it costs some headroom.
- **Check it on the real quad.** Balance it on two fingertips placed under the middle of the front and rear arm pairs, battery fitted. It should sit level. If the tail drops, slide the battery forward.

## Thrust

- **Hover:** about 162 g per motor in setup B.
- **Measured data point:** one retailer test table gives 1,021 g per motor at 60% throttle on 24 V with a 5.1" prop. That's about 6.3:1 thrust-to-weight at 60% throttle.
- **Maximum:** about 1.6 kg per motor is my estimate, not a measured figure.

## Arms

I modelled each arm as a cantilever clamped at the edge of the centre plate (radius 41 mm) and loaded at the motor (radius 116 mm). Material: PETG with E = 1.8 GPa in the print plane and yield ≈ 40 MPa (Prusa and Ultimaker datasheets).

| | Previous arm (4 mm plate, 8 mm spine) | **Current arm (5 mm plate, 14 mm spine)** |
|---|---|---|
| Stiffness at the motor | 9 N/mm | **33 N/mm** |
| First bending mode, with motor | **75 Hz** ❌ | **≈ 140 Hz** |
| Tip deflection, hover / 60% / max | 0.16 / 1.10 / 1.73 mm | 0.05 / 0.31 / 0.48 mm |
| Peak stress at max thrust | 12 MPa | 4.6 MPa (safety factor ≈ 9) |

At 75 Hz, the old arm vibrated right in the band where the flight controller's filters do their work, and below the motors' rotation frequency at hover. I made the arm thicker (5 mm) and gave it a taller, wider spine. It now weighs about 4 g more per arm.

- **Screw changes.** A 1 mm counterbore under each motor screw keeps M3×8 screws at 4 mm of thread in the motor. The arm bolts are now M3×12.
- **Expect a lower real frequency.** The clamp and the plate flex, and printed PETG varies. After the first hover, log the FFT (`INS_LOG_BAT_MASK`) and look for a peak around 110–150 Hz.
  - Use ArduPilot's RPM-based harmonic notch (bidirectional DShot on Bluejay) to handle motor noise.
  - If an arm peak shows up, add a static notch at that frequency.
- **Not modelled.** Crash loads, fatigue, arm torsion, and how much the plate itself flexes.
