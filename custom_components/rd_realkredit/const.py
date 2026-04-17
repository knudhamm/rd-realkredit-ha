"""Konstanter for Realkredit Danmark integration."""

DOMAIN = "rd_realkredit"
API_URL = "https://rd.dk/api/Rates/GetOpenOffers"
SCAN_INTERVAL_MINUTES = 30

# Lånetyper
LOAN_TYPE_FAST = "01"       # Fast rente (S-serien)
LOAN_TYPE_TILPASNING = "16" # Tilpasningslån (afdragsfri)
LOAN_TYPE_FKORT = "09"      # F-kort / rentetilpasning

LOAN_TYPE_NAMES = {
    LOAN_TYPE_FAST: "Fast rente",
    LOAN_TYPE_TILPASNING: "Tilpasningslån",
    LOAN_TYPE_FKORT: "F-kort / Rentetilpasning",
}

# Attribut-navne
ATTR_NAVN = "navn"
ATTR_ISIN = "fondskode"
ATTR_NOMINEL_RENTE = "nominel_rente"
ATTR_LOEBETID = "løbetid"
ATTR_UDBETALINGSKURS = "udbetalingskurs"
ATTR_AABEN = "åben_for_tilbud"
ATTR_GRUPPE = "gruppe"
ATTR_KURS_DATO = "kurs_dato"
ATTR_SIDST_OPDATERET = "sidst_opdateret"

