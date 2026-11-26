// =====================================================================
//  KAT-TR — 1.2 m printable tilt-rotor VTOL (tilt-tricopter)
//  Printed on a Bambu Lab P1P / P1S (256 x 256 x 256 mm)
//
//  Layout: high wing, fuselage pod, carbon tail boom, V-tail.
//          Two front motors on wing pods tilt from vertical (hover) to
//          forward (cruise) on servos. One rear motor on the boom faces up
//          and only runs in hover. Flight software: ArduPilot (QuadPlane,
//          Q_FRAME_CLASS = 7 tri, Q_TILT_TYPE = continuous, vectored yaw).
//
//  Assembly coordinates: X = aft (0 = wing leading edge), Y = right,
//  Z = up (0 = wing chord line / top of fuselage). Units: mm.
//
//  Export a part:  openscad -D 'part="wing_1_L"' -o wing_1_L.stl kat_tr.scad
//  Every printable part comes out already in its print orientation.
// =====================================================================

part = "assembly";
tilt = 0;            // assembly preview only: 0 = hover, 90 = cruise
show_hardware = true;

$fn = 40;

// ---------------- Global dimensions ---------------------------------
wing_c      = 200;           // wing chord (sections 1-2), root of section 3
tip_c       = 150;           // chord at the wing tip
sec_len     = 200;           // span of one wing section (3 per side → 1.2 m)
skin        = 0.45;          // single-line LW-PLA skin
rib_t       = 0.5;           // internal diagonal ribs
rib_pitch   = 60;
bulk_t      = 0.8;           // end bulkhead printed on the bed
spar_x      = 0.30;          // main spar at 30 % chord (origin of airfoil)
spar_hole   = 10.3;          // 10 mm carbon tube
spar_sleeve = 12;
rod_x       = 0.60;          // rear rod at 60 % chord
rod_hole    = 4.3;           // 4 mm carbon rod
rod_sleeve  = 7;
ail_cut     = 0.715;         // wing ends here in section 3
ail_start   = 0.73;          // aileron starts here (1.5 % chord hinge gap)

fus_w = 76; fus_h = 86; fus_wall = 0.8;
boom_d = 16; boom_hole = 16.3;
boom_z = -0.3 * fus_h / 2;   // boom axis height
boom_x0 = 280; boom_x1 = 675;

nac_y   = 230;               // tilt-motor pod position (each side)
piv     = [-105, 0, -22];    // tilt pivot (local to a pod)
yoke_d  = 24;                // pivot → motor plate top
rear_motor_x = 375;

tail_c  = 130;               // V-tail chord
tail_span = 230;
tail_dihedral = 35;
tail_x  = 545;               // V-tail leading edge
tail_r0 = 18;                // panel root distance from boom axis
rv_cut  = 0.695; rv_start = 0.71;

// Servo pocket (MG90S / 9-13 g metal-gear class, 23 x 12.5 mm body)
sv_L = 23; sv_W = 12.5; sv_H = 23; sv_tab = 32.5; sv_shaft = 6;

// ---------------- NACA 4-digit airfoils ------------------------------
function nc(x,m,p)  = m==0 ? 0 : (x<p ? m/(p*p)*(2*p*x-x*x) : m/((1-p)*(1-p))*((1-2*p)+2*p*x-x*x));
function ndc(x,m,p) = m==0 ? 0 : (x<p ? 2*m/(p*p)*(p-x) : 2*m/((1-p)*(1-p))*(p-x));
function nyt(x,t)   = 5*t*(0.2969*sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x*x*x-0.1036*x*x*x*x);
function nxs(i,n)   = (1-cos(180*i/n))/2;
function nup(x,m,p,t) = let(th=atan(ndc(x,m,p))) [x-nyt(x,t)*sin(th), nc(x,m,p)+nyt(x,t)*cos(th)];
function nlo(x,m,p,t) = let(th=atan(ndc(x,m,p))) [x+nyt(x,t)*sin(th), nc(x,m,p)-nyt(x,t)*cos(th)];
function naca(m,p,t,n=60) = concat([for(i=[n:-1:0]) nup(nxs(i,n),m,p,t)],
                                   [for(i=[1:n-1])  nlo(nxs(i,n),m,p,t)]);
WING_AF = naca(0.02, 0.4, 0.12);    // NACA 2412
TAIL_AF = naca(0, 0, 0.09);         // NACA 0009
function wcam(x) = nc(x, 0.02, 0.4) * wing_c;   // camber height (mm) on the wing

// 2D airfoil, chord c, origin at the spar (x0·c), clipped to chord fraction [a,b]
module af2d(pts, c, a=0, b=1, x0=spar_x) {
    aa = a <= 0 ? -0.1 : a;  bb = b >= 1 ? 1.1 : b;
    intersection() {
        translate([-x0*c, 0]) scale(c) polygon(pts);
        translate([(aa-x0)*c, -c]) square([(bb-aa)*c, 2*c]);
    }
}
// Straight loft between chord c0 at z=0 and c1 at z=L, evaluated over [z0,z1]
module loft(pts, c0, c1, L, z0, z1, a=0, b=1, off=0) {
    ca = c0 + (c1-c0)*z0/L;  cb = c0 + (c1-c0)*z1/L;
    hull() {
        translate([0,0,z0]) linear_extrude(0.01) offset(delta=off) af2d(pts, ca, a, b);
        translate([0,0,z1-0.01]) linear_extrude(0.01) offset(delta=off) af2d(pts, cb, a, b);
    }
}
module ribs_raw(L) {
    for (xk = [-180 : rib_pitch : 180]) for (ang = [45, -45])
        translate([xk, 0, L/2]) rotate([0, ang, 0]) cube([rib_t, 100, 3*L], center=true);
}

// Hollow single-wall panel: skin + diagonal ribs + bottom bulkhead
module thin_panel(pts, c0, c1, L, b, spar_y, spar_len, rod=false, rod_pos=[0,0]) {
    union() {
        difference() {
            loft(pts, c0, c1, L, 0, L, 0, b);
            loft(pts, c0, c1, L, -1, L+1, 0, b, -skin);
        }
        translate([0,0,0]) linear_extrude(bulk_t) af2d(pts, c0, 0, b);
        intersection() {
            loft(pts, c0, c1, L, 0, L, 0, b, -skin/2);
            union() {
                difference() { ribs_raw(L); children(0); }       // rib clearances
                translate([0, spar_y, 0]) cylinder(d=spar_sleeve, h=spar_len);
                if (rod) translate([rod_pos[0], rod_pos[1], 0]) cylinder(d=rod_sleeve, h=L);
            }
        }
    }
}

// ---------------- Wing sections (left wing, print orientation) ------
// Local: x = chord (0 at spar), y = thickness, z = span from the root of
// the section. Printed standing on the root bulkhead.
module wing_section(i) {
    c1 = i==3 ? tip_c : wing_c;   // chord at top of section
    b  = i==3 ? ail_cut : 1;
    spar_len = i==3 ? 100 : sec_len;
    sy = wcam(spar_x);
    rp = [(rod_x-spar_x)*wing_c, wcam(rod_x)];
    tun = [30, wcam(0.45)];           // wire tunnel position
    difference() {
        thin_panel(WING_AF, wing_c, c1, sec_len, b, sy, spar_len, i<3, rp) {
            union() {
                translate([tun[0], tun[1], -1]) cylinder(d=9, h=sec_len+2);
                if (i==1) for (bx = [-35, 50])
                    translate([bx, 0, 25]) rotate([90,0,0]) cylinder(d=14, h=80, center=true);
                if (i==2) {
                    translate([-15, -30, 30-4]) cube([30, 44, 8]);      // front pod tongue
                    translate([50, -30, 30-4]) cube([20, 40, 8]);       // rear pod tongue
                    translate([22, -30, 30-6]) cube([20, 30, 12]);      // pod wire pass
                }
                if (i==3) translate([22, -30, 17]) cube([34, 45, 30]);  // aileron servo
            }
        }
        // spar, rod, wire tunnel
        translate([0, sy, -1]) cylinder(d=spar_hole, h=spar_len+1.01);
        if (i<3) translate([rp[0], rp[1], -1]) cylinder(d=rod_hole, h=sec_len+2);
        translate([tun[0], tun[1], -1]) cylinder(d=8, h=sec_len+2);
        if (i==1) {
            // wing bolt tubes (4 x M4 nylon bolts) + wire exit into the fuselage
            for (bx = [-35, 50]) translate([bx, 0, 25]) rotate([90,0,0]) cylinder(d=8.3, h=80, center=true);
            translate([68, -25, 8]) cube([14, 23, 20]);
        }
        if (i==2) {
            // slots for the pod tongues and pod wiring (bottom skin only)
            translate([-12, -30, 30-3.2]) cube([24, 30.5, 6.4]);
            translate([52, -30, 30-3.2]) cube([16, 30.5, 6.4]);
            translate([25, -30, 30-5]) cube([14, 29, 10]);
            translate([0, sy, 30-3.3]) cylinder(d=spar_sleeve+1, h=6.6);  // sleeve gap for the tongue
            translate([rp[0], rp[1], 30-3.3]) cylinder(d=rod_sleeve+1, h=6.6);
        }
        if (i==3) translate([25, -30, 20]) cube([28, 27, 24]);           // servo opening
    }
}

module aileron() {   // solid part, printed standing on its root end
    loft(WING_AF, wing_c, tip_c, sec_len, 1.5, sec_len-1.5, ail_start, 1);
}
module tip_cap(pts, c, b) {   // plug (into the open tip) + rounded cap
    union() {
        linear_extrude(3) offset(delta=-skin-0.25) af2d(pts, c, 0, b);
        translate([0,0,3]) hull() {
            linear_extrude(0.01) af2d(pts, c, 0, b);
            translate([0,0,6]) linear_extrude(0.01) scale([0.94, 0.35]) af2d(pts, c, 0, b);
        }
    }
}

module wing_tip() tip_cap(WING_AF, tip_c, ail_cut);
module vtail_tip() tip_cap(TAIL_AF, tail_c, rv_cut);

// ---------------- Fuselage ------------------------------------------
module fus_profile() hull() for (s=[-1,1]) {
    translate([s*(fus_w/2-6), -6]) circle(r=6);
    translate([s*(fus_w/2-16), -fus_h+16]) circle(r=16);
}
module to_fus(x) multmatrix([[0,0,1,x],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) children();
module fslice(x, s, off=0) to_fus(x) linear_extrude(0.01) offset(delta=off) scale(s) fus_profile();
module fus_hull(xs, ss, off=0) hull() for (k=[0:len(xs)-1]) fslice(xs[k], ss[k], off);
module fus_ring(x, s=1) to_fus(x) linear_extrude(bulk_t)
    difference() { scale(s) fus_profile(); offset(delta=-6) scale(s) fus_profile(); }

// Region above the wing's lower surface (for the saddle and pod tops)
WING_LOWER = [for (i=[0:60]) nlo(nxs(i,60), 0.02, 0.4, 0.12) * wing_c];
module wing_cut(dz=0, w=100) translate([0,0,dz]) rotate([90,0,0])
    linear_extrude(w, center=true) polygon(concat(WING_LOWER, [[wing_c+8,0],[wing_c+8,80],[-8,80],[-8,0]]));

nose_x = -220;         // front of the fuselage
module fuse_nose() {   // x nose_x..0, printed rear end down
    difference() {
        union() {
            difference() {
                fus_hull([nose_x,-60,0], [0.6,1,1]);
                fus_hull([nose_x-1,-60,1], [0.6,1,1], -fus_wall);
            }
            fus_ring(-bulk_t);
        }
        translate([nose_x+30, -24, -6]) cube([160, 48, 12]);  // battery hatch
    }
}
module fuse_center() { // x 0..200, printed front end down, wing saddle on top
    difference() {
        union() {
            difference() {
                difference() { fus_hull([0,200],[1,1]); wing_cut(0); }
                difference() { fus_hull([-1,201],[1,1], -fus_wall); wing_cut(-fus_wall); }
            }
            fus_ring(0);
        }
        for (bx=[25,110], by=[-25,25]) translate([bx,by,-15]) cylinder(d=4.6, h=30);
        translate([125, -30, -10]) cube([28, 60, 20]);      // wing wiring
    }
}
module fuse_tail() {   // x 200..340, printed front end down, boom socket at the end
    sx = 0.3;
    difference() {
        union() {
            difference() {
                fus_hull([200,340],[1,sx]);
                fus_hull([199,341],[1+0.007,sx], -fus_wall);
            }
            fus_ring(200);
            intersection() {
                fus_hull([200,340],[1,sx], -fus_wall/2);
                union() {
                    translate([270, 0, boom_z]) rotate([0,90,0]) cylinder(d=boom_hole+4, h=70);
                    translate([200, -0.6, -fus_h]) cube([140, 1.2, fus_h]);
                    translate([200, -fus_w/2, boom_z-0.6]) cube([140, fus_w, 1.2]);
                }
            }
        }
        translate([268, 0, boom_z]) rotate([0,90,0]) cylinder(d=boom_hole, h=80);
        translate([320, 0, boom_z]) cylinder(d=3.2, h=40, center=true);   // M3 cross bolt
    }
}
module hatch() {       // printed top face down
    union() {
        translate([nose_x+28, -27, 0]) cube([164, 54, 1.6]);
        translate([0,0,-3]) difference() {
            translate([nose_x+30.5, -23.5, 0]) cube([159, 47, 3]);
            translate([nose_x+31.7, -22.3, -1]) cube([156.6, 44.6, 5]);
        }
    }
}
cam_w = 19;
module camera_plate() {   // closes the nose; holds a 19 mm-wide camera on M2 screws
    s = 0.6;
    difference() {
        union() {
            to_fus(nose_x-2) linear_extrude(2) scale(s) fus_profile();
            to_fus(nose_x) linear_extrude(3) offset(delta=-fus_wall-0.25) scale(s) fus_profile();
            for (sy=[-1,1]) translate([nose_x, sy*(cam_w/2+1.3) - 1.2, -0.6*fus_h/2 - 9])
                cube([18, 2.4, 18]);
        }
        translate([nose_x-10, 0, -0.6*fus_h/2]) rotate([0,90,0]) cylinder(d=17, h=20);
        for (sy=[-1,1]) translate([nose_x+10, sy*15, -0.6*fus_h/2]) rotate([90,0,0]) cylinder(d=2.2, h=10, center=true);
    }
}
module wing_mount_plate() {   // glued under the saddle, nut traps for 4 x M4
    difference() {
        intersection() {
            translate([12, -30, -12]) cube([110, 60, 14]);
            difference() { translate([0,-50,-40]) cube([wing_c, 100, 60]); wing_cut(-fus_wall); }
        }
        for (bx=[25,110], by=[-25,25]) {
            translate([bx,by,-20]) cylinder(d=4.4, h=30);
            translate([bx,by,-12.1]) cylinder(d=8.1, h=3.4, $fn=6);
        }
        translate([60, -30, -13]) cube([30, 60, 20]);     // lightening
    }
}
module bolt_tube() difference() { cylinder(d=8, h=24); translate([0,0,-1]) cylinder(d=4.5, h=26); }

// ---------------- Tilt pods (right side, local y = 0) ---------------
module pod_outer() hull() {
    translate(piv) rotate([90,0,0]) cylinder(r=15, h=34, center=true);
    translate([-80, -17, -37]) cube([1, 34, 30]);
    translate([-30, -17, -40]) cube([1, 34, 35]);
    translate([0, -17, -40]) cube([100, 34, 42]);
    translate([127, -10, -30]) cube([1, 20, 22]);
}
module pod_inner() hull() {
    translate([-76, -15, -38]) cube([1, 30, 29]);
    translate([-30, -15, -38]) cube([1, 30, 31]);
    translate([0, -15, -38]) cube([98, 30, 40]);
    translate([124, -8, -28]) cube([1, 16, 18]);
}
module servo_pocket() {
    sb = -10;    // servo bottom (y); top face at sb + sv_H, boss/horn beyond
    translate([piv[0]-sv_shaft, sb-15, piv[2]-sv_W/2-0.25]) cube([sv_L+0.4, 15+sv_H+0.4, sv_W+0.5]);
    translate([piv[0]-sv_shaft-(sv_tab-sv_L)/2-0.3, -20, piv[2]-sv_W/2-0.25]) cube([sv_tab+0.6, 28.3, sv_W+0.5]);
    translate(piv) rotate([-90,0,0]) cylinder(d=13, h=30);    // boss + spline through the wall
}
module pod() {
    sy = wcam(spar_x); ry = wcam(rod_x);
    difference() {
        union() {
            difference() {
                difference() { pod_outer(); wing_cut(0, 40); }
                difference() { pod_inner(); wing_cut(-2, 40); }
            }
            // tongues that wrap the spar and rear rod inside the wing
            hull() { translate([60,0,sy]) rotate([90,0,0]) cylinder(r=9, h=5, center=true);
                     translate([49,-2.5,-12]) cube([22,5,1]); }
            hull() { translate([120,0,ry]) rotate([90,0,0]) cylinder(r=6, h=5, center=true);
                     translate([113,-2.5,-12]) cube([14,5,1]); }
            translate([33, -7, -40]) cube([14, 14, 16]);          // landing-leg socket block
        }
        servo_pocket();
        translate([60,0,sy]) rotate([90,0,0]) cylinder(d=spar_hole, h=10, center=true);
        translate([120,0,ry]) rotate([90,0,0]) cylinder(d=rod_hole, h=10, center=true);
        translate([35, -5, -41]) cube([10, 10, 15]);               // leg socket
        translate([5, -11, -45]) cube([25, 22, 8]);               // ESC access (tape over)
        translate([86, -6, -10]) cube([12, 12, 20]);               // wires up into the wing
        // servo-cover screw holes (M2)
        for (cx=[-110,-88], cz=[-10.5,10.5]) translate([cx, -25, piv[2]+cz]) rotate([-90,0,0]) cylinder(d=1.6, h=14);
    }
}
module servo_cover() {   // closes the servo pocket, carries the M3 pivot bolt
    difference() {
        hull() {
            translate([piv[0], 0, piv[2]]) rotate([90,0,0]) cylinder(r=14, h=2.5);
            translate([-86, -2.5, piv[2]-13.5]) cube([4, 2.5, 27]);
        }
        translate([piv[0], 1, piv[2]]) rotate([90,0,0]) cylinder(d=3.2, h=5);
        for (cx=[-110,-88], cz=[-10.5,10.5]) translate([cx, 1, piv[2]+cz]) rotate([90,0,0]) cylinder(d=2.3, h=5);
    }
}
// Tilt yoke: motor plate + two arms. Local: pivot at origin, motor axis +Z (hover).
module tilt_mount() {
    difference() {
        union() {
            translate([-16, -24, yoke_d-4]) cube([32, 45.5, 4]);
            hull() { translate([0,19.5,0]) rotate([90,0,0]) cylinder(r=8, h=4, center=true);
                     translate([-16,17.5,yoke_d-4]) cube([32,4,4]); }
            hull() { translate([0,-22,0]) rotate([90,0,0]) cylinder(r=8, h=4, center=true);
                     translate([-16,-24,yoke_d-4]) cube([32,4,4]); }
        }
        for (sx=[-1,1], sy=[-1,1]) translate([sx*8, sy*8, 0]) cylinder(d=3.3, h=40);  // 16x16 M3
        translate([0,0,0]) cylinder(d=8, h=40);
        // servo-horn recess on the inside of the right arm + horn screw holes
        translate([0, 17.4, 0]) rotate([-90,0,0]) linear_extrude(2.3)
            hull() { circle(d=8); translate([0,-15]) circle(d=5); }
        translate([0, 15, 0]) rotate([-90,0,0]) cylinder(d=3, h=10);
        for (r=[9,13]) translate([0, 15, r]) rotate([-90,0,0]) cylinder(d=1.4, h=10);
        translate([0, -30, 0]) rotate([-90,0,0]) cylinder(d=3.2, h=12);                 // M3 pivot
    }
}
module landing_leg() {   // TPU; peg goes into the pod socket
    union() {
        translate([-4.8,-4.8,0]) cube([9.6, 9.6, 14]);
        hull() { translate([0,0,-1]) cylinder(d=14, h=1); translate([0,0,-44]) sphere(r=6); }
    }
}

// ---------------- Boom hardware ------------------------------------
module boom_clamp_2d(od=26) difference() {
    union() { circle(d=od); translate([-6, -od/2-6]) square([12, 8]); }
    circle(d=boom_hole); translate([-1, -od/2-7]) square([2, 9]);
}
module rear_motor_mount() {   // extruded along the boom (X)
    difference() {
        rotate([0,90,0]) rotate([0,0,90]) linear_extrude(34) union() {
            boom_clamp_2d();
            translate([-8, 10]) square([16, 16]);
            translate([-17, 25]) square([34, 4]);
        }
        translate([17, 0, -16]) rotate([90,0,0]) cylinder(d=3.2, h=40, center=true);   // clamp bolt
        for (sx=[-1,1], sy=[-1,1]) translate([17+sx*8, sy*8, 20]) cylinder(d=3.3, h=20);
        translate([17, 0, 20]) cylinder(d=8, h=20);
    }
}
module boom_servo_mount() {   // OPTIONAL: clamp + frame for a 9 g servo on the boom (makes the plane tail-heavy)
    difference() {
        rotate([0,90,0]) rotate([0,0,90]) linear_extrude(32) union() {
            boom_clamp_2d(24);
            translate([8, -3]) square([22, 6]);
        }
        translate([16, 0, -15]) rotate([90,0,0]) cylinder(d=3.2, h=40, center=true);
        translate([4.4, 12.7, -5]) cube([23.2, 12.8, 10]);       // servo body
        for (ex=[2.2, 29.8]) translate([ex, 19.1, -5]) cylinder(d=1.6, h=10);
    }
}

// ---------------- V-tail --------------------------------------------
cdi = cos(tail_dihedral); sdi = sin(tail_dihedral);
module to_tail_R() multmatrix([[1,0,0,tail_x+spar_x*tail_c],[0,-sdi,cdi,0],[0,cdi,sdi,boom_z],[0,0,0,1]])
    children();
module vtail_panel() {   // printed standing on its root
    difference() {
        thin_panel(TAIL_AF, tail_c, tail_c, tail_span, rv_cut, 0, tail_span-5) { cube(0.01); }
        translate([0,0,-1]) cylinder(d=rod_hole, h=tail_span-4);
    }
}
module ruddervator() loft(TAIL_AF, tail_c, tail_c, tail_span, 1.5, tail_span-1.5, rv_start, 1);
module tail_mount() {
    difference() {
        union() {
            translate([tail_x-5, 0, boom_z]) rotate([0,90,0]) cylinder(d=22, h=tail_c+10);
            for (m=[0,1]) mirror([0,m,0]) to_tail_R() linear_extrude(tail_r0) af2d(TAIL_AF, tail_c, 0, rv_cut);
        }
        translate([tail_x-6, 0, boom_z]) rotate([0,90,0]) cylinder(d=boom_hole, h=tail_c+7);
        for (m=[0,1]) mirror([0,m,0]) to_tail_R() translate([0,0,4]) cylinder(d=rod_hole, h=tail_r0);
        translate([tail_x+20, 0, boom_z]) cylinder(d=3.2, h=40, center=true);
    }
}
module control_horn() difference() {
    union() { translate([-8,-4,0]) cube([16,8,1.5]);
              hull() { translate([-6,-0.75,0]) cube([12,1.5,1.5]); translate([-1,-0.75,13]) cube([2,1.5,1]); } }
    for (z=[6,9.5,12.5]) translate([0,0,z]) rotate([90,0,0]) cylinder(d=1.6, h=4, center=true);
}
module servo_tray() difference() {
    union() { cube([30, 26, 14]); translate([-2,-2,0]) cube([34, 30, 1.2]); }
    translate([1,1,1.2]) cube([28, 24, 14]);
}

// ---------------- Placement helpers (assembly) ----------------------
module wing_L(i) translate([spar_x*wing_c, -(i-1)*sec_len, 0]) rotate([90,0,0]) children();
module pod_R() translate([0, nac_y, 0]) children();

// ---------------- Preview hardware ----------------------------------
module motor_prop(d_prop=178) {
    color("silver") cylinder(d=30, h=26);
    color([0.3,0.6,1,0.25]) translate([0,0,32]) cylinder(d=d_prop, h=1);
}

module assembly() {
    // wing
    for (i=[1:3]) {
        color("lightsteelblue") wing_L(i) wing_section(i);
        color("lightsteelblue") mirror([0,1,0]) wing_L(i) wing_section(i);
    }
    color("orange") wing_L(3) aileron();
    color("orange") mirror([0,1,0]) wing_L(3) aileron();
    color("lightsteelblue") wing_L(4) tip_cap(WING_AF, tip_c, ail_cut);
    color("lightsteelblue") mirror([0,1,0]) wing_L(4) tip_cap(WING_AF, tip_c, ail_cut);
    // fuselage
    color("gainsboro") { fuse_nose(); fuse_center(); fuse_tail(); }
    color("dimgray") translate([0,0,0.1]) hatch();
    color("dimgray") camera_plate();
    // pods + tilt mechanism
    for (m=[0,1]) mirror([0,m,0]) pod_R() {
        color("slategray") pod();
        color("dimgray") translate([0,-17,0]) servo_cover();
        color("dimgray") translate([40,0,-40]) landing_leg();
        translate(piv) rotate([0,-tilt,0]) {
            color("darkorange") tilt_mount();
            if (show_hardware) translate([0,0,yoke_d]) motor_prop();
        }
    }
    // boom, rear motor, tail
    color("black") translate([boom_x0,0,boom_z]) rotate([0,90,0]) cylinder(d=boom_d, h=boom_x1-boom_x0);
    color("darkorange") translate([rear_motor_x-17,0,boom_z]) rear_motor_mount();
    if (show_hardware) translate([rear_motor_x,0,boom_z+29]) motor_prop();
    color("darkorange") tail_mount();
    for (m=[0,1]) mirror([0,m,0]) to_tail_R() translate([0,0,tail_r0]) {
        color("lightsteelblue") vtail_panel();
        color("orange") ruddervator();
        color("lightsteelblue") translate([0,0,tail_span]) tip_cap(TAIL_AF, tail_c, rv_cut);
    }
    // carbon spar & rod (preview)
    color("black") translate([spar_x*wing_c, 0, wcam(spar_x)]) rotate([90,0,0]) cylinder(d=10, h=1000, center=true);
    color("black") translate([rod_x*wing_c, 0, wcam(rod_x)]) rotate([90,0,0]) cylinder(d=4, h=800, center=true);
}

// ---------------- Part selector (print orientation) -----------------
module mx() mirror([1,0,0]) children();   // right-hand version of a wing part
if (part == "assembly") assembly();
if (part == "wing_1_L") wing_section(1);
if (part == "wing_1_R") mx() wing_section(1);
if (part == "wing_2_L") wing_section(2);
if (part == "wing_2_R") mx() wing_section(2);
if (part == "wing_3_L") wing_section(3);
if (part == "wing_3_R") mx() wing_section(3);
if (part == "aileron_L") translate([0,0,-1.5]) aileron();
if (part == "aileron_R") mx() translate([0,0,-1.5]) aileron();
if (part == "wingtip_L") wing_tip();
if (part == "wingtip_R") mx() wing_tip();
if (part == "fuse_nose")   rotate([0,90,0]) fuse_nose();
if (part == "fuse_center") rotate([0,-90,0]) fuse_center();
if (part == "fuse_tail")   translate([0,0,-200]) rotate([0,-90,0]) fuse_tail();
if (part == "hatch")       rotate([180,0,0]) hatch();
if (part == "camera_plate") translate([0,0,-nose_x+2]) rotate([0,-90,0]) camera_plate();
if (part == "wing_mount_plate") wing_mount_plate();
if (part == "bolt_tube")   bolt_tube();
if (part == "pod_R")       rotate([90,0,0]) pod();
if (part == "pod_L")       mirror([1,0,0]) rotate([90,0,0]) pod();
if (part == "servo_cover") rotate([-90,0,0]) servo_cover();
if (part == "tilt_mount_R") rotate([180,0,0]) tilt_mount();
if (part == "tilt_mount_L") mirror([0,1,0]) rotate([180,0,0]) tilt_mount();
if (part == "landing_leg") landing_leg();
if (part == "rear_motor_mount") rotate([0,-90,0]) rear_motor_mount();
if (part == "boom_servo_mount") rotate([0,-90,0]) boom_servo_mount();
if (part == "tail_mount")  rotate([0,-90,0]) tail_mount();
if (part == "vtail_panel") vtail_panel();
if (part == "ruddervator") translate([0,0,-1.5]) ruddervator();
if (part == "vtail_tip")   vtail_tip();
if (part == "control_horn") control_horn();
if (part == "servo_tray")  servo_tray();
