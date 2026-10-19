"""Schema vettoriale riproducibile del banco logger, pin da hardware.json."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'data-logger/docs/hardware.json').read_text(encoding='utf-8'))['wiring_proposal']['pins']
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1320" viewBox="0 0 1800 1320">',
         '<title>Cruscotto C3+AI — Data Logger — Collegamenti banco 0.3.0</title>',
         '<rect width="1800" height="1320" fill="white"/>',
         '<g font-family="Arial, sans-serif" fill="#172b42">']

def rect(x,y,w,h,fill,stroke='#24384c',radius=0):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

def text(x,y,value,size=21,color='#172b42',bold=False):
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{"bold" if bold else "normal"}">{html.escape(str(value))}</text>')

def wire(path,color,width=3):
    parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')

def dot(x,y,color,r=5):
    parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

def holes(x,y,w,h):
    for a,b in [(x+14,y+14),(x+w-14,y+14),(x+14,y+h-14),(x+w-14,y+h-14)]:
        parts.append(f'<circle cx="{a}" cy="{b}" r="7" fill="white" stroke="#9aa8b0" stroke-width="3"/>')

VCC='#bd2834'; GND='#283b4a'; SDA='#167b45'; SCL='#2566c0'
text(55,65,'COLLEGAMENTI PER LA PRIMA PROVA A BANCO',33,bold=True)
text(55,105,'Firmware 0.3.0 · profilo esp32-hw394-logger · alimentazione soltanto USB',24)
text(55,140,'Pin disposti per leggibilità: usare le serigrafie dei pezzi, non la posizione nel disegno.',21)

# ESP32 illustrated PCB. GPIO ordering is logical, explicitly not a footprint.
rect(110,240,390,780,'#173d36',radius=16); holes(110,240,390,780)
rect(176,320,255,355,'#bac2c6',radius=8)
text(198,390,'ESP-32D',29,bold=True)
text(196,433,'ESP32 HW-394',23)
text(198,475,'30 pin / 4 MB',20)
for dy in range(5):
    wire(f'M205 {540+dy*19} h170', '#73858e', 5)
rect(218,730,150,100,'#1e242b',radius=3)
text(238,790,'CH340',22,'#e0e7ed')
for y in range(280,980,38):
    rect(122,y,15,15,'#cbb77b'); rect(473,y,15,15,'#cbb77b')
rect(239,1000,128,50,'#c4c9ce',radius=5)
wire('M303 1050 V1110 H150',GND,9)
text(70,1145,'USB verso PC',22,bold=True)
text(140,219,'HW-ESP32',25,bold=True)

# Continuous supply rails, separated from signal wiring.
wire('M500 280 H555 V175 H1640 V980',VCC)
wire('M500 310 H585 V205 H1710 V1080',GND)
text(1445,168,'3V3',21,VCC,True); text(1625,200,'GND',21,GND,True)
text(415,272,'3V3',20,'#ffb7bd',True); text(415,304,'GND',20,'white',True)

# MicroSD module and six labelled contacts.
rect(1100,240,435,285,'#16699a',radius=7); holes(1100,240,435,285)
text(1110,234,'HW-SD-MODULE · MicroSD SPI',23,bold=True)
rect(1230,290,205,155,'#abb8c1',radius=5)
rect(1273,410,120,90,'#20282f',radius=3)
text(1288,461,'microSD',19,'white')
for pin,y in [('MOSI',340),('CLK',380),('MISO',420),('CS',460)]:
    dot(1100,y,'#d1b975'); text(1115,y-7,pin,18,'white')
for pin,y,color,rail in [('3V3',270,VCC,1640),('GND',310,GND,1710)]:
    dot(1535,y,'#d1b975'); text(1465,y-8,pin,19,'white');wire(f'M1535 {y} H{rail}',color);dot(rail,y,color)
for key,y,label,color in [('kMosi',340,'MOSI','#b47112'),('kSck',380,'CLK','#8b4caa'),('kMiso',420,'MISO','#147e8c'),('kSdCs',460,'CS','#bd6b25')]:
    wire(f'M500 {y} H1100',color)
    text(520,y-10,f'GPIO{PINS[key]} → {label}',21,color,True)

# RTC DS3231, visible IC and unused SQW/32K explicitly marked.
text(1110,570,'HW-RTC · DS3231',25,bold=True)
rect(1100,590,435,170,'#176d9e',radius=7);holes(1100,590,435,170)
rect(1260,620,138,100,'#252b32',radius=3)
for y in range(630,710,12):
    wire(f'M1245 {y} H1260 M1398 {y} H1413','#b7bec4',5)
text(1270,660,'DS3231',20,'white')
text(1270,690,'RTC',19,'#c5d7dc')
for pin,y,c in [('SDA',650,SDA),('SCL',700,SCL)]:
    dot(1100,y,'#d1b975');text(1115,y-8,pin,18,'white')
for pin,y,c,rail in [('VCC',620,VCC,1640),('GND',660,GND,1710)]:
    dot(1535,y,'#d1b975');text(1465,y-8,pin,18,'white');wire(f'M1535 {y} H{rail}',c);dot(rail,y,c)
text(1130,747,'SQW e 32K: non collegati',19,'white')

# OLED illustrated module, not a claim of controller identification.
text(1110,807,'HW-OLED · I2C',25,bold=True)
rect(1100,825,435,170,'#24292f',radius=7);holes(1100,825,435,170)
rect(1222,849,208,111,'#080f18',stroke='#8ca1ab',radius=2)
text(1232,891,'C3+AI LOGGER',18,'#59cee8')
text(1232,922,'STATO / RIGHE',17,'#59cee8')
for pin,y,c in [('SDA',880,SDA),('SCL',930,SCL)]:
    dot(1100,y,'#d1b975');text(1115,y-8,pin,18,'white')
for pin,y,c,rail in [('VCC',850,VCC,1640),('GND',890,GND,1710)]:
    dot(1535,y,'#d1b975');text(1465,y-8,pin,18,'white');wire(f'M1535 {y} H{rail}',c);dot(rail,y,c)

# Shared I2C buses, joined only at marked junctions.
wire('M500 650 H865 V880 H1100',SDA);wire('M865 650 H1100',SDA);dot(865,650,SDA)
wire('M500 700 H935 V930 H1100',SCL);wire('M935 700 H1100',SCL);dot(935,700,SCL)
text(520,630,f'GPIO{PINS["kSda"]} → SDA comune',21,SDA,True)
text(520,740,f'GPIO{PINS["kScl"]} → SCL comune',21,SCL,True)
text(540,790,'Incrocio senza punto = nessun contatto',18)

# Normally-open STOP, no series interruption of power.
wire('M500 975 H715 V1060 H830 M935 1060 H1710',GND)
dot(1710,1060,GND)
dot(830,1060,GND);dot(935,1060,GND)
wire('M830 1060 L920 1025 M880 1027 V1000',GND)
text(525,959,f'GPIO{PINS["kStopPin"]}',21,bold=True)
text(1005,1050,'STOP · normalmente aperto',23,bold=True)
text(1005,1081,'Premuto: collega GPIO32 a GND',20)

# Notes and full title block.
text(60,1190,'Collegare a USB scollegata. Moduli alimentati a 3,3 V, masse in comune.',21,bold=True)
text(60,1223,'RTC: lasciare fuori la CR2032 finché il ramo di ricarica non è disabilitato (D-019).',19)
text(60,1255,'Per questo banco: MCP2515, VP230, K-line e tutti i fili auto scollegati.',19)
rect(25,25,1750,1270,'none')
rect(1010,1125,740,145,'white')
wire('M1010 1172 H1750 M1010 1220 H1750 M1430 1220 V1270',GND,2)
text(1025,1157,'Cruscotto C3+AI · Data Logger',25,bold=True)
text(1025,1204,'Collegamenti banco · Firmware 0.3.0',22)
text(1025,1249,'C3AI-DL-EL-003 · REV A',21,bold=True)
text(1445,1242,'19/10/2026 · 1/1',19)
text(1445,1263,'PROPOSTO / NON COLLAUDATO',14)
parts.extend(['</g>','</svg>'])
out=ROOT/'data-logger/docs/collegamenti-banco-030.svg'
out.write_text('\n'.join(parts)+'\n',encoding='utf-8')
print(out)
