# KAT-5 stability and structure check

Mass properties come from the actual CAD meshes. Each printed part was exported in its assembled position, and its volume, centre of gravity and inertia were integrated at its printed density (PETG at 92% fill for the arms and plates). Bought parts and hardware use their published weights at their mounted positions. The script is `tools/stab.py`; drawing sheet 9 summarises the results.

## Balance

The thrust centre is the geometric centre of the four motors.

| Setup | All-up weight | CG fore/aft (+ = forward) | CG height | Motor-load imbalance | Tip-over angle |
|---|---|---|---|---|---|
| A: as drawn (battery at rear, GoPro mount fitted, no camera) | 631 g | −7.9 mm | 33.2 mm | ±9.6% | 69° |
| **B: no action camera, GoPro mount removed, battery slid forward** | **628 g** | **−0.8 mm** | 33.1 mm | **±1.0%** | 70° |
| C: full-size GoPro HERO (154 g) on the mount, battery at rear | 785 g | +1.5 mm | 43.7 mm | ±1.8% | 64° |
| D: stripped "naked" GoPro (30 g), battery at rear | 661 g | −5.7 mm | 35.6 mm | ±7.0% | 68° |

- **Battery position.** Without an action camera, leave the GoPro mount off and slide the battery forward until its front edge is flush with the front of the top plate (setup B). With a full GoPro, keep the battery at the rear (setup C). Both are balanced to within about 1.5%.
- **Naked GoPro (setup D).** The rear motors work about 7.5% harder. ArduPilot copes with that, but it costs some headroom. Either accept it or add a few grams of nose weight.
- **CG height.** The CG sits 5.6 mm above the prop plane in setup B. That's normal for a top-mounted battery and has no effect on an actively stabilised quad.
- **Landing stability.** The quad would have to tilt 64–70° before tipping over on landing.

## Thrust

- **Hover:** about 157 g per motor in setup B.
- **Measured data point:** one retailer test table gives 1,021 g per motor at 60% throttle on 24 V with a 5.1" prop. That's about 6.5:1 thrust-to-weight at 60% throttle, so the quad has plenty of thrust.
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
