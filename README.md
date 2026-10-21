# Produktsammenligner

Sammenlign 2–4 Elkjøp-produkter (varekode eller lenke). To faner:

- **Anbefaling** – kunden velger hva som er viktigst, appen anbefaler.
- **Funksjoner og bruk** – viktigste forskjeller, funksjoner (✓/✕), hvem
  passer hvilket produkt til, fordeler/ulemper og «Velg X hvis …».

## Kjør

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

## Struktur

```
main.py                      starter appen
src/models.py                felles dataklasser
src/text.py                  æøå, enheter, desimalkomma
src/fetching/                VAREHENTING – varekode/lenke → produkt
src/categories/              KATEGORIGUIDE
  guide.py                     25 kategorier og hvilke spesifikasjoner som teller
  scenarios.py                 bruksområder per kategori («Brød og tunge deiger» …)
  detector.py                  finner kategori fra URL, navn og produkttype
  validation.py                sjekker at hele guiden henger sammen
src/comparison/              SAMMENLIGNING (fanen «Anbefaling»)
  spec_matcher.py              finner riktig spesifikasjon (med typesjekk)
  fallback_extractor.py        henter fra produktnavn og beskrivelse
  scorer.py, summarizer.py     poeng, sammendrag, konklusjon
src/insights/                INNSIKT (fanen «Funksjoner og bruk»)
src/ui/                      GRENSESNITT
tools/diagnose.py            feilsøk én vare: python -m tools.diagnose 457340
tests/                       python -m pytest
  real_pages.py                ekte etiketter fra Elkjøp – oppdater ved endringer
```

## Når noe er feil

1. `python -m tools.diagnose <varekode>` viser hva som ble funnet og hvor.
2. Juster mønsteret i `src/categories/guide.py`.
3. `python -m pytest` – testene sjekker alle kategorier, ikke bare den du endret.
