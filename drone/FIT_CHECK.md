# KAT-5 fit check

Every recommended part was modelled at its published size and placed where it mounts in `kat5.scad` (`comp()` module). OpenSCAD then intersected it with every frame part it could touch (`placed()` module). Next it grew each part by 0.5, 1, 2, 3 and 5 mm on every side and tested again. The gap reported is the largest growth that still showed no overlap. The script is `tools/fit.py`, and the full report is sheet 7 of the drawings.

## Part sizes used

| Part | Model | Size (mm) | Source |
|---|---|---|---|
| Flight controller | SpeedyBee F405 V4 | 41.6 × 39.4 × 7.8 | Retailer specs |
| ESC 4-in-1 | SpeedyBee BLS 55A | 45.6 × 44 × 8 | Retailer specs |
| Stack height | FC + ESC + grommets | 18.3 | SpeedyBee manual |
| VTX | SpeedyBee TX800 | 28 × 28 board, 20 × 20 mount, 5.5 thick (thickness assumed) | Retailer specs |
| Camera | Caddx Ratel 2 | 19 × 19 × 20 | Retailer specs |
| Motor | iFlight XING2 2207 | Ø29.08 × 19.1, 16 × 16 M3 | Retailer specs |
| Prop | 5.1" tri-blade | Ø129.5 | Nominal |
| Battery | Tattu R-Line V5 6S 1200 | 78 × 40 × 34 | Retailer specs |
| GPS | Matek M10Q-5883 | 20 × 20 × 12.4 | Retailer specs |
| Receiver | Radiomaster RP1 V2 | 13 × 11 × 3 | Radiomaster |
| XT60 female | Amass XT60 | 15.8 × 8.2 × 16 | Common size; **not confirmed from a datasheet** |

## Problems found and fixed in this revision

1. **ESC didn't fit.** The 45.6 mm ESC didn't fit inside the 42 mm body (39.6 mm inside the canopy). The body is now 50 mm wide, with 10 mm corner radii.
2. **Battery didn't fit.** A 78 mm battery didn't fit in the 76.5 mm space between the GoPro mount and the GPS tower. The tower moved back 4 mm, giving an 80.5 mm bay, and the strap slots moved out to 43 mm apart.
3. **The VTX had nowhere to mount.** A 20 × 20 mm VTX plate now sits on top of the stack.
4. **The GPS platform intruded into its own pocket.** The platform stood 1 mm into the GPS pocket; it's fixed.
5. **The motor wires had no way out of the canopy.** Four exits are now cut at the corners.
6. **Bolt holes now Ø3.4 (were Ø3.3).** This leaves positional tolerance for two printed parts on one bolt; see drawing sheet 8.
7. **Canopy height now 31.6 mm (was 32).** The canopy can no longer hold the top plate off the standoffs.
8. **Stiffer arms.** A 5 mm plate and a 14 mm spine give about 8 mm of clearance under the props. See [STABILITY.md](STABILITY.md).
9. **Prop-tip margin.** The wheelbase grew from 225 to 230 mm, giving 5.6 mm of prop-tip clearance with 5.1" props.

## Results

| Interface | Min. gap (mm) | Result |
|---|---|---|
| ESC ↔ canopy wall | 1.0 | Pass |
| FC ↔ canopy wall | 3.0 | Pass |
| VTX ↔ top plate | 2.7 | Pass |
| VTX plate ↔ FC | 2.4 | Pass (sits on stack nuts) |
| Camera ↔ cradle walls | 0.2 per side | Snug (intended friction fit) |
| Camera ↔ FC (at 30° tilt) | ≥ 2 | Pass |
| Motor bell ↔ arm spine | 2.5 | Pass |
| Prop tip ↔ body / canopy | 5.6 | Pass |
| Prop ↔ antenna mount | ≥ 3 | Pass |
| Prop ↔ tower, GoPro mount, plates | ≥ 5 | Pass |
| Battery ↔ GoPro mount / tower | 1.25 each end | Pass |
| GPS ↔ pocket | 0.3 per side | Snug |
| XT60 ↔ pocket | 0.25 per side | Snug, held by a zip tie |

## Limits

- **Part sizes:** they come from retailer listings. Measure your actual parts and print `test_coupon.stl` first.
- **Assumed sizes:** the VTX thickness and the XT60 length are assumptions.
- **Not modelled:** wires, solder joints, connectors and capacitors.
