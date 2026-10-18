from pathlib import Path
from html import escape
import re
ROOT=Path(__file__).resolve().parents[1]
def txt(x,y,t,size=21,bold=False):
 return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="#172b42"'+(' font-weight="bold"' if bold else '')+f'>{escape(t)}</text>'
def line(d,color='#263b50',width=2.5):return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"/>'
def cart(w,h,code,title,rev):
 x=w-1000;y=h-205
 s=f'<g id="cartiglio"><rect x="25" y="25" width="{w-50}" height="{h-50}" fill="none" stroke="#172b42" stroke-width="2"/><rect x="{x}" y="{y}" width="975" height="180" fill="white" stroke="#172b42" stroke-width="2"/>'
 s+=line(f'M{x} {y+48} H{w-25} M{x} {y+94} H{w-25} M{x} {y+140} H{w-25} M{x+500} {y+94} V{h-25} M{x+680} {y+94} V{h-25}')
 for a,b,t,z,bo in [(x+16,y+32,'Cruscotto C3+AI',27,True),(x+16,y+79,'Sottoprogetto: Data Logger',23,False),(x+16,y+125,title,20,True),(x+515,y+125,'REV. '+rev,23,True),(x+695,y+125,'18/10/2026',22,False),(x+16,y+168,'Codice: '+code,21,False),(x+515,y+168,'Foglio 1/1',19,False),(x+695,y+168,'PRELIMINARE · NON VALIDATO',16,False)]:s+=txt(a,b,t,z,bo)
 return s+'</g>'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1600" viewBox="0 0 2000 1600"><title>Cruscotto C3+AI - Data Logger - Schema collegamenti Rev D</title><desc>Schema a livello di moduli con fili continui. Incroci senza punto non collegati. Disposizione simbolica, non posizione fisica dei connettori.</desc><rect width="2000" height="1600" fill="white"/>',txt(65,80,'SCHEMA DEI COLLEGAMENTI · BANCO USB',32,True),txt(65,120,'Illustrazioni indicative: non riproducono la piedinatura fisica. Collegare per nome GPIO / pin, verificando le serigrafie.'),txt(65,155,'Proposta GPIO per il futuro firmware. Prima del cablaggio: verificare moduli, pull-up I²C, alimentazione e batteria RTC.',20)]
def pcbrect(x,y,w,h,fill,stroke='#263b50',r=4):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def silkscreen(x,y,t,size=16,color='#ffffff'):
 s.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}">{escape(t)}</text>')
def chip(x,y,w,h,label):
 for k in range(6):
  yy=y+9+k*(h-18)/5
  pcbrect(x-8,yy,10,4,'#c5cbd1',r=0);pcbrect(x+w-2,yy,10,4,'#c5cbd1',r=0)
 pcbrect(x,y,w,h,'#20252b',r=3);silkscreen(x+7,y+h/2+5,label,13,'#d5dce4')
def box(x,y,w,h,name):
 s.append(txt(x+6,y-16,name,25,True))
 if 'ESP32' in name:
  bx=x+75;by=y+38;bw=235;bh=h-65
  pcbrect(bx,by,bw,bh,'#172830',r=17)
  # Headers: 15 contacts each; indicative locations, not a pinout.
  for side in [bx+12,bx+bw-26]:
   pcbrect(side-5,by+32,25,bh-64,'#14191e',r=2)
   for i in range(15):pcbrect(side,by+44+i*(bh-100)/14,14,14,'#c6a65c',r=1)
  pcbrect(bx+48,by+27,140,270,'#4a7848')
  s.append(line(f'M{bx+61} {by+52} h95 v16 h-80 v16 h80 v16 h-80 v16 h80','#d6bb61',5))
  pcbrect(bx+48,by+137,140,158,'#bac1c8',stroke='#6e7881',r=5)
  silkscreen(bx+60,by+182,'ESP-32D',21,'#263b50');silkscreen(bx+60,by+212,'RF MODULE',13,'#263b50')
  chip(bx+80,by+355,75,70,'USB-UART')
  for dx in [55,156]:
   pcbrect(bx+dx,by+500,30,40,'#e0e3e5');s.append(f'<circle cx="{bx+dx+15}" cy="{by+520}" r="10" fill="#252b30"/>')
  silkscreen(bx+48,by+561,'EN',14);silkscreen(bx+153,by+561,'BOOT',14)
  pcbrect(bx+75,by+bh-55,85,62,'#bbc2c9',r=7);pcbrect(bx+87,by+bh-35,61,28,'#263b50',r=3)
  silkscreen(bx+52,by+465,'HW-394 / ESP32',16)
  for i in range(7):pcbrect(bx+55+(i%3)*45,by+315+(i//3)*20,16,8,'#c6b997',r=1)
 elif 'RTC' in name:
  bx=x+100;by=y+8;bw=175;bh=h-20
  pcbrect(bx,by,bw,bh,'#185a9d',r=10)
  s.append(f'<circle cx="{bx+106}" cy="{by+90}" r="51" fill="#8e98a3" stroke="#c9d0d7" stroke-width="5"/>')
  s.append(f'<circle cx="{bx+106}" cy="{by+90}" r="42" fill="#c9cfd5"/>')
  silkscreen(bx+80,by+96,'BAT',18,'#3a4652');chip(bx+13,by+40,45,65,'RTC')
  silkscreen(bx+13,by+25,'DS3231',16);silkscreen(bx+12,by+bh-10,'I²C RTC · illustrativo',12)
 elif 'OLED' in name:
  bx=x+80;by=y+17;bw=215;bh=h-25
  pcbrect(bx,by,bw,bh,'#16518c',r=9);pcbrect(bx+12,by+15,bw-24,bh-35,'#080f18',r=4)
  silkscreen(bx+25,by+49,'DATA LOGGER',18,'#4bc5ed');silkscreen(bx+25,by+87,'SD  --  RTC',18,'#4bc5ed');silkscreen(bx+25,by+119,'STATO: BANCO',16,'#4bc5ed')
 elif 'MicroSD' in name:
  bx=x+95;by=y+22;bw=180;bh=h-35
  pcbrect(bx,by,bw,bh,'#1c6496',r=10)
  pcbrect(bx+18,by+22,144,150,'#bdc6ce',r=6)
  s.append(f'<path d="M{bx+35} {by+39} h95 l14 18 v96 h-109 Z" fill="#454c55" stroke="#8e969e" stroke-width="3"/>')
  silkscreen(bx+48,by+92,'micro',15,'#e0e5e8');silkscreen(bx+56,by+124,'SD',30,'#e0e5e8');silkscreen(bx+25,by+bh-19,'SPI · 3V3',18)
 # Mounting holes and visible passive components are illustrative.
 if 'ESP32' not in name:
  for xx,yy in [(bx+8,by+8),(bx+bw-8,by+bh-8)]:s.append(f'<circle cx="{xx}" cy="{yy}" r="5" fill="white" stroke="#c0a151" stroke-width="3"/>')

def pin(x,y,name,right=True):
 # x is edge of module; extension endpoint is +/-20
 end=x+20 if right else x-20
 s.append(line(f'M{x} {y} H{end}'));s.append(f'<circle cx="{end}" cy="{y}" r="4" fill="white" stroke="#172b42"/>')
 label_x=x-18 if right else (x-220 if x==560 else x-125)
 s.append(txt(label_x,y-9,name,18))
 # Leader connects the symbolic terminal to the illustrated PCB edge.
 board_edge=870 if x==960 else 635 if x==560 else (1530 if y<480 else 1510 if y<750 else 1525) if x==1430 else (1705 if y<480 else 1725 if y<750 else 1705)
 s.append(line(f'M{x} {y} H{board_edge}','#607589',1.8))
 return end,y
P='#b42318';G='#17633b';D='#145ca3';C='#a85d00'
box(560,280,400,800,'U1 · ESP32 HW-394')

for y,n in [(310,'3V3'),(380,'GPIO21 · SDA'),(420,'GPIO22 · SCL'),(860,'GPIO18 · SCK'),(900,'GPIO23 · MOSI'),(940,'GPIO19 · MISO'),(980,'GPIO27 · CS'),(1040,'GND')]:pin(960,y,n)
for y,n in [(880,'GPIO32 · pagina'),(1000,'GPIO33 · conferma')]:pin(560,y,n,False)
for y,h,name in [(280,200,'U2 · RTC DS3231'),(520,200,'U3 · OLED I²C'),(800,260,'U4 · MicroSD SPI 3,3 V')]:box(1430,y,370,h,name)
for y in [380,620]:pin(1430,y,'SDA',False)
for y in [420,660]:pin(1430,y,'SCL',False)
for y,n in [(860,'CLK / SCK'),(900,'MOSI / DI'),(940,'MISO / DO'),(980,'CS')]:pin(1430,y,n,False)
for y,n in [(310,'VCC'),(550,'VCC'),(830,'3V3'),(450,'GND'),(690,'GND'),(1030,'GND')]:pin(1800,y,n)
# Continuous power and ground buses; branches marked with junction dots.
s.append(line('M980 310 H1000 V205 H1860 V830',P))
s.append(line('M980 1040 H1000 V1180 H1910 V450',G))
for yy in [310,550,830]:
 s.append(line(f'M1820 {yy} H1860',P));s.append(f'<circle cx="1860" cy="{yy}" r="5" fill="{P}"/>')
for yy in [450,690,1030]:
 s.append(line(f'M1820 {yy} H1910',G));s.append(f'<circle cx="1910" cy="{yy}" r="5" fill="{G}"/>')
s.append(txt(1460,194,'+3V3 · corrente del regolatore da verificare',20))
# Shared I2C buses.
s.append(line('M980 380 H1410 M1050 380 V620 H1410',D))
s.append(line('M980 420 H1410 M1100 420 V660 H1410',C))
for x,y,col in [(1050,380,D),(1100,420,C)]:s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{col}"/>')
s.append(txt(1160,365,'SDA',19));s.append(txt(1160,406,'SCL',19))
for yy,n in [(860,'SCK'),(900,'MOSI'),(940,'MISO'),(980,'CS')]:s.append(line(f'M980 {yy} H1410',D));s.append(txt(1160,yy-10,n,19))
# Optional switches, normally open. All returns join ground outside the modules.
for yy,label in [(880,'S1 · PAGINA'),(1000,'S2 · CONFERMA')]:
 s.append(txt(160,yy-42,label,22,True));s.append(line(f'M540 {yy} H330 M285 {yy} H100 M330 {yy} L290 {yy-25}'))
 for xx in [285,330]:s.append(f'<circle cx="{xx}" cy="{yy}" r="5" fill="white" stroke="#172b42"/>')
 s.append(f'<circle cx="100" cy="{yy}" r="5" fill="{G}"/>')
 pcbrect(267,yy-28,75,56,'#8896a3',r=5)
 s.append(f'<circle cx="304" cy="{yy}" r="21" fill="#232d37" stroke="#4a5965" stroke-width="3"/>')
s.append(line('M100 880 V1180 H1000',G));s.append(f'<circle cx="1000" cy="1180" r="5" fill="{G}"/>');s.append(txt(150,1165,'GND comune',20))
import textwrap
note_lines=['NOTE DI PROGETTO']
for note in ['Pulsanti opzionali NO: INPUT_PULLUP e antirimbalzo nel firmware.', 'I²C: verificare pull-up montate e valore equivalente; solo verso 3,3 V.', 'RTC: SQW / 32K non collegati. Verificare ricarica prima della batteria.', 'MicroSD: verificare picchi di corrente e disaccoppiamento.', 'Firmware 0.1.0: solo seriale; GPIO non ancora configurati.']:
 note_lines.extend(textwrap.wrap('• '+note,width=43))
 note_lines.append('')
for i,t in enumerate(note_lines):s.append(txt(70,245+i*27,t,18,i==0))

for i,t in enumerate(['AUTO — COLLEGAMENTI ANCORA DA DEFINIRE','OBD: verificare i moduli CAN esistenti; BSI: protocollo e punto di accesso da identificare.','Alimentazione 12 V: convertitore automotive, fusibile e protezioni da dimensionare.','Nessun collegamento diretto auto → GPIO. La sezione auto sarà completata dopo le verifiche.']):s.append(txt(70,1230+i*33,t,21,i==0))
s.append(txt(65,1435,'LEGENDA',21,True));s.append(txt(65,1475,'Punto pieno = giunzione elettrica.',20));s.append(txt(65,1510,'Incrocio senza punto = nessun contatto.',20));s.append(txt(65,1545,'Rosso: 3V3 · verde: GND · altri: segnali.',20))
s.append(cart(2000,1600,'C3AI-DL-EL-001','Collegamenti con moduli illustrati','D'));s.append('</svg>')
(ROOT/'schema-collegamenti.svg').write_text('\n'.join(s),encoding='utf-8')
# Existing block drawing: preserve original artwork, add margin and shared title block.
f=ROOT/'schema-sistema.svg';old=f.read_text(encoding='utf-8')
if 'id="cartiglio"' not in old:
 old=re.sub(r'height="1100"','height="1380"',old,count=1);old=old.replace('viewBox="0 0 1600 1100"','viewBox="0 0 1600 1380"')
 old=old.replace('</svg>',cart(1600,1380,'C3AI-DL-BL-001','Architettura funzionale del sistema','B')+'</svg>');f.write_text(old,encoding='utf-8')
import xml.etree.ElementTree as ET
for f in ROOT.glob('*.svg'):ET.parse(f)
print('SVG generati e XML validato')
