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
//    "standoff"      – optional printed standoff (does NOT fit inside the canopy)
// =====================================================================

part = "assembly";

$fn = 64;

// ---------------- Main geometry --------------------------------------
wheelbase      = 225;          // motor-to-motor diagonal
prop_d         = 127;          // 5" props (preview / clearance)

arm_t          = 4;            // arm plate thickness
plate_t        = 3;            // centre (bottom) plate thickness
top_t          = 3;            // top plate thickness
standoff_h     = 30;           // M3 x 30 standoffs
tpu_base_t     = 2;            // TPU accessory bases under the standoffs

body_w         = 42;           // centre body width  (X)
body_l         = 92;           // centre body length (Y)
body_r         = 6;
fillet_r       = 6;            // inside-corner fillets on plates and arms

// Arms
arm_root_d     = 22;           // width of the arm root paddle
paddle_r0      = 14;           // paddle runs from this radius...
paddle_r1      = 30;           // ...to this one (bolted under the plate)
arm_w_tip      = 15;
arm_bolt_r     = 31;           // two side-by-side M3 bolts at this radius
arm_bolt_off   = 6;            //   ±6 mm either side of the arm centreline
spine_w_top    = 4;            // stiffening spine on top of each arm
spine_w_base   = 8;            //   flared base (acts as a fillet)
spine_h_start  = 5;
spine_h_peak   = 8;
spine_h_tip    = 3;

// Motor mount (16 x 16 M3)
motor_pad_d    = 32;
motor_spacing  = 16;
motor_hole_d   = 3.3;
motor_shaft_d  = 7.5;
bell_clear_r   = 17;

// Flight stack (30.5 x 30.5 M3) — the stack bolts also hold the arms
stack_spacing  = 30.5;
stack_hole_d   = 3.3;

// Standoffs (M3)
so_x           = 16;
so_y           = 40;
so_hole_d      = 3.3;

// Camera
cam_w          = 19;
cam_pivot_y    = 37;
cam_pivot_z    = 14;           // pivot height above the centre plate

// Battery straps
strap_w        = 22;
strap_t        = 3.5;
strap_x        = 17;           // slots 34 mm apart, at the pack edges
strap_y        = 15;

// GPS / XT60 tower
gps_size       = 25;           // square GPS module (M10 class 20–25 mm)
tower_hole_y   = -54;          // M3 holes in the top-plate rear tab

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
    for (s=[-1,1]) hole_at([arm_bolt_r, s*arm_bolt_off], 3.3);
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
    translate([0, -body_l/2 - 7]) offset(4) square([28-8, 18-8], center=true);   // rear tab for the GPS/XT60 tower
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
        for (sx=[-1,1]) hole_at([sx*8, tower_hole_y], 3.3);
    }
}

// ---------------- Canopy (between the plates) -----------------------
canopy_wall = 1.2;
canopy_h    = top_z - plate_top;          // 32 mm
module canopy() {      // local: Z = 0 sits on the centre plate
    difference() {
        linear_extrude(canopy_h) difference() { body_2d(); offset(delta=-canopy_wall) body_2d(); }
        // camera window (front) and antenna / battery-lead opening (rear)
        translate([-14, body_l/2 - 8, 3]) cube([28, 10, canopy_h - 6]);
        translate([-17.5, -body_l/2 - 2, 3]) cube([35, 10, canopy_h - 6]);
        // notches over the TPU camera / antenna bases
        translate([-20.4, 30.6, -1]) cube([40.8, 16, tpu_base_t + 1.4]);
        translate([-20.4, -46.4, -1]) cube([40.8, 12.8, tpu_base_t + 1.4]);
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
    y0 = -50.5; y1 = -80;                 // front / rear of the tower
    bw = 22; px = gps_size + 0.6;          // box width, GPS pocket
    difference() {
        union() {
            translate([-14, tower_hole_y - 6, 0]) cube([28, 10, 2.5]);        // base on the tab
            translate([-bw/2, y1, 0]) cube([bw, y0 - y1, 13]);                // XT60 box
            for (s=[-1,1]) translate([s*(bw/2 - 1.25) - 1.25, y1, 0]) cube([2.5, y0 - y1, 26]);  // posts
            translate([-(px/2 + 1.5), y1, 23.5]) cube([px + 3, y0 - y1, 2.5]);  // GPS platform
            difference() {                                                    // GPS rim
                translate([-(px/2 + 1.5), y1, 23.5]) cube([px + 3, y0 - y1, 4.5]);
                translate([-px/2, (y0+y1)/2 - px/2, 25]) cube([px, px, 10]);
            }
        }
        for (sx=[-1,1]) translate([sx*8, tower_hole_y, -1]) cylinder(d=3.3, h=10);
        // XT60 pocket: 16 x 8.2 mm body, mating face to the rear
        translate([-8.15, y1 - 1, 2]) cube([16.3, (y0 - y1) - 1, 8.5]);
        translate([-6, y0 - 3, 3.5]) cube([12, 5, 5.5]);                     // pigtail wires (front)
        // zip-tie slots: one round the XT60, two for the GPS
        translate([-15, -68, 4]) cube([30, 3, 4.5]);
        for (sy=[-55, -75.5]) translate([-9, sy - 1.5, 20]) cube([18, 3, 10]);
    }
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
module dummy_motor() { color("silver") cylinder(d=28, h=18); color("silver") translate([0,0,18]) cylinder(d=5, h=12); }
module dummy_prop()  color([0.2,0.6,1,0.25]) cylinder(d=prop_d, h=1);
module assembly(show_canopy=true) {
    for (a = arm_angles) color("dimgray") rotate(a) arm();
    color("gray") translate([0,0,plate_z]) bottom_plate();
    color("orange") translate([0,0,plate_top]) cam_mount();
    color("orange") translate([0,0,plate_top]) antenna_mount();
    for (sx=[-1,1], sy=[-1,1]) color("gold")
        translate([sx*so_x, sy*so_y, plate_top + tpu_base_t]) cylinder(d=5.5, h=standoff_h, $fn=6);
    color("green")     translate([0,0,plate_top + 5])  linear_extrude(1.6) offset(2) square(32, center=true);
    color("darkgreen") translate([0,0,plate_top + 13]) linear_extrude(1.6) offset(2) square(32, center=true);
    color("black") translate([0, cam_pivot_y, plate_top + cam_pivot_z]) rotate([25,0,0]) cube([19,20,19], center=true);
    if (show_canopy) color("steelblue") translate([0,0,plate_top]) canopy();
    color("dimgray") translate([0,0,top_z]) top_plate();
    color("orange") translate([0,26,top_z + top_t]) gopro_mount();
    color("dimgray") translate([0,0,top_z + top_t]) gps_xt60_mount();
    color("khaki") translate([0, -65.25, top_z + top_t + 26]) cube([gps_size-1, gps_size-1, 8], center=true);
    color("yellow") translate([0, -65, top_z + top_t + 6.5]) cube([16, 15.8, 8.2], center=true);
    color("red") translate([0, -12, top_z + top_t + 14]) cube([35, 75, 28], center=true);
    for (a = arm_angles) rotate(a) translate([motor_r, 0, arm_t]) { dummy_motor(); translate([0,0,24]) dummy_prop(); }
}

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
if (part == "cam_mount")       cam_mount();
if (part == "antenna_mount")   antenna_mount();
if (part == "gopro_mount")     gopro_mount();
