// =====================================================================
//  KAT-5  —  5" FPV freestyle quad, designed for FDM printing (PETG/PLA+)
//  Fits a Bambu Lab P1P / P1S (256 x 256 x 256 mm build volume)
//
//  Units: millimetres. Origin = frame centre, +Y = forward (camera side),
//  Z = 0 is the underside of the arms.
//
//  Stack-up (bottom → top): 4 bolt-on arms → centre plate → TPU mount bases
//  → 30 mm standoffs (inside the canopy) → top plate → GPS/XT60 tower.
//
//  Render a single part:  openscad -D 'part="arm"' -o arm.stl kat5.scad
//
//  Parts:
//    "assembly"      – everything with dummy motors/props/stack (preview only)
//    "arm"           – bolt-on arm, print 4 (+ spares)            (PETG / PLA+)
//    "bottom_plate"  – centre plate the arms bolt under          (PETG / PLA+)
//    "top_plate"     – top plate, battery-strap slots, rear tab  (PETG / PLA+)
//    "canopy"        – shell between the plates                  (PETG / PLA, or TPU)
//    "gps_xt60_mount"– XT60 holder with GPS platform on top      (PETG)
//    "cam_mount"     – 19 mm micro FPV camera cradle             (TPU 95A)
//    "antenna_mount" – rear VTX SMA + ELRS antenna holder        (TPU 95A)
//    "gopro_mount"   – 3-prong action-cam mount, 20° tilt        (TPU 95A)
//    "vtx_plate"     – 20x20 VTX mount that sits on the 30.5 stack (PETG)
//    "test_coupon"   – 10-minute fit test: motor, stack, M2, camera, XT60, GPS (PETG)
//    "standoff"      – optional printed standoff (does NOT fit inside the canopy)
// =====================================================================

part = "assembly";

$fn = 64;

// ---------------- Main geometry --------------------------------------
wheelbase      = 230;          // motor-to-motor diagonal (5.5 mm prop-tip clearance at 5.1")
prop_d         = 129.5;        // 5.1" props (preview / clearance)

arm_t          = 5;            // arm plate thickness (stiffness: first bending mode ~145 Hz)
plate_t        = 3;            // centre (bottom) plate thickness
top_t          = 3;            // top plate thickness
standoff_h     = 30;           // M3 x 30 standoffs
tpu_base_t     = 2;            // TPU accessory bases under the standoffs

body_w         = 50;           // centre body width (X): fits a 45.6 mm ESC inside the canopy
body_l         = 92;           // centre body length (Y)
body_r         = 10;           // large corner radius keeps prop tips clear
fillet_r       = 6;            // inside-corner fillets on plates and arms

// Arms
arm_root_d     = 22;           // width of the arm root paddle
paddle_r0      = 14;           // paddle runs from this radius...
paddle_r1      = 30;           // ...to this one (bolted under the plate)
arm_w_tip      = 15;
arm_bolt_r     = 31;           // two side-by-side M3 bolts at this radius
arm_bolt_off   = 6;            //   ±6 mm either side of the arm centreline
spine_w_top    = 6;            // stiffening spine on top of each arm
spine_w_base   = 10;            //   flared base (acts as a fillet)
spine_h_start  = 8;
spine_h_peak   = 14;
spine_h_tip    = 5;

// Motor mount (16 x 16 M3)
motor_pad_d    = 32;
motor_spacing  = 16;
motor_hole_d   = 3.4;           // M3 clearance (FDM holes print ~0.1 undersize)
motor_shaft_d  = 7.5;
bell_clear_r   = 17;

// Flight stack (30.5 x 30.5 M3) — the stack bolts also hold the arms
stack_spacing  = 30.5;
stack_hole_d   = 3.4;

// Standoffs (M3)
so_x           = 16;
so_y           = 40;
so_hole_d      = 3.4;

// Camera
cam_w          = 19;
cam_pivot_y    = 37;
cam_pivot_z    = 14;           // pivot height above the centre plate

// Battery straps
strap_w        = 22;
strap_t        = 3.5;
strap_x        = 21.5;         // slots 43 mm apart, at the edges of a 38–40 mm pack
strap_y        = 15;

// GPS / XT60 tower
gps_size       = 20;           // GPS module width (Matek M10Q-5883 = 20 x 20 x 12.4)
tower_hole_y   = -58;          // M3 holes in the top-plate rear tab

// Derived
motor_r   = wheelbase / 2;
motor_xy  = motor_r / sqrt(2);
stack_r   = stack_spacing / 2 * sqrt(2);
paddle_end = paddle_r1 + arm_root_d/2;     // where the plate lobe ends
arm_angles = [45, 135, 225, 315];
plate_z   = arm_t;                         // underside of the centre plate
plate_top = arm_t + plate_t;
top_z     = plate_top + tpu_base_t + standoff_h;   // underside of the top plate

// ---------------- Helpers --------------------------------------------
module closing(r) offset(r=-r) offset(r=r) children();   // rounds inside corners
module body_2d() offset(body_r) square([body_w - 2*body_r, body_l - 2*body_r], center=true);
module hole_at(p, d, h=100) translate([p[0], p[1], -1]) cylinder(d=d, h=h);
module standoff_holes(d=so_hole_d) for (sx=[-1,1], sy=[-1,1]) hole_at([sx*so_x, sy*so_y], d);
module paddle_2d() hull() { translate([paddle_r0,0]) circle(d=arm_root_d); translate([paddle_r1,0]) circle(d=arm_root_d); }
// Arm root holes in arm-local coordinates (arm along +X)
module arm_root_holes() {
    hole_at([stack_r, 0], stack_hole_d);
    for (s=[-1,1]) hole_at([arm_bolt_r, s*arm_bolt_off], 3.4);
}

// ---------------- Bolt-on arm (local: along +X, bottom at Z=0) ------
module arm_2d() closing(5) union() {
    paddle_2d();
    hull() { translate([paddle_r1,0]) circle(d=arm_root_d); translate([motor_r,0]) circle(d=arm_w_tip); }
    translate([motor_r,0]) circle(d=motor_pad_d);
}
module arm_spine() {
    r0 = paddle_end; r1 = motor_r - bell_clear_r; rp = r0 + 9;
    module sec(r, h, wb) hull() {
        translate([r, -wb/2, arm_t-0.01]) cube([0.1, wb, 0.01]);
        translate([r, -spine_w_top/2, arm_t-0.01]) cube([0.1, spine_w_top, h]);
    }
    hull() { sec(r0, spine_h_start, spine_w_base); sec(rp, spine_h_peak, spine_w_base);
             sec(r1, spine_h_tip, spine_w_base - 2); }
}
module arm() {
    difference() {
        union() { linear_extrude(arm_t) arm_2d(); arm_spine(); }
        arm_root_holes();
        translate([motor_r,0,0]) {
            for (sx=[-1,1], sy=[-1,1]) hole_at([sx*motor_spacing/2, sy*motor_spacing/2], motor_hole_d);
            // 1 mm counterbores under the motor screws: M3x8 keeps 4 mm of thread in the motor
            for (sx=[-1,1], sy=[-1,1]) translate([sx*motor_spacing/2, sy*motor_spacing/2, -1]) cylinder(d=6, h=2);
            hole_at([0,0], motor_shaft_d);
        }
        // zip-tie slots for the motor wires, either side of the spine
        for (r=[58, 82], s=[-1,1]) translate([r, s*(spine_w_base/2 + 2.6), -1])
            linear_extrude(arm_t + 2) square([3.2, 1.8], center=true);
    }
}

// ---------------- Centre (bottom) plate -----------------------------
module bottom_plate_2d() closing(fillet_r) union() {
    body_2d();
    for (a = arm_angles) rotate(a) paddle_2d();
}
module bottom_plate() {
    difference() {
        linear_extrude(plate_t) bottom_plate_2d();
        for (sx=[-1,1], sy=[-1,1]) hole_at([sx*stack_spacing/2, sy*stack_spacing/2], stack_hole_d);
        for (a = arm_angles) rotate(a) arm_root_holes();
        standoff_holes();
        for (sy=[-1,1]) translate([0, sy*27, -1]) linear_extrude(plate_t+2) offset(2) square([12,2], center=true);
        hole_at([0,0], 14);
    }
}

// ---------------- Top plate -----------------------------------------
module top_plate_2d() closing(4) union() {
    body_2d();
    translate([0, -body_l/2 - 11]) offset(4) square([28-8, 18-8], center=true);  // rear tab for the GPS/XT60 tower
}
module top_plate() {
    difference() {
        linear_extrude(top_t) top_plate_2d();
        standoff_holes();
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*strap_x, sy*strap_y, -1]) linear_extrude(top_t+2)
                offset(strap_t/2 - 0.01) square([0.02, strap_w - strap_t], center=true);
        translate([0, 29, -1]) linear_extrude(top_t+2) offset(1.5) square([16, 0.5], center=true);  // GoPro strap
        translate([0, -6, -1]) linear_extrude(top_t+2) offset(3) square([10, 22], center=true);     // wire pass
        for (sx=[-1,1]) hole_at([sx*8, tower_hole_y], 3.4);
    }
}

// ---------------- Canopy (between the plates) -----------------------
canopy_wall = 1.2;
canopy_gap  = 0.4;                         // tolerance: canopy must stay shorter than the standoff + TPU-base stack
canopy_h    = top_z - plate_top - canopy_gap;   // 31.6 mm
module canopy() {      // local: Z = 0 sits on the centre plate
    difference() {
        linear_extrude(canopy_h) difference() { body_2d(); offset(delta=-canopy_wall) body_2d(); }
        // camera window (front) and antenna / battery-lead opening (rear)
        translate([-14, body_l/2 - 8, 3]) cube([28, 10, canopy_h - 6]);
        translate([-17.5, -body_l/2 - 2, 3]) cube([35, 10, canopy_h - 6]);
        // notches over the TPU camera / antenna bases
        translate([-20.4, 30.6, -1]) cube([40.8, 16, tpu_base_t + 1.4]);
        translate([-20.4, -46.4, -1]) cube([40.8, 12.8, tpu_base_t + 1.4]);
        // motor-wire exits at the four corners, level with the ESC pads
        for (sx=[-1,1], sy=[-1,1]) translate([sx*(body_w/2 - 4), sy*(body_l/2 - 28), 0]) cube([16, 14, 18], center=true);
        // USB access, both sides
        translate([-30, -8, 8]) cube([60, 16, 12]);
        // slanted cooling vents, rear half
        for (y=[-34, -26, -18], s=[-1,1])
            translate([s*body_w/2, y, canopy_h/2]) rotate([25,0,0]) cube([4, 3, 16], center=true);
        // engraved name
        translate([body_w/2 - 0.6, 15, canopy_h/2 - 3]) multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
            linear_extrude(1) text("KAT-5", size=6, font="Liberation Sans:style=Bold");
        mirror([1,0,0]) translate([body_w/2 - 0.6, 37, canopy_h/2 - 3])
            multmatrix([[0,0,1,0],[-1,0,0,0],[0,1,0,0],[0,0,0,1]])
            linear_extrude(1) text("KAT-5", size=6, font="Liberation Sans:style=Bold");
    }
}

// ---------------- GPS + XT60 tower (local: Z = 0 on top-plate top) --
module gps_xt60_mount() {
    y0 = -54.5; y1 = -84;                 // front / rear (80.5 mm battery bay ahead of it)
    bw = 22; px = gps_size + 0.6;          // box width, GPS pocket
    difference() {
        union() {
            translate([-14, tower_hole_y - 6, 0]) cube([28, 10, 2.5]);        // base on the tab
            translate([-bw/2, y1, 0]) cube([bw, y0 - y1, 13]);                // XT60 box
            for (s=[-1,1]) translate([s*(bw/2 - 1.25) - 1.25, y1, 0]) cube([2.5, y0 - y1, 24.5]);  // posts (stop below the GPS floor)
            translate([-(px/2 + 1.5), y1, 23.5]) cube([px + 3, y0 - y1, 1.5]);  // GPS platform (floor at 25)
            difference() {                                                    // GPS rim
                translate([-(px/2 + 1.5), y1, 23.5]) cube([px + 3, y0 - y1, 4.5]);
                translate([-px/2, (y0+y1)/2 - px/2, 25]) cube([px, px, 10]);
            }
        }
        for (sx=[-1,1]) translate([sx*8, tower_hole_y, -1]) cylinder(d=3.4, h=10);
        // XT60 pocket: 16 x 8.2 mm body, mating face to the rear
        translate([-8.15, y1 - 1, 2]) cube([16.3, (y0 - y1) - 1, 8.5]);
        translate([-6, y0 - 3, 3.5]) cube([12, 5, 5.5]);                     // pigtail wires (front)
        // zip-tie slots: one round the XT60, two for the GPS
        translate([-15, (y0+y1)/2 - 1.5, 4]) cube([30, 3, 4.5]);
        for (sy=[y0 - 6, y1 + 6]) translate([-9, sy - 1.5, 20]) cube([18, 3, 10]);
    }
}

// ---------------- VTX plate (sits on top of the 30.5 mm stack) ------
vtx_hole = 20;                          // 20 x 20 mm VTX mount (SpeedyBee TX800: 28 x 28 board)
module vtx_plate() difference() {
    linear_extrude(1.6) offset(3) square(stack_spacing, center=true);
    for (sx=[-1,1], sy=[-1,1]) hole_at([sx*stack_spacing/2, sy*stack_spacing/2], stack_hole_d);
    for (sx=[-1,1], sy=[-1,1]) hole_at([sx*vtx_hole/2, sy*vtx_hole/2], 2.2);
    hole_at([0,0], 12);
    for (s=[-1,1]) translate([s*12.5, 0, -1]) linear_extrude(4) offset(1) square([2, 14], center=true);
}

// ---------------- Fit-test coupon (print this first, ~10 min) -------
// Checks the critical fits on your printer before the long prints:
// M3 holes on the 16x16 motor pattern + 7.5 shaft hole, two M3 holes at
// 30.5 mm (stack), an M2 hole, the 19.4 mm camera slot, the XT60 opening
// (16.3 x 8.5) and the GPS pocket (20.6 square).
module test_coupon() difference() {
    linear_extrude(2) offset(3) square([92, 40]);
    translate([14, 20, 0]) {
        for (sx=[-1,1], sy=[-1,1]) hole_at([sx*motor_spacing/2, sy*motor_spacing/2], motor_hole_d);
        hole_at([0,0], motor_shaft_d);
    }
    hole_at([32, 5], stack_hole_d); hole_at([32, 5 + stack_spacing], stack_hole_d);
    hole_at([40, 20], 2.2);
    translate([46, 10.3, -1]) cube([19.4, 19.4, 4]);                      // camera width
    translate([70, 4, -1]) cube([16.3, 8.5, 4]);                          // XT60 body
    translate([68.7, 16, -1]) cube([gps_size + 0.6, gps_size + 0.6, 4]);   // GPS pocket
}

// ---------------- Printed standoff (optional) -----------------------
module standoff() difference() {
    cylinder(d=8, h=standoff_h, $fn=6);
    translate([0,0,-1]) cylinder(d=2.6, h=standoff_h + 2);
}

// ---------------- Camera cradle (TPU) -------------------------------
cam_wall_t  = 3;
cam_wall_in = cam_w + 0.4;
module cam_mount() {   // local: Z = 0 on the centre plate
    difference() {
        union() {
            translate([-(so_x + 4), 31, 0]) cube([2*(so_x + 4), 46 - 31, tpu_base_t]);
            for (s=[-1,1]) translate([s*(cam_wall_in/2 + cam_wall_t/2), cam_pivot_y, 0]) hull() {
                translate([-cam_wall_t/2, -8, 0]) cube([cam_wall_t, 16, 1]);
                translate([0, 0, cam_pivot_z]) rotate([0,90,0]) cylinder(d=12, h=cam_wall_t, center=true);
            }
        }
        for (sx=[-1,1]) hole_at([sx*so_x, so_y], so_hole_d);
        translate([-cam_wall_in/2, 32, -1]) cube([cam_wall_in, 12.5, tpu_base_t + 2]);
        translate([0, cam_pivot_y, cam_pivot_z]) rotate([0,90,0]) cylinder(d=2.2, h=60, center=true);
    }
}

// ---------------- Antenna mount (TPU) -------------------------------
module antenna_mount() {
    difference() {
        union() {
            translate([-(so_x + 4), -46, 0]) cube([2*(so_x + 4), 12, tpu_base_t]);
            translate([-9, -46, 0]) cube([18, 3, 20]);
            for (s=[-1,1]) translate([s*13, -40, 0]) rotate([45,0,0]) cylinder(d=6.5, h=26);
        }
        for (sx=[-1,1]) hole_at([sx*so_x, -so_y], so_hole_d);
        translate([0, -44, 12]) rotate([90,0,0]) cylinder(d=6.6, h=10, center=true);
        for (s=[-1,1]) translate([s*13, -40, 0]) rotate([45,0,0]) translate([0,0,-5]) cylinder(d=2.4, h=40);
        translate([-50, -80, -20]) cube([100, 100, 20]);
    }
}

// ---------------- GoPro mount (TPU) ---------------------------------
gp_tilt = 20;
module gopro_mount() {
    difference() {
        union() {
            translate([-17, 0, 0]) cube([34, 20, 3]);
            hull() {
                translate([-8, 7, 0]) cube([16, 12, 3]);
                translate([0, 13, 12]) rotate([gp_tilt,0,0]) cube([15.4, 10, 2], center=true);
            }
            translate([0, 13, 12]) rotate([gp_tilt,0,0]) gopro_prongs();
        }
        translate([-12, 1.5, -1]) cube([24, 3, 5]);
        translate([0, 13, 12]) rotate([gp_tilt,0,0]) translate([0,0,9])
            rotate([0,90,0]) cylinder(d=5.3, h=30, center=true);
    }
}
module gopro_prongs() for (i=[-1,0,1]) translate([i*6.2, 0, 0]) hull() {
    translate([-1.5, -5, 0]) cube([3, 10, 1]);
    translate([0, 0, 9]) rotate([0,90,0]) cylinder(d=10, h=3, center=true);
}

// ---------------- Preview -------------------------------------------
module dummy_motor() { color("silver") cylinder(d=29.08, h=19.1); color("silver") translate([0,0,19.1]) cylinder(d=5, h=13.5); }
module dummy_prop()  color([0.2,0.6,1,0.25]) cylinder(d=prop_d, h=1);
module assembly(show_canopy=true) {
    for (a = arm_angles) color("dimgray") rotate(a) arm();
    color("gray") translate([0,0,plate_z]) bottom_plate();
    color("orange") translate([0,0,plate_top]) cam_mount();
    color("orange") translate([0,0,plate_top]) antenna_mount();
    for (sx=[-1,1], sy=[-1,1]) color("gold")
        translate([sx*so_x, sy*so_y, plate_top + tpu_base_t]) cylinder(d=5.5, h=standoff_h, $fn=6);
    color("green")     translate([0,0,plate_top + 1 + 4]) cube([45.6, 44, 8], center=true);
    color("darkgreen") translate([0,0,plate_top + 10.5 + 3.9]) cube([41.6, 39.4, 7.8], center=true);
    color("black") translate([0, cam_pivot_y, plate_top + cam_pivot_z]) rotate([25,0,0]) cube([19,20,19], center=true);
    if (show_canopy) color("steelblue") translate([0,0,plate_top]) canopy();
    color("dimgray") translate([0,0,top_z]) top_plate();
    color("orange") translate([0,26,top_z + top_t]) gopro_mount();
    color("dimgray") translate([0,0,top_z + top_t]) gps_xt60_mount();
    color("khaki") translate([0, -69.25, top_z + top_t + 25 + 6.2]) cube([20, 20, 12.4], center=true);
    color("yellow") translate([0, -75, top_z + top_t + 6.1]) cube([15.8, 16, 8.2], center=true);
    color("red") translate([0, -14.25, top_z + top_t + 17]) cube([40, 78, 34], center=true);
    color("darkgreen") translate([0,0,plate_top + 20.7]) vtx_plate();
    color("navy") translate([0,0,plate_top + 26.55]) cube([28,28,5.5], center=true);
    for (a = arm_angles) rotate(a) translate([motor_r, 0, arm_t]) { dummy_motor(); translate([0,0,21]) dummy_prop(); }
}

// ---------------- Fit check: frame parts in place + real components --
// Component sizes are published specs (see FIT_CHECK.md); `c` inflates a
// component by c mm on every side so a clearance can be tested.
module placed(n) {
    if (n=="arm") for (a = arm_angles) rotate(a) arm();
    if (n=="bottom_plate") translate([0,0,plate_z]) bottom_plate();
    if (n=="cam_mount") translate([0,0,plate_top]) cam_mount();
    if (n=="antenna_mount") translate([0,0,plate_top]) antenna_mount();
    if (n=="canopy") translate([0,0,plate_top]) canopy();
    if (n=="top_plate") translate([0,0,top_z]) top_plate();
    if (n=="gopro_mount") translate([0,26,top_z + top_t]) gopro_mount();
    if (n=="gps_xt60_mount") translate([0,0,top_z + top_t]) gps_xt60_mount();
    if (n=="vtx_plate") translate([0,0,plate_top + 20.7]) vtx_plate();
    if (n=="standoffs") for (sx=[-1,1], sy=[-1,1])
        translate([sx*so_x, sy*so_y, plate_top + tpu_base_t]) cylinder(d=6.35, h=standoff_h, $fn=6);
}
module cbox(size, c=0) cube([size[0]+2*c, size[1]+2*c, size[2]+2*c], center=true);
module comp(n, c=0) {
    if (n=="esc")     translate([0,0,plate_top + 5])     cbox([45.6, 44, 8], c);      // SpeedyBee BLS 55A
    if (n=="fc")      translate([0,0,plate_top + 14.4])  cbox([41.6, 39.4, 7.8], c);  // SpeedyBee F405 V4
    if (n=="vtx")     translate([0,0,plate_top + 26.55]) cbox([28, 28, 5.5], c);      // SpeedyBee TX800
    if (n=="camera")  translate([0, cam_pivot_y, plate_top + cam_pivot_z]) rotate([30,0,0]) {
        cbox([19, 20, 19], c);                                                       // Caddx Ratel 2
        translate([0, 10, 0]) rotate([-90,0,0]) cylinder(d=14 + 2*c, h=6 + c); }      // lens
    if (n=="motors")  for (a = arm_angles) rotate(a) translate([motor_r, 0, arm_t + 0.05 - c])
        cylinder(d=29.08 + 2*c, h=19.1 + 2*c);                                       // XING2 2207
    if (n=="props")   for (a = arm_angles) rotate(a) translate([motor_r, 0, arm_t + 20 - c])
        cylinder(d=prop_d + 2*c, h=10 + 2*c);                                        // 5.1" tri-blade envelope
    if (n=="battery") translate([0, -14.25, top_z + top_t + 2 + 17]) cbox([40, 78, 34], c);   // 6S 1200 (Tattu R-Line)
    if (n=="gps")     translate([0, -69.25, top_z + top_t + 25.05 + 6.2]) cbox([20, 20, 12.4], c); // Matek M10Q-5883
    if (n=="xt60")    translate([0, -76, top_z + top_t + 2 + 4.2]) {
        cbox([15.8, 16, 8.2], c);                                                    // XT60 body
        translate([0, 11.5, 0]) cbox([12, 7, 6], c); }                               // solder cups + wire
}
if (part == "fit_pair") intersection() { placed(fa); comp(fb, fc_); }
if (part == "fit_cc")   intersection() { comp(fa, fc_); comp(fb, 0); }
fa = ""; fb = ""; fc_ = 0;

// ---------------- Part selector -------------------------------------
if (part == "assembly")        assembly();
if (part == "assembly_open")   assembly(false);
if (part == "exploded") {
    for (a = arm_angles) color("dimgray") rotate(a) translate([25,0,-30]) arm();
    color("gray") translate([0,0,plate_z]) bottom_plate();
    color("orange") translate([0,0,plate_top + 20]) { cam_mount(); antenna_mount(); }
    color("steelblue") translate([0,0,plate_top + 50]) canopy();
    color("dimgray") translate([0,0,top_z + 70]) top_plate();
    color("orange") translate([0,26,top_z + top_t + 85]) gopro_mount();
    color("dimgray") translate([0,-25,top_z + top_t + 100]) gps_xt60_mount();
}
if (part == "arm")             arm();
if (part == "bottom_plate")    bottom_plate();
if (part == "top_plate")       top_plate();
if (part == "canopy")          canopy();
if (part == "gps_xt60_mount")  gps_xt60_mount();
if (part == "standoff")        standoff();
if (part == "vtx_plate")       vtx_plate();
if (part == "test_coupon")     test_coupon();
if (part == "cam_mount")       cam_mount();
if (part == "antenna_mount")   antenna_mount();
if (part == "gopro_mount")     gopro_mount();
