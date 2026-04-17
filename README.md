# Realkredit Danmark Kurser — Home Assistant Integration

Custom integration der henter realkreditkurser fra [Realkredit Danmark](https://rd.dk) direkte ind i Home Assistant via deres åbne API.

## Funktioner

- Vælg frit hvilke obligationer du vil følge via UI (ingen YAML)
- To sensorer per obligation: **dagskurs** og **effektiv rente**
- Opdateres automatisk hvert 30. minut
- Understøtter alle tre lånetyper: Fast rente, Tilpasningslån og F-kort
- Fuld attribut-info: ISIN, løbetid, udbetalingskurs, status m.m.
- Kan ændres efter oprettelse via Indstillinger → Integrationer → Konfigurer
- Inkluderer klar-til-brug Lovelace dashboard med grafer

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
- `sensor.0500_rd_23s_2056_kurs` — dagskurs
- `sensor.0500_rd_23s_2056_effektiv_rente` — effektiv rente

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

## Lovelace dashboard

Repoet indeholder filen `dashboard_mushroom.yaml` — et klar-til-brug Lovelace kort med mushroom-cards, chips, farvede entity-kort og to mini-grafer der viser kursudvikling og effektiv rente over tid.

### Krav til HACS frontend-komponenter

Installer disse via **HACS → Frontend** inden du bruger dashboardet:

| Komponent | Bruges til |
|---|---|
| [mushroom-cards](https://github.com/piitaya/lovelace-mushroom) | Titel, chips og entity-kort |
| [mini-graph-card](https://github.com/kalkih/mini-graph-card) | Kursgraf over tid |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Farver og styling |

### Installation af dashboardet

1. Åbn `dashboard_mushroom.yaml` i dette repo og kopiér indholdet
2. Gå til dit HA dashboard → **Rediger → Tilføj kort → Manuelt**
3. Slet det der står og indsæt den kopierede YAML
4. Ret entity-navnene til dine egne — de følger mønsteret:  
   `sensor.RENTE_NAVN_kurs` og `sensor.RENTE_NAVN_effektiv_rente`
5. Klik **Gem**

### Eksempel på hvad dashboardet indeholder

- Chips-bar med live kurser øverst
- Farvede kort for kurs og effektiv rente per obligation
- Template-kort med status og løbetid
- Graf over kurser de seneste 7 dage
- Graf over effektiv rente de seneste 7 dage

## API

Data hentes fra RD's åbne REST API:  
`https://rd.dk/api/Rates/GetOpenOffers`

Ingen API-nøgle påkrævet.
