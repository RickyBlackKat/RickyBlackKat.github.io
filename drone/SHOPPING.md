# KAT-5 shopping list

> A printable, tickable version with QR-code links is in [`drawings/KAT-5_parts_list.pdf`](drawings/KAT-5_parts_list.pdf) ([PARTS_LIST.md](PARTS_LIST.md)).

Parts for the KAT-5 quad, chosen so the **radio, flight software, video ground station and charger carry over to the KAT-TR tilt-rotor**.

Prices are rough US street prices from late 2025, for planning only. Check current prices and stock before you buy. Product names are examples of the right class of part; any equivalent with the same specs fits the frame.

✈️ = carries over to the KAT-TR plane.

## 1. Frame (printed)

| Item | Spec | Qty | ≈ Price |
|---|---|---|---|
| PETG filament | 1 kg, any brand. The frame, canopy and tower use about 110 g, so there's plenty for spare arms. | 1 | $20 |
| TPU 95A filament | For the camera, antenna and GoPro mounts | 1 | $25 |
| Aluminium standoffs | M3 × 30 mm | 4 (buy 8) | $8 |
| M3 screw kit | M3 × 8 / 10 / 12 / 35 mm, plus about 20 nylock nuts. See the fastener list in [PARTS_LIST.md](PARTS_LIST.md) | 1 kit | $12 |
| M2 screws | M2 × 6 mm, for the camera pivot | 4 | (in kit) |
| Battery straps | 20 mm wide, non-slip | 2 (buy 4) | $8 |
| Battery pad | Grippy silicone or foam pad | 1 | $4 |

## 2. Power and flight

| Item | Spec / example | Qty | ≈ Price |
|---|---|---|---|
| Flight stack | **30.5 × 30.5 mm F405 or H743 FC with a 50–55 A 4-in-1 ESC that runs ArduPilot**, e.g. SpeedyBee F405 V4 stack. Check that your FC is on ArduPilot's supported-boards list. | 1 | $75–90 |
| Motors | 2207, **1750–1950 KV for 6S**, 16 × 16 mm M3 bolt pattern, e.g. iFlight XING2 2207 1855 KV (Ø29.1 × 19.1 mm). Use M3×8 screws; the supplied ones are too short. | 4 (+1 spare) | $90–110 |
| Props | 5.1" tri-blade, e.g. 5.1 × 3.6 × 3 | 6+ sets | $20 |
| Batteries | **6S 1100–1200 mAh LiPo**, XT60, **no larger than 78 × 40 × 34 mm** (e.g. Tattu R-Line V5 1200, CNHL Black 1100) | 3 | $100–130 |
| Capacitor | Low-ESR 35 V / 1000 µF (usually in the stack box) | 1 | – |
| GPS + compass | M10 GPS with compass, about 20 mm, e.g. Matek M10Q-5883 class. Needed for ArduPilot's position hold and return-to-home. It sits on the printed GPS/XT60 tower at the back of the top plate (up to 25 mm square). | 1 | $25–35 |

## 3. Radio control ✈️

| Item | Spec / example | Qty | ≈ Price |
|---|---|---|---|
| Handheld radio | **ExpressLRS 2.4 GHz**, e.g. Radiomaster Pocket (compact) or Boxer (full-size). Doubles as a USB joystick for the simulator. | 1 | $70–140 |
| Receiver | ExpressLRS 2.4 GHz nano with a T-antenna, e.g. Radiomaster RP1/RP2 | 1 | $15–20 |

## 4. Video to your laptop ✈️

Pick **one** option:

**Option A: analog (cheapest, lowest latency). Recommended for the quad.**

| Item | Spec / example | Qty | ≈ Price |
|---|---|---|---|
| FPV camera | 19 mm "micro" analog camera, e.g. Caddx Ratel 2 or RunCam Phoenix 2 | 1 | $30 |
| Video transmitter | 5.8 GHz, 25–800 mW, **20 × 20 mm mount, 5 V input**, e.g. SpeedyBee TX800 (28 × 28 mm board, MMCX→SMA pigtail included). Sits on the printed VTX plate. | 1 | $25–40 |
| VTX antenna | 5.8 GHz SMA, right-hand circular polarized | 1 | $10 |
| Laptop receiver | **5.8 GHz UVC USB receiver.** It shows up as a webcam, e.g. Skydroid UVC or Eachine ROTG02 | 1 | $25–45 |

**Option B: digital HD (OpenIPC). Better picture, and reused on the plane.**

| Item | Spec / example | Qty | ≈ Price |
|---|---|---|---|
| Air unit + camera | OpenIPC-based, e.g. RunCam WiFiLink class, or an SSC338Q board with an IMX415 camera | 1 | $100–150 |
| Laptop adapter | USB Wi-Fi with an RTL8812AU or RTL8812EU chip, supported by OpenIPC (check the current list) | 1 | $40–70 |
| Antennas | 5.8 GHz pair for the ground adapter | 1 set | $15 |

Option B's air unit is bigger than an analog VTX. Mount it on top of the stack and check that the 30 mm plate gap clears it.

## 5. Charging and safety ✈️

| Item | Spec / example | Qty | ≈ Price |
|---|---|---|---|
| Charger | AC/DC balance charger, 6S capable, ≥100 W (e.g. ToolkitRC M7AC, ISDT 608AC) | 1 | $60–90 |
| LiPo safe bag | Fire-resistant charging and storage bag | 1 | $15 |
| Battery checker | Cell voltage checker | 1 | $8 |

## 6. Legal (US) ✈️

| Item | Note | ≈ Price |
|---|---|---|
| FAA registration | Required over 250 g; the KAT-5 is about 500 g. Covers all your recreational drones. | $5 |
| TRUST test | Free online test | $0 |
| Remote ID module | Broadcast module (the quad's FC won't do Remote ID on its own). Moves to the plane later. | $40–60 |

## 7. Tools (if you don't have them)

| Item | Note | ≈ Price |
|---|---|---|
| Soldering iron | Temperature-controlled, 60 W+ (e.g. Pinecil) | $30–40 |
| Solder, flux, heat shrink | 63/37 leaded solder flows easiest | $15 |
| Smoke stopper | Fuse plug for the first power-up; saves the ESC if something's shorted | $10 |
| Multimeter | For continuity and short checks | $15 |
| Hex drivers | 1.5 / 2.0 / 2.5 mm, plus a prop nut wrench | $10 |
| Zip ties, double-sided tape, electrical tape | | $8 |

## Totals (approximate)

| Setup | ≈ Total |
|---|---|
| With analog video, including tools | **$650–800** |
| With digital video (OpenIPC), including tools | $750–950 |
| If you already have tools | Subtract about $90 |

About $250–350 of that (radio, video ground station, charger, Remote ID) is reused on the KAT-TR.

## Before you buy, check

- **Stack:** the flight controller is on ArduPilot's supported-boards list.
- **Motors:** they're 16 × 16 mm M3 mount and rated for 6S.
- **Camera:** it's 19 mm wide.
- **Batteries:** XT60 connector, 6S, and about 30–38 mm wide; the strap slots sit right at the edges of the pack (most 6S 1100–1300 packs are 33–35 mm).
- **Video transmitter:** 20 × 20 mm or 30.5 mm mount, with an SMA connector.
