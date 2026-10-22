# Endringer 7 – viktigste spesifikasjoner for alle produkttyper

## Hva er nytt
- **Grafikkort og prosessor rangeres.** Ny fil `src/comparison/hardware.py` gir omtrentlig ytelsespoeng
  for GPU (RTX 20–50, Radeon RX 6000–9000, Intel Arc) og CPU (Intel Core i/Ultra/Core 3-5-7, Ryzen, Apple M,
  mobilbrikker). Vinner kåres bare når forskjellen er tydelig – ellers «Likt».
- **Prosessor vises med modellnummer**: «Intel Core i7» + «Nummer: 14700F» → «Intel Core i7 14700F» (ny `append` i guiden).
- **Stasjonære PC-er**: grafikkort først, så grafikkminne, prosessor, kjerner, RAM, maks RAM, lagring, strømforsyning, kjøling.
- **TV, vaskemaskin, tørketrommel, hodetelefoner, kaffemaskin, kamera** gjennomgått med ekte Elkjøp-etiketter
  (bl.a. Bildepanelfrekvens, Panelscore, HDMI-standard, VRR/ALLM, lydnivå sentrifugering, varmepumpe, ANC-batteritid,
  melkefunksjon, vannbeholder «(I)»).
- **Knapp**: «Gi anbefaling →» vises bare første gang. Deretter brukes «Endre», og anbefalingen oppdateres med en gang du endrer et nivå.
- Fargene fra abonnementskalkulatoren og meldingen «Produkt A er …, kan ikke sammenlignes.» er tatt med.
- `use_container_width` er byttet til `width="stretch"` (Streamlit fjerner den gamle). Krever streamlit 1.46+.

## Tester
559 tester består (nye: ekte sider for 2 gaming-PC-er, TV, vaskemaskin, tørketrommel, hodetelefoner, kaffemaskin,
CPU/GPU-rangering, og at hver kategori har minst tre sammenlignbare spesifikasjoner).
