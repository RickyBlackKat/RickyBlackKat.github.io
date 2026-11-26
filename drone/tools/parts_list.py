import qrcode, qrcode.image.svg, html, io, os
HERE=os.path.dirname(os.path.abspath(__file__))
REPO='https://github.com/RickyBlackKat/RickyBlackKat.github.io/tree/claude/makerworld-model-build-3e6s4d/drone'
PRINTED=[ # qty, file, part, material, settings, grams each
 ('1','test_coupon.stl','Fit-test coupon — PRINT FIRST','PETG','2 walls, 20%','5'),
 ('4 (+2)','arm.stl','Arm, bolt-on','PETG','6 walls, 5 top/bottom, 40% gyroid, flat','20'),
 ('1','bottom_plate.stl','Centre plate','PETG','6 walls, 40%, flat','16'),
 ('1','top_plate.stl','Top plate','PETG','6 walls, 40%, flat','15'),
 ('1','canopy.stl','Canopy','PETG / PLA (TPU optional)','3 walls, upright, no supports','8'),
 ('1','gps_xt60_mount.stl','GPS + XT60 tower','PETG','4 walls, 30%, upright','7'),
 ('1','vtx_plate.stl','VTX plate','PETG','4 walls, 100%','2'),
 ('1','cam_mount.stl','Camera mount','TPU 95A','3 walls, 25%','2'),
 ('1','antenna_mount.stl','Antenna mount','TPU 95A','3 walls, 25%','2'),
 ('1','gopro_mount.stl','GoPro mount (only with an action camera)','TPU 95A','3 walls, 25%, tree supports optional','3'),
]
# group, qty, item, spec, example, url, approx price (USD)
BUY=[
 ('Flight','1','Flight stack FC + 4-in-1 ESC','30.5 mm, F405, 55 A, runs ArduPilot','SpeedyBee F405 V4 BLS 55A stack','https://www.getfpv.com/speedybee-f405-v4-stack-f4-v4-fc-55a-blheli-s-esc-30x30.html','75–90'),
 ('Flight','5','Motor (4 + 1 spare)','2207, 1750–1950 KV, 6S, 16×16 M3','iFlight XING2 2207 1855KV','https://shop.iflight.com/xing2-2207-4s-6s-fpv-motor-unibell-pro1464','90–110'),
 ('Flight','6 sets','Props 5.1" tri-blade','5 mm shaft, 2 CW + 2 CCW per set','Gemfan Hurricane 51433','https://www.progressiverc.com/products/gemfan-hurricane-51433-tri-blade-propellers','20'),
 ('Flight','1','GPS + compass','M10, ≤ 20.6 mm square','Matek M10Q-5883','https://www.racedayquads.com/products/matek-sam-m10q-5883-gnss-gps-module','25–35'),
 ('Flight','1','XT60 pigtail + capacitor','12 AWG, 35 V 1000 µF','XT60 pigtail w/ capacitor (3 pcs)','https://www.getfpv.com/black-xt60-lipo-pigtail-w-35v-1000uf-capacitor-12awg-3pcs.html','10'),
 ('Flight','4','Standoff M3 × 30','Aluminium, ≤ 5.5 mm hex','HQProp M3 hex 30 mm (4 pcs)','https://www.myfpvstore.com/870b','5'),
 ('Flight','2','Battery strap','20 mm × 250 mm, non-slip','Lumenier Kevlar strap 20×250 (3 pcs)','https://www.getfpv.com/lumenier-indestructible-kevlar-lipo-strap-20x250mm-3pcs.html','10'),
 ('Power','3','Battery 6S LiPo','1100–1200 mAh, XT60, ≤ 78 × 40 × 34 mm','Tattu R-Line V5 6S 1200','https://www.progressiverc.com/products/tattu-r-line-v5-6s-1200mah-150c','100–130'),
 ('Power','1','Charger','6S balance, ≥ 100 W, AC/DC','ToolkitRC M7AC','https://www.getfpv.com/toolkitrc-m7ac-100w-ac-300w-dc-15a-2-6s-multi-function-ac-smart-balance-charger.html','60–90'),
 ('Power','1','Smoke stopper','XT60, resettable fuse','RDQ / BengineeringLabs smoke stopper','https://www.racedayquads.com/products/smoke-stopper-by-rdq-and-bengineeringlabs','15'),
 ('Video','1','FPV camera','19 mm micro analog','Caddx Ratel 2','https://www.getfpv.com/caddx-ratel-2-micro-starlight-1200tvl-low-latency-fpv-camera.html','30'),
 ('Video','1','Video transmitter','5.8 GHz, 20×20 mount, 5 V, MMCX→SMA','SpeedyBee TX800','https://www.racedayquads.com/products/speedybee-tx800-20x20-25-800mw-5-8ghz-vtx-mmcx','25–40'),
 ('Video','1','Laptop video receiver','5.8 GHz UVC (shows as a webcam)','Skydroid UVC or Eachine ROTG02 — any UVC OTG receiver','','25–45'),
 ('Radio','1','Radio transmitter','ExpressLRS 2.4 GHz','RadioMaster Pocket (ELRS)','https://www.progressiverc.com/products/radiomaster-pocket','70–90'),
 ('Radio','1','Receiver','ExpressLRS 2.4 GHz nano','Radiomaster RP1 V2','https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver','15–20'),
 ('Legal','1','Remote ID module (US)','Broadcast module on the FAA list','Dronetag Beacon V2','https://www.getfpv.com/electronics/remote-id/dronetag-beacon-v2-broadcast-remote-id-module.html','40–60'),
 ('Print','1 kg','PETG filament','1.75 mm','Bambu Lab PETG HF','https://www.matterhackers.com/store/l/bambu-lab-petg-hf-filament-175mm-1kg/sk/MDG9ZMY3','20–25'),
 ('Print','1 kg','TPU 95A filament','1.75 mm (not via AMS)','Bambu Lab TPU 95A HF','https://eu.store.bambulab.com/en/products/tpu-95a-hf','30–40'),
 ('Tools','1','Soldering iron','temperature-controlled, 60 W+','Pinecil V2','https://pine64.org/documentation/Pinecil/_full/','26–40'),
]
FASTENERS=[('16','M3 × 8 socket head','motor → arm (1 mm counterbore, 4 mm in motor)'),('8','M3 × 12 + nylock','arm → centre plate'),
 ('4','M3 × 35 + nylock','stack bolts through arm roots (M3 × 30 is too short)'),('8','M3 × 8','standoffs, top + bottom'),
 ('2','M3 × 10 + nylock','tower → top-plate tab'),('2','M2 × 6','camera pivot'),('4','M2 nylon + 1.5 mm spacer','VTX → VTX plate'),
 ('1','M5 thumbscrew','GoPro mount (only with an action camera)')]
EXTRA=[('FAA DroneZone (registration)','https://faadronezone-access.faa.gov/'),('FAA list of Remote ID modules','https://uasdoc.faa.gov/listDocs'),
       ('KAT-5 files (STL, CAD, drawings)',REPO)]
def qr(url, px=58):
    img=qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    s=img.to_string(encoding='unicode')
    return s.replace('<svg ', f'<svg width="{px}" height="{px}" ',1)
def short(u):
    u=u.replace('https://','').replace('www.','')
    return u if len(u)<46 else u[:44]+'…'
CSS='''@page{size:Letter;margin:0.45in 0.45in 0.5in}
body{font-family:'DejaVu Sans',Arial,sans-serif;color:#000;font-size:9.5pt;margin:0}
h1{font-size:20pt;letter-spacing:2px;margin:0}
.sub{font-size:9pt;margin:2px 0 10px}
h2{font-size:11.5pt;letter-spacing:1.5px;margin:14px 0 5px;border-bottom:1.5px solid #000;padding-bottom:2px}
table{border-collapse:collapse;width:100%}
th{font-size:7.5pt;letter-spacing:1px;text-align:left;border-bottom:1.2px solid #000;padding:3px 4px}
td{border-bottom:0.6px solid #888;padding:4px;vertical-align:middle}
tr{page-break-inside:avoid}
.box{width:11px;height:11px;border:1.2px solid #000;display:inline-block}
.u{font-family:'DejaVu Sans Mono',monospace;font-size:7.2pt;word-break:break-all}
.n{text-align:center;white-space:nowrap}.r{text-align:right;white-space:nowrap}
.note{font-size:8.2pt;margin-top:6px}
.grp td{background:#eee;font-weight:bold;letter-spacing:1px;font-size:8pt;padding:3px 4px}
.head{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #000;padding-bottom:6px}
.qrc{width:62px}
.f{font-family:'DejaVu Sans Mono',monospace;font-size:7.4pt;white-space:nowrap}'''
def build():
    h=[f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>']
    h.append(f'<div class="head"><div><h1>KAT-5 PARTS LIST</h1><div class="sub">5" FPV quad · printed frame · rev. B (bolt-on arms, 5 mm arm, Ø3.4 holes) · 2026-11-26</div></div>'
             f'<div style="text-align:center">{qr(REPO,70)}<div style="font-size:6.5pt">PROJECT FILES</div></div></div>')
    h.append('<p class="note">Tick each box as you buy or print. Prices are rough US street prices from late 2025 and will have changed; links go to example retailers, and any part with the same spec fits. Scan a QR code with your phone to open the link.</p>')
    h.append('<h2>1 · PRINT THESE (Bambu P1P / P1S)</h2><table><tr><th></th><th>QTY</th><th>FILE (stl/)</th><th>PART</th><th>MATERIAL</th><th>SETTINGS</th><th class="r">≈ g EACH</th></tr>')
    for q,f,p,m,st,g in PRINTED:
        h.append(f'<tr><td><span class="box"></span></td><td class="n">{q}</td><td class="f">{f}</td><td>{html.escape(p)}</td><td>{m}</td><td>{st}</td><td class="r">{g}</td></tr>')
    h.append('</table><p class="note">PETG: 0.2 mm layers, 245 °C nozzle, 70 °C bed, textured PEI. TPU: 3 mm³/s maximum flow, external spool. Print the coupon first and check that an M3 screw passes freely, then check the camera, XT60 and GPS fits.</p>')
    h.append('<h2>2 · BUY THESE</h2><table><tr><th></th><th>QTY</th><th>ITEM</th><th>MUST MATCH</th><th>EXAMPLE + LINK</th><th class="qrc">SCAN</th><th class="r">≈ $</th></tr>')
    last=None
    for grp,q,it,spec,ex,url,pr in BUY:
        if grp!=last: h.append(f'<tr class="grp"><td colspan="7">{grp.upper()}</td></tr>'); last=grp
        link=f'<div class="u">{short(url)}</div>' if url else '<div class="u">search the example name</div>'
        h.append(f'<tr><td><span class="box"></span></td><td class="n">{q}</td><td><b>{html.escape(it)}</b></td><td>{html.escape(spec)}</td>'
                 f'<td>{html.escape(ex)}{link}</td><td>{qr(url) if url else ""}</td><td class="r">{pr}</td></tr>')
    h.append('</table><p class="note"><b>Approximate total: $650–850</b>, including the radio, charger and soldering iron. About $250–350 of it carries over to the KAT-TR plane.</p>')
    h.append('<h2>3 · FASTENERS (any M3 / M2 assortment kit)</h2><table><tr><th></th><th>QTY</th><th>SIZE</th><th>WHERE</th></tr>')
    for q,sz,w in FASTENERS: h.append(f'<tr><td><span class="box"></span></td><td class="n">{q}</td><td><b>{sz}</b></td><td>{w}</td></tr>')
    h.append('</table>')
    h.append('<h2>4 · ALSO NEEDED</h2><table><tr><th></th><th>ITEM</th></tr>')
    for t in ['Solder (63/37), flux, heat-shrink','Multimeter','Hex drivers 1.5 / 2.0 / 2.5 mm + prop nut wrench','Zip ties, double-sided tape, battery pad','LiPo safe bag + cell checker']:
        h.append(f'<tr><td style="width:18px"><span class="box"></span></td><td>{t}</td></tr>')
    h.append('</table><h2>5 · LINKS</h2><table><tr><th>WHAT</th><th>LINK</th><th class="qrc">SCAN</th></tr>')
    for w,u in EXTRA: h.append(f'<tr><td><b>{w}</b></td><td class="u">{u}</td><td>{qr(u)}</td></tr>')
    h.append('</table><p class="note">US: register the quad (it weighs over 250 g), pass the free TRUST test, and fit a Remote ID module. Flying from a screen still needs a visual observer next to you.</p></body></html>')
    open(os.path.join(HERE,'parts_list.html'),'w').write(''.join(h))
    # markdown twin
    m=['# KAT-5 parts list\n','Printable version: [`KAT-5_parts_list.pdf`](drawings/KAT-5_parts_list.pdf), with QR codes for every link. Prices are rough late-2025 US prices. The links are example retailers; any part with the same spec fits.\n',
       '## Print\n','| Qty | File | Part | Material | Settings |','|---|---|---|---|---|']
    m+= [f'| {q} | `stl/{f}` | {p} | {mt} | {st} |' for q,f,p,mt,st,g in PRINTED]
    m+= ['\n## Buy\n','| Qty | Item | Must match | Example | ≈ $ |','|---|---|---|---|---|']
    m+= [f'| {q} | {it} | {spec} | {f"[{ex}]({url})" if url else ex} | {pr} |' for grp,q,it,spec,ex,url,pr in BUY]
    m+= ['\n## Fasteners\n','| Qty | Size | Where |','|---|---|---|']+[f'| {q} | {s} | {w} |' for q,s,w in FASTENERS]
    m+= ['\n## Links\n']+[f'- [{w}]({u})' for w,u in EXTRA]
    open(os.path.join(HERE,'PARTS_LIST.md'),'w').write('\n'.join(m)+'\n')
build()
