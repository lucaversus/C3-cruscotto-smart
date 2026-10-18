from pathlib import Path
from html import escape
from itertools import product

ROOT = Path(__file__).resolve().parents[1]
# Static bounds only: no SPICE simulation, dynamic or automotive qualification.
thresholds=[]
for a,b,c,d in product((.99,1.01), repeat=4):
    ak=10000*b/(68000*a+10000*b)
    ar=10000*d/(150000*c+10000*d)
    for supply in (9,16):
        for offset in (-.003,.003):
            thresholds.append((supply*ar+offset)/(supply*ak))
assert min(thresholds)>.3 and max(thresholds)<.7
max_input=16*10100/(67320+10100)
assert max_input < 4.75-2
base_min=(2.5-1.2)/(330*1.05)-1.2/(47000*.95)
collector_max=16/(510*.99)
assert collector_max/base_min<10
print(f"DC model: threshold/VBAT={min(thresholds):.4f}..{max(thresholds):.4f}; input_max={max_input:.3f}V; forced_beta_max={collector_max/base_min:.2f}; R3_power_max={16**2/(510*.99):.3f}W")


s=['<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1750" viewBox="0 0 2200 1750"><rect width="2200" height="1750" fill="white"/>']
INK='#20364b'
def text(x,y,t,size=23,bold=False,anchor='start',color=None):
 s.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" fill="{color or INK}" font-weight="{700 if bold else 400}">{escape(t)}</text>')
def wire(d):s.append(f'<path d="{d}" stroke="{INK}" stroke-width="3" fill="none"/>')
def dot(x,y):s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{INK}"/>')
def box(x,y,w,h,fill='white'):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
def ground(x,y):wire(f'M{x} {y} v10 m-18 0 h36 m-29 8 h22 m-16 8 h10')
def res(x,y,ref,value,v=False):
 if v:
  wire(f'M{x} {y} v15 m0 50 v15');box(x-10,y+15,20,50);text(x+22,y+32,ref,20,True);text(x+22,y+59,value,20)
 else:
  wire(f'M{x} {y} h15 m65 0 h15');box(x+15,y-10,65,20);text(x+46,y-43,ref,20,True,'middle');text(x+46,y-18,value,20,False,'middle')
def cap(x,y,ref,value,polar=False):
 wire(f'M{x} {y} v30 m-20 0 h40 m-40 12 h40 m-20 0 v38')
 text(x+28,y+32,ref,20,True);text(x+28,y+60,value,20)
 if polar:text(x-38,y+22,'+',22,True)
box(25,25,2150,1700)
text(65,80,'INTERFACCIA K-LINE — SCHEMA ELETTRICO',35,True)
text(65,118,'Rev. D · integrato con piedinatura completa · alimentazione stabilizzata da banco · non collaudato',23)
# Transmission and K bus
text(80,182,'TRASMISSIONE',24,True)
text(80,470,'TX_INV',23,True,color='#1763a3');wire('M80 490 H210');res(210,490,'R1','330 Ω');wire('M305 490 H470');dot(360,490)
wire('M360 490 V570');res(360,570,'R2','47 kΩ',True);wire('M360 650 V710');ground(360,710)
wire('M470 450 V530 M470 470 L530 425 V330 M470 510 L530 555 V710')
s.append(f'<path d="M512 532 L528 553 L505 544 Z" fill="{INK}"/>');ground(530,710)
text(545,515,'Q1',24,True);text(545,545,'2N5551',23);text(540,414,'C',20);text(445,445,'B',20);text(540,585,'E',20)
text(80,785,'TX invertita: livello basso = linea rilasciata.',21)
text(80,818,'Q1: verificare E/B/C del produttore ordinato.',21)
wire('M530 330 H850');dot(650,330)
# External signal ports; directions refer to the K-line module.
s.append('<rect x="70" y="230" width="365" height="70" rx="8" fill="#fff2dc" stroke="#b76500" stroke-width="3"/>')
text(90,258,'K-LINE ↔ LINEA ESTERNA',23,True,color='#a45100')
text(90,284,'Bidirezionale · banco: K_BENCH',19,color='#a45100')
wire('M250 300 V330 H530');dot(530,330)
text(80,420,'INGRESSO DA ESP32 ↓',21,True,color='#1763a3')
s.append(f'<rect x="605" y="135" width="245" height="175" rx="5" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="8 6"/>')
text(618,158,'SIMULATORE ESTERNO',17,True)
text(680,195,'VBENCH',21,True);wire('M650 180 V210')
res(650,210,'R3','510 Ω / 1 W',True);wire('M650 290 V330')
# Receive divider
res(850,330,'R4','68 kΩ');wire('M945 330 H1020 V600 H1080');dot(1020,600)
wire('M1020 600 V745');res(1020,745,'R5','10 kΩ',True);wire('M1020 825 V855');ground(1020,855)
text(960,215,'RICEZIONE',24,True)
# Central complete package
box(1160,380,390,390,'#f0f5f8');wire('M1315 380 a40 30 0 0 0 80 0')
text(1355,346,'U1 · LM2903B',27,True,'middle')
text(1355,735,'SOIC-8 · vista dall’alto',21,False,'middle')
for num,label,y in [(1,'OUT1',440),(2,'IN1−',520),(3,'IN1+',600),(4,'GND',680)]:
 wire(f'M1080 {y} H1160');text(1120,y-12,str(num),20,True,'middle');text(1182,y+7,label,23)
for num,label,y in [(8,'VCC',440),(7,'OUT2',520),(6,'IN2−',600),(5,'IN2+',680)]:
 wire(f'M1550 {y} H1630');text(1590,y-12,str(num),20,True,'middle');text(1528,y+7,label,23,False,'end')
# Output loops above chip, pullup and RX
wire('M1080 440 H1060 V305 H1770');dot(1730,305)
text(1680,157,'3V3',22,True);wire('M1730 170 V190');res(1730,190,'R8','4,7 kΩ',True);wire('M1730 270 V305')
wire('M1770 305 H1850');res(1850,305,'R9','1 kΩ');wire('M1945 305 H2090');s.append('<rect x="1880" y="330" width="260" height="68" rx="8" fill="#e6f5ed" stroke="#157348" stroke-width="3"/>');text(1895,357,'RX_3V3 → ESP32',23,True,color='#157348');text(1895,384,'USCITA logica a 3,3 V',19,color='#157348')
# VREF label on input and divider, no ambiguous crossings
wire('M1080 520 H1100');text(1095,500,'VREF',20,True,'end')
wire('M1080 680 H1100 V855');ground(1100,855)
# unused comparator explicitly connected
wire('M1630 520 H1670');wire('M1660 510 l20 20 m0 -20 l-20 20');text(1700,528,'NC',21)
wire('M1630 600 H1680');text(1695,608,'VREF',22,True)
wire('M1630 680 H1670 V855');ground(1670,855)
# +5V and real bypass caps
wire('M1630 440 H1990');dot(1840,440);dot(1990,440);text(1865,420,'+5V',24,True)
wire('M1840 440 V595');cap(1840,595,'C1','100 nF');wire('M1840 675 V855');ground(1840,855)
wire('M1990 440 V595');cap(1990,595,'C2','10 µF / 16 V',True);wire('M1990 675 V855');ground(1990,855)
# Reference, adjacent below transmit stage
text(650,470,'RIFERIMENTO',22,True);text(680,515,'VBENCH',21,True);wire('M730 530 V550');res(730,550,'R6','150 kΩ',True)
wire('M730 630 V665 H880');dot(730,665);text(805,645,'VREF',22,True)
wire('M730 665 V710');res(730,710,'R7','10 kΩ',True);wire('M730 790 V855');ground(730,855)
text(80,923,'VREF: stesso nodo sui pin 2 e 6. Tutte le masse GND sono comuni. NC = piedino lasciato libero.',22)
text(80,990,'Alimentazioni esterne: +5V, 3V3 e riferimento VBENCH 9–16 V; GND comune anche con ESP32.',21)
text(80,956,'R3 appartiene solo al simulatore esterno: non montarla nel modulo. UART 10400 baud, 8N1; RX normale.',22)
# Complete bill of materials, same sheet
text(80,1020,'DISTINTA BASE — MODULO E SIMULATORE ESTERNO',27,True)
rows=[('U1','1','LM2903B, SOIC-8','Con adattatore SOIC-8 → DIP-8 e zoccolo'),('Q1','1','2N5551, NPN TO-92','Piedinatura E/B/C secondo produttore'),('R1 / R2','1 + 1','330 Ω / 47 kΩ','0,25 W · 5%'),('R3','1','510 Ω','1 W · 1% · ESTERNA al modulo, solo simulatore'),('R4 / R6','1 + 1','68 kΩ / 150 kΩ','0,25 W · 1%'),('R5, R7','2','10 kΩ','0,25 W · 1%'),('R8 / R9','1 + 1','4,7 kΩ / 1 kΩ','0,25 W · R8 1%, R9 non vincolata'),('C1 / C2','1 + 1','100 nF / 10 µF 16 V','Ceramico / elettrolitico polarizzato'),('Montaggio','1 insieme','Millefori, morsetti e fili','Adattatore e zoccolo inclusi nella voce U1')]
cols=[80,340,470,1070,2120];top=1040;rh=40
box(80,top,2040,rh,'#eaf0f5')
for x,t in zip(cols,['Riferimento','Qtà','Componente / valore','Specifiche / note']):text(x+12,top+28,t,22,True)
for i,row in enumerate(rows):
 y=top+rh*(i+1);box(80,y,2040,rh,'white' if i%2 else '#f7f9fb')
 for x,t in zip(cols,row):text(x+12,y+27,t,21)
for x in cols[1:-1]:wire(f'M{x} {top} V{top+rh*(len(rows)+1)}')
text(80,1525,'Rev. D: porte esterne evidenziate. TX = ingresso; RX = uscita; K-line = bidirezionale. Pinout U1: TI §4.',20)
# Title block
box(80,1560,2040,135);wire('M80 1605 H2120 M80 1650 H2120 M1370 1605 V1695 M1710 1605 V1695')
text(100,1591,'Cruscotto C3+AI  /  Data Logger',28,True)
text(100,1637,'Interfaccia K-line autocostruita',24,True);text(1390,1637,'REV. D',25,True);text(1730,1637,'18/10/2026',24)
text(100,1680,'C3AI-DL-KL-001 · Foglio 1/1 · Sorgente SVG modificabile',22)
text(1390,1680,'NON COLLAUDATO',21,True);text(1730,1680,'SOLO BANCO',24,True)
s.append('</svg>')
(ROOT/'schema-kline-banco.svg').write_text(''.join(s),encoding='utf-8')
