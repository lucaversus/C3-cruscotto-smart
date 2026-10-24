# Meccanica del cruscotto

- `scheda-madre-contorno.dxf`: contorno della scheda madre (178,7 × 74 mm, 6 fori Ø3),
  esportato dall'utente il 24/10/2026 dal modello 3D del cruscotto (D-045). Unità mm,
  origine al centro del lato inferiore (x da −89,3 a +89,3; y da 9 a 83). Letto da
  `tools/genera-ingombro-scheda-madre.py` per lo studio C3AI-CR-PL-001.
- `assieme-cruscotto.step`: assieme del cruscotto dell'utente (SolidWorks 2020, STEP AP214,
  24/10/2026) con frontale stampato (200,6 × 94,3 × 22 mm), scheda S3 "tft 5inch"
  (137 × 84 × 9,7), scheda madre (spessore 1,6) e due pulsanti originali.
  Posizioni ricavate (mm, assieme): S3 centrata in x a y 44,5, da z 2,4 a 12,1; scheda madre
  traslata di (0, 12, 22), quindi il retro della S3 è a circa **9,9 mm** dalla scheda madre;
  pulsanti originali in (±84,28, 44,16), ruotati di circa ±21°, con l'estremità posteriore
  a z 15,7, cioè circa **6,3 mm** davanti alla scheda madre. Valori dal modello, da
  confermare sul pezzo stampato.
