/**
 * ============================================================================
 * 🛠️ DACH Handwerker-, Baukalkulations- & Aufmaß-Suite 2026 (JavaScript / Node.js)
 * ============================================================================
 * Professionelle Baukalkulation nach VOB/B, VOB/C, BGB § 650c, SIA 118 & ÖNORM B 2110
 * für Handwerksbetriebe und Bauunternehmer in Deutschland, der Schweiz und Österreich.
 *
 * Zero-Dependency: Läuft direkt in Node.js (CLI / Server) und modernen Webbrowsern.
 *
 * Module:
 *   1. Stundensatz-Kalkulation (Mittellohn, Lohnzusatzkosten DE/CH/AT, AGK, W&G)
 *   2. Nachtragskalkulation (§ 2 VOB/B vs. § 650c BGB, SIA 118, ÖNORM B 2110 + 80%-Abschlag)
 *   3. VOB/C Aufmaß-Rechner (Übermessungsregeln DIN 18299, 18350, 18363, Laibungszulagen)
 *   4. Steuerbonus-Rechner (§ 35a Abs. 3 EStG DE, AT Handwerkerbonus, CH Liegenschaftsunterhalt)
 *
 * Website: https://dach-digitalwerk.netlify.app/handwerker-stundensatz-aufmass/
 * Lizenz: MIT
 * Copyright (c) 2026 DACH Digitalwerk
 * ============================================================================
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.HandwerkerKalkulator = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ============================================================================
  // KONSTANTEN & BRANCHEN-BENCHMARKS (STAND 2026)
  // ============================================================================

  const TAX_RATES = {
    DE: 0.19,     // 19.0% Deutschland
    CH: 0.081,    //  8.1% Schweiz (seit 01.01.2024)
    AT: 0.20      // 20.0% Österreich
  };

  const CURRENCIES = {
    DE: 'EUR',
    CH: 'CHF',
    AT: 'EUR'
  };

  // Standard-Lohnzusatzkosten in %
  const DEFAULT_LZK = {
    DE: 82.5,     // Gesetzl. SV (21.5%) + BG-Bau (5.5%) + SOKA-Bau (14.5%) + Lohnfortzahlung (41.0%)
    CH: 52.0,     // AHV/IV/EO/ALV (6.4%) + BVG (8.5%) + SUVA (4.8%) + FAR (5.5%) + Ferien/13. (26.8%)
    AT: 94.0      // SV-DGA (21.25%) + DB/DZ/KommSt (7.06%) + BUAK (26.5%) + Sonderzahlungen/Urlaub (39.19%)
  };

  const TRADE_PRESETS = {
    shk: {
      name: 'Sanitär, Heizung, Klima (SHK)',
      DE: { hourlyWage: 24.50, lzkPct: 82.0, agkPct: 32.0, wgPct: 6.5 },
      CH: { hourlyWage: 45.00, lzkPct: 52.0, agkPct: 34.0, wgPct: 7.0 },
      AT: { hourlyWage: 23.80, lzkPct: 93.0, agkPct: 33.0, wgPct: 6.5 }
    },
    elektro: {
      name: 'Elektrotechnik / Gebäudeautomation',
      DE: { hourlyWage: 24.00, lzkPct: 80.0, agkPct: 30.0, wgPct: 7.0 },
      CH: { hourlyWage: 46.50, lzkPct: 50.0, agkPct: 32.0, wgPct: 7.5 },
      AT: { hourlyWage: 23.50, lzkPct: 92.0, agkPct: 31.0, wgPct: 6.5 }
    },
    maler: {
      name: 'Maler & Lackierer / Stuckateur',
      DE: { hourlyWage: 20.80, lzkPct: 85.0, agkPct: 28.0, wgPct: 6.0 },
      CH: { hourlyWage: 41.50, lzkPct: 53.0, agkPct: 29.0, wgPct: 6.5 },
      AT: { hourlyWage: 20.20, lzkPct: 96.0, agkPct: 28.5, wgPct: 6.0 }
    },
    dachdecker: {
      name: 'Dachdecker & Spengler / Zimmerer',
      DE: { hourlyWage: 23.20, lzkPct: 88.0, agkPct: 34.0, wgPct: 7.5 },
      CH: { hourlyWage: 44.00, lzkPct: 56.0, agkPct: 35.0, wgPct: 8.0 },
      AT: { hourlyWage: 22.90, lzkPct: 98.0, agkPct: 34.0, wgPct: 7.5 }
    },
    tischler: {
      name: 'Schreiner / Tischler / Innenausbau',
      DE: { hourlyWage: 22.50, lzkPct: 79.0, agkPct: 36.0, wgPct: 6.5 },
      CH: { hourlyWage: 43.50, lzkPct: 51.0, agkPct: 36.0, wgPct: 7.0 },
      AT: { hourlyWage: 21.80, lzkPct: 91.0, agkPct: 35.0, wgPct: 6.5 }
    },
    bauhaupt: {
      name: 'Bauhauptgewerbe (Maurer, Betonbauer)',
      DE: { hourlyWage: 23.80, lzkPct: 89.0, agkPct: 26.0, wgPct: 6.0 },
      CH: { hourlyWage: 46.00, lzkPct: 58.5, agkPct: 28.0, wgPct: 6.5 },
      AT: { hourlyWage: 23.10, lzkPct: 99.0, agkPct: 27.0, wgPct: 6.0 }
    },
    fliesen: {
      name: 'Fliesen-, Platten- & Mosaikleger',
      DE: { hourlyWage: 21.50, lzkPct: 83.0, agkPct: 29.0, wgPct: 6.5 },
      CH: { hourlyWage: 42.00, lzkPct: 52.0, agkPct: 30.0, wgPct: 7.0 },
      AT: { hourlyWage: 21.00, lzkPct: 95.0, agkPct: 29.5, wgPct: 6.5 }
    },
    galabau: {
      name: 'Garten- und Landschaftsbau (GaLaBau)',
      DE: { hourlyWage: 19.80, lzkPct: 76.0, agkPct: 31.0, wgPct: 6.5 },
      CH: { hourlyWage: 39.50, lzkPct: 49.0, agkPct: 32.0, wgPct: 7.0 },
      AT: { hourlyWage: 19.50, lzkPct: 89.0, agkPct: 30.0, wgPct: 6.5 }
    }
  };

  // Hilfsfunktion: Rundung auf 2 Dezimalstellen
  function round2(num) {
    return Math.round((Number(num) + Number.EPSILON) * 100) / 100;
  }

  // Hilfsfunktion: Rundung auf 3 Dezimalstellen
  function round3(num) {
    return Math.round((Number(num) + Number.EPSILON) * 1000) / 1000;
  }

  // ============================================================================
  // 1. MODUL: STUNDENSATZ-KALKULATION
  // ============================================================================

  function calculateMittellohn(workers) {
    if (!Array.isArray(workers) || workers.length === 0) {
      throw new Error('Arbeitskräfte-Liste darf nicht leer sein.');
    }
    let totalWageSum = 0;
    let totalCount = 0;

    for (const w of workers) {
      const count = Number(w.count != null ? w.count : 1);
      const wage = Number(w.hourly_wage != null ? w.hourly_wage : (w.hourlyWage != null ? w.hourlyWage : 0));
      totalWageSum += wage * count;
      totalCount += count;
    }

    if (totalCount <= 0) {
      throw new Error('Gesamtzahl der Arbeitskräfte muss größer als 0 sein.');
    }

    const mittellohn = totalWageSum / totalCount;
    return {
      total_workers: totalCount,
      total_wage_sum: round2(totalWageSum),
      mittellohn: round2(mittellohn),
      workers: workers
    };
  }

  function calculateProduktivstunden(options = {}) {
    const totalCalendarDays = options.totalCalendarDays || 365;
    const weekendDays = options.weekendDays || 104;
    const publicHolidays = options.publicHolidays != null ? options.publicHolidays : 11;
    const vacationDays = options.vacationDays != null ? options.vacationDays : 30;
    const sickDays = options.sickDays != null ? options.sickDays : 14;
    const hoursPerDay = options.hoursPerDay || 8.0;
    const unproductivePct = options.unproductivePct != null ? options.unproductivePct : 12.0;

    const workingDays = totalCalendarDays - (weekendDays + publicHolidays + vacationDays + sickDays);
    const presenceHours = workingDays * hoursPerDay;
    const unproductiveHours = presenceHours * (unproductivePct / 100.0);
    const productiveHours = presenceHours - unproductiveHours;

    return {
      total_calendar_days: totalCalendarDays,
      non_working_days: weekendDays + publicHolidays + vacationDays + sickDays,
      working_days: workingDays,
      presence_hours: round2(presenceHours),
      unproductive_pct: unproductivePct,
      unproductive_hours: round2(unproductiveHours),
      productive_hours_per_year: round2(productiveHours)
    };
  }

  function calculateHourlyRate(options) {
    let hourlyWage, country, lzkPct, agkPct, wgPct, productiveHours, annualOverheadFixed;

    if (typeof options === 'number') {
      hourlyWage = options;
      country = arguments[1] || 'DE';
      lzkPct = arguments[2] != null ? arguments[2] : null;
      agkPct = arguments[3] != null ? arguments[3] : 30.0;
      wgPct = arguments[4] != null ? arguments[4] : 6.0;
      productiveHours = arguments[5] || 1520.0;
      annualOverheadFixed = arguments[6] || null;
    } else {
      hourlyWage = options.hourly_wage != null ? options.hourly_wage : options.hourlyWage;
      country = (options.country || 'DE').toUpperCase();
      lzkPct = options.lzk_pct != null ? options.lzk_pct : options.lzkPct;
      agkPct = options.agk_pct != null ? options.agk_pct : (options.agkPct != null ? options.agkPct : 30.0);
      wgPct = options.wg_pct != null ? options.wg_pct : (options.wgPct != null ? options.wgPct : 6.0);
      productiveHours = options.productive_hours != null ? options.productive_hours : (options.productiveHours || 1520.0);
      annualOverheadFixed = options.annual_overhead_fixed != null ? options.annual_overhead_fixed : options.annualOverheadFixed;
    }

    country = country.toUpperCase();
    if (!TAX_RATES[country]) {
      throw new Error(`Ungültiges Land '${country}'. Erlaubt sind DE, CH, AT.`);
    }

    const curr = CURRENCIES[country];
    const taxRate = TAX_RATES[country];

    if (lzkPct == null) {
      lzkPct = DEFAULT_LZK[country];
    }

    // 1. Fertigungslohn & Lohnzusatzkosten
    const wage = Number(hourlyWage);
    const lzkAmount = wage * (lzkPct / 100.0);
    const directLaborCost = wage + lzkAmount;

    // 2. Betriebsgemeinkosten
    let agkAmount;
    let effectiveAgkPct;
    if (annualOverheadFixed != null && annualOverheadFixed > 0) {
      agkAmount = annualOverheadFixed / productiveHours;
      effectiveAgkPct = (agkAmount / directLaborCost) * 100.0;
    } else {
      agkAmount = directLaborCost * (agkPct / 100.0);
      effectiveAgkPct = agkPct;
    }

    // 3. Selbstkosten (Kostendeckender Mindestsatz)
    const selfCost = directLaborCost + agkAmount;

    // 4. Wagnis & Gewinn
    const wgAmount = selfCost * (wgPct / 100.0);

    // 5. Netto-Stundensatz
    const netRate = selfCost + wgAmount;

    // 6. Brutto-Stundensatz
    const taxAmount = netRate * taxRate;
    const grossRate = netRate + taxAmount;

    // 7. Kennzahlen
    const dailyRateNet = netRate * 8.0;
    const monthlyBreakEvenTurnover = (selfCost * productiveHours) / 12.0;
    const monthlyTargetTurnover = (netRate * productiveHours) / 12.0;

    return {
      country: country,
      currency: curr,
      tax_rate_pct: round2(taxRate * 100.0),
      base_wage: round2(wage),
      lzk_pct: round2(lzkPct),
      lzk_amount: round2(lzkAmount),
      direct_labor_cost: round2(directLaborCost),
      agk_pct: round2(effectiveAgkPct),
      agk_amount: round2(agkAmount),
      self_cost_minimum: round2(selfCost),
      wg_pct: round2(wgPct),
      wg_amount: round2(wgAmount),
      net_hourly_rate: round2(netRate),
      gross_hourly_rate: round2(grossRate),
      tax_amount: round2(taxAmount),
      daily_rate_net_8h: round2(dailyRateNet),
      monthly_break_even_turnover: round2(monthlyBreakEvenTurnover),
      monthly_target_turnover: round2(monthlyTargetTurnover),
      productive_hours_year: productiveHours
    };
  }

  // ============================================================================
  // 2. MODUL: NACHTRAGSKALKULATION
  // ============================================================================

  function calculateNachtrag(options) {
    const framework = (options.framework || 'VOB_B').toUpperCase();
    const validFrameworks = ['VOB_B', 'BGB_650C', 'SIA_118', 'OENORM_B2110'];
    if (!validFrameworks.includes(framework)) {
      throw new Error(`Ungültiger Standard '${framework}'. Erlaubt: ${validFrameworks.join(', ')}`);
    }

    const country = framework === 'SIA_118' ? 'CH' : (framework === 'OENORM_B2110' ? 'AT' : 'DE');
    const currency = CURRENCIES[country];
    const taxRate = TAX_RATES[country];

    const laborHours = Number(options.labor_hours != null ? options.labor_hours : (options.laborHours || 0));
    const laborHourlyRate = Number(options.labor_hourly_rate != null ? options.labor_hourly_rate : (options.laborHourlyRate || 0));
    const materialCost = Number(options.material_cost != null ? options.material_cost : (options.materialCost || 0));
    const equipmentCost = Number(options.equipment_cost != null ? options.equipment_cost : (options.equipmentCost || 0));
    const subcontractorCost = Number(options.subcontractor_cost != null ? options.subcontractor_cost : (options.subcontractorCost || 0));
    const agkPct = Number(options.agk_pct != null ? options.agk_pct : (options.agkPct != null ? options.agkPct : 20.0));
    const wgPct = Number(options.wg_pct != null ? options.wg_pct : (options.wgPct != null ? options.wgPct : 6.0));
    const description = options.description || 'Nachtragsleistung';

    let materialSurchargePct = options.material_surcharge_pct != null ? options.material_surcharge_pct : options.materialSurchargePct;
    if (materialSurchargePct == null) {
      materialSurchargePct = framework === 'SIA_118' ? 12.0 : 0.0;
    }

    // 1. Einzelkosten der Teilleistungen (EKdT)
    const directLabor = laborHours * laborHourlyRate;
    const matSurcharge = materialSurchargePct > 0 ? materialCost * (materialSurchargePct / 100.0) : 0;
    const effectiveMaterial = materialCost + matSurcharge;
    const totalEkdt = directLabor + effectiveMaterial + equipmentCost + subcontractorCost;

    // 2. Zuschläge für Gemeinkosten und Gewinn
    const agkAmount = totalEkdt * (agkPct / 100.0);
    const costBasis = totalEkdt + agkAmount;
    const wgAmount = costBasis * (wgPct / 100.0);

    const netTotal = costBasis + wgAmount;
    const taxTotal = netTotal * taxRate;
    const grossTotal = netTotal + taxTotal;

    // BGB § 650c Abs. 3: 80% Abschlagsanspruch
    const abschlag80Netto = framework === 'BGB_650C' ? round2(netTotal * 0.80) : null;
    const abschlag80Brutto = framework === 'BGB_650C' ? round2(grossTotal * 0.80) : null;

    let legalBasis = '';
    let notificationHint = '';

    if (framework === 'VOB_B') {
      legalBasis = '§ 2 Abs. 5 & 6 VOB/B (Urkalkulationsfortschreibung)';
      notificationHint = '⚠️ Wichtig nach § 2 Abs. 6 Nr. 1 VOB/B: Ansprüche für Zusatzleistungen VOR Ausführung schriftlich ankündigen!';
    } else if (framework === 'BGB_650C') {
      legalBasis = '§ 650b & § 650c BGB (Tatsächlich erforderliche Kosten)';
      notificationHint = `⚖️ BGB-Bauvertrag: Nach 30 Tagen Verhandlung Anordnungsrecht. Sofortiger 80%-Abschlagsanspruch (§ 650c Abs. 3): ${abschlag80Netto ? abschlag80Netto.toFixed(2) : '0'} ${currency} Netto!`;
    } else if (framework === 'SIA_118') {
      legalBasis = 'SIA 118 Art. 48 & Art. 84-91 (Regietarif & Materialaufschlag)';
      notificationHint = '🇨🇭 SIA 118: Wöchentliche Regierapporte. Nicht beanstandete Rapporte gelten nach 10 Tagen als stillschweigend genehmigt (Art. 86).';
    } else {
      legalBasis = 'ÖNORM B 2110 Pkt. 7.3 & 7.4 (Mehrkostenforderung MKF)';
      notificationHint = '🇦🇹 ÖNORM B 2110: Mehrkostenforderung unverzüglich dem AG anzeigen unter Bezugnahme auf K3/K7-Blatt.';
    }

    return {
      framework: framework,
      legal_basis: legalBasis,
      description: description,
      country: country,
      currency: currency,
      breakdown: {
        labor_hours: round2(laborHours),
        labor_rate: round2(laborHourlyRate),
        labor_sum: round2(directLabor),
        material_base: round2(materialCost),
        material_surcharge_pct: round2(materialSurchargePct),
        material_surcharge_amount: round2(matSurcharge),
        material_effective: round2(effectiveMaterial),
        equipment_cost: round2(equipmentCost),
        subcontractor_cost: round2(subcontractorCost),
        total_ekdt: round2(totalEkdt),
        agk_pct: round2(agkPct),
        agk_amount: round2(agkAmount),
        wg_pct: round2(wgPct),
        wg_amount: round2(wgAmount),
        net_total: round2(netTotal),
        tax_rate_pct: round2(taxRate * 100.0),
        tax_total: round2(taxTotal),
        gross_total: round2(grossTotal)
      },
      abschlag_80_netto: abschlag80Netto,
      abschlag_80_brutto: abschlag80Brutto,
      notification_hint: notificationHint
    };
  }

  // ============================================================================
  // 3. MODUL: AUFMAß NACH VOB/C
  // ============================================================================

  function calculateVobAufmass(grossArea, openings, tradeType = 'wand_putz_maler', revealDepthM = 0.20) {
    const threshold = tradeType === 'boden_estrich' ? 0.50 : 2.50;

    let processedOpenings = [];
    let totalOpeningsArea = 0;
    let deductedArea = 0;
    let overmeasuredArea = 0;
    let totalRevealArea = 0;

    const opList = Array.isArray(openings) ? openings : [];

    for (const op of opList) {
      const name = op.name || 'Öffnung';
      const w = Number(op.width || 0);
      const h = Number(op.height || 0);
      const count = Number(op.count != null ? op.count : 1);
      const singleArea = w * h;
      const totalOpArea = singleArea * count;
      totalOpeningsArea += totalOpArea;

      const isDeducted = singleArea > threshold;
      let revealArea = 0;

      let status = '';
      if (isDeducted) {
        deductedArea += totalOpArea;
        const revealPerimeter = (2.0 * h) + w;
        revealArea = revealPerimeter * revealDepthM * count;
        totalRevealArea += revealArea;
        status = `Abzug (Fläche > ${threshold.toFixed(2)} m²) + Laibungszulage`;
      } else {
        overmeasuredArea += totalOpArea;
        status = `Übermessen nach VOB/C (Fläche ≤ ${threshold.toFixed(2)} m²)`;
      }

      processedOpenings.push({
        name: name,
        dimensions: `${w.toFixed(2)}m x ${h.toFixed(2)}m`,
        single_area_m2: round3(singleArea),
        count: count,
        total_area_m2: round3(totalOpArea),
        deducted: isDeducted,
        status: status,
        reveal_area_m2: round3(revealArea)
      });
    }

    const billableArea = Number(grossArea) - deductedArea + totalRevealArea;

    return {
      trade_type: tradeType,
      vob_c_threshold_m2: threshold,
      gross_area_m2: round3(grossArea),
      total_openings_count: opList.length,
      total_openings_area_m2: round3(totalOpeningsArea),
      overmeasured_area_m2: round3(overmeasuredArea),
      deducted_area_m2: round3(deductedArea),
      total_reveal_area_m2: round3(totalRevealArea),
      billable_area_m2: round3(billableArea),
      openings_detail: processedOpenings,
      rule_explanation: `VOB/C Regelung: Einzelflächen bis einschließlich ${threshold.toFixed(2)} m² werden übermessen (voll vergütet). Flächen über ${threshold.toFixed(2)} m² werden abgezogen, dafür werden Laibungen abgerechnet.`
    };
  }

  // ============================================================================
  // 4. MODUL: STEUERBONUS (§ 35a EStG DE, AT HANDWERKERBONUS, CH UNTERHALT)
  // ============================================================================

  function calculateHandwerkerSteuerbonus(laborCostGross, country = 'DE', travelCostGross = 0, equipmentCostGross = 0, marginalTaxRateChPct = 28.0) {
    const c = country.toUpperCase();
    if (!TAX_RATES[c]) {
      throw new Error(`Ungültiges Land '${c}'. Erlaubt: DE, AT, CH.`);
    }

    const eligibleGross = Number(laborCostGross) + Number(travelCostGross) + Number(equipmentCostGross);

    if (c === 'DE') {
      const ratePct = 20.0;
      const maxBonus = 1200.0;
      const maxEligible = 6000.0;
      const calculatedBonus = eligibleGross * 0.20;
      const effectiveBonus = Math.min(calculatedBonus, maxBonus);
      const isCapped = calculatedBonus > maxBonus;
      const legalRef = '§ 35a Abs. 3 EStG (Handwerkerleistungen für Renovierung/Erhaltung)';
      const notice = 'Zahlungshinweis: Barzahlungen werden vom Finanzamt nicht anerkannt! Rechnungsbetrag muss unbar auf das Konto des Handwerksbetriebs überwiesen werden.';

      return {
        country: 'DE',
        currency: 'EUR',
        legal_basis: legalRef,
        eligible_labor_gross: round2(eligibleGross),
        bonus_rate_pct: ratePct,
        calculated_bonus: round2(calculatedBonus),
        max_legal_bonus_year: maxBonus,
        effective_tax_saving: round2(effectiveBonus),
        is_capped: isCapped,
        max_eligible_expenses: maxEligible,
        notice: notice
      };
    } else if (c === 'AT') {
      const taxRate = TAX_RATES['AT'];
      const eligibleNet = eligibleGross / (1.0 + taxRate);
      const ratePct = 20.0;
      const maxBonus = 2000.0;
      const maxEligibleNet = 10000.0;
      const calculatedBonus = eligibleNet * 0.20;
      const effectiveBonus = Math.min(calculatedBonus, maxBonus);
      const isCapped = calculatedBonus > maxBonus;
      const legalRef = 'Handwerkerbonus Österreich (Bundesministerium für Arbeit und Wirtschaft)';
      const notice = 'Gilt für die Renovierung oder Errichtung von Wohnraum. Antrag online über handwerkerbonus.gv.at einreichbar.';

      return {
        country: 'AT',
        currency: 'EUR',
        legal_basis: legalRef,
        eligible_labor_gross: round2(eligibleGross),
        eligible_labor_net: round2(eligibleNet),
        bonus_rate_pct: ratePct,
        calculated_bonus: round2(calculatedBonus),
        max_legal_bonus_year: maxBonus,
        effective_tax_saving: round2(effectiveBonus),
        is_capped: isCapped,
        max_eligible_expenses_net: maxEligibleNet,
        notice: notice
      };
    } else { // CH
      const effectiveSaving = eligibleGross * (marginalTaxRateChPct / 100.0);
      const legalRef = 'Art. 32 DBG / Kantonale Steuergesetze (Werterhaltender Liegenschaftsunterhalt)';
      const notice = 'Werterhaltende Reparaturen, Maler-, Sanitär- und Dacharbeiten sind zu 100 % vom steuerbaren Einkommen bei Bund, Kanton und Gemeinde abzugsfähig.';

      return {
        country: 'CH',
        currency: 'CHF',
        legal_basis: legalRef,
        deductible_expenses_total: round2(eligibleGross),
        marginal_tax_rate_pct: marginalTaxRateChPct,
        effective_tax_saving: round2(effectiveSaving),
        notice: notice
      };
    }
  }

  // ============================================================================
  // 5. AUTOMATISIERTE TESTSUITE (--test)
  // ============================================================================

  function runAutomatedTests() {
    console.log('\n======================================================================');
    console.log('🧪 DACH HANDWERKER-KALKULATOR JS: AUTOMATISIERTER SELBSTTEST');
    console.log('======================================================================');

    let totalTests = 0;
    let passedTests = 0;

    function assertTest(condition, testName, details = '') {
      totalTests++;
      if (condition) {
        passedTests++;
        console.log(`  ✅ [PASS] ${testName}`);
      } else {
        console.log(`  ❌ [FAIL] ${testName}: ${details}`);
      }
    }

    // Test 1: Stundensatz DE Referenz
    const resDe = calculateHourlyRate(23.00, 'DE', 82.5, 30.0, 6.0);
    assertTest(resDe.base_wage === 23.00, 'Stundensatz DE: Mittellohn Basis');
    assertTest(Math.abs(resDe.direct_labor_cost - 41.98) < 0.05, 'Stundensatz DE: Lohnkosten inkl. 82.5% LZK (~41.98 €)');
    assertTest(Math.abs(resDe.self_cost_minimum - 54.57) < 0.05, 'Stundensatz DE: Selbstkosten inkl. 30% AGK (~54.57 €)');
    assertTest(Math.abs(resDe.net_hourly_rate - 57.84) < 0.05, 'Stundensatz DE: Netto-Stundensatz inkl. 6% W&G (~57.84 €)');
    assertTest(Math.abs(resDe.gross_hourly_rate - 68.83) < 0.05, 'Stundensatz DE: Brutto-Stundensatz inkl. 19% MwSt (~68.83 €)');

    // Test 2: Stundensatz CH Referenz
    const resCh = calculateHourlyRate(44.00, 'CH', 52.0, 32.0, 6.5);
    assertTest(resCh.currency === 'CHF', 'Stundensatz CH: Währung CHF');
    assertTest(Math.abs(resCh.tax_rate_pct - 8.1) < 0.01, 'Stundensatz CH: MwSt 8.1%');
    assertTest(resCh.net_hourly_rate > 90.0, 'Stundensatz CH: Netto-Stundensatz plausibel > 90 CHF');

    // Test 3: Stundensatz AT Referenz
    const resAt = calculateHourlyRate(22.00, 'AT', 94.0, 31.0, 6.0);
    assertTest(resAt.currency === 'EUR', 'Stundensatz AT: Währung EUR');
    assertTest(Math.abs(resAt.tax_rate_pct - 20.0) < 0.01, 'Stundensatz AT: USt 20.0%');
    assertTest(resAt.net_hourly_rate > 55.0, 'Stundensatz AT: Netto-Stundensatz plausibel > 55 EUR');

    // Test 4: Mittellohn Kolonne
    const workers = [
      { title: 'Meister', hourly_wage: 30.00, count: 1 },
      { title: 'Geselle', hourly_wage: 22.00, count: 2 },
      { title: 'Helfer', hourly_wage: 16.00, count: 1 }
    ];
    const resCol = calculateMittellohn(workers);
    assertTest(resCol.mittellohn === 22.50, 'Mittellohn Kolonne: Exakte Mischkalkulation (22.50 €)');

    // Test 5: Nachtrag BGB § 650c
    const resBgb = calculateNachtrag({
      framework: 'BGB_650C',
      labor_hours: 15.0,
      labor_hourly_rate: 60.00,
      material_cost: 500.00,
      equipment_cost: 100.00,
      agk_pct: 20.0,
      wg_pct: 6.0
    });
    assertTest(resBgb.breakdown.total_ekdt === 1500.00, 'Nachtrag BGB § 650c: EKdT Summe 1500 €');
    assertTest(resBgb.breakdown.net_total === 1908.00, 'Nachtrag BGB § 650c: Netto Nachtragssumme 1908 €');
    assertTest(resBgb.abschlag_80_netto === 1526.40, 'Nachtrag BGB § 650c: 80% Abschlagsanspruch (1526.40 €)');

    // Test 5b: SIA 118 Schweiz
    const resSia = calculateNachtrag({
      framework: 'SIA_118',
      labor_hours: 10.0,
      labor_hourly_rate: 95.00,
      material_cost: 1000.00,
      agk_pct: 15.0,
      wg_pct: 5.0
    });
    assertTest(resSia.currency === 'CHF', 'SIA 118: Währung CHF');
    assertTest(resSia.breakdown.material_surcharge_amount === 120.00, 'SIA 118: 12% Materialzuschlag (120 CHF)');
    assertTest(Math.abs(resSia.breakdown.net_total - 2499.53) < 0.05, 'SIA 118: Netto Regiesumme (~2499.53 CHF)');

    // Test 5c: ÖNORM B 2110
    const resOenorm = calculateNachtrag({
      framework: 'OENORM_B2110',
      labor_hours: 8.0,
      labor_hourly_rate: 65.00,
      material_cost: 400.00,
      agk_pct: 18.0,
      wg_pct: 5.0
    });
    assertTest(resOenorm.currency === 'EUR', 'ÖNORM B 2110: Währung EUR');
    assertTest(resOenorm.breakdown.tax_rate_pct === 20.0, 'ÖNORM B 2110: 20% USt');

    // Test 6: VOB/C Aufmaß
    const openings = [
      { name: 'Fenster klein', width: 1.0, height: 1.2, count: 1 },
      { name: 'Doppelfenster', width: 2.0, height: 1.8, count: 1 }
    ];
    const resAufmass = calculateVobAufmass(100.0, openings, 'wand_putz_maler', 0.20);
    assertTest(resAufmass.overmeasured_area_m2 === 1.20, 'VOB/C Aufmaß: Öffnung 1.20 m² übermessen');
    assertTest(resAufmass.deducted_area_m2 === 3.60, 'VOB/C Aufmaß: Öffnung 3.60 m² abgezogen');
    assertTest(Math.abs(resAufmass.total_reveal_area_m2 - 1.12) < 0.01, 'VOB/C Aufmaß: Laibung 1.12 m²');
    assertTest(Math.abs(resAufmass.billable_area_m2 - 97.52) < 0.01, 'VOB/C Aufmaß: Nettofläche 97.52 m²');

    // Test 7: § 35a EStG
    const resTaxNormal = calculateHandwerkerSteuerbonus(3000.00, 'DE');
    assertTest(resTaxNormal.effective_tax_saving === 600.00, '§ 35a EStG: 20% von 3000 € = 600 € Ersparnis');

    const resTaxCapped = calculateHandwerkerSteuerbonus(8000.00, 'DE');
    assertTest(resTaxCapped.effective_tax_saving === 1200.00, '§ 35a EStG: 1200 € Deckelung');
    assertTest(resTaxCapped.is_capped === true, '§ 35a EStG: is_capped Flag aktiv');

    // Test 8: AT Handwerkerbonus
    const resTaxAt = calculateHandwerkerSteuerbonus(6000.00, 'AT');
    assertTest(Math.abs(resTaxAt.effective_tax_saving - 1000.00) < 0.01, 'AT Handwerkerbonus: 20% Netto-Arbeitskosten');

    console.log('======================================================================');
    console.log(`Ergebnis: ${passedTests} von ${totalTests} JS-Tests erfolgreich absolviert!`);
    console.log('======================================================================');
    return passedTests === totalTests;
  }

  // ============================================================================
  // NODE.JS CLI HANDLER
  // ============================================================================

  if (typeof process !== 'undefined' && process.argv && process.argv.length > 1) {
    const args = process.argv.slice(2);

    if (args.includes('--test')) {
      const ok = runAutomatedTests();
      process.exit(ok ? 0 : 1);
    }

    if (args.includes('--presets')) {
      console.log('\n📋 DACH-HANDWERK BRANCHENRICHTWERTE 2026:');
      console.log('---------------------------------------------------------------------------');
      console.log('Gewerke-Kürzel  | Gewerk                              | DE (€/h)   | CH (CHF/h)');
      console.log('---------------------------------------------------------------------------');
      for (const [code, info] of Object.entries(TRADE_PRESETS)) {
        console.log(`${code.padEnd(15)} | ${info.name.padEnd(35)} | ${info.DE.hourlyWage.toFixed(2)} €    | ${info.CH.hourlyWage.toFixed(2)} CHF`);
      }
      console.log('---------------------------------------------------------------------------');
      process.exit(0);
    }

    if (args.includes('--stundensatz')) {
      let wage = 23.50;
      let country = 'DE';
      let lzk = null;
      let agk = 30.0;
      let wg = 6.0;

      for (let i = 0; i < args.length; i++) {
        if (args[i] === '--wage' && args[i + 1]) wage = parseFloat(args[i + 1]);
        if (args[i] === '--country' && args[i + 1]) country = args[i + 1].toUpperCase();
        if (args[i] === '--lzk' && args[i + 1]) lzk = parseFloat(args[i + 1]);
        if (args[i] === '--agk' && args[i + 1]) agk = parseFloat(args[i + 1]);
        if (args[i] === '--wg' && args[i + 1]) wg = parseFloat(args[i + 1]);
      }

      const res = calculateHourlyRate(wage, country, lzk, agk, wg);
      if (args.includes('--json')) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log('\n=================================================================');
        console.log(`📊 STUNDENSATZ-KALKULATION (${res.country} - ${res.currency})`);
        console.log('=================================================================');
        console.log(`• Mittellohn Fertigung         : ${res.base_wage.toFixed(2)} ${res.currency}/h`);
        console.log(`• Lohnzusatzkosten (${res.lzk_pct.toFixed(1)} %)     : + ${res.lzk_amount.toFixed(2)} ${res.currency}/h`);
        console.log(`-> Fertigungslohnkosten        : ${res.direct_labor_cost.toFixed(2)} ${res.currency}/h`);
        console.log(`• Gemeinkosten (AGK ${res.agk_pct.toFixed(1)} %)     : + ${res.agk_amount.toFixed(2)} ${res.currency}/h`);
        console.log('-----------------------------------------------------------------');
        console.log(`🎯 KOSTENDECKENDE SELBSTKOSTEN  : ${res.self_cost_minimum.toFixed(2)} ${res.currency}/h (MINDESTSATZ!)`);
        console.log(`• Wagnis & Gewinn (${res.wg_pct.toFixed(1)} %)       : + ${res.wg_amount.toFixed(2)} ${res.currency}/h`);
        console.log('=================================================================');
        console.log(`🚀 KALKULIERTER NETTO-STUNDENSATZ: ${res.net_hourly_rate.toFixed(2)} ${res.currency}/h`);
        console.log(`• Brutto inkl. ${res.tax_rate_pct.toFixed(1)}% MwSt  : ${res.gross_hourly_rate.toFixed(2)} ${res.currency}/h`);
        console.log('=================================================================');
      }
      process.exit(0);
    }
  }

  return {
    TAX_RATES,
    CURRENCIES,
    DEFAULT_LZK,
    TRADE_PRESETS,
    calculateMittellohn,
    calculateProduktivstunden,
    calculateHourlyRate,
    calculateNachtrag,
    calculateVobAufmass,
    calculateHandwerkerSteuerbonus,
    runAutomatedTests
  };
}));
