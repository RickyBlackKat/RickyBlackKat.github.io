# KAT-5: printable 5" FPV freestyle quad

A parametric OpenSCAD frame designed to print on a **Bambu Lab P1P or P1S** in **PETG or PLA+**. The TPU accessories are optional.

![assembly](img/assembly.png)

| Spec | Value |
|---|---|
| Layout | True-X, 225 mm wheelbase (motor to motor, diagonal) |
| Props | 5" (up to 5.1") |
| Motors | 22xx/23xx with a 16×16 M3 bolt pattern (2207, 2306, 2306.5) |
| Flight stack | 30.5×30.5 M3 FC and ESC |
| FPV camera | 19 mm "micro" camera on an M2 pivot, tilt 0–40° |
| Plate gap | 30 mm (M3×30 standoffs) |
| Battery | Top-mounted, 4S/6S 1100–1500 mAh, two straps |
| Frame weight | Estimated 45–50 g in PETG at the settings below (62 g if printed solid, calculated from the STL volume) |
| Largest part | Unibody, 191×191×12 mm (the P1 bed is 256×256) |

## Parts (`stl/`)

| File | Qty | Material | Notes |
|---|---|---|---|
| `unibody.stl` | 1 | PETG / PLA+ | Bottom plate and arms in one piece. Print flat with the spines facing up. |
| `top_plate.stl` | 1 | PETG / PLA+ | Has the battery-strap slots and a GoPro strap slot. |
| `cam_mount.stl` | 1 | TPU 95A | Clamps under the two front standoffs. |
| `antenna_mount.stl` | 1 | TPU 95A | Clamps under the two rear standoffs. Holds the VTX SMA connector and two ELRS antenna tubes. |
| `gopro_mount.stl` | 1 | TPU 95A | 3-prong mount at a 20° tilt, strapped to the front of the top plate. |
| `standoff.stl` | 4 | PETG | Optional. M3×30 aluminium standoffs are stiffer and preferred. |

## Print settings (Bambu Studio)

**PETG / PLA+ parts (unibody, top plate):**
- 0.4 mm nozzle, 0.2 mm layers.
- **6 walls**, 5 top and 5 bottom layers. The walls carry the load, so don't skimp on them.
- 40% gyroid infill. The unibody ends up close to solid anyway.
- Print flat. Layer lines then run along the arms, which is the strong direction for crash loads.
- Use a textured PEI plate, no supports and no brim.
- PETG: 245 °C nozzle, 70 °C bed, part fan at about 40%. PLA+: 215 °C nozzle, 55 °C bed.

**TPU parts:**
- 0.2 mm layers, 3 walls, 25% infill, about 3 mm³/s maximum volumetric speed.
- On the P1S, feed the TPU from the external spool holder, not the AMS.
- Supports: none for the camera and antenna mounts. Tree supports under the GoPro prongs are optional.

## Hardware

- 16× M3×8 screws for the motors. **Check that the screw tips don't touch the motor windings.** Use 4 mm of thread into the motor at most.
- 4× M3×30 standoffs, plus 8× M3×8 screws to fix them to the plates.
- 4× M3×20–25 screws and nylon nuts for the stack, with soft-mount grommets.
- 2× M2×6 screws for the camera pivot.
- 1× M5 GoPro thumbscrew.
- 2× 20 mm battery straps, a grippy battery pad, and zip ties for the motor wires (there are slots in each arm).

## Assembly

1. Bolt the motors to the arm pads, with the screw heads underneath. Run the motor wires along the arm spine and zip-tie them through the arm slots.
2. Mount the ESC and FC on the 30.5 mm stack holes with soft-mount grommets.
3. Put the TPU camera mount over the front standoff holes and the antenna mount over the rear ones. Then screw the standoffs down through them.
4. Fit the camera between the cradle walls with the two M2 pivot screws. Set the tilt to about 25–35° for freestyle. The TPU walls hold the angle by friction.
5. Fit the VTX SMA connector through the rear tab, then push the ELRS antenna leads into the two angled tubes.
6. Bolt on the top plate and strap the GoPro mount to its front slot. The battery goes behind it, held by two straps.

## Change the design

Every dimension is a parameter at the top of `kat5.scad`: wheelbase, plate thickness, spine height, motor pattern, standoff height, camera size and so on. To re-export a part:

```sh
openscad -D 'part="unibody"' -o stl/unibody.stl kat5.scad
```

Useful changes:
- **3" build:** set `wheelbase = 140`, `prop_d = 76`, `motor_spacing = 12`, `motor_hole_d = 2.2`, `stack_spacing = 20` and `stack_hole_d = 2.2`. Shrink the body to fit.
- **Stiffer arms:** raise `rib_h_root` to 10–12, or `plate_t` to 5. The model is designed for PETG, which is about 10× less stiff than carbon fibre, so the arm spines provide most of the stiffness.
- **More camera room:** increase `standoff_h`.

## Honest limitations

- **Stiffness:** a printed frame will never be as stiff as a carbon fibre one. Expect to lower the D-term and add filtering in Betaflight if you see oscillation. Check the gyro trace with Blackbox before you push the PIDs.
- **Crashes:** printed arms break where carbon fibre would only scratch. Print a spare unibody to keep on hand.
- **PLA:** plain PLA softens in summer heat and on warm motor mounts. Use PETG, or PLA+ at the very least.
