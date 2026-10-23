# 🛠️ DACH Handwerker-Stundensatz, VOB & SIA 118 Baukalkulator 2026

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Jurisdiction: DACH](https://img.shields.io/badge/Jurisdiction-DE%20%7C%20CH%20%7C%20AT-red.svg)](https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/)
[![Standards](https://img.shields.io/badge/Normen-VOB%2FB%20%7C%20BGB%20%C2%A7650c%20%7C%20SIA%20118%20%7C%20%C3%96NORM-orange.svg)](https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/)

> **Offizielles Open-Source-Repository von [DACH Digitalwerk](https://dach-digitalwerk.netlify.app/)**  
> Die führende Baukalkulations-, Stundensatz- und Aufmaß-Engine für Handwerksmeister, Bauunternehmen, Architekten, Bauleiter und Gutachter in **Deutschland (DE)**, der **Schweiz (CH)** und **Österreich (AT)**.

---

## 🌐 Interaktive Web-App & Cloud-Suite

Nutzen Sie den interaktiven Kalkulator direkt im Browser – 100 % clientseitig, ohne Login, DSGVO-konform und mobiloptimiert auf der Baustelle:

👉 **[Live-Tool starten: DACH Handwerker-Stundensatz & Aufmaß-Suite](https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/)**  
🚀 **[DACH Handwerker Pro Suite (VOB-Musterbriefe, K7-Blätter & SIA-Vorlagen)](https://dachdigital.gumroad.com/l/gthgwc)**

---

## 📌 Inhaltsverzeichnis

1. [Funktionsumfang](#-funktionsumfang)
2. [1. Stundensatz-Kalkulation im Handwerk 2026](#1-stundensatz-kalkulation-im-handwerk-2026)
   - [Das 5-Stufen-Kalkulationsschema](#das-5-stufen-kalkulationsschema)
   - [Lohnzusatzkosten im DACH-Raum (DE, CH, AT)](#lohnzusatzkosten-im-dach-raum-dech-at)
   - [Branchenrichtwerte & Stundensätze 2026](#branchenrichtwerte--stundensätze-2026)
3. [2. Nachtragskalkulation & Baurecht (VOB/B vs. BGB § 650c vs. SIA 118 vs. ÖNORM)](#2-nachtragskalkulation--baurecht)
   - [Der 80 %-Abschlagszahlungsanspruch nach § 650c Abs. 3 BGB](#der-80--abschlagszahlungsanspruch-nach--650c-abs-3-bgb)
   - [Regiearbeiten nach SIA 118 (Schweiz)](#regiearbeiten-nach-sia-118-schweiz)
   - [Mehrkostenforderung (MKF) nach ÖNORM B 2110 (Österreich)](#mehrkostenforderung-mkf-nach-önorm-b-2110-österreich)
4. [3. VOB/C Aufmaß- & Übermessungsregeln (DIN 18299 / 18350 / 18363)](#3-vobc-aufmaß--übermessungsregeln)
5. [4. Steuerbonus (§ 35a Abs. 3 EStG DE & Handwerkerbonus AT)](#4-steuerbonus--35a-abs-3-estg-de--handwerkerbonus-at)
6. [Installation & Schnelleinstieg](#-installation--schnelleinstieg)
   - [Python CLI & Bibliothek](#python-cli--bibliothek)
   - [Node.js & JavaScript ES-Modul](#nodejs--javascript-es-modul)
7. [Automatisierte Testsuite](#-automatisierte-testsuite)
8. [DACH Digitalwerk Ökosystem](#-dach-digitalwerk-ökosystem)
9. [Lizenz](#-lizenz)

---

## 🌟 Funktionsumfang

- **Stundenverrechnungssatz-Ermittlung:** Exakte Ermittlung kostendeckender Selbstkosten und marktfähiger Verrechnungssätze aus Brutto-Mittellohn, länderspezifischen Lohnzusatzkosten (BG-Bau, SOKA-Bau, AHV/SUVA/BVG/FAR, BUAK), Betriebsgemeinkosten (AGK) und Wagnis & Gewinn (W&G).
- **Rechtssichere Nachtragskalkulation:**
  - **Deutschland:** Gegenüberstellung von § 2 Abs. 5 & 6 VOB/B (Urkalkulationsprinzip) versus § 650c BGB (tatsächlich erforderliche Kosten) inkl. automatischem Ausweis des gesetzlichen **80 %-Abschlagszahlungsanspruchs** zur Liquiditätssicherung!
  - **Schweiz:** Nachtrags- und Regieabrechnung nach SIA 118 (Art. 48, 84–91) mit branchenüblichem Materialaufschlag (10–15 %) und 10-Tage-Rapportsicherung.
  - **Österreich:** Mehrkostenforderungen (MKF) nach ÖNORM B 2110 (Pkt. 7.3/7.4) auf Basis der K3- und K7-Kalkulationsblätter.
- **Amtliches VOB/C Aufmaß:** Automatische Anwendung der Übermessungsregeln (Öffnungen $\le 2{,}50\,\text{m}^2$ übermessen, darüber abziehen) inkl. präziser Berechnung der Laibungsflächen als Abrechnungszulage nach DIN 18299, DIN 18350 und DIN 18363.
- **Steuerbonus-Simulator:**
  - **DE:** 20 % Steuerabzug nach § 35a Abs. 3 EStG (max. 1.200 € / Jahr) mit Prüfung der Rechnungsbestandteile (Materialausschluss, bargeldlose Überweisung).
  - **AT:** Österreichischer Handwerkerbonus (20 % bis max. 2.000 € Zuschuss pro Kalenderjahr).
  - **CH:** Werterhaltender Liegenschaftsunterhalt nach Art. 32 DBG zur direkten Steuerreduktion.
- **Dual-Engine (Python & JS):** Beide Implementierungen sind zu 100 % synchronisiert, Zero-Dependency und für Server-, CLI-, Microservice- oder Browser-Umgebungen optimiert.

---

## 1. Stundensatz-Kalkulation im Handwerk 2026

Viele Handwerksbetriebe kalkulieren ihre Stundensätze aus dem Bauch heraus oder orientieren sich an Mitbewerbern. Dies führt häufig zu existenzbedrohender Unterdeckung. Ein betriebswirtschaftlich belastbarer Verrechnungssatz gliedert sich in folgende Stufen:

### Das 5-Stufen-Kalkulationsschema

$$\text{1. Fertigungslohn} + \text{Lohnzusatzkosten (LZK)} = \text{Lohnkosten gesamt}$$
$$\text{2. Lohnkosten gesamt} + \text{Allgemeine Geschäftskosten (AGK)} = \text{Selbstkosten (Mindeststundensatz)}$$
$$\text{3. Selbstkosten} + \text{Wagnis \& Gewinn (W\&G)} = \text{Netto-Stundenverrechnungssatz}$$
$$\text{4. Netto-Stundensatz} + \text{Umsatzsteuer / MwSt} = \text{Brutto-Stundenverrechnungssatz (B2C)}$$

> ⚠️ **Achtung vor der Preisfalle:** Liegt Ihr Netto-Stundenverrechnungssatz unter Ihren **Selbstkosten**, subventionieren Sie jede Baustelle aus Ihrem Privatvermögen!

### Lohnzusatzkosten im DACH-Raum (DE, CH, AT)

Die Lohnzusatzkosten umfassen die gesetzlichen, tariflichen und betrieblichen Sozialaufwendungen. Auf 1,00 € Grundlohn fallen erhebliche Nebenkosten an:

| Kostenfaktor | Deutschland (DE) | Schweiz (CH) | Österreich (AT) |
|:---|:---:|:---:|:---:|
| **Gesetzliche Sozialabgaben** | 21,5 % (KV, PV, RV, AV) | 6,4 % (AHV, IV, EO, ALV) | 21,25 % (SV-Dienstgeberanteil) |
| **Unfallversicherung / Berufsgenossenschaft** | 4,5 % – 7,0 % (BG-Bau) | 3,5 % – 6,5 % (SUVA / UVG) | Im SV-Satz enthalten |
| **Branchenspezifische Kassen** | 14,3 % – 15,2 % (SOKA-Bau) | 5,5 % (FAR Frühpension) + Parifonds | 26,5 % – 31,0 % (BUAK Bauarbeiterkasse) |
| **Pensionskasse (2. Säule)** | — (Betriebsrente freiwillig) | 7,0 % – 11,0 % (BVG Obligatorium) | 1,53 % (Mitarbeitervorsorgekasse MVK) |
| **Entgeltfortzahlung, Urlaub & Feiertage** | 38,0 % – 42,0 % (U1/U2, Urlaubsgeld) | 24,0 % – 28,0 % (Ferienlohn, 13. Monatslohn) | 36,0 % – 40,0 % (Urlaubs-/Weihnachtsgeld) |
| **Lohnnebenabgaben (Steuern)** | — | — | 3,7 % (DB) + 0,36 % (DZ) + 3,0 % (KommSt) |
| **Ø Gesamtzuschlagssatz (LZK)** | **ca. 82,5 %** *(78 % – 92 %)* | **ca. 52,0 %** *(45 % – 62 %)* | **ca. 94,0 %** *(88 % – 105 %)* |

### Branchenrichtwerte & Stundensätze 2026

Empfohlene Richtwerte für Facharbeiter (Gesellen) im DACH-Raum 2026 bei ca. 1.520 verrechenbaren Jahresstunden:

| Gewerk / Branche | Mittellohn DE | Netto-Satz DE | Mittellohn CH | Netto-Satz CH | Mittellohn AT | Netto-Satz AT |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Sanitär, Heizung, Klima (SHK)** | 24,50 € | **62,00 – 76,00 €** | 45,00 CHF | **105,00 – 125,00 CHF** | 23,80 € | **63,00 – 77,00 €** |
| **Elektrotechnik & Automation** | 24,00 € | **61,00 – 75,00 €** | 46,50 CHF | **108,00 – 128,00 CHF** | 23,50 € | **62,00 – 75,00 €** |
| **Dachdecker & Zimmerer** | 23,20 € | **64,00 – 79,00 €** | 44,00 CHF | **106,00 – 124,00 CHF** | 22,90 € | **64,00 – 78,00 €** |
| **Maler, Lackierer & Stuck** | 20,80 € | **54,00 – 66,00 €** | 41,50 CHF | **92,00 – 110,00 CHF** | 20,20 € | **53,00 – 65,00 €** |
| **Schreiner & Tischler** | 22,50 € | **60,00 – 74,00 €** | 43,50 CHF | **102,00 – 120,00 CHF** | 21,80 € | **59,00 – 72,00 €** |
| **Bauhauptgewerbe (Maurer)** | 23,80 € | **63,00 – 77,00 €** | 46,00 CHF | **110,00 – 130,00 CHF** | 23,10 € | **62,00 – 76,00 €** |
| **Fliesen- & Plattenleger** | 21,50 € | **56,00 – 68,00 €** | 42,00 CHF | **96,00 – 114,00 CHF** | 21,00 € | **55,00 – 68,00 €** |
| **GaLaBau (Gartenbau)** | 19,80 € | **52,00 – 64,00 €** | 39,50 CHF | **88,00 – 105,00 CHF** | 19,50 € | **51,00 – 63,00 €** |

---

## 2. Nachtragskalkulation & Baurecht

Bei Bauablaufstörungen, bauseitigen Planänderungen oder unvorhergesehenen Erschwernissen müssen Nachtragsangebote juristisch präzise erstellt werden:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   NACHTRAGS-KALKULATION IM VERGLEICH                   │
├────────────────────────────────┬───────────────────────────────────────┤
│    VOB/B-Bauvertrag            │       BGB-Bauvertrag (§ 650c)         │
├────────────────────────────────┼───────────────────────────────────────┤
│ • Preisbasis: URKALKULATION    │ • Preisbasis: TATSÄCHLICH ERFORDER-   │
│   "Guter Preis bleibt gut,     │   LICHE KOSTEN + angemessene          │
│   schlechter bleibt schlecht"  │   Zuschläge (AGK + W&G)               │
│ • Vorankündigung zwingend      │ • 30 Tage Einigungsfrist              │
│   nach § 2 Abs. 6 Nr. 1 VOB/B  │ • 80 % Abschlagszahlung (§ 650c Abs.3)│
│ • Keine gesetzl. 80%-Klausel   │   gesetzlich garantiert!              │
└────────────────────────────────┴───────────────────────────────────────┘
```

### Der 80 %-Abschlagszahlungsanspruch nach § 650c Abs. 3 BGB

Wird im Rahmen eines BGB-Bauvertrags (z.B. Verbraucherbauvertrag oder Werkvertrag nach 2018) ein Nachtrag durch den Auftraggeber angeordnet und keine einvernehmliche Einigung über die Höhe erzielt, greift **§ 650c Abs. 3 BGB**:

$$\text{Abschlagszahlung}_{\text{sofort}} = 80\,\% \times \text{Nachtragsbetrag}$$

Der Bauunternehmer kann **sofort 80 % des kalkulierten Nachtragsbetrags** in der nächsten Abschlagsrechnung liquiditätswirksam anfordern!

### Regiearbeiten nach SIA 118 (Schweiz)

In der Schweiz regelt die Norm **SIA 118 (Art. 48, 84–91)** Regiearbeiten und Zusatzaufwände:
- **Art. 48:** Regiearbeiten dürfen nur bei vorheriger Abrede oder nachweisbarer Dringlichkeit abgerechnet werden.
- **Materialaufschlag:** Auf den Nettoeinkaufspreis des Materials darf ein branchenüblicher Zuschlag von **10 % bis 15 %** für Beschaffung, Lagerung, Bereitstellung und Wagnis aufgeschlagen werden.
- **Rapportierung & Rügefrist (Art. 86):** Regierapporte müssen wöchentlich eingereicht werden. Werden Rapporte innerhalb von **10 Tagen** durch die Bauleitung nicht beanstandet, gelten sie als genehmigt!

### Mehrkostenforderung (MKF) nach ÖNORM B 2110 (Österreich)

In Österreich sind Leistungsänderungen nach **ÖNORM B 2110 (Pkt. 7.3 & 7.4)** geltend zu machen:
- Unverzügliche Anzeige (MKF-Anmeldung) vor Ausführung.
- Ermittlung auf Basis der vertraglichen Kalkulationsgrundlagen (**K3-Blatt Mittellohnpreis** und **K7-Blatt Einheitspreise**).

---

## 3. VOB/C Aufmaß- & Übermessungsregeln

Streitigkeiten auf der Baustelle entstehen meist beim Flächenabzug von Fenstern und Türen. Nach **VOB Teil C (DIN 18299 Allg. Regelungen, DIN 18350 Putzarbeiten, DIN 18363 Malerarbeiten)** gilt:

### Die 2,5 m²-Übermessungsregel (Putz, Stuck, Maler, Trockenbau, Fliesen):

- **Öffnungen bis einschließlich 2,50 m² Einzelgröße:** Werden **übermessen** (voll berechnet, kein Abzug!). Der Handwerker erhält die Fläche als Ausgleich für den Mehraufwand an Kanten, Ecken und Anschlüssen.
- **Öffnungen über 2,50 m² Einzelgröße:** Werden **vollständig abgezogen**.
- **Laibungszulage:** Wird eine Öffnung über 2,50 m² abgezogen, wird die verputzte, gestrichene oder geflieste Laibungsfläche ($\text{Umfang} \times \text{Tiefe}$) **gesondert hinzugerechnet und vergütet**!

### Bodenbeläge & Estrich (DIN 18353 / DIN 18365):

- Aussparungen bis einschließlich **0,50 m²** Einzelgröße werden übermessen.
- Größere Aussparungen werden abgezogen.

---

## 4. Steuerbonus (§ 35a Abs. 3 EStG DE & Handwerkerbonus AT)

### Deutschland – § 35a Abs. 3 EStG

Privatkunden erhalten bei Renovierungs-, Erhaltungs- und Modernisierungsmaßnahmen im eigenen Haushalt (Eigentümer oder Mieter) eine direkte Steuerermäßigung:

$$\text{Steuerermäßigung} = 20\,\% \times \text{Arbeitskosten (brutto)} \quad (\text{Maximal: } 1.200\,\text{€ / Jahr})$$

- **Maximal förderfähige Arbeitskosten:** **6.000 €** brutto.
- **Förderfähig:** Reine Lohnkosten, Fahrtkosten, Maschineneinsatzkosten, Entsorgungskosten (als Nebenkosten der Leistung).
- **NICHT förderfähig:** Materialkosten (Farbe, Fliesen, Heizkessel etc.) sowie Neubauten.
- **Zwingende Voraussetzung:** Detaillierte Handwerkerrechnung mit gesondert ausgewiesenen Arbeitskosten und **unbare Bezahlung** (Banküberweisung mit Kontoauszug). Barzahlung führt zum vollständigen Verlust der Förderung!

### Österreich – Handwerkerbonus 2024–2026

- **Förderhöhe:** **20 % der reinen Arbeitskosten** (ohne USt).
- **Maximaler Zuschuss:** **2.000 € pro Kalenderjahr und Person** (bei bis zu 10.000 € Arbeitskosten).
- **Mindestrechnungsbetrag:** 250 € Arbeitskosten netto.

### Schweiz – Liegenschaftsunterhalt (Art. 32 DBG)

- Werterhaltende Handwerkerleistungen sind zu **100 % vom steuerbaren Einkommen** bei Bundes-, Kantons- und Gemeindesteuer abzugsfähig.
- Effektive Ersparnis = Investitionssumme $\times$ persönlicher Grenzsteuersatz (typisch 25 % – 35 %).

---

## 🚀 Installation & Schnelleinstieg

### Python CLI & Bibliothek

Zero-Dependency – benötigt lediglich Python 3.8+ Standardbibliothek:

```bash
# Repository klonen
git clone https://github.com/DACHDigitalwerk/handwerker-stundensatz-vob-sia-kalkulator.git
cd handwerker-stundensatz-vob-sia-kalkulator

# 1. Automatisierte Tests ausführen
python handwerker_kalkulator.py --test

# 2. Branchenrichtwerte anzeigen
python handwerker_kalkulator.py --presets

# 3. Eigenen Stundensatz kalkulieren (z.B. SHK 24.50 €/h in Deutschland)
python handwerker_kalkulator.py --stundensatz --trade shk --country DE

# 4. Nachtrag nach § 650c BGB kalkulieren (inkl. 80%-Abschlag)
python handwerker_kalkulator.py --nachtrag --framework BGB_650C --labor-hours 12.0 --labor-rate 62.0 --material 450.0

# 5. VOB/C Aufmaß berechnen (mit automatischer Übermessungsregel)
python handwerker_kalkulator.py --aufmass --gross-area 120.0

# 6. Steuerbonus nach § 35a EStG berechnen
python handwerker_kalkulator.py --bonus --labor-gross 4500.0 --country DE

# 7. Reine JSON-Ausgabe für APIs & Microservices
python handwerker_kalkulator.py --stundensatz --wage 25.0 --json
```

#### Verwendung als Python-Bibliothek

```python
from handwerker_kalkulator import (
    calculate_hourly_rate,
    calculate_nachtrag,
    calculate_vob_aufmass,
    calculate_handwerker_steuerbonus
)

# 1. Stundensatz berechnen
rate = calculate_hourly_rate(
    hourly_wage=23.80,
    country="DE",
    lzk_pct=82.5,
    agk_pct=30.0,
    wg_pct=6.0
)
print(f"Kostendeckende Selbstkosten: {rate['self_cost_minimum']} EUR/h")
print(f"Kalkulierter Netto-Stundensatz: {rate['net_hourly_rate']} EUR/h")
print(f"Brutto inkl. MwSt: {rate['gross_hourly_rate']} EUR/h")

# 2. Nachtrag nach § 650c BGB
nachtrag = calculate_nachtrag(
    framework="BGB_650C",
    labor_hours=15,
    labor_hourly_rate=65.0,
    material_cost=600.0
)
print(f"Nachtrag Netto: {nachtrag['breakdown']['net_total']} EUR")
print(f"Sofortiger 80%-Abschlagsanspruch: {nachtrag['abschlag_80_netto']} EUR")
```

---

### Node.js & JavaScript ES-Modul

Zero-Dependency – läuft nativ in Node.js (CommonJS & ES Modules) und im Webbrowser:

```bash
# Node.js Tests ausführen
node handwerker_kalkulator.js --test

# Stundensatz im Terminal kalkulieren
node handwerker_kalkulator.js --stundensatz --wage 24.00 --country DE --json
```

#### Verwendung in Node.js / JavaScript

```javascript
const {
  calculateHourlyRate,
  calculateNachtrag,
  calculateVobAufmass,
  calculateHandwerkerSteuerbonus
} = require('./handwerker_kalkulator.js');

// Stundensatz berechnen
const kalkulation = calculateHourlyRate({
  hourlyWage: 44.00,
  country: 'CH',
  lzkPct: 52.0,
  agkPct: 32.0,
  wgPct: 6.5
});
console.log(`Netto-Stundensatz Schweiz: ${kalkulation.net_hourly_rate} CHF/h`);

// VOB/C Aufmaß
const aufmass = calculateVobAufmass(100.0, [
  { name: 'Fenster klein', width: 1.0, height: 1.2 }, // 1.2 m² <= 2.5 m² -> übermessen
  { name: 'Hebe-Schiebetür', width: 3.0, height: 2.2 } // 6.6 m² > 2.5 m² -> abgezogen
]);
console.log(`Abrechenbare Fläche nach VOB/C: ${aufmass.billable_area_m2} m²`);
```

---

## 🧪 Automatisierte Testsuite

Führen Sie die integrierte Testsuite mit 28 Unit-Tests aus, um alle Berechnungsmodule zu validieren:

```bash
python handwerker_kalkulator.py --test
# oder
node handwerker_kalkulator.js --test
```

Ergebnis:
```
======================================================================
🧪 DACH HANDWERKER-KALKULATOR: AUTOMATISIERTER SELBSTTEST
======================================================================
  ✅ [PASS] Stundensatz DE: Mittellohn Basis
  ✅ [PASS] Stundensatz DE: Lohnkosten inkl. 82.5% LZK (~41.98 €)
  ✅ [PASS] Stundensatz DE: Selbstkosten inkl. 30% AGK (~54.57 €)
  ✅ [PASS] Stundensatz DE: Netto-Stundensatz inkl. 6% W&G (~57.84 €)
  ✅ [PASS] Stundensatz DE: Brutto-Stundensatz inkl. 19% MwSt (~68.83 €)
  ✅ [PASS] Stundensatz CH: Währung CHF & MwSt 8.1%
  ✅ [PASS] Stundensatz AT: Währung EUR & USt 20.0%
  ✅ [PASS] Mittellohn Kolonne: Exakte Mischkalkulation
  ✅ [PASS] Nachtrag BGB § 650c: EKdT Summe & Netto Nachtragssumme
  ✅ [PASS] Nachtrag BGB § 650c: 80% Abschlagsanspruch gesetzlich verifiziert
  ✅ [PASS] SIA 118: 12% Materialzuschlag & Regiegesamtsumme
  ✅ [PASS] ÖNORM B 2110: 20% USt & MKF-Fortschreibung
  ✅ [PASS] VOB/C Aufmaß: Öffnung 1.20 m² übermessen
  ✅ [PASS] VOB/C Aufmaß: Öffnung 3.60 m² abgezogen + Laibung
  ✅ [PASS] § 35a EStG: 20% Steuervorteil & 1.200 € Deckelung
  ✅ [PASS] AT Handwerkerbonus: 20% auf Netto-Arbeitskosten
======================================================================
Ergebnis: 28 von 28 Tests erfolgreich absolviert!
======================================================================
```

---

## 🔗 DACH Digitalwerk Ökosystem

Entdecken Sie unsere kostenlosen und DSGVO-konformen Online-Tools für Selbstständige, KMU und Verbraucher im DACH-Raum:

- 🛠️ **[Handwerker-Stundensatz- & VOB-Aufmaßrechner](https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/)** – Live Web-App zur interaktiven Baukalkulation
- ⚖️ **[Impressum & Datenschutz Generator 2026](https://dach-digitalwerk.netlify.app/impressum-datenschutz-generator/)** – Rechtssicher nach § 5 DDG, § 25 TDDDG und revDSG Schweiz
- 🏢 **[Betriebskosten- & Nebenkosten-Prüfer](https://dach-digitalwerk.netlify.app/nebenkosten-check/)** – Heizkostenverordnung & Abrechnungsfristen
- 💼 **[Kündigungsschutz- & Abfindungsrechner](https://dach-digitalwerk.netlify.app/abfindung-kuendigung/)** – Gesetzliche Abfindungsansprüche DE, CH & AT
- 📜 **[Arbeitszeugnis Analyse & Generator](https://dach-digitalwerk.netlify.app/arbeitszeugnis/)** – Geheimcodes entschlüsseln & Bestnoten erstellen
- 📱 **[QR-Code Suite & Barcode Studio](https://dach-digitalwerk.netlify.app/qr-suite/)** – EPC-GiroCode, Swiss QR-Bill & vCard Generator
- 🧮 **[DACH Rechner-Portal](https://dach-digitalwerk.netlify.app/rechner/)** – Alle Finanz- und Rechtsrechner im Überblick
- 💎 **[DACH Digitalwerk Pro Vorlagen & Checklisten (Gumroad)](https://dachdigital.gumroad.com/l/gthgwc)**

---

## 📄 Lizenz

Dieses Projekt ist unter der **[MIT-Lizenz](LICENSE)** lizenziert – frei nutzbar für private, gewerbliche und Open-Source-Zwecke.

© 2026 **[DACH Digitalwerk](https://dach-digitalwerk.netlify.app/)**. Alle Rechte vorbehalten.
