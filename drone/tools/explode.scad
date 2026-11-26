use </home/user/RickyBlackKat.github.io/drone/kat5.scad>
marker = 0;       // >0: render only the anchor sphere for that balloon item
// item: [number, kind, name, offset, anchor (in assembled coords), colour]
AW = [45,135,225,315];
function rad(a, r) = [cos(a)*r, sin(a)*r, 0];
module X(off) translate(off) children();
module scene() {
  for (a=AW) X(rad(a,30) + [0,0,-45]) { color("#4a7fc1") rotate(a) arm(); }
  color("#6f97c9") placed("bottom_plate");
  X([0,28,12]) color("#e08a2c") placed("cam_mount");
  X([0,62,28]) color("#333") comp("camera");
  X([0,-32,12]) color("#e08a2c") placed("antenna_mount");
  X([0,0,22]) color("#d8c24a") placed("standoffs");
  X([0,0,22]) color("#2f7d4f") comp("esc");
  X([0,0,42]) color("#3fa266") comp("fc");
  X([0,0,62]) color("#7aa64a") placed("vtx_plate");
  X([0,0,74]) color("#1f3f7a") comp("vtx");
  X([0,0,100]) color("#9bb7da") placed("canopy");
  X([0,0,130]) color("#6f97c9") placed("top_plate");
  X([0,18,158]) color("#e08a2c") placed("gopro_mount");
  X([0,-30,150]) color("#55606e") placed("gps_xt60_mount");
  X([0,-62,150]) color("#e0c040") comp("xt60");
  X([0,-30,185]) color("#c8b77a") comp("gps");
  X([0,0,215]) color("#c0392b") comp("battery");
  for (a=AW) X(rad(a,30) + [0,0,-45+14]) color("#b8bec6") rotate(a) translate([116,0,5]) cylinder(d=29.08, h=19.1);
}
ANCH = [ // [item no, point]
 [1,  rad(45,30)+[0,0,-45] + [55,55,4]],
 [2,  [-28,-18,7]],
 [3,  [0,0,130] + [22,30,42]],
 [4,  [0,0,100] + [25,10,25]],
 [5,  [0,-30,150] + [11,-78,55]],
 [6,  [0,28,12] + [-20,40,8]],
 [7,  [0,-32,12] + [-13,-55,25]],
 [8,  [0,18,158] + [-8,40,58]],
 [9,  [0,0,62] + [-18,-15,29]],
 [10, [0,0,22] + [16,-40,30]],
 [11, rad(135,30)+[0,0,-31] + [-82,82,24]],
 [13, [0,0,22] + [-22.8,10,12]],
 [14, [0,0,74] + [14,-10,36]],
 [15, [0,62,28] + [9,37,21]],
 [16, [0,-30,185] + [10,-69,73]],
 [17, [0,-62,150] + [-8,-76,48]],
 [18, [0,0,215] + [-20,-30,60]],
 [21, [0,0,42] + [20.8,-10,22]]
];
if (marker == 0) scene();
else for (a = ANCH) if (a[0] == marker) translate(a[1]) color("red") sphere(r=3.5, $fn=24);
