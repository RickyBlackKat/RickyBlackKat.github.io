// =====================================================================
//  KAT-5  —  5" FPV freestyle quad, designed for FDM printing (PETG/PLA+)
//  Fits a Bambu Lab P1P / P1S (256 x 256 x 256 mm build volume)
//
//  Units: millimetres. Origin = frame centre, +Y = forward (camera side),
//  Z = 0 is the bottom face of the unibody plate.
//
//  Render a single part by setting `part` below, or from the command line:
//    openscad -D 'part="unibody"' -o unibody.stl kat5.scad
//
//  Parts:
//    "assembly"     – everything together with dummy motors/props/stack (preview only)
//    "unibody"      – bottom plate + arms, one piece          (PETG / PLA+)
//    "top_plate"    – top plate with battery-strap slots       (PETG / PLA+)
//    "standoff"     – optional printed 30 mm standoff, print 4 (PETG) – aluminium preferred
//    "cam_mount"    – 19 mm micro FPV camera cradle            (TPU 95A)
//    "antenna_mount"– rear VTX SMA + ELRS antenna holder       (TPU 95A)
//    "gopro_mount"  – 3-prong action-cam mount, 20° tilt       (TPU 95A)
//    "plate_layout" – unibody + top plate side by side (bed-fit check)
// =====================================================================

part = "assembly";

$fn = 64;

// ---------------- Main geometry --------------------------------------
wheelbase      = 225;          // motor-to-motor diagonal (5" standard ~220-230)
prop_d         = 127;          // 5.0 inch props (for clearance checks / preview)

plate_t        = 4;            // unibody plate thickness
top_t          = 3;            // top plate thickness
standoff_h     = 30;           // gap between plates (M3 x 30 standoffs)

body_w         = 42;           // centre body width  (X)
body_l         = 92;           // centre body length (Y)
body_r         = 6;            // body corner radius

// Arms
arm_w_root     = 18;
arm_w_tip      = 15;
rib_w          = 4;            // stiffening spine on top of each arm
rib_h_root     = 8;            // spine height at the body
rib_h_tip      = 3;            // spine height near the motor
rib_r_start    = 30;           // spine start (radius from centre)

// Motor mount (16 x 16 M3, 22xx/23xx motors)
motor_pad_d    = 32;
motor_spacing  = 16;           // square bolt pattern
motor_hole_d   = 3.3;
motor_shaft_d  = 7.5;          // clearance for shaft / circlip
bell_clear_r   = 17;           // spine stops this far from motor centre

// Flight stack (30.5 x 30.5 M3)
stack_spacing  = 30.5;
stack_hole_d   = 3.3;

// Standoffs (M3)
so_x           = 16;
so_y           = 40;
so_hole_d      = 3.3;

// Camera (19 mm "micro" FPV cam)
cam_w          = 19;
cam_pivot_y    = 37;           // pivot screw position (Y)
cam_pivot_z    = 14;           // pivot height above unibody top
tpu_base_t     = 2;            // thickness of TPU accessory bases

// Battery straps
strap_w        = 22;           // slot length (fits 20 mm straps)
strap_t        = 3.5;          // slot width
strap_x        = 13.5;         // slot offset from centre
strap_y        = 15;           // two straps at +/- this Y

// Derived
motor_r = wheelbase / 2;
motor_xy = motor_r / sqrt(2);
motor_pos = [ [ motor_xy,  motor_xy], [-motor_xy,  motor_xy],
              [-motor_xy, -motor_xy], [ motor_xy, -motor_xy] ];
arm_angles = [45, 135, 225, 315];

// ---------------- Helpers --------------------------------------------
module rrect(w, l, r, h) {
    linear_extrude(h)
        offset(r) square([w - 2*r, l - 2*r], center = true);
}

module hole_at(p, d, h = 100) {
    translate([p[0], p[1], -1]) cylinder(d = d, h = h);
}

module standoff_holes(d = so_hole_d) {
    for (sx = [-1, 1], sy = [-1, 1]) hole_at([sx*so_x, sy*so_y], d);
}

// ---------------- Unibody (bottom plate + arms) ----------------------
module arm_2d(a) {
    rotate(a) hull() {
        translate([20, 0]) circle(d = arm_w_root);
        translate([motor_r, 0]) circle(d = arm_w_tip);
    }
    rotate(a) translate([motor_r, 0]) circle(d = motor_pad_d);
}

module arm_rib(a) {
    len = motor_r - bell_clear_r - rib_r_start;
    rotate(a)
        hull() {
            translate([rib_r_start, -rib_w/2, plate_t - 0.01])
                cube([0.1, rib_w, rib_h_root]);
            translate([rib_r_start + len, -rib_w/2, plate_t - 0.01])
                cube([0.1, rib_w, rib_h_tip]);
        }
}

module motor_holes(p) {
    translate([p[0], p[1], 0]) {
        for (sx = [-1, 1], sy = [-1, 1])
            hole_at([sx*motor_spacing/2, sy*motor_spacing/2], motor_hole_d);
        hole_at([0, 0], motor_shaft_d);
    }
}

// Zip-tie slots to hold motor wires against the arm, either side of the spine
module ziptie_slots(a) {
    rotate(a) for (r = [55, 80]) for (s = [-1, 1])
        translate([r, s * (rib_w/2 + 3), -1])
            linear_extrude(plate_t + 2) square([3.2, 1.8], center = true);
}

module unibody() {
    difference() {
        union() {
            linear_extrude(plate_t) union() {
                offset(body_r) square([body_w - 2*body_r, body_l - 2*body_r], center = true);
                for (a = arm_angles) arm_2d(a);
            }
            for (a = arm_angles) arm_rib(a);
        }
        for (p = motor_pos) motor_holes(p);
        // stack
        for (sx = [-1, 1], sy = [-1, 1])
            hole_at([sx*stack_spacing/2, sy*stack_spacing/2], stack_hole_d);
        standoff_holes();
        for (a = arm_angles) ziptie_slots(a);
        // weight-saving slots beside the stack (outside the 36 mm board footprint)
        for (sy = [-1, 1]) translate([0, sy * 27, -1])
            linear_extrude(plate_t + 2) offset(2) square([12, 2], center = true);
        // centre hole under the stack (ESC cooling / weight)
        hole_at([0, 0], 14);
    }
}

// ---------------- Top plate ------------------------------------------
module top_plate() {
    difference() {
        rrect(body_w, body_l, body_r, top_t);
        standoff_holes();
        // battery-strap slots
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx*strap_x, sy*strap_y, -1])
                linear_extrude(top_t + 2)
                    offset(strap_t/2 - 0.01) square([0.02, strap_w - strap_t], center = true);
        // GoPro-mount strap slot (front)
        translate([0, 29, -1]) linear_extrude(top_t + 2)
            offset(1.5) square([16, 0.5], center = true);
        // lightening / wire-pass slot down the middle
        translate([0, -6, -1]) linear_extrude(top_t + 2)
            offset(3) square([10, 22], center = true);
    }
}

// ---------------- Printed standoff (optional) ------------------------
// 2.6 mm pilot holes: M3 screws self-tap into PETG from each end.
module standoff() {
    difference() {
        cylinder(d = 8, h = standoff_h, $fn = 6);
        translate([0, 0, -1]) cylinder(d = 2.6, h = standoff_h + 2);
    }
}

// ---------------- Camera cradle (TPU) --------------------------------
cam_wall_t   = 3;
cam_wall_in  = cam_w + 0.4;                 // inner gap between walls
cam_wall_h   = cam_pivot_z + 7;
module cam_mount() {
    difference() {
        union() {
            // base strip, clamped under the front standoffs
            translate([-(so_x + 4), 28, 0]) cube([2*(so_x + 4), 46 - 28, tpu_base_t]);
            // side walls
            for (s = [-1, 1])
                translate([s * (cam_wall_in/2 + cam_wall_t/2), cam_pivot_y, 0])
                    hull() {
                        translate([-cam_wall_t/2, -8, 0]) cube([cam_wall_t, 16, 1]);
                        translate([0, 0, cam_pivot_z]) rotate([0, 90, 0])
                            cylinder(d = 12, h = cam_wall_t, center = true);
                    }
        }
        // standoff screw holes
        for (sx = [-1, 1]) hole_at([sx*so_x, so_y], so_hole_d);
        // opening so the camera can tilt through the base
        translate([-cam_wall_in/2, 29.5, -1]) cube([cam_wall_in, 15, tpu_base_t + 2]);
        // M2 pivot holes
        translate([0, cam_pivot_y, cam_pivot_z]) rotate([0, 90, 0])
            cylinder(d = 2.2, h = 60, center = true);
    }
}

// ---------------- Antenna mount (TPU) --------------------------------
module antenna_mount() {
    difference() {
        union() {
            translate([-(so_x + 4), -46, 0]) cube([2*(so_x + 4), 12, tpu_base_t]);
            // rear tab for the VTX SMA connector
            translate([-9, -46, 0]) cube([18, 3, 20]);
            // ELRS antenna tubes, angled 45° up and back
            for (s = [-1, 1])
                translate([s * 13, -40, 0]) rotate([45, 0, 0])
                    cylinder(d = 6.5, h = 26);
        }
        for (sx = [-1, 1]) hole_at([sx*so_x, -so_y], so_hole_d);
        // SMA bulkhead hole (6.5 mm)
        translate([0, -44, 12]) rotate([90, 0, 0]) cylinder(d = 6.6, h = 10, center = true);
        // antenna bores
        for (s = [-1, 1])
            translate([s * 13, -40, 0]) rotate([45, 0, 0])
                translate([0, 0, -5]) cylinder(d = 2.4, h = 40);
        // flatten the bottom
        translate([-50, -80, -20]) cube([100, 100, 20]);
    }
}

// ---------------- GoPro mount (TPU) ----------------------------------
gp_tilt = 20;
module gopro_mount() {
    base_l = 20;
    difference() {
        union() {
            translate([-17, 0, 0]) cube([34, base_l, 3]);
            // wedge + prongs, tilted back by gp_tilt
            hull() {
                translate([-8, 7, 0]) cube([16, 12, 3]);
                translate([0, 13, 12]) rotate([gp_tilt, 0, 0])
                    cube([15.4, 10, 2], center = true);
            }
            translate([0, 13, 12]) rotate([gp_tilt, 0, 0]) gopro_prongs();
        }
        // strap slot through the base (behind the wedge)
        translate([-12, 1.5, -1]) cube([24, 3, 5]);
        // bolt hole through the prongs (M5 thumbscrew)
        translate([0, 13, 12]) rotate([gp_tilt, 0, 0]) translate([0, 0, 9])
            rotate([0, 90, 0]) cylinder(d = 5.3, h = 30, center = true);
    }
}
module gopro_prongs() {
    // 3 prongs, 3.0 mm thick, 3.2 mm gaps (standard GoPro "buckle" side)
    for (i = [-1, 0, 1])
        translate([i * 6.2, 0, 0]) hull() {
            translate([-1.5, -5, 0]) cube([3, 10, 1]);
            translate([0, 0, 9]) rotate([0, 90, 0]) cylinder(d = 10, h = 3, center = true);
        }
}

// ---------------- Preview dummies ------------------------------------
module dummy_motor() {
    color("silver") cylinder(d = 28, h = 18);
    color("silver") translate([0, 0, 18]) cylinder(d = 5, h = 12);
}
module dummy_prop() {
    color([0.2, 0.6, 1, 0.25]) cylinder(d = prop_d, h = 1);
}

module assembly() {
    color("dimgray") unibody();
    top_z = plate_t + tpu_base_t + standoff_h;
    color("dimgray") translate([0, 0, top_z]) top_plate();
    // standoffs
    for (sx = [-1, 1], sy = [-1, 1])
        color("gold") translate([sx*so_x, sy*so_y, plate_t + tpu_base_t]) standoff();
    // stack
    color("green") translate([0, 0, plate_t + 5]) rrect(36, 36, 2, 1.6);
    color("darkgreen") translate([0, 0, plate_t + 13]) rrect(36, 36, 2, 1.6);
    // accessories
    color("orange") translate([0, 0, plate_t]) cam_mount();
    color("orange") translate([0, 0, plate_t]) antenna_mount();
    color("orange") translate([0, 26, top_z + top_t]) gopro_mount();
    // camera
    color("black") translate([0, cam_pivot_y, plate_t + cam_pivot_z])
        rotate([25, 0, 0]) cube([19, 20, 19], center = true);
    // battery (6S 1100 class)
    color("red") translate([0, -12, top_z + top_t + 14])
        cube([34, 75, 28], center = true);
    // motors + props
    for (p = motor_pos) translate([p[0], p[1], plate_t]) {
        dummy_motor();
        translate([0, 0, 24]) dummy_prop();
    }
}

// ---------------- Part selector --------------------------------------
if (part == "assembly")      assembly();
if (part == "unibody")       unibody();
if (part == "top_plate")     top_plate();
if (part == "standoff")      standoff();
if (part == "cam_mount")     cam_mount();
if (part == "antenna_mount") antenna_mount();
if (part == "gopro_mount")   gopro_mount();
if (part == "plate_layout") {
    unibody();
    translate([0, 0, 0]) translate([0, -150, 0]) top_plate();
}
