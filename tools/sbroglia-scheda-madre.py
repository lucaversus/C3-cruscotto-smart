"""Sbroglio automatico della scheda madre con Freerouting (KiCad 10 + Freerouting CLI 2.5).

Uso (con il Python di KiCad, dopo tools/genera-pcb-scheda-madre.py):
  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" tools/sbroglia-scheda-madre.py <freerouting-cli.exe> [passate]
Passi: classi di rete (larghezze delle piste), piani di massa sulle due facce, esportazione Specctra
(.dsn), sbroglio con Freerouting, importazione delle piste (.ses), riempimento dei piani, salvataggio.
Freerouting (GPL-3) non è nel repository: si scarica dalla pagina delle release del progetto.
Il risultato è una prima stesura da controllare con il DRC e da rifinire, non uno sbroglio collaudato.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'cruscotto/pcb/scheda-madre/scheda-madre.kicad_pcb'
FR = Path(sys.argv[1])
PASSES = sys.argv[2] if len(sys.argv) > 2 else '40'
mm = pcbnew.FromMM

# Classi di rete: (nome, pista, distanza, via, foro, reti). Correnti stimate in scheda-madre.md.
CLASSES = [
    ('Potenza', 1.0, 0.25, 0.8, 0.4, ['VBAT_IN', 'VBAT_P', '+12V_F', '+5V', 'S3_5V', 'SW_5V', '+12V_FAN',
                                      'SPK_*', 'RADIO_*', 'S3_SPK_*', 'SPK_SERIE', 'RELAY_COIL', 'GND']),
    ('Medio', 0.5, 0.2, 0.6, 0.3, ['+3V3_AON', '+3V3_SW', '+3V3_USB', 'USB_VBUS', 'SW_3V3', 'KLINE', 'VAN_DATA*',
                                   'KEY_IN', 'U2_BOOT', 'U3_BOOT', 'CH_V3']),
]

board = pcbnew.LoadBoard(str(PCB))
ds = board.GetDesignSettings()
ns = ds.m_NetSettings
default = ns.GetDefaultNetclass()
default.SetTrackWidth(mm(0.25))
default.SetClearance(mm(0.2))
default.SetViaDiameter(mm(0.6))
default.SetViaDrill(mm(0.3))
ns.ClearNetclassPatternAssignments()
for name, w, c, vd, vh, pats in CLASSES:
    nc = pcbnew.NETCLASS(name)
    nc.SetTrackWidth(mm(w))
    nc.SetClearance(mm(c))
    nc.SetViaDiameter(mm(vd))
    nc.SetViaDrill(mm(vh))
    ns.SetNetclass(name, nc)
    for p in pats:
        ns.SetNetclassPatternAssignment(p, name)
board.SynchronizeNetsAndNetClasses(True)

# Piani di massa: un rettangolo più grande della scheda, ritagliato dal contorno al riempimento.
for z in list(board.Zones()):
    board.Remove(z)
gnd = board.FindNet('GND')
bb = board.GetBoardEdgesBoundingBox()
bb.Inflate(mm(2))
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNetCode(gnd.GetNetCode())
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                 (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        ol.Append(x, y)
    board.Add(z)

with tempfile.TemporaryDirectory() as tmp:
    dsn, ses = Path(tmp) / 'scheda-madre.dsn', Path(tmp) / 'scheda-madre.ses'
    assert pcbnew.ExportSpecctraDSN(board, str(dsn)), 'esportazione DSN non riuscita'
    r = subprocess.run([str(FR), '-de', str(dsn), '-do', str(ses), '-mp', PASSES], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    print('\n'.join(l for l in r.stdout.splitlines()[-12:]))
    assert ses.is_file(), 'Freerouting non ha prodotto la sessione .ses:\n' + r.stderr[-2000:]
    assert pcbnew.ImportSpecctraSES(board, str(ses)), 'importazione SES non riuscita'

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(str(PCB), board)
tracks = [t for t in board.GetTracks()]
print(PCB, len([t for t in tracks if t.GetClass() == 'PCB_TRACK']), 'piste,',
      len([t for t in tracks if t.GetClass() == 'PCB_VIA']), 'via')
