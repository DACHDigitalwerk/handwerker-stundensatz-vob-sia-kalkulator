#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🛠️ DACH Handwerker-, Baukalkulations- & Aufmaß-Suite 2026
================================================================================
Professionelle Baukalkulation nach VOB/B, VOB/C, BGB § 650c, SIA 118 & ÖNORM B 2110
für Handwerksbetriebe und Bauunternehmer in Deutschland, der Schweiz und Österreich.

Enthaltene Berechnungsmodule:
  1. Stundensatz-Kalkulation (Mittellohn, Lohnzusatzkosten DE/CH/AT, AGK, W&G)
  2. Nachtragskalkulation (§ 2 VOB/B vs. § 650c BGB, SIA 118, ÖNORM B 2110 + 80%-Abschlag)
  3. VOB/C Aufmaß-Rechner (Übermessungsregeln DIN 18299, 18350, 18363, Laibungszulagen)
  4. Steuerbonus-Rechner (§ 35a Abs. 3 EStG DE, AT Handwerkerbonus, CH Liegenschaftsunterhalt)

Website: https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/
Lizenz: MIT
Copyright (c) 2026 DACH Digitalwerk
================================================================================
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any, Optional, Tuple

# ============================================================================
# KONSTANTEN & BRANCHEN-BENCHMARKS (STAND 2026)
# ============================================================================

# Mehrwertsteuer / Umsatzsteuer Normalsätze
TAX_RATES = {
    "DE": 0.19,     # 19.0% Deutschland
    "CH": 0.081,    #  8.1% Schweiz (seit 01.01.2024)
    "AT": 0.20      # 20.0% Österreich
}

# Währungskennzeichen
CURRENCIES = {
    "DE": "EUR",
    "CH": "CHF",
    "AT": "EUR"
}

# Standard-Lohnzusatzkosten (LZK / Sozialaufwand) in %
DEFAULT_LZK = {
    "DE": 82.5,     # Gesetzl. SV (21.5%) + BG-Bau (5.5%) + SOKA-Bau (14.5%) + Lohnfortzahlung (41.0%)
    "CH": 52.0,     # AHV/IV/EO/ALV (6.4%) + BVG (8.5%) + SUVA (4.8%) + FAR (5.5%) + Ferien/13. (26.8%)
    "AT": 94.0      # SV-DGA (21.25%) + DB/DZ/KommSt (7.06%) + BUAK (26.5%) + Sonderzahlungen/Urlaub (39.19%)
}

# Branchenprofile im DACH-Handwerk (Lohn- und Zuschlags-Richtwerte 2026)
TRADE_PRESETS = {
    "shk": {
        "name": "Sanitär, Heizung, Klima (SHK)",
        "DE": {"hourly_wage": 24.50, "lzk_pct": 82.0, "agk_pct": 32.0, "wg_pct": 6.5},
        "CH": {"hourly_wage": 45.00, "lzk_pct": 52.0, "agk_pct": 34.0, "wg_pct": 7.0},
        "AT": {"hourly_wage": 23.80, "lzk_pct": 93.0, "agk_pct": 33.0, "wg_pct": 6.5}
    },
    "elektro": {
        "name": "Elektrotechnik / Gebäudeautomation",
        "DE": {"hourly_wage": 24.00, "lzk_pct": 80.0, "agk_pct": 30.0, "wg_pct": 7.0},
        "CH": {"hourly_wage": 46.50, "lzk_pct": 50.0, "agk_pct": 32.0, "wg_pct": 7.5},
        "AT": {"hourly_wage": 23.50, "lzk_pct": 92.0, "agk_pct": 31.0, "wg_pct": 6.5}
    },
    "maler": {
        "name": "Maler & Lackierer / Stuckateur",
        "DE": {"hourly_wage": 20.80, "lzk_pct": 85.0, "agk_pct": 28.0, "wg_pct": 6.0},
        "CH": {"hourly_wage": 41.50, "lzk_pct": 53.0, "agk_pct": 29.0, "wg_pct": 6.5},
        "AT": {"hourly_wage": 20.20, "lzk_pct": 96.0, "agk_pct": 28.5, "wg_pct": 6.0}
    },
    "dachdecker": {
        "name": "Dachdecker & Spengler / Zimmerer",
        "DE": {"hourly_wage": 23.20, "lzk_pct": 88.0, "agk_pct": 34.0, "wg_pct": 7.5},
        "CH": {"hourly_wage": 44.00, "lzk_pct": 56.0, "agk_pct": 35.0, "wg_pct": 8.0},
        "AT": {"hourly_wage": 22.90, "lzk_pct": 98.0, "agk_pct": 34.0, "wg_pct": 7.5}
    },
    "tischler": {
        "name": "Schreiner / Tischler / Innenausbau",
        "DE": {"hourly_wage": 22.50, "lzk_pct": 79.0, "agk_pct": 36.0, "wg_pct": 6.5},
        "CH": {"hourly_wage": 43.50, "lzk_pct": 51.0, "agk_pct": 36.0, "wg_pct": 7.0},
        "AT": {"hourly_wage": 21.80, "lzk_pct": 91.0, "agk_pct": 35.0, "wg_pct": 6.5}
    },
    "bauhaupt": {
        "name": "Bauhauptgewerbe (Maurer, Betonbauer)",
        "DE": {"hourly_wage": 23.80, "lzk_pct": 89.0, "agk_pct": 26.0, "wg_pct": 6.0},
        "CH": {"hourly_wage": 46.00, "lzk_pct": 58.5, "agk_pct": 28.0, "wg_pct": 6.5},
        "AT": {"hourly_wage": 23.10, "lzk_pct": 99.0, "agk_pct": 27.0, "wg_pct": 6.0}
    },
    "fliesen": {
        "name": "Fliesen-, Platten- & Mosaikleger",
        "DE": {"hourly_wage": 21.50, "lzk_pct": 83.0, "agk_pct": 29.0, "wg_pct": 6.5},
        "CH": {"hourly_wage": 42.00, "lzk_pct": 52.0, "agk_pct": 30.0, "wg_pct": 7.0},
        "AT": {"hourly_wage": 21.00, "lzk_pct": 95.0, "agk_pct": 29.5, "wg_pct": 6.5}
    },
    "galabau": {
        "name": "Garten- und Landschaftsbau (GaLaBau)",
        "DE": {"hourly_wage": 19.80, "lzk_pct": 76.0, "agk_pct": 31.0, "wg_pct": 6.5},
        "CH": {"hourly_wage": 39.50, "lzk_pct": 49.0, "agk_pct": 32.0, "wg_pct": 7.0},
        "AT": {"hourly_wage": 19.50, "lzk_pct": 89.0, "agk_pct": 30.0, "wg_pct": 6.5}
    }
}


# ============================================================================
# 1. MODUL: STUNDENSATZ-KALKULATION (HOURLY RATE CALCULATION)
# ============================================================================

def calculate_mittellohn(workers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Berechnet den gewichteten Mittellohn (Fertigungslohn) einer Kolonne.
    workers: Liste von Dictionaries mit 'title', 'hourly_wage', 'count'
    Beispiel:
      [
        {"title": "Vorarbeiter/Meister", "hourly_wage": 28.50, "count": 1},
        {"title": "Facharbeiter/Geselle", "hourly_wage": 23.00, "count": 2},
        {"title": "Bauhelfer", "hourly_wage": 17.50, "count": 1}
      ]
    """
    total_wage_sum = 0.0
    total_count = 0.0

    for w in workers:
        count = float(w.get("count", 1))
        wage = float(w.get("hourly_wage", 0.0))
        total_wage_sum += wage * count
        total_count += count

    if total_count <= 0:
        raise ValueError("Gesamtzahl der Arbeitskräfte muss größer als 0 sein.")

    mittellohn = total_wage_sum / total_count
    return {
        "total_workers": total_count,
        "total_wage_sum": round(total_wage_sum, 2),
        "mittellohn": round(mittellohn, 2),
        "workers": workers
    }


def calculate_produktivstunden(
    total_calendar_days: int = 365,
    weekend_days: int = 104,
    public_holidays: int = 11,
    vacation_days: int = 30,
    sick_days: int = 14,
    hours_per_day: float = 8.0,
    unproductive_pct: float = 12.0
) -> Dict[str, Any]:
    """
    Berechnet die tatsächlich abrechenbaren (produktiven) Arbeitsstunden pro Mitarbeiter und Jahr.
    """
    working_days = total_calendar_days - (weekend_days + public_holidays + vacation_days + sick_days)
    presence_hours = working_days * hours_per_day
    unproductive_hours = presence_hours * (unproductive_pct / 100.0)
    productive_hours = presence_hours - unproductive_hours

    return {
        "total_calendar_days": total_calendar_days,
        "non_working_days": weekend_days + public_holidays + vacation_days + sick_days,
        "working_days": working_days,
        "presence_hours": round(presence_hours, 1),
        "unproductive_pct": unproductive_pct,
        "unproductive_hours": round(unproductive_hours, 1),
        "productive_hours_per_year": round(productive_hours, 1)
    }


def calculate_hourly_rate(
    hourly_wage: float,
    country: str = "DE",
    lzk_pct: Optional[float] = None,
    agk_pct: float = 30.0,
    wg_pct: float = 6.0,
    productive_hours: float = 1520.0,
    annual_overhead_fixed: Optional[float] = None
) -> Dict[str, Any]:
    """
    Kalkuliert den kostendeckenden Selbstkostensatz und den kalkulatorischen
    Stundenverrechnungssatz (netto & brutto) für Handwerk und Bau.

    Parameter:
      - hourly_wage: Mittellohn / Bruttolohn pro Fertigungsstunde (€ oder CHF)
      - country: 'DE', 'CH', oder 'AT'
      - lzk_pct: Lohnzusatzkosten in % (falls None, Standardwert für Land)
      - agk_pct: Allgemeine Geschäftskosten / Betriebsgemeinkosten in % auf Fertigungskosten
      - wg_pct: Wagnis & Gewinn in % auf Selbstkosten
      - productive_hours: Jahresproduktivstunden pro Mitarbeiter (Default 1520 h)
      - annual_overhead_fixed: Optional feste Gemeinkosten pro Mitarbeiter/Jahr (übersteuert agk_pct)
    """
    country = country.upper()
    if country not in TAX_RATES:
        raise ValueError(f"Ungültiges Land '{country}'. Erlaubt sind DE, CH, AT.")

    curr = CURRENCIES[country]
    tax_rate = TAX_RATES[country]

    if lzk_pct is None:
        lzk_pct = DEFAULT_LZK[country]

    # 1. Fertigungslohn & Lohnzusatzkosten
    wage = float(hourly_wage)
    lzk_amount = wage * (lzk_pct / 100.0)
    direct_labor_cost = wage + lzk_amount  # Fertigungslohnkosten je Stunde

    # 2. Betriebsgemeinkosten (BGK / AGK)
    if annual_overhead_fixed is not None and annual_overhead_fixed > 0:
        agk_amount = annual_overhead_fixed / productive_hours
        effective_agk_pct = (agk_amount / direct_labor_cost) * 100.0
    else:
        agk_amount = direct_labor_cost * (agk_pct / 100.0)
        effective_agk_pct = agk_pct

    # 3. Selbstkosten (Kostendeckender Mindeststundensatz)
    self_cost = direct_labor_cost + agk_amount

    # 4. Wagnis & Gewinn (W&G)
    wg_amount = self_cost * (wg_pct / 100.0)

    # 5. Kalkulatorischer Verrechnungssatz (Netto)
    net_rate = self_cost + wg_amount

    # 6. Verrechnungssatz Brutto inkl. MwSt
    tax_amount = net_rate * tax_rate
    gross_rate = net_rate + tax_amount

    # 7. Wirtschaftlichkeits-Kennzahlen
    daily_rate_net = net_rate * 8.0
    monthly_break_even_turnover = (self_cost * productive_hours) / 12.0
    monthly_target_turnover = (net_rate * productive_hours) / 12.0

    return {
        "country": country,
        "currency": curr,
        "tax_rate_pct": round(tax_rate * 100.0, 1),
        "base_wage": round(wage, 2),
        "lzk_pct": round(lzk_pct, 2),
        "lzk_amount": round(lzk_amount, 2),
        "direct_labor_cost": round(direct_labor_cost, 2),
        "agk_pct": round(effective_agk_pct, 2),
        "agk_amount": round(agk_amount, 2),
        "self_cost_minimum": round(self_cost, 2),
        "wg_pct": round(wg_pct, 2),
        "wg_amount": round(wg_amount, 2),
        "net_hourly_rate": round(net_rate, 2),
        "gross_hourly_rate": round(gross_rate, 2),
        "tax_amount": round(tax_amount, 2),
        "daily_rate_net_8h": round(daily_rate_net, 2),
        "monthly_break_even_turnover": round(monthly_break_even_turnover, 2),
        "monthly_target_turnover": round(monthly_target_turnover, 2),
        "productive_hours_year": productive_hours
    }


# ============================================================================
# 2. MODUL: NACHTRAGSKALKULATION (VARIATION & CHANGE ORDER)
# ============================================================================

def calculate_nachtrag(
    framework: str,
    labor_hours: float,
    labor_hourly_rate: float,
    material_cost: float = 0.0,
    equipment_cost: float = 0.0,
    subcontractor_cost: float = 0.0,
    agk_pct: float = 20.0,
    wg_pct: float = 6.0,
    material_surcharge_pct: Optional[float] = None,
    description: str = "Nachtragsleistung"
) -> Dict[str, Any]:
    """
    Kalkuliert ein Nachtragsangebot nach geltenden Baurechts-Standards:
      - 'VOB_B': § 2 Abs. 5 (Änderung) & § 2 Abs. 6 (Zusatzleistung) VOB/B (Urkalkulationsprinzip)
      - 'BGB_650C': § 650c BGB (Tatsächlich erforderliche Kosten + 80% Abschlagsanspruch)
      - 'SIA_118': SIA 118 Art. 48/84-91 Regiearbeiten (Schweiz, Materialzuschlag)
      - 'OENORM_B2110': ÖNORM B 2110 Pkt. 7.3/7.4 Mehrkostenforderung MKF (Österreich)
    """
    framework = framework.upper()
    valid_frameworks = ["VOB_B", "BGB_650C", "SIA_118", "OENORM_B2110"]
    if framework not in valid_frameworks:
        raise ValueError(f"Ungültiger Standard '{framework}'. Erlaubt: {valid_frameworks}")

    country = "CH" if framework == "SIA_118" else ("AT" if framework == "OENORM_B2110" else "DE")
    currency = CURRENCIES[country]
    tax_rate = TAX_RATES[country]

    if material_surcharge_pct is None:
        material_surcharge_pct = 12.0 if framework == "SIA_118" else 0.0

    # 1. Einzelkosten der Teilleistungen (EKdT)
    direct_labor = labor_hours * labor_hourly_rate

    # Materialkosten inkl. branchenüblichem Beschaffungs-/Lagerzuschlag (besonders relevant bei SIA 118 Regie)
    mat_surcharge = material_cost * (material_surcharge_pct / 100.0) if material_surcharge_pct > 0 else 0.0
    effective_material = material_cost + mat_surcharge
    total_ekdt = direct_labor + effective_material + equipment_cost + subcontractor_cost

    # 2. Zuschläge für Gemeinkosten und Gewinn
    agk_amount = total_ekdt * (agk_pct / 100.0)
    cost_basis = total_ekdt + agk_amount
    wg_amount = cost_basis * (wg_pct / 100.0)

    net_total = cost_basis + wg_amount
    tax_total = net_total * tax_rate
    gross_total = net_total + tax_total

    # BGB § 650c Abs. 3: 80 % Abschlagsanspruch des Nachtragswertes
    abschlag_80_netto = round(net_total * 0.80, 2) if framework == "BGB_650C" else None
    abschlag_80_brutto = round(gross_total * 0.80, 2) if framework == "BGB_650C" else None

    # Juristische Hinweise und Begründung
    if framework == "VOB_B":
        legal_basis = "§ 2 Abs. 5 & 6 VOB/B (Urkalkulationsfortschreibung)"
        notification_hint = (
            "⚠️ Wichtig nach § 2 Abs. 6 Nr. 1 VOB/B: Die Vergütungsansprüche für Zusatzleistungen "
            "MÜSSEN dem Auftraggeber VOR Beginn der Ausführung schriftlich angekündigt werden!"
        )
    elif framework == "BGB_650C":
        legal_basis = "§ 650b & § 650c BGB (Tatsächlich erforderliche Kosten)"
        notification_hint = (
            "⚖️ BGB-Bauvertrag: Nach 30-tägiger Verhandlungsphase Anordnungsrecht des Bestellers. "
            f"Liquiditätssicherung: Nach § 650c Abs. 3 BGB dürfen sofort 80 % ({abschlag_80_netto:.2f} {currency}) "
            "als Abschlagszahlung in Rechnung gestellt werden!"
        )
    elif framework == "SIA_118":
        legal_basis = "SIA 118 Art. 48 & Art. 84-91 (Regietarif & Materialaufschlag)"
        notification_hint = (
            "🇨🇭 SIA 118: Regierapporte müssen wöchentlich der Bauleitung vorgelegt werden. "
            "Art. 86 SIA 118: Nicht beanstandete Rapporte gelten nach 10 Tagen als stillschweigend genehmigt."
        )
    else:  # OENORM_B2110
        legal_basis = "ÖNORM B 2110 Pkt. 7.3 & 7.4 (Mehrkostenforderung MKF)"
        notification_hint = (
            "🇦🇹 ÖNORM B 2110: Mehrkostenforderung (MKF) unverzüglich dem Auftraggeber anzeigen "
            "unter Angabe der kalkulatorischen K3/K7-Blatt-Grundlagen."
        )

    return {
        "framework": framework,
        "legal_basis": legal_basis,
        "description": description,
        "country": country,
        "currency": currency,
        "breakdown": {
            "labor_hours": round(labor_hours, 2),
            "labor_rate": round(labor_hourly_rate, 2),
            "labor_sum": round(direct_labor, 2),
            "material_base": round(material_cost, 2),
            "material_surcharge_pct": round(material_surcharge_pct, 2),
            "material_surcharge_amount": round(mat_surcharge, 2),
            "material_effective": round(effective_material, 2),
            "equipment_cost": round(equipment_cost, 2),
            "subcontractor_cost": round(subcontractor_cost, 2),
            "total_ekdt": round(total_ekdt, 2),
            "agk_pct": round(agk_pct, 2),
            "agk_amount": round(agk_amount, 2),
            "wg_pct": round(wg_pct, 2),
            "wg_amount": round(wg_amount, 2),
            "net_total": round(net_total, 2),
            "tax_rate_pct": round(tax_rate * 100.0, 1),
            "tax_total": round(tax_total, 2),
            "gross_total": round(gross_total, 2)
        },
        "abschlag_80_netto": abschlag_80_netto,
        "abschlag_80_brutto": abschlag_80_brutto,
        "notification_hint": notification_hint
    }


# ============================================================================
# 3. MODUL: AUFMAß NACH VOB/C (DIN 18299, 18350, 18363, 18352)
# ============================================================================

def calculate_vob_aufmass(
    gross_area: float,
    openings: List[Dict[str, Any]],
    trade_type: str = "wand_putz_maler",
    reveal_depth_m: float = 0.20
) -> Dict[str, Any]:
    """
    Berechnet das abrechenbare Aufmaß nach den amtlichen VOB/C Übermessungsregeln:
      - DIN 18350 (Putzarbeiten) & DIN 18363 (Malerarbeiten):
        * Öffnungen <= 2.50 m² Einzelgröße werden ÜBERMESSEN (kein Abzug).
        * Öffnungen > 2.50 m² Einzelgröße werden VOLL ABGEZOGEN.
        * Laibungen bei abgezogenen Öffnungen werden als Zulage hinzugefügt (Umfang × Laibungstiefe).
      - DIN 18353 / DIN 18365 (Estrich, Bodenbeläge):
        * Aussparungen <= 0.50 m² werden ÜBERMESSEN.
        * Aussparungen > 0.50 m² werden ABGEZOGEN.
      - DIN 18352 (Fliesen- & Plattenarbeiten):
        * Aussparungen <= 0.10 m² (Einzelöffnungen) bzw. <= 2.50 m² (Wandöffnungen).

    Parameter:
      - gross_area: Brutto-Wand- oder Bodenfläche in m²
      - openings: Liste von Dictionaries [{'name': 'Fenster 1', 'width': 1.20, 'height': 1.40}, ...]
      - trade_type: 'wand_putz_maler' (2.5 m² Schwelle) oder 'boden_estrich' (0.5 m² Schwelle)
      - reveal_depth_m: Laibungstiefe in Metern (Standard 0.20 m = 20 cm)
    """
    # Schwellenwert nach VOB/C
    threshold = 0.50 if trade_type == "boden_estrich" else 2.50

    processed_openings = []
    total_openings_area = 0.0
    deducted_area = 0.0
    overmeasured_area = 0.0
    total_reveal_area = 0.0

    for op in openings:
        name = op.get("name", "Öffnung")
        w = float(op.get("width", 0.0))
        h = float(op.get("height", 0.0))
        count = int(op.get("count", 1))
        single_area = w * h
        total_op_area = single_area * count
        total_openings_area += total_op_area

        is_deducted = single_area > threshold
        reveal_area = 0.0

        if is_deducted:
            deducted_area += total_op_area
            # Laibungsberechnung: Umfang der Öffnung × Tiefe (oben, links, rechts - ohne Fensterbank/Boden)
            # Standard bei Fenstern: 2 * Höhe + 1 * Breite
            reveal_perimeter = (2.0 * h) + w
            reveal_area = reveal_perimeter * reveal_depth_m * count
            total_reveal_area += reveal_area
            status = "Abzug (Fläche > {:.2f} m²) + Laibungszulage".format(threshold)
        else:
            overmeasured_area += total_op_area
            status = "Übermessen nach VOB/C (Fläche ≤ {:.2f} m²)".format(threshold)

        processed_openings.append({
            "name": name,
            "dimensions": f"{w:.2f}m x {h:.2f}m",
            "single_area_m2": round(single_area, 3),
            "count": count,
            "total_area_m2": round(total_op_area, 3),
            "deducted": is_deducted,
            "status": status,
            "reveal_area_m2": round(reveal_area, 3)
        })

    # Netto-Abrechnungsfläche
    billable_area = gross_area - deducted_area + total_reveal_area

    return {
        "trade_type": trade_type,
        "vob_c_threshold_m2": threshold,
        "gross_area_m2": round(gross_area, 3),
        "total_openings_count": len(openings),
        "total_openings_area_m2": round(total_openings_area, 3),
        "overmeasured_area_m2": round(overmeasured_area, 3),
        "deducted_area_m2": round(deducted_area, 3),
        "total_reveal_area_m2": round(total_reveal_area, 3),
        "billable_area_m2": round(billable_area, 3),
        "openings_detail": processed_openings,
        "rule_explanation": (
            f"VOB/C Regelung: Einzelflächen bis einschließlich {threshold:.2f} m² "
            f"werden übermessen (voll vergütet). Flächen über {threshold:.2f} m² "
            f"werden abgezogen, dafür werden Laibungen abgerechnet."
        )
    }


# ============================================================================
# 4. MODUL: STEUERBONUS (§ 35a EStG DE, AT HANDWERKERBONUS, CH UNTERHALT)
# ============================================================================

def calculate_handwerker_steuerbonus(
    labor_cost_gross: float,
    country: str = "DE",
    travel_cost_gross: float = 0.0,
    equipment_cost_gross: float = 0.0,
    marginal_tax_rate_ch_pct: float = 28.0
) -> Dict[str, Any]:
    """
    Berechnet den staatlichen Handwerkerbonus / Steuervorteil:
      - Deutschland (§ 35a Abs. 3 EStG):
        * 20 % der Lohn-, Fahrt- und Maschinenkosten inkl. MwSt
        * Maximal 1.200 € Steuerabzug pro Haushalt und Kalenderjahr (bei 6.000 € Arbeitskosten)
        * Reine Materialkosten sind vom Bonus ausgeschlossen!
        * Unbare Bezahlung (Überweisung) ist zwingende Voraussetzung!
      - Österreich (Handwerkerbonus 2024-2026):
        * 20 % der reinen Arbeitskosten (ohne USt)
        * Maximal 2.000 € Förderbetrag pro Person und Jahr (bei 10.000 € Arbeitskosten)
      - Schweiz (Liegenschaftsunterhalt DBG Art. 32):
        * 100 % der werterhaltenden Handwerkerkosten sind vom steuerbaren Einkommen absetzbar
        * Effektive Ersparnis = Betrag × Grenzsteuersatz
    """
    country = country.upper()
    if country not in TAX_RATES:
        raise ValueError(f"Ungültiges Land '{country}'. Erlaubt: DE, AT, CH.")

    eligible_gross = labor_cost_gross + travel_cost_gross + equipment_cost_gross

    if country == "DE":
        rate_pct = 20.0
        max_bonus = 1200.0
        max_eligible = 6000.0
        calculated_bonus = eligible_gross * 0.20
        effective_bonus = min(calculated_bonus, max_bonus)
        is_capped = calculated_bonus > max_bonus
        legal_ref = "§ 35a Abs. 3 EStG (Handwerkerleistungen für Renovierung/Erhaltung)"
        notice = (
            "Zahlungshinweis: Barzahlungen werden vom Finanzamt nicht anerkannt! "
            "Rechnungsbetrag muss unbar auf das Konto des Handwerksbetriebs überwiesen werden."
        )
        return {
            "country": "DE",
            "currency": "EUR",
            "legal_basis": legal_ref,
            "eligible_labor_gross": round(eligible_gross, 2),
            "bonus_rate_pct": rate_pct,
            "calculated_bonus": round(calculated_bonus, 2),
            "max_legal_bonus_year": max_bonus,
            "effective_tax_saving": round(effective_bonus, 2),
            "is_capped": is_capped,
            "max_eligible_expenses": max_eligible,
            "notice": notice
        }

    elif country == "AT":
        # Handwerkerbonus AT gilt für Netto-Arbeitskosten
        tax_rate = TAX_RATES["AT"]
        eligible_net = eligible_gross / (1.0 + tax_rate)
        rate_pct = 20.0
        max_bonus = 2000.0
        max_eligible_net = 10000.0
        calculated_bonus = eligible_net * 0.20
        effective_bonus = min(calculated_bonus, max_bonus)
        is_capped = calculated_bonus > max_bonus
        legal_ref = "Handwerkerbonus Österreich (Bundesministerium für Arbeit und Wirtschaft)"
        notice = (
            "Gilt für die Renovierung oder Errichtung von Wohnraum. "
            "Antrag online über handwerkerbonus.gv.at einreichbar."
        )
        return {
            "country": "AT",
            "currency": "EUR",
            "legal_basis": legal_ref,
            "eligible_labor_gross": round(eligible_gross, 2),
            "eligible_labor_net": round(eligible_net, 2),
            "bonus_rate_pct": rate_pct,
            "calculated_bonus": round(calculated_bonus, 2),
            "max_legal_bonus_year": max_bonus,
            "effective_tax_saving": round(effective_bonus, 2),
            "is_capped": is_capped,
            "max_eligible_expenses_net": max_eligible_net,
            "notice": notice
        }

    else:  # CH
        # Schweiz: Vollabzug vom steuerbaren Einkommen bei werterhaltendem Unterhalt
        effective_saving = eligible_gross * (marginal_tax_rate_ch_pct / 100.0)
        legal_ref = "Art. 32 DBG / Kantonale Steuergesetze (Werterhaltender Liegenschaftsunterhalt)"
        notice = (
            "Werterhaltende Reparaturen, Maler-, Sanitär- und Dacharbeiten sind zu 100 % "
            "vom steuerbaren Einkommen bei Bund, Kanton und Gemeinde abzugsfähig."
        )
        return {
            "country": "CH",
            "currency": "CHF",
            "legal_basis": legal_ref,
            "deductible_expenses_total": round(eligible_gross, 2),
            "marginal_tax_rate_pct": marginal_tax_rate_ch_pct,
            "effective_tax_saving": round(effective_saving, 2),
            "notice": notice
        }


# ============================================================================
# 5. AUTOMATISIERTE TESTSUITE (--test)
# ============================================================================

def run_automated_tests() -> bool:
    """
    Führt automatisierte Selbsttests durch und verifiziert alle Berechnungsmodule.
    """
    print("\n" + "=" * 70)
    print("🧪 DACH HANDWERKER-KALKULATOR: AUTOMATISIERTER SELBSTTEST")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    def assert_test(condition: bool, test_name: str, details: str = ""):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  ✅ [PASS] {test_name}")
        else:
            print(f"  ❌ [FAIL] {test_name}: {details}")

    # Test 1: Stundensatz DE Referenz
    res_de = calculate_hourly_rate(hourly_wage=23.00, country="DE", lzk_pct=82.5, agk_pct=30.0, wg_pct=6.0)
    assert_test(res_de["base_wage"] == 23.00, "Stundensatz DE: Mittellohn Basis")
    assert_test(abs(res_de["direct_labor_cost"] - 41.98) < 0.05, "Stundensatz DE: Lohnkosten inkl. 82.5% LZK (~41.98 €)")
    assert_test(abs(res_de["self_cost_minimum"] - 54.57) < 0.05, "Stundensatz DE: Selbstkosten inkl. 30% AGK (~54.57 €)")
    assert_test(abs(res_de["net_hourly_rate"] - 57.84) < 0.05, "Stundensatz DE: Netto-Stundensatz inkl. 6% W&G (~57.84 €)")
    assert_test(abs(res_de["gross_hourly_rate"] - 68.83) < 0.05, "Stundensatz DE: Brutto-Stundensatz inkl. 19% MwSt (~68.83 €)")

    # Test 2: Stundensatz CH Referenz
    res_ch = calculate_hourly_rate(hourly_wage=44.00, country="CH", lzk_pct=52.0, agk_pct=32.0, wg_pct=6.5)
    assert_test(res_ch["currency"] == "CHF", "Stundensatz CH: Währung CHF")
    assert_test(abs(res_ch["tax_rate_pct"] - 8.1) < 0.01, "Stundensatz CH: Mehrwertsteuersatz 8.1%")
    assert_test(res_ch["net_hourly_rate"] > 90.0, "Stundensatz CH: Netto-Stundensatz plausibel > 90 CHF")

    # Test 3: Stundensatz AT Referenz
    res_at = calculate_hourly_rate(hourly_wage=22.00, country="AT", lzk_pct=94.0, agk_pct=31.0, wg_pct=6.0)
    assert_test(res_at["currency"] == "EUR", "Stundensatz AT: Währung EUR")
    assert_test(abs(res_at["tax_rate_pct"] - 20.0) < 0.01, "Stundensatz AT: USt 20.0%")
    assert_test(res_at["net_hourly_rate"] > 55.0, "Stundensatz AT: Netto-Stundensatz plausibel > 55 EUR")

    # Test 4: Mittellohn-Kolonnenberechnung
    workers = [
        {"title": "Meister", "hourly_wage": 30.00, "count": 1},
        {"title": "Geselle", "hourly_wage": 22.00, "count": 2},
        {"title": "Helfer", "hourly_wage": 16.00, "count": 1}
    ]
    res_col = calculate_mittellohn(workers)
    # (30*1 + 22*2 + 16*1)/4 = (30 + 44 + 16)/4 = 90 / 4 = 22.50
    assert_test(res_col["mittellohn"] == 22.50, "Mittellohn Kolonne: Exakte Mischkalkulation (22.50 €)")

    # Test 5: Nachtrag BGB § 650c mit 80% Abschlagsanspruch
    res_bgb = calculate_nachtrag(
        framework="BGB_650C",
        labor_hours=15.0,
        labor_hourly_rate=60.00,
        material_cost=500.00,
        equipment_cost=100.00,
        agk_pct=20.0,
        wg_pct=6.0
    )
    # EKdT = 15*60 (900) + 500 + 100 = 1500 €
    # AGK 20% = 300 € -> 1800 €
    # W&G 6% = 108 € -> Netto 1908 €
    assert_test(res_bgb["breakdown"]["total_ekdt"] == 1500.00, "Nachtrag BGB § 650c: EKdT Summe 1500 €")
    assert_test(res_bgb["breakdown"]["net_total"] == 1908.00, "Nachtrag BGB § 650c: Netto Nachtragssumme 1908 €")
    # 80% Abschlagsanspruch: 1908 * 0.80 = 1526.40 €
    assert_test(res_bgb["abschlag_80_netto"] == 1526.40, "Nachtrag BGB § 650c: 80% Abschlagsanspruch gesetzlich verifiziert")

    # Test 5b: Nachtrag SIA 118 (Schweiz) mit 12% Materialzuschlag
    res_sia = calculate_nachtrag(
        framework="SIA_118",
        labor_hours=10.0,
        labor_hourly_rate=95.00,
        material_cost=1000.00,
        agk_pct=15.0,
        wg_pct=5.0
    )
    # Material = 1000 + 12% = 1120 CHF
    # Lohn = 950 CHF -> EKdT = 2070 CHF
    # AGK 15% = 310.50 -> 2380.50 CHF
    # W&G 5% = 119.025 -> Netto 2499.53 CHF
    assert_test(res_sia["currency"] == "CHF", "SIA 118: Währung CHF")
    assert_test(res_sia["breakdown"]["material_surcharge_amount"] == 120.00, "SIA 118: 12% Materialzuschlag (120 CHF)")
    assert_test(abs(res_sia["breakdown"]["net_total"] - 2499.53) < 0.05, "SIA 118: Netto Regiegesamtsumme (~2499.53 CHF)")

    # Test 5c: Nachtrag ÖNORM B 2110 (Österreich)
    res_oenorm = calculate_nachtrag(
        framework="OENORM_B2110",
        labor_hours=8.0,
        labor_hourly_rate=65.00,
        material_cost=400.00,
        agk_pct=18.0,
        wg_pct=5.0
    )
    assert_test(res_oenorm["currency"] == "EUR", "ÖNORM B 2110: Währung EUR")
    assert_test(res_oenorm["breakdown"]["tax_rate_pct"] == 20.0, "ÖNORM B 2110: 20% USt")

    # Test 6: VOB/C Aufmaß Übermessungsregeln
    openings = [
        {"name": "Fenster klein", "width": 1.0, "height": 1.2, "count": 1},    # 1.20 m² <= 2.5 m² -> übermessen!
        {"name": "Doppelfenster", "width": 2.0, "height": 1.8, "count": 1}     # 3.60 m² > 2.5 m² -> abgezogen + Laibung!
    ]
    res_aufmass = calculate_vob_aufmass(gross_area=100.0, openings=openings, reveal_depth_m=0.20)
    assert_test(res_aufmass["overmeasured_area_m2"] == 1.20, "VOB/C Aufmaß: Öffnung 1.20 m² übermessen")
    assert_test(res_aufmass["deducted_area_m2"] == 3.60, "VOB/C Aufmaß: Öffnung 3.60 m² abgezogen")
    # Laibung: (2*1.8 + 2.0) * 0.20 = 5.6 * 0.20 = 1.12 m²
    assert_test(abs(res_aufmass["total_reveal_area_m2"] - 1.12) < 0.01, "VOB/C Aufmaß: Laibungszulage korrekt berechnet (1.12 m²)")
    # Billable: 100 - 3.60 + 1.12 = 97.52 m²
    assert_test(abs(res_aufmass["billable_area_m2"] - 97.52) < 0.01, "VOB/C Aufmaß: Abrechenbare Nettofläche 97.52 m²")

    # Test 7: Steuerbonus § 35a EStG DE
    res_tax_normal = calculate_handwerker_steuerbonus(labor_cost_gross=3000.00, country="DE")
    assert_test(res_tax_normal["effective_tax_saving"] == 600.00, "§ 35a EStG: 20% auf 3000 € = 600 € Steuerersparnis")

    res_tax_capped = calculate_handwerker_steuerbonus(labor_cost_gross=8000.00, country="DE")
    assert_test(res_tax_capped["effective_tax_saving"] == 1200.00, "§ 35a EStG: Gesetzliche Deckelung auf max. 1.200 € / Jahr")
    assert_test(res_tax_capped["is_capped"] is True, "§ 35a EStG: Cap-Indikator aktiv")

    # Test 8: Österreich Handwerkerbonus
    res_tax_at = calculate_handwerker_steuerbonus(labor_cost_gross=6000.00, country="AT")
    # Netto = 6000 / 1.20 = 5000 €; 20% = 1000 €
    assert_test(abs(res_tax_at["effective_tax_saving"] - 1000.00) < 0.01, "AT Handwerkerbonus: 20% auf Netto-Arbeitskosten")

    print("=" * 70)
    print(f"Ergebnis: {passed_tests} von {total_tests} Tests erfolgreich absolviert!")
    print("=" * 70)
    return passed_tests == total_tests


# ============================================================================
# CLI INTERACTION & DISPATCHER
# ============================================================================

def print_presets():
    """Gibt die Branchenrichtwerte für Handwerksbetriebe aus."""
    print("\n📋 DACH-HANDWERK BRANCHENRICHTWERTE 2026:")
    print("-" * 75)
    print(f"{'Gewerke-Kürzel':<15} | {'Gewerk':<35} | {'DE (€/h)':<10} | {'CH (CHF/h)':<10}")
    print("-" * 75)
    for code, info in TRADE_PRESETS.items():
        name = info["name"]
        de_wage = f"{info['DE']['hourly_wage']:.2f} €"
        ch_wage = f"{info['CH']['hourly_wage']:.2f} CHF"
        print(f"{code:<15} | {name:<35} | {de_wage:<10} | {ch_wage:<10}")
    print("-" * 75)


def main():
    parser = argparse.ArgumentParser(
        description="🛠️ DACH Handwerker-, Baukalkulations- & Aufmaß-Suite 2026 (DE / CH / AT)",
        epilog="Online-Version & Pro-Vorlagen: https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/"
    )
    parser.add_argument("--test", action="store_true", help="Führt den automatisierten Selbsttest aller Module aus.")
    parser.add_argument("--presets", action="store_true", help="Zeigt vorkonfigurierte Richtwerte für verschiedene Handwerkszweige.")
    parser.add_argument("--stundensatz", action="store_true", help="Berechnet den Stundenverrechnungssatz.")
    parser.add_argument("--nachtrag", action="store_true", help="Kalkuliert ein Nachtragsangebot nach VOB/B oder BGB § 650c.")
    parser.add_argument("--aufmass", action="store_true", help="Berechnet Wand-/Bodenflächen nach VOB/C Übermessungsregeln.")
    parser.add_argument("--bonus", action="store_true", help="Berechnet den Steuerbonus (§ 35a EStG DE / Handwerkerbonus AT).")

    # Parameter für Stundensatz
    parser.add_argument("--country", type=str, default="DE", choices=["DE", "CH", "AT"], help="Land: DE, CH oder AT (Default: DE)")
    parser.add_argument("--trade", type=str, choices=list(TRADE_PRESETS.keys()), help="Handwerksbranche für Presets")
    parser.add_argument("--wage", type=float, help="Mittellohn / Bruttolohn pro Stunde (€ oder CHF)")
    parser.add_argument("--lzk", type=float, help="Lohnzusatzkosten in %% (Standard: DE=82.5%%, CH=52.0%%, AT=94.0%%)")
    parser.add_argument("--agk", type=float, default=30.0, help="Betriebsgemeinkostenzuschlag (AGK) in %% (Default: 30.0%%)")
    parser.add_argument("--wg", type=float, default=6.0, help="Wagnis & Gewinn in %% (Default: 6.0%%)")
    parser.add_argument("--hours", type=float, default=1520.0, help="Produktive Jahresstunden (Default: 1520 h)")

    # Parameter für Nachtrag
    parser.add_argument("--framework", type=str, default="VOB_B", choices=["VOB_B", "BGB_650C", "SIA_118", "OENORM_B2110"])
    parser.add_argument("--labor-hours", type=float, default=10.0, help="Lohnstunden für Nachtrag")
    parser.add_argument("--labor-rate", type=float, default=58.0, help="Stundensatz für Nachtrag")
    parser.add_argument("--material", type=float, default=250.0, help="Materialkosten netto")
    parser.add_argument("--equipment", type=float, default=50.0, help="Gerätekosten netto")

    # Parameter für Aufmaß
    parser.add_argument("--gross-area", type=float, help="Bruttofläche in m² für Aufmaß")
    parser.add_argument("--opening-w", type=float, help="Breite einer Öffnung in m")
    parser.add_argument("--opening-h", type=float, help="Höhe einer Öffnung in m")

    # Parameter für Bonus
    parser.add_argument("--labor-gross", type=float, help="Arbeitskosten brutto für Steuerbonus")

    # JSON Output Flag
    parser.add_argument("--json", action="store_true", help="Gibt die Ergebnisse maschinenlesbar als reines JSON aus.")

    args = parser.parse_args()

    if args.test:
        success = run_automated_tests()
        sys.exit(0 if success else 1)

    if args.presets:
        print_presets()
        sys.exit(0)

    # 1. Stundensatz-Modus
    if args.stundensatz or args.wage or args.trade:
        country = args.country
        wage = args.wage
        lzk = args.lzk
        agk = args.agk
        wg = args.wg

        if args.trade and args.trade in TRADE_PRESETS:
            preset_data = TRADE_PRESETS[args.trade][country]
            if wage is None:
                wage = preset_data["hourly_wage"]
            if lzk is None:
                lzk = preset_data["lzk_pct"]
            agk = preset_data["agk_pct"]
            wg = preset_data["wg_pct"]

        if wage is None:
            wage = 23.50  # Fallback

        res = calculate_hourly_rate(
            hourly_wage=wage,
            country=country,
            lzk_pct=lzk,
            agk_pct=agk,
            wg_pct=wg,
            productive_hours=args.hours
        )

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("\n" + "=" * 65)
            print(f"📊 STUNDENSATZ-KALKULATION ({res['country']} - {res['currency']})")
            print("=" * 65)
            print(f"• Fertigungs-Mittellohn         : {res['base_wage']:.2f} {res['currency']}/h")
            print(f"• Lohnzusatzkosten ({res['lzk_pct']:.1f} %)     : + {res['lzk_amount']:.2f} {res['currency']}/h")
            print(f"-> Fertigungslohnkosten        : {res['direct_labor_cost']:.2f} {res['currency']}/h")
            print(f"• Gemeinkosten (AGK {res['agk_pct']:.1f} %)     : + {res['agk_amount']:.2f} {res['currency']}/h")
            print(f"-----------------------------------------------------------------")
            print(f"🎯 KOSTENDECKENDE SELBSTKOSTEN  : {res['self_cost_minimum']:.2f} {res['currency']}/h  (MINDESTSATZ!)")
            print(f"• Wagnis & Gewinn ({res['wg_pct']:.1f} %)       : + {res['wg_amount']:.2f} {res['currency']}/h")
            print(f"=================================================================")
            print(f"🚀 KALKULIERTER NETTO-STUNDENSATZ: {res['net_hourly_rate']:.2f} {res['currency']}/h")
            print(f"• Brutto inkl. {res['tax_rate_pct']:.1f}% MwSt  : {res['gross_hourly_rate']:.2f} {res['currency']}/h")
            print(f"-----------------------------------------------------------------")
            print(f"• Tagessatz Netto (8 Std.)     : {res['daily_rate_net_8h']:.2f} {res['currency']}")
            print(f"• Break-Even Monatsumsatz/MA   : {res['monthly_break_even_turnover']:.2f} {res['currency']}")
            print("=" * 65)
        sys.exit(0)

    # 2. Nachtrag-Modus
    if args.nachtrag:
        res = calculate_nachtrag(
            framework=args.framework,
            labor_hours=args.labor_hours,
            labor_hourly_rate=args.labor_rate,
            material_cost=args.material,
            equipment_cost=args.equipment,
            agk_pct=args.agk,
            wg_pct=args.wg
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("\n" + "=" * 65)
            print(f"📑 NACHTRAGSKALKULATION NACH {res['framework']}")
            print(f"Rechtsgrundlage: {res['legal_basis']}")
            print("=" * 65)
            bd = res["breakdown"]
            print(f"• Lohnkosten ({bd['labor_hours']:.1f} h à {bd['labor_rate']:.2f} {res['currency']}) : {bd['labor_sum']:.2f} {res['currency']}")
            print(f"• Materialkosten (inkl. Zuschlag)    : {bd['material_effective']:.2f} {res['currency']}")
            print(f"• Gerätekosten / Maschinen           : {bd['equipment_cost']:.2f} {res['currency']}")
            print(f"-> Einzelkosten (EKdT) Summe         : {bd['total_ekdt']:.2f} {res['currency']}")
            print(f"• AGK-Zuschlag ({bd['agk_pct']:.1f} %)              : + {bd['agk_amount']:.2f} {res['currency']}")
            print(f"• Wagnis & Gewinn ({bd['wg_pct']:.1f} %)            : + {bd['wg_amount']:.2f} {res['currency']}")
            print("-----------------------------------------------------------------")
            print(f"💰 NETTO-NACHTRAGSBETRAG             : {bd['net_total']:.2f} {res['currency']}")
            print(f"• MwSt ({bd['tax_rate_pct']:.1f} %)                  : + {bd['tax_total']:.2f} {res['currency']}")
            print(f"🌟 BRUTTO-NACHTRAGSBETRAG            : {bd['gross_total']:.2f} {res['currency']}")
            if res["abschlag_80_netto"] is not None:
                print(f"⚡ § 650c Abs. 3 BGB 80%-Abschlag    : {res['abschlag_80_netto']:.2f} {res['currency']} (Netto)")
            print("-----------------------------------------------------------------")
            print(f"{res['notification_hint']}")
            print("=" * 65)
        sys.exit(0)

    # 3. Aufmaß-Modus
    if args.aufmass or args.gross_area:
        gross = args.gross_area or 85.0
        openings = []
        if args.opening_w and args.opening_h:
            openings.append({"name": "Öffnung 1", "width": args.opening_w, "height": args.opening_h, "count": 1})
        else:
            openings = [
                {"name": "Zimmertür", "width": 0.90, "height": 2.10, "count": 2}, # 1.89 m² <= 2.5 m² -> übermessen
                {"name": "Großes Fenster", "width": 2.20, "height": 1.50, "count": 1} # 3.30 m² > 2.5 m² -> Abzug
            ]
        res = calculate_vob_aufmass(gross_area=gross, openings=openings)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("\n" + "=" * 65)
            print("📐 VOB/C AUFMAß-BERECHNUNG (DIN 18299, 18350, 18363)")
            print("=" * 65)
            print(f"• Bruttofläche vor Abzügen : {res['gross_area_m2']:.2f} m²")
            print(f"• Übermessene Öffnungen    : {res['overmeasured_area_m2']:.2f} m² (nicht abgezogen nach VOB)")
            print(f"• Abgezogene Öffnungen     : - {res['deducted_area_m2']:.2f} m² (Einzelgröße > 2.5 m²)")
            print(f"• Laibungszulagen          : + {res['total_reveal_area_m2']:.2f} m²")
            print("-----------------------------------------------------------------")
            print(f"🏆 ABRECHENBARE FLÄCHE     : {res['billable_area_m2']:.2f} m²")
            print("=" * 65)
        sys.exit(0)

    # 4. Steuerbonus-Modus
    if args.bonus or args.labor_gross:
        labor_val = args.labor_gross or 3500.0
        res = calculate_handwerker_steuerbonus(labor_cost_gross=labor_val, country=args.country)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("\n" + "=" * 65)
            print(f"🏛️ STEUERBONUS / HANDWERKERFÖRDERUNG ({res['country']})")
            print(f"Rechtsgrundlage: {res['legal_basis']}")
            print("=" * 65)
            if res['country'] == 'DE':
                print(f"• Förderfähige Arbeitskosten: {res['eligible_labor_gross']:.2f} €")
                print(f"• Fördersatz               : {res['bonus_rate_pct']:.1f} %")
                print(f"💶 EFFEKTIVE STEUERERSPARNIS: {res['effective_tax_saving']:.2f} €")
                print(f"• Maximaler Förderbetrag/J : {res['max_legal_bonus_year']:.2f} €")
            elif res['country'] == 'AT':
                print(f"• Förderfähige Lohnkosten Netto : {res['eligible_labor_net']:.2f} €")
                print(f"💶 AUSGEZAHLTER FÖRDERBONUS    : {res['effective_tax_saving']:.2f} €")
                print(f"• Maximaler Förderbonus        : {res['max_legal_bonus_year']:.2f} €")
            else:
                print(f"• Abzugsfähige Kosten        : {res['deductible_expenses_total']:.2f} CHF")
                print(f"💶 GESCHÄTZTE STEUERERSPARNIS : {res['effective_tax_saving']:.2f} CHF")
            print("-----------------------------------------------------------------")
            print(f"ℹ️ {res['notice']}")
            print("=" * 65)
        sys.exit(0)

    # Wenn keine spezifische Flagge gesetzt ist, Hilfe anzeigen
    parser.print_help()


if __name__ == "__main__":
    main()
