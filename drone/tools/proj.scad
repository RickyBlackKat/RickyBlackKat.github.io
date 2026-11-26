use </home/user/RickyBlackKat.github.io/drone/kat5.scad>
item=""; view="top"; kind="placed"; lev=-1000;
module V() {
  if (view=="top")   children();
  if (view=="front") multmatrix([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]]) children();
  if (view=="side")  multmatrix([[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,1]]) children();
}
module part_by_name(n) {
  if (n=="arm") arm(); if (n=="bottom_plate") bottom_plate(); if (n=="top_plate") top_plate();
  if (n=="canopy") canopy(); if (n=="gps_xt60_mount") gps_xt60_mount(); if (n=="cam_mount") cam_mount();
  if (n=="antenna_mount") antenna_mount(); if (n=="gopro_mount") gopro_mount(); if (n=="vtx_plate") vtx_plate();
}
module obj() { if (kind=="placed") placed(item); if (kind=="comp") comp(item, 0); if (kind=="part") part_by_name(item); }
projection() V() intersection() { obj(); translate([-2500,-2500,lev]) cube(5000); }
