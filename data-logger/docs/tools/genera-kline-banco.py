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

s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1320" viewBox="0 0 1800 1320"><rect width="1800" height="1320" fill="white"/>']
def text(x,y,t,size=22,bold=False):
 s.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="#172b42" font-weight="{700 if bold else 400}">{escape(t)}</text>')
def wire(d):s.append(f'<path d="{d}" stroke="#263b50" stroke-width="3" fill="none"/>')
def dot(x,y):s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#263b50"/>')
def res(x,y,label,value,vertical=False):
 if vertical:
  wire(f'M{x} {y} v15 m0 50 v15');s.append(f'<rect x="{x-10}" y="{y+15}" width="20" height="50" fill="white" stroke="#263b50" stroke-width="3"/>');text(x-95 if x==1215 else x+19,y+34,label,19);text(x-95 if x==1215 else x+19,y+60,value,19)
 else:
  wire(f'M{x} {y} h15 m65 0 h15');s.append(f'<rect x="{x+15}" y="{y-10}" width="65" height="20" fill="white" stroke="#263b50" stroke-width="3"/>');text(x+10,y-40,label,19);text(x+4,y-18,value,19)
def ground(x,y):wire(f'M{x} {y} v10 m-18 0 h36 m-29 8 h22 m-16 8 h10')
text(65,75,'Interfaccia K-line autocostruita — prototipo da banco',33,True)
text(65,112,'Solo alimentazione stabilizzata 9–16 V, limitata in corrente. Nessun collegamento all’auto.',23,True)
# Transmitter section
text(70,175,'A · Trasmissione a collettore aperto',26,True)
text(85,315,'TX_INV',22,True);wire('M85 335 H220');res(220,335,'R1','330 Ω');wire('M315 335 H455');dot(380,335)
wire('M380 335 V400');res(380,400,'R2','47 kΩ',True);wire('M380 480 V500');ground(380,500)
# NPN symbol: base and separate C/E paths
wire('M455 298 V372 M455 318 L515 270 V235 M455 352 L515 397 V500')
s.append('<path d="M499 375 L513 394 L491 386 Z" fill="#263b50"/>');ground(515,500)
text(535,340,'Q1 · 2N5551',23,True);text(535,370,'E → GND',20);text(535,400,'Verificare piedini sul datasheet',18)
wire('M515 235 H720');text(645,220,'K_BENCH',22,True)
# bench pull-up independent rail near right edge
text(755,180,'VBENCH',21,True);wire('M790 190 V205');s.append('<circle cx="790" cy="211" r="5" fill="white" stroke="#263b50" stroke-width="2"/><circle cx="790" cy="238" r="5" fill="white" stroke="#263b50" stroke-width="2"/>');text(815,229,'JP1',19);wire('M790 243 V270');res(790,270,'R3','510 Ω / 1 W',True);wire('M790 350 V420');text(700,450,'K_BENCH',22,True)
text(85,555,'TX_INV basso = Q1 spento = linea rilasciata.',21)
text(85,585,'UART TX invertita; RX normale. Nessun optoisolamento.',21)
text(85,615,'JP1 chiuso solo per banco; pull-up auto da definire.',21)
# Comparator RX
text(970,175,'B · Ricezione a soglia proporzionale',26,True)
text(975,320,'K_BENCH',21,True);wire('M980 280 H1060');res(1060,280,'R4','68 kΩ');wire('M1155 280 H1300');dot(1215,280)
wire('M1215 280 V350');res(1215,350,'R5','10 kΩ',True);wire('M1215 430 V455');ground(1215,455)
# triangle inputs 3 plus, 2 minus; output 1
s.append('<path d="M1300 240 L1300 370 L1430 305 Z" fill="#eef5fa" stroke="#263b50" stroke-width="3"/>')
text(1308,284,'+',23);text(1308,346,'−',23);text(1260,271,'3',18);text(1260,366,'2',18)
wire('M1300 340 H1260 V520 H1180');text(1060,526,'VREF',22,True)
wire('M1430 305 H1500');dot(1500,305);wire('M1500 305 V250');res(1500,170,'R8','4,7 kΩ',True);wire('M1500 170 V145');text(1460,132,'3V3',22,True)
wire('M1500 305 H1530');res(1530,305,'R9','1 kΩ');wire('M1625 305 H1720');text(1640,342,'RX_3V3',21,True)
text(1415,332,'1',18);text(1320,420,'U1A · LM2903B',22,True)
text(1300,456,'Pin 8 = +5V ; pin 4 = GND',19)
text(1300,486,'Uscita open collector',19)
# Reference divider bottom left
text(70,720,'C · Riferimento e alimentazione',26,True)
text(120,775,'VBENCH',22,True);wire('M160 790 V805');res(160,805,'R6','150 kΩ',True);wire('M160 885 V915 H360');dot(160,915);text(275,897,'VREF',22,True)
wire('M160 915 V945');res(160,945,'R7','10 kΩ',True);wire('M160 1025 V1040');ground(160,1040)
text(420,795,'U1B non usato: pin 5 → GND, pin 6 → VREF, pin 7 libero.',21)
text(420,835,'C1 = 100 nF e C2 = 10 µF / 16 V fra +5V e GND, vicino a U1.',21)
text(420,875,'Tutte le reti GND sono comuni. VBENCH non è il pin VIN ESP32.',21)
text(420,915,'Soglia nominale: K ≈ 0,4875 × VBENCH. UART: 10400, 8N1.',21)
text(420,955,'Stessi nomi di rete = connessione elettrica; nessuna piedinatura auto.',21)
text(420,995,'Componenti e connessioni complete: kline-autocostruita.md.',21)
text(420,1035,'Calcoli DC superati; dinamica, guasti ed EMC NON collaudati.',22,True)
# cartiglio
s.append('<rect x="25" y="25" width="1750" height="1270" fill="none" stroke="#172b42" stroke-width="2"/><rect x="650" y="1120" width="1125" height="175" fill="white" stroke="#172b42" stroke-width="2"/>')
wire('M650 1170 H1775 M650 1225 H1775 M1190 1170 V1295 M1420 1170 V1295')
text(675,1155,'Cruscotto C3+AI — Data Logger',27,True)
text(675,1205,'K-line discreta, schema elettrico banco',22,True);text(1210,1205,'REV. A',23,True);text(1440,1205,'18/10/2026',22)
text(675,1260,'C3AI-DL-KL-001 · Foglio 1/1',22);text(1210,1260,'NON VALIDATO',18,True);text(1440,1260,'SOLO BANCO',20,True)
s.append('</svg>')
(ROOT/'schema-kline-banco.svg').write_text(''.join(s), encoding='utf-8')
