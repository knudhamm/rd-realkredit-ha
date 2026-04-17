# Realkredit Danmark Kurser — Home Assistant Integration

Custom integration der henter realkreditkurser fra [Realkredit Danmark](https://rd.dk) direkte ind i Home Assistant via deres åbne API.

## Funktioner

- Vælg frit hvilke obligationer du vil følge via UI (ingen YAML)
- To sensorer per obligation: **dagskurs** og **effektiv rente**
- Opdateres automatisk hvert 30. minut
- Understøtter alle tre lånetyper: Fast rente, Tilpasningslån og F-kort
- Fuld attribut-info: ISIN, løbetid, udbetalingskurs, status m.m.
- Kan ændres efter oprettelse via Indstillinger → Integrationer → Konfigurer

## Installation via HACS

1. Gå til **HACS → Integrationer → ⋮ → Brugerdefinerede arkiver**
2. Tilføj: `https://github.com/ditbrugernavn/rd-realkredit-ha`  
   Kategori: **Integration**
3. Find **Realkredit Danmark Kurser** i HACS og installer
4. Genstart Home Assistant

## Manuel installation

Kopiér mappen `custom_components/rd_realkredit/` til din HA's  
`config/custom_components/rd_realkredit/` og genstart.

## Opsætning

1. Gå til **Indstillinger → Enheder & Tjenester → + Tilføj integration**
2. Søg efter **Realkredit Danmark**
3. Vælg de obligationer du vil følge i listen  
   *(★ markerer obligationer der er åbne for tilbud)*
4. Klik **Send**

Dine sensorer oprettes med navne som:
- `sensor.rd_kurs_05_00_rd_23s_2056` — dagskurs
- `sensor.rd_rente_05_00_rd_23s_2056` — effektiv rente

## Ændre valgte obligationer

**Indstillinger → Enheder & Tjenester → Realkredit Danmark → Konfigurer**

## Sensor-attributter (kurssensor)

| Attribut | Beskrivelse |
|---|---|
| `navn` | Obligationens fulde navn |
| `fondskode` | ISIN-kode |
| `nominel_rente` | Nominel rente i % |
| `løbetid` | Lånets maksimale løbetid |
| `udbetalingskurs` | Aktuel udbetalingskurs (null hvis lukket) |
| `åben_for_tilbud` | true / false |
| `gruppe` | Fast rente / Tilpasningslån / F-kort |
| `kurs_dato` | Dato for seneste kurs |
| `sidst_opdateret` | Tidsstempel fra RD |

## Eksempel — Lovelace kort

```yaml
type: entities
title: Realkredit Danmark
entities:
  - entity: sensor.rd_kurs_05_00_rd_23s_2056
    name: Dagskurs
  - entity: sensor.rd_rente_05_00_rd_23s_2056
    name: Effektiv rente
```

## API

Data hentes fra RD's åbne REST API:  
`https://rd.dk/api/Rates/GetOpenOffers`

Ingen API-nøgle påkrævet.

