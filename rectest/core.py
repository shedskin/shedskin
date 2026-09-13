"""
wokkel core engine.

geschreven in shedskin-compatible python subset, voor transpilatie naar C++.

"""
import collections
import sys
import time


def _month_days():
    """
    op basis van bekende maandlengtes en schrikkeljaren, bereken vanaf 2000-01-01
    tot 10 jaar vanaf nu:

    - per maand, het aantal dagen ("days") tot het begin van de maand
    - per dag, de datum als YYYYMMDD ("ymd") integer

    dit berekenen we handmatig, zodat we hierna vooral met integers kunnen rekenen,
    wat in C++ extreem snel is.

    """
    month_days = []
    days_ymd = []
    days = 0
    for year in range(2000, time.localtime().tm_year+10):
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0:
            month_lengths[1] = 29
        for m, length in enumerate(month_lengths):
            month_days.append(days)
            days_ymd.extend([year * 10000 + (m + 1) * 100 + d + 1 for d in range(length)])
            days += length
    return month_days, days_ymd


MONTH_DAYS, DAYS_YMD = _month_days()


def get_days(ymd):
    """
    voor een YYYMMDD integer, bereken het aantal dagen vanaf 2000-01-01

    """
    y = ymd // 10000 - 2000
    m = (ymd // 100) % 100 - 1
    d = ymd % 100 - 1

    return MONTH_DAYS[12 * y + m] + d


def get_ymd(days):
    """
    voor een aantal dagen vanaf 2000-01-01, geef YYYYMMDD integer terug

    """
    days = max(days, 0)  # bijv. bij aflevercontext (dagen_voor=1000000)
    days = min(days, len(DAYS_YMD)-1)  # bijv. bij correctie/schuiven kun je tot ver in de toekomst komen
    return DAYS_YMD[days]


def shift_months(ymd, n):  # TODO gaat dit goed voor PatientEU voorloop periode (niet aan begin maand).. assert d == 1?
    """
    shift YYYYMMDD integer met +/- n maanden

    """
    y = ymd // 10000
    m = (ymd // 100) % 100
    d = ymd % 100

    maanden = 12 * y + (m-1) + n
    year = maanden // 12
    month = (maanden % 12) + 1

    return 10000 * year + 100 * month + d


def shift_days(ymd, n):
    """
    shift YYYYMMDD integer met +/- n dagen

    """
    return get_ymd(get_days(ymd) + n)


def datum_fmt(ymd):
    """
    datum op zijn nederlands formatteren

    """
    y = ymd // 10000
    m = (ymd // 100) % 100
    d = ymd % 100
    return '%02d-%02d-%04d' % (d, m, y)


def format_float(f, decimalen=3):
    """
    formatteer float, afgerond op N decimalen

    """
    if decimalen == 0:
        return '%.0f' % f
    elif decimalen == 1:
        return '%.1f' % f
    elif decimalen == 2:
        return '%.2f' % f
    elif decimalen == 3:
        return '%.3f' % f
    else:
        raise ValueError(f"te veel decimalen: {decimalen}")


class ATC:
    """
    ATC code

    we houden hier middelgroepen bij waar de ATC mogelijk onder valt
    (bijv. A10123 valt onder A10)

    """
    def __init__(self, code):
        self.code = code
        self.atc1 = code[:1]
        self.atc2 = code[:3]
        self.atc3 = code[:4]
        self.atc4 = code[:5]
        self.mgroepen = []

    def add_mgroep(self, mgroep):
        self.mgroepen.append(mgroep)

    def clear_mgroepen(self):
        self.mgroepen.clear()


def set_atcs(codes):
    """
    vul ATC gerelateerd globale dictionaries

    """
    global g_atcs, g_code_atcs

    # atc code -> ATC instantie (bijv. 'A10' -> ATC('A10'))
    g_atcs = {}
    for code in codes:
        g_atcs[code] = ATC(code)

    # atc code -> bijbehorende ATC (sub) instanties (bijv. 'A10' -> [ATC('A10'), ATC('A101'), ..])
    g_code_atcs = collections.defaultdict(set)
    for code, atc in g_atcs.items():
        for i in range(1, len(code)+1):
            g_code_atcs[code[:i]].add(atc)


def set_pref_beleid(pref):
    """
    vul preferente middelen (historisch)

    """
    global g_pref_beleid
    g_pref_beleid = pref


def set_atc5_naam(atc5_naam):  # TODO samenvoegen met set_atcs?
    """
    vul atc5 namen

    """
    global g_atc5_naam
    g_atc5_naam = atc5_naam


def set_codes_vervolguitgifte(codes):
    """
    vul codes vervolguitgifte (voor eerste uitgifte bepaling)

    """
    global CODES_VERVOLGUITGIFTE
    CODES_VERVOLGUITGIFTE = codes


class Groep:
    """
    Groep: (nawnr, patnr) -> Patient instantie

    """
    def __init__(self, data):
        self.data = data


class Artikel:
    """
    G-Standaard artikel

    """
    def __init__(self, nr, atc, farmaceutische_vorm_code, toedieningsweg_code, prk, gpk, hpk, ddd, inkoopkanaal, naam):
        self.nr = nr
        self.atc = g_atcs.get(atc)
        self.farmaceutische_vorm_code = farmaceutische_vorm_code
        self.toedieningsweg_code = toedieningsweg_code
        self.prk = prk
        self.gpk = gpk
        self.hpk = hpk
        self.ddd = ddd
        self.inkoopkanaal = inkoopkanaal
        self.naam = naam


class Recept:
    """
    Recept (verstrekking van een g-standaard artikel in de apotheek)

    """
    def __init__(self, artikel, datum, einddatum, aantaldagen, standaard_periode, modulaire_tariefcode, zorgverzekeraar,
                 statuswtg, hoeveelheid, sv, ddd, hoeveelheidperdag, pufjes, agb):
        self.artikel = artikel
        self.datum = datum
        self.einddatum = einddatum
        self.standaard_periode = standaard_periode
        self.modulaire_tariefcode = modulaire_tariefcode
        self.zorgverzekeraar = zorgverzekeraar
        self.statuswtg = statuswtg
        self.hoeveelheid = hoeveelheid
        self.sv = sv
        self.ddd = ddd
        self.hoeveelheidperdag = hoeveelheidperdag
        self.aantaldagen = aantaldagen
        self.pufjes = pufjes
        self.agb = agb


class Verstrekking:
    """
    Verstrekking van recept (aparte klasse voor efficientie bij correctie)

    """
    def __init__(self, recept):
        self.recept = recept
        self.atc = recept.artikel.atc  # voor indexeer performance, hoeft dan niet via via TODO nog een keer meten
        self.datum = recept.datum
        self.einddatum = recept.einddatum
        self.ddd = recept.ddd


class Patient:
    """
    Patient

    """
    def __init__(self, nawnr, patientnr, geslacht, geboortejaar, vrsn, einddatum):
        self.nawnr = nawnr
        self.patientnr = patientnr
        self.geslacht = geslacht
        self.geboortejaar = geboortejaar
        self.vrsn = vrsn
        self.indexed = False
        self._passant_cache = {}
        self._fout_cache = {}

    def is_passant(self, einddatum):
        """
        is de patient een passant? let op, 2 jaar aan data benodigd!

        per-patient cache zodat check maar 1 keer gebeurt.

        """
        result = self._passant_cache.get(einddatum, -1)
        if result != -1:
            return bool(result)

        if self.patientnr == '9999999999':
            return True

        i1 = vrs_index(self.vrsn, shift_months(einddatum, -24))
        i2 = vrs_index(self.vrsn, einddatum)

        if i1 == i2:  # geen recepten
            result = 0
        else:
            datum_a = self.vrsn[i2-1].datum
            datum_b = self.vrsn[i1].datum
            result = int(get_days(datum_a) - get_days(datum_b) <= 4)

        self._passant_cache[einddatum] = result
        return bool(result)  # TODO meteen bool van maken? of traag?

    def is_fout(self, einddatum):
        """
        is de patient wssch niet echt? let op, 1 jaar aan data benodigd!

        per-patient cache zodat check maar 1 keer gebeurt.
        """
        result = self._fout_cache.get(einddatum, -1)
        if result != -1:
            return bool(result)

        result = 0
        year = einddatum // 10000

        # geslacht check
        if self.geslacht == "O":
            result = 1

        # leeftijd check
        elif year - self.geboortejaar > 110 or year - self.geboortejaar < 0:
            result = 1
        else:
            idx_eind = vrs_index(self.vrsn, einddatum)
            idx_maand = vrs_index(self.vrsn, shift_months(einddatum, -1))
            idx_jaar = vrs_index(self.vrsn, shift_months(einddatum, -12))

            # uzovi check
            ongeldige_zorgverzekeraar = True  # TODO iemand helemaal zonder vrs in afg jaar wordt ook als fout gezien!?
            for i in range(idx_jaar, idx_eind):
                vrs = self.vrsn[i]
                if vrs.recept.zorgverzekeraar not in (9999, 9998):
                    ongeldige_zorgverzekeraar = False
                    break
            if ongeldige_zorgverzekeraar:
                result = 1

            elif idx_eind - idx_maand > 100:  # meer dan 100 in laatste maand
                result = 1
            elif idx_eind - idx_jaar > 1000:  # meer dan 1000 in laatste jaar
                result = 1

        self._fout_cache[einddatum] = result
        return bool(result)  # TODO meteen bool van maken? of traag?

    def is_recent(self, einddatum):
        """
        is de patient recent nog geweest?

        per-patient cache zodat check maar 1 keer gebeurt.
        """
        return vrs_index(self.vrsn, shift_months(einddatum, -4)) != vrs_index(self.vrsn, einddatum)

    def leeftijd(self, einddatum):
        """
        bepaal patient leeftijd op basis van geboortejaar

        """
        year = einddatum // 10000
        if einddatum % 1000 == 101:  # TODO wat gebeurt hier?
            year -= 1
        return year - self.geboortejaar


class MiddelGroep:
    """
        een middelgroep wordt gedefinieerd door een verzameling wel/niet
        condities, bijv.: wel atc A10, maar niet hpk 1234.

        bij indexeren worden alle verstrekkingen van een patient
        eenmalig afgelopen en toegevoegd aan het 'vrsn' attribuut van de
        bijbehorende middelgroepen.

        wanneer er alleen atc wel/niet zijn gegeven, kunnen we hierbij
        heel efficient checken of een verstrekking er toe behoort.

    """
    def __init__(self, naam=None, omschrijving=None, atc_wel=None, atc_niet=None, farm_vorm=None, niet_farm_vorm=None,
                 toedieningsweg=None, niet_toedieningsweg=None, prk=None, prk_niet=None, gpk=None, gpk_niet=None,
                 hpk=None, hpk_niet=None):
        self.naam = naam
        self.omschrijving = omschrijving

        self.atc_wel = atc_wel.upper().split() if atc_wel else None
        self.atc_niet = atc_niet.upper().split() if atc_niet else None
        self.farm_vorm = [int(fv) for fv in farm_vorm.split()] if farm_vorm else None
        self.niet_farm_vorm = [int(fv) for fv in niet_farm_vorm.split()] if niet_farm_vorm else None
        self.toedieningsweg = [int(t) for t in toedieningsweg.split()] if toedieningsweg else None
        self.niet_toedieningsweg = [int(t) for t in niet_toedieningsweg.split()] if niet_toedieningsweg else None
        self.hpk = [int(t) for t in hpk.split()] if hpk else None
        self.niet_hpk = [int(t) for t in hpk_niet.split()] if hpk_niet else None
        self.prk = [int(t) for t in prk.split()] if prk else None
        self.niet_prk = [int(t) for t in prk_niet.split()] if prk_niet else None
        self.gpk = [int(t) for t in gpk.split()] if gpk else None
        self.niet_gpk = [int(t) for t in gpk_niet.split()] if gpk_niet else None

        self.vrsn = []

        # only atc_wel/atc_niet
        self.fast_contains = True
        if (
            self.hpk or self.niet_hpk or
            self.prk or self.niet_prk or
            self.gpk or self.niet_gpk or
            self.farm_vorm or self.niet_farm_vorm or
            self.toedieningsweg or self.niet_toedieningsweg
        ):
            self.fast_contains = False

        self.atc_wel = self.atc_wel
        self.atc_niet = self.atc_niet
        self.farm_vorm = self.farm_vorm
        self.niet_farm_vorm = self.niet_farm_vorm
        self.toedieningsweg = self.toedieningsweg
        self.niet_toedieningsweg = self.niet_toedieningsweg
        self.hpk = self.hpk
        self.niet_hpk = self.niet_hpk
        self.prk = self.prk
        self.niet_prk = self.niet_prk
        self.gpk = self.gpk
        self.niet_gpk = self.niet_gpk

    def __contains__(self, vrs):
        """
        valt de gegeven verstrekking onder deze middelgroep? (trage versie!)

        """
        if self.farm_vorm and vrs.recept.artikel.farmaceutische_vorm_code not in self.farm_vorm:
            return False
        if self.niet_farm_vorm and vrs.recept.artikel.farmaceutische_vorm_code in self.niet_farm_vorm:
            return False

        if self.toedieningsweg and vrs.recept.artikel.toedieningsweg_code not in self.toedieningsweg:
            return False
        if self.niet_toedieningsweg and vrs.recept.artikel.toedieningsweg_code in self.niet_toedieningsweg:
            return False

        if self.atc_niet and vrs.atc:
            for code in self.atc_niet:
                if vrs.atc.code.startswith(code):
                    return False

        if self.niet_gpk and vrs.recept.artikel.gpk in self.niet_gpk:
            return False
        if self.niet_prk and vrs.recept.artikel.prk in self.niet_prk:
            return False
        if self.niet_hpk and vrs.recept.artikel.hpk in self.niet_hpk:
            return False

        if self.atc_wel or self.hpk or self.prk or self.gpk:
            match = False
            if self.atc_wel and vrs.atc:
                for code in self.atc_wel:
                    if vrs.atc.code.startswith(code):
                        match = True
            if self.hpk and vrs.recept.artikel.hpk in self.hpk:
                match = True
            if self.prk and vrs.recept.artikel.prk in self.prk:
                match = True
            if self.gpk and vrs.recept.artikel.gpk in self.gpk:
                match = True
            if not match:
                return False

        return True


class Marker:
    """
    markers worden alleen gebruikt in vrs_interactie.

    per verstrekking maken we hierbij twee markers: eentje voor de
    start datum en eentje voor eind datum.

    het 'i' attribuut wijst naar de bijbehorende verstrekking lijst.

    de 'add' attributen helpen bepalen hoeveel lijsten er op een
    gegeven moment overlappen.

    """
    def __init__(self, i, datum, add, add_verplicht):
        self.i = i
        self.datum = datum
        self.add = add
        self.add_verplicht = add_verplicht


class Period:
    """
    eenvoudige periode, bestaande uit start en eind datum

    """
    def __init__(self, start, eind):
        self.start = start
        self.eind = eind


NO_PERIODS = []  # sneller om deze te cachen


def vrs_gebruik(vrsn, start, eind):  # TODO snellere versie als geen perioden nodig alleen ja/nee
    """
    worden de verstrekkingen gebruikt binnen de aangegeven periode?

    """
    if not vrsn:
        return NO_PERIODS
    return vrs_interactie([vrsn], start, eind)


def vrs_interactie(vrsnn, startdatum, einddatum, minimum=-1, vrsnn_verplicht=[]):  # snellere case voor 1 vrsn lijst (gebruik?) zou kunnen; perioden vaak ook niet nodig, kan zelf onaf/totaal checken
    """
    bepaalt overlap in gebruik tussen de gegeven verstrekking lijsten,
    binnen de aangegeven periode.

    het 'minimum' argument geeft het minimum aantal verstrekking lijsten dat moet
    overlappen (default alles).

    het 'vrsnn_verplicht' geeft verstrekking lijsten die verplicht onderdeel zijn
    van een overlap.

    de functie geeft een lijst met perioden terug.

    implementatie:

    per verstrekking maken we twee Marker objecten aan, 1 voor start en 1 voor
    eind datum. makers weten tot welke verstrekking lijst ze behoren ('i' attribuut).

    we sorteren nu alle markers op datum, en lopen het resultaat af, waarbij we
    ondertussen bijhouden bij elke marker wat er op het betreffende moment allemaal
    overlapt, en of dat bijv. boven het minimum valt en alle verplichte lijsten
    betreft.

    """
    total = len(vrsnn) + len(vrsnn_verplicht)
    if minimum == -1:
        minimum = total

    # check minimale vrsn aanwezig voor gevraagde interactie
    iets = 0
    for vrsn in vrsnn:
        if vrsn:
            iets += 1
    for vrsn in vrsnn_verplicht:
        if vrsn:
            iets += 1
        else:
            return NO_PERIODS
    if iets < minimum:
        return NO_PERIODS

    periods = []
    vrsnn = vrsnn_verplicht + vrsnn

    # start, eind makers maken en sorteren
    markers = []
    for i, vrsn in enumerate(vrsnn):
        verplicht = (i < len(vrsnn_verplicht))
        for vrs in vrsn:
            markers.append(Marker(i, vrs.datum, 1, 1 if verplicht else 0))
            markers.append(Marker(i, vrs.einddatum, -1, -1 if verplicht else 0))
    markers.sort(key=lambda m: m.datum)

    # markers aflopen en overlap status bijhouden
    counts = [0] * total
    counts_verplicht = [0] * total
    i = 0
    overlap = False
    while i < len(markers):
        datum = markers[i].datum
        while i < len(markers) and markers[i].datum == datum:
            counts[markers[i].i] += markers[i].add
            counts_verplicht[markers[i].i] += markers[i].add_verplicht
            i += 1

        # check status per unieke dag
        count = 0
        count_verplicht = 0
        for j in range(total):
            if counts[j] > 0:
                count += 1
            if counts_verplicht[j] > 0:
                count_verplicht += 1

        # overlap?
        nu_overlap = (count >= minimum) and (count_verplicht == len(vrsnn_verplicht))

        # wel->niet of niet->wel overlap switch?
        if not overlap and nu_overlap:
            start = datum
        elif overlap and not nu_overlap:
            if datum > startdatum and start < einddatum:
                start = max(start, startdatum)
                eind = min(datum, einddatum)
                periods.append(Period(start, eind))

        overlap = nu_overlap

    return periods


def vrs_index(recepten, datum):
    """
    bisection search op datum.

    veel efficienter dan hele (al gesorteerde) lijsten aflopen.

    zie: https://docs.python.org/3/library/bisect.html

    """
    _lo, _hi = 0, len(recepten)
    while _lo < _hi:
        mid = (_lo + _hi) // 2
        if recepten[mid].datum < datum:
            _lo = mid + 1
        else:
            _hi = mid
    return _lo


def vrs_schuiven(vrsn):
    """
    schuif verstrekkingen vooruit in de tijd zodat ze niet overlappen

    voor efficientie maken we alleen nieuwe Verstrekking instanties bij wijzigingen.

    """
    result = vrsn[:]

    for i, vrs in enumerate(vrsn):
        # schuif na laatste verstrekking
        if i > 0 and vrs.datum < laatst:
            vrs2 = Verstrekking(vrs.recept)
            days = get_days(laatst) - get_days(vrs.datum)
            vrs2.datum = shift_days(vrs.datum, days)
            vrs2.einddatum = shift_days(vrs.einddatum, days)
            result[i] = vrs2

        # verstrekking ongewijzigd
        else:
            vrs2 = vrs

        laatst = vrs2.einddatum

    return result


def vrs_correctie(vrsn, nivo, atc_wissel=None):
    """
    corrigeer verstrekkingen op gegeven nivo.

    dit is niets anders dan opsplitsen op nivo en schuiven, en dan weer
    sorteren op datum.

    """
    if nivo is None:
        return vrs_schuiven(vrsn)
    key_vrsn = vrs_split(vrsn, nivo, atc_wissel)
    result = []
    for key, vrsn in key_vrsn.items():
        result.extend(vrs_schuiven(vrsn))
    result.sort(key=lambda v: v.datum)
    return result


def vrs_split(vrsn, nivo, atc_wissel=None):
    """
    split verstrekkingen op aangegeven nivo.

    met atc-wissels kunnen we uitzonderingen maken voor specifieke atcs,
    zodat deze onder een andere nivo 'key' terecht komen.

    """
    key_vrsn = {}

    # deze atcs zijn uitwisselbaar binnen de gebruikte context,
    # dus als 1 groep corrigeren (bijv. 2 groepen: 'A10A+A10B A10C+A10D+A10E')
    atc_map = None
    if atc_wissel:
        atc_map = {}
        for atcs_term in atc_wissel.split():
            atcs = atcs_term.upper().split("+")
            for code in atcs[1:]:
                atc_map[code] = atcs[0]

    for vrs in vrsn:  # TODO gebruik vrs_split
        atc = vrs.recept.artikel.atc
        if nivo == 'atc1':
            code = atc.atc1
        elif nivo == 'atc2':
            code = atc.atc2
        elif nivo == 'atc3':
            code = atc.atc3
        elif nivo == 'atc4':
            code = atc.atc4
        elif nivo == 'atc5':
            code = atc.code
        else:
            raise ValueError(f'ongeldig nivo: "{nivo}"')
        if atc_wissel:
            code = atc_map.get(code, code)
        if code in key_vrsn:
            key_vrsn[code].append(vrs)
        else:
            key_vrsn[code] = [vrs]

    return key_vrsn


def vrs_aantal(_vrsn, datum_begin, datum_eind):
    """
    bepaalt het aantal verstrekkingen in een periode.
    """
    return vrs_index(_vrsn, datum_eind) - vrs_index(_vrsn, datum_begin)


def vrs_gemiddeld_hulp(vrs, soort_dosering):
    """
    geeft aangegeven soort 'dosering' terug voor verstrekking.

    helper voor vrs_gemiddeld.

    """
    if soort_dosering == "DDD":
        return vrs.ddd
    elif soort_dosering == "eenheid":
        if vrs.recept.artikel.atc.code.startswith("R03"):
            return vrs.recept.pufjes
        return vrs.recept.hoeveelheid
    elif soort_dosering == "gebruiksdagen":
        return get_days(vrs.einddatum) - get_days(vrs.datum)
    else:
        raise ValueError(f'ongeldige soort_dosering: "{soort_dosering}"')


def vrs_gemiddeld(_vrsn, soort_dosering, aantal_iets, vrs_of_dag, soort_periode, start_periode, eind_periode):
    """
    berekent gemiddelde van 'soort_dosering' tussen afleverdatum eerste en laatste voorschrift,
    met veel opties. correspondeert 1 op 1 met wokkel patient dosering criterium.

    """
    # [(afleverdatum, (totale) dosering), ..]
    dos_per_iets = []
    if vrs_of_dag == "verstrekkingen":
        for vrs in _vrsn:
            hoeveel = vrs_gemiddeld_hulp(vrs, soort_dosering)
            dos_per_iets.append((vrs.datum, hoeveel))
    else:
        dag_totaal = {}
        for vrs in _vrsn:
            hoeveel = vrs_gemiddeld_hulp(vrs, soort_dosering)
            try:
                dag_totaal[vrs.datum] += hoeveel
            except KeyError:
                dag_totaal[vrs.datum] = hoeveel
        for dag in sorted(dag_totaal):
            dos_per_iets.append((dag, dag_totaal[dag]))

    # haal laatste zoveel verstrekkingen/dagen eruit
    if aantal_iets != -1:
        if len(dos_per_iets) < aantal_iets:  # kunnen we niks mee
            return None
        dos_per_iets = dos_per_iets[-aantal_iets:]

    # bepaal gemiddelde dosering
    totaal = sum([d[1] for d in dos_per_iets])
    if soort_periode == "starter":
        _dagen = get_days(eind_periode) - get_days(dos_per_iets[0][0])
    elif soort_periode == "stopper":
        _dagen = get_days(max([vrs.einddatum for vrs in _vrsn])) - get_days(start_periode)  # TODO ok om voorbij eind_periode te gaan..?
    else:
        totaal = sum([d[1] for d in dos_per_iets[:-1]])
        _dagen = get_days(dos_per_iets[-1][0]) - get_days(dos_per_iets[0][0])
    if _dagen == 0:
        return None  # kunnen we niks mee
    return totaal, _dagen


class Rapportage:
    """
    Rapportage.

    base klasse voor PatientOverzicht, en (eventueel) andere rapportages.

    """
    def setup(self, mgroepen, vrslijsten, patcrits):
        """
        bewaar alles wat nodig is voor indexeren, lengte bepaling.

        """
        self.mgroepen = mgroepen
        for vcrit in vrslijsten:
            vcrit.rapportage = self
        self.maanden = 0
        for v in vrslijsten:
            self.maanden = max(self.maanden, v.lengte())
        for p in patcrits:
            self.maanden = max(self.maanden, p.lengte())

    def lengte(self):
        """
        de lengte geeft aan hoeveel data er voor de betreffende rapportage
        (wokkel) nodig is.
        """
        return self.maanden

    def maak_index(self):
        """
        bepaal (eenmalig) per ATC code welke middelgroepen er (mogelijk)
        bij horen.

        dit kijkt alleen naar middelgroep "atc wel/niet", en is dus niet
        voldoende als er nog meer middelgroep condities zijn.

        """
        for atc in g_atcs.values():
            atc.clear_mgroepen()  # TODO alleen gebruikte mgroepen?
        wel = set()
        niet = set()
        for mgroep in self.mgroepen:
            wel.clear()
            niet.clear()
            if mgroep.atc_wel:
                for atc_wel in mgroep.atc_wel:
                    wel.update(g_code_atcs[atc_wel])
            if mgroep.atc_niet:
                for atc_niet in mgroep.atc_niet:
                    niet.update(g_code_atcs[atc_niet])
            for atc in wel:
                if atc not in niet:
                    atc.add_mgroep(mgroep)

    def indexeer(self, p, i1, i2):
        """
        voor een gegeven patient, gebruik index uit maak_index om efficient
        alle (mogelijke) verstrekkingen voor alle middelgroepen te bepalen.

        """
        for mgroep in self.mgroepen:  # TODO kan nog sneller met bijv. timestamps..?
            mgroep.vrsn.clear()

        for i in range(i1, i2):
            vrs = p.vrsn[i]
            if vrs.atc is not None:  # TODO wat als het None is..?
                mgroepen = vrs.atc.mgroepen
                for mgroep in mgroepen:
                    mgroep.vrsn.append(vrs)


class Indicator:  # pragma: nocover
    """
    deprecated!

    """
    def __init__(self, naam, omschrijving=None, teller_criterium=None, noemer_criterium=None, tonen=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.teller = teller_criterium
        self.noemer = noemer_criterium


class Indicatoren:  # pragma: nocover
    """
    deprecated!

    """
    def __init__(self, naam, omschrijving=None, lijst=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijst = lijst


class IndicatorLijst(Rapportage):  # pragma: nocover
    """
    deprecated!

    """
    def __init__(self, naam, omschrijving=None, indicatoren=None, patient_keuze=None, uitsluiten=None, verhaal=None, info=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.patient_keuze = patient_keuze
        self.uitsluiten = uitsluiten
        assert len(indicatoren.lijst) == 1
        self.indicatoren = indicatoren

    def __call__(self, groep, einddatum):
        result = []
        self.maak_index()
        for p in groep.data.values():
            p.indexed = False
            if self.uitsluiten is not None and self.uitsluiten(p, einddatum):  # TODO check of uitsluiten/selectie sneller om te checken (als patienteig?)
                continue
            if self.patient_keuze is not None and not self.patient_keuze(p, einddatum):
                continue
            indicator = self.indicatoren.lijst[0]
            if indicator.noemer(p, einddatum):
                patient_in_teller = 0
                if indicator.teller(p, einddatum):
                    patient_in_teller = 1
                result.append({
                    'nawnr': str(p.nawnr),
                    'patientnr': str(p.patientnr),
                    'patient_in_teller': str(patient_in_teller),
                    'geslacht': p.geslacht,
                    'geboortejaar': str(p.geboortejaar),
                })
        return result


class PatientOverzicht(Rapportage):
    """
    selecteert patienten op basis van selectie/exclusie patient criteria.

    per 'informatie' component bepaalt het vervolgens de gevraagde
    informatie per patient.

    """
    def __init__(self, naam, omschrijving=None, selectie=None, exclusie=None, info=None, verhaal=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.selectie = selectie
        self.exclusie = exclusie
        self.info = info

    def __call__(self, groep, einddatum):
        result = []
        self.maak_index()
        for p in groep.data.values():
            p.indexed = False
            if self.exclusie is not None and self.exclusie(p, einddatum):
                continue
            if self.selectie is not None and not self.selectie(p, einddatum):
                continue
            for info in self.info.lijst:
                result.append({
                    'nawnr': str(p.nawnr),
                    'patientnr': str(p.patientnr),
                    'info': info.naam,
                    'waarde': info(p, einddatum) or '',
                })
        return result


class CorrectieTerm:
    """
    hiermee kun je uitzonderingen op een reguliere correctie definieren.

    bijv. opties='atc', waarden='A10A A10B', vaste_periode=20

    deze worden verwerkt in VerstrekkingLijstEigenschappen.corrigeer.

    """
    def __init__(self, naam=None, omschrijving=None, opties=None, waarden=None, vaste_periode=-1, ddd_factor=1.0):
        self.naam = naam
        self.omschrijving = omschrijving
        self.opties = opties
        self.waarden = waarden.upper().split() if waarden else None
        self.vaste_periode = vaste_periode
        self.ddd_factor = ddd_factor


class Correctie:
    """
    parameters voor correctie.

    plus mogelijke uitzonderingen hierop (atc_wissel, correctietermen).

    deze parameters worden verwerkt in VerstrekkingLijstEigenschappen.corrigeer.

    """
    def __init__(self, naam=None, omschrijving=None, nivo=None, standaard_periode=1, ddd_factor=1.0, vaste_periode=-1, vaste_verlenging=-1,
                 gmddd_van=-1.0, gmddd_tot=-1.0, atc_wissel=None, correctietermen=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.nivo = nivo
        self.standaard_periode = standaard_periode
        self.ddd_factor = ddd_factor
        self.vaste_periode = vaste_periode
        self.vaste_verlenging = vaste_verlenging
        self.gmddd_van = gmddd_van
        self.gmddd_tot = gmddd_tot
        self.atc_wissel = atc_wissel
        self.correctietermen = correctietermen


class VerstrekkingCriterium:
    """
    base klasse voor verstrekking criteria (geeft ja/nee voor een gegeven verstrekking)

    """
    def __call__(self, v):
        raise NotImplementedError  # pragma: nocover


class VerstrekkingEigenschappen(VerstrekkingCriterium):
    """
    verstrekking criterium dat kijkt naar de eigenschappen van een verstrekking.

    """
    def __init__(self, naam, omschrijving=None, wmg=None, voorschrijver=None, modulairetariefcode=None, middelgroep=None,
                 ddd_van=-1.0, ddd_tot=-1.0, ddd_per_dag_van=-1.0, ddd_per_dag_tot=-1.0, dagen_van=-1, dagen_tot=-1,
                 zorgverzekeraar=None, inkoopkanaal_naam=None, preferente_middelen=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.wmg = wmg
        self.voorschrijver = voorschrijver
        self.middelgroep = middelgroep
        self.modulaire_tariefcode = [int(mtc) for mtc in modulairetariefcode.split()] if modulairetariefcode else None
        self.ddd_van = ddd_van
        self.ddd_tot = ddd_tot
        self.ddd_per_dag_van = ddd_per_dag_van
        self.ddd_per_dag_tot = ddd_per_dag_tot
        self.dagen_van = dagen_van
        self.dagen_tot = dagen_tot
        self.zorgverzekeraar = [int(zv) for zv in zorgverzekeraar.split()] if zorgverzekeraar else None
        self.inkoopkanaal_naam = inkoopkanaal_naam
        self.preferente_middelen = preferente_middelen

    def __call__(self, vrs):
        if self.middelgroep and vrs not in self.middelgroep:  # TODO geen fast_contains? naar __contains__?
            return False

        if self.wmg:
            if self.wmg == 'ja' and vrs.recept.statuswtg != 1:
                return False
            elif self.wmg == 'nee' and vrs.recept.statuswtg == 1:
                return False

        if self.voorschrijver:
            if (
                (self.voorschrijver == "huisarts" and vrs.recept.sv != 1)
                or (self.voorschrijver == "specialist" and vrs.recept.sv not in (3, 6, 9))
                or (self.voorschrijver == "specialist of overig" and vrs.recept.sv == 1)
            ):
                return False

        if self.modulaire_tariefcode:
            if vrs.recept.modulaire_tariefcode not in self.modulaire_tariefcode:
                return False

        if self.zorgverzekeraar:
            if vrs.recept.zorgverzekeraar not in self.zorgverzekeraar:
                return False

        if self.ddd_van != -1 and vrs.ddd < self.ddd_van:  # TODO helper
            return False
        if self.ddd_tot != -1 and vrs.ddd >= self.ddd_tot:
            return False

        if self.ddd_per_dag_van != -1 or self.ddd_per_dag_tot != -1:
            dagen = get_days(vrs.einddatum) - get_days(vrs.datum)
            if dagen and vrs.ddd:
                ddd_per_dag = vrs.ddd / dagen
                if self.ddd_per_dag_van != -1.0 and ddd_per_dag < self.ddd_per_dag_van:  # TODO helper
                    return False
                if self.ddd_per_dag_tot != -1.0 and ddd_per_dag >= self.ddd_per_dag_tot:
                    return False
            else:
                return False

        if self.dagen_van != -1 or self.dagen_tot != -1:
            dagen = get_days(vrs.einddatum) - get_days(vrs.datum)
            if self.dagen_van != -1 and dagen < self.dagen_van:  # TODO helper
                return False
            if self.dagen_tot != -1 and dagen >= self.dagen_tot:
                return False

        if self.inkoopkanaal_naam:
            assert self.inkoopkanaal_naam == 'generiek'  # TODO
            if vrs.recept.artikel.inkoopkanaal not in (2, 4):
                return False

        if self.preferente_middelen:
            assert self.preferente_middelen == 'ja'
            jaar = vrs.datum // 10000
            maand = (vrs.datum // 100) % 100
            artikelnr = vrs.recept.artikel.nr
            if not (artikelnr, vrs.recept.zorgverzekeraar) in g_pref_beleid[jaar, maand]:  # TODO this can't be very fast....
                return False

        return True


class VerstrekkingLogischTerm(VerstrekkingCriterium):
    """
    logisch verstrekking criterium term (wel/niet verstrekking criterium)

    bijv. "NIET: verstrekking-via-huisarts"

    """
    def __init__(self, naam, omschrijving='', welniet=None, criterium=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.welniet = (welniet == 'WEL')
        self.criterium = criterium

    def __call__(self, vrs):
        if self.criterium is None:
            return False
        if self.welniet:
            return self.criterium(vrs)
        else:
            return not self.criterium(vrs)


class VerstrekkingLogisch(VerstrekkingCriterium):
    """
    logisch verstrekking criterium (en/of van verstrekking logisch termen)

    bijv. "verstrekking ddd > 4 EN NIET: verstrekking-via-huisarts"

    """
    def __init__(self, naam, omschrijving='', enof=None, termen=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.of = (enof == 'OF')
        self.termen = termen

    def __call__(self, vrs):
        if self.of:
            for term in self.termen:
                if term(vrs):
                    return True
            return False
        else:
            for term in self.termen:
                if not term(vrs):
                    return False
            return True


class VerstrekkingLijstCriterium:
    """
    base klasse voor verstrekking lijst criteria (geeft een lijst met al dan niet gecorrigeerde verstrekkingen)

    """
    def setup_einddatum(self, einddatum):  # pragma: nocover
        pass

    def bepaal(self, p, einddatum):
        raise NotImplementedError  # pragma: nocover

    def lengte(self):  # pragma: nocover
        return -1


class VerstrekkingLijstEigenschappen(VerstrekkingLijstCriterium):
    """
    verstrekking lijst criterium dat kijkt naar eventuele middelgroep en/of verstrekking filter,
    en het resultaat eventueel corrigeert.

    indien er geen middelgroep is gegeven, worden alle patient verstrekkingen genomen
    (binnen gegeven periode).

    """
    def __init__(self, naam, omschrijving=None, middelgroep=None, correctie=None, datum_tot=0, datum_van=-1, verstrekking=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.middelgroep = middelgroep
        self.datum_tot = datum_tot
        self.datum_van = datum_van
        self.correctie = correctie
        self.verstrekking = verstrekking
        self.vrsn = []
        self.vrsn_temp = []
        self.slow_check = bool(middelgroep) and (not bool(middelgroep.atc_wel) or bool(middelgroep.hpk) or bool(middelgroep.prk) or bool(middelgroep.gpk))

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def lengte(self):
        return self.datum_van

    def corrigeer(self, vrs):
        """
        corrigeer (schuif) gegeven verstrekkingen op basis van gegeven correctie
        (en eventueel correctietermen) parameters.

        """
        correctie = self.correctie

        # corrigeer aantaldagen
        gmddd_van, gmddd_tot = correctie.gmddd_van, correctie.gmddd_tot
        aantaldagen = vrs.recept.aantaldagen
        if gmddd_van != -1.0 or gmddd_tot != -1.0:
            if (
                not vrs.recept.hoeveelheidperdag
                or (gmddd_van != -1.0 and not gmddd_van <= vrs.recept.hoeveelheidperdag)  # TODO staat er een AND NOT in wokkel3..?
                or (gmddd_tot != -1.0 and not vrs.recept.hoeveelheidperdag <= gmddd_tot)
            ):
                aantaldagen = int(vrs.recept.hoeveelheid * (vrs.recept.artikel.ddd or 1))  # TODO wat is verschil tussen recept.ddd en artikel.ddd?
        if correctie.vaste_periode != -1:
            aantaldagen = correctie.vaste_periode
        elif aantaldagen:
            pass
        elif correctie.standaard_periode != -1:
            aantaldagen = correctie.standaard_periode  # niet -1?
        else:
            aantaldagen = 1
        if correctie.vaste_verlenging != -1:
            aantaldagen += correctie.vaste_verlenging

        # corrigeer ddd
        ddd = vrs.ddd * correctie.ddd_factor

        # uitzonderingen
        correctietermen = correctie.correctietermen
        if correctietermen:
            for term in correctietermen:
                uitzondering = False

                waarden = term.waarden
                if not waarden:
                    continue

                opties = term.opties
                if opties == "atc":
                    atc5 = vrs.recept.artikel.atc.code
                    uitzondering = bool([atc for atc in waarden if atc5.startswith(atc)])
                elif opties == "hpk":
                    uitzondering = vrs.recept.artikel.hpk in [int(w) for w in waarden]
                elif opties == "prk":
                    uitzondering = vrs.recept.artikel.prk in [int(w) for w in waarden]
                elif opties == "gpk":
                    uitzondering = vrs.recept.artikel.gpk in [int(w) for w in waarden]

                if uitzondering:
                    if term.vaste_periode != -1:
                        aantaldagen = term.vaste_periode

                    ddd = term.ddd_factor * vrs.recept.ddd

        # corrigeer vrs
        einddatum = shift_days(vrs.datum, aantaldagen)
        if einddatum != vrs.einddatum or ddd != vrs.ddd:
            vrs = Verstrekking(vrs.recept)
            vrs.einddatum = einddatum
            vrs.ddd = ddd
        return vrs

    def bepaal(self, p, einddatum):
        """
        bepaal (lazy!) de verstrekkingen voor dit criterium.

        """
        self.vrsn.clear()
        self.vrsn_temp.clear()

        # middelgroep/patient vrsn
        middelgroep = self.middelgroep
        if middelgroep is None:
            i1 = vrs_index(p.vrsn, shift_months(einddatum, -self.datum_van))
            i2 = vrs_index(p.vrsn, shift_months(einddatum, -self.datum_tot))
            for i in range(i1, i2):
                vrs = p.vrsn[i]
                self.vrsn_temp.append(self.corrigeer(vrs))
        else:
            # indexeer pas wanneer een vrs lijst nodig blijkt
            if not p.indexed:
                i1 = vrs_index(p.vrsn, shift_months(einddatum, -self.rapportage.maanden))
                i2 = vrs_index(p.vrsn, einddatum)
                self.rapportage.indexeer(p, i1, i2)
                p.indexed = True

            # gebruik geindexeerde vrsn
            if self.slow_check:
                i1 = vrs_index(p.vrsn, shift_months(einddatum, -self.datum_van))
                i2 = vrs_index(p.vrsn, shift_months(einddatum, -self.datum_tot))
                for i in range(i1, i2):
                    vrs = p.vrsn[i]
                    if vrs in middelgroep:
                        self.vrsn_temp.append(self.corrigeer(vrs))
            else:
                i1 = vrs_index(middelgroep.vrsn, self.start)
                i2 = vrs_index(middelgroep.vrsn, self.eind)
                for i in range(i1, i2):
                    vrs = middelgroep.vrsn[i]
                    if middelgroep.fast_contains or vrs in middelgroep:
                        self.vrsn_temp.append(self.corrigeer(vrs))

        # schuiven en filteren
        if self.vrsn_temp:
            vrsn = self.vrsn_temp
            correctie = self.correctie

            # schuiven
            if correctie is not None and correctie.nivo and len(vrsn) > 1:
                nivo = correctie.nivo
                if nivo == 'geneesmiddelgroep':  # TODO gewoon doorgeven, in vrs_correctie checken?
                    nivo = None
                atc_wissel = correctie.atc_wissel
                vrsn = vrs_correctie(vrsn, nivo, atc_wissel)

            # filteren
            if self.verstrekking is not None:
                vrsn = [vrs for vrs in vrsn if self.verstrekking(vrs)]

            self.vrsn.extend(vrsn)


class VerstrekkingLijstSamengesteld(VerstrekkingLijstCriterium):
    """
    verstrekking lijst criterium, waarmee de verstrekkingen van meerdere
    verstrekking lijst criteria kunnen worden samengevoegd.

    het resultaat wordt eventueel (weer) gecorrigeerd op het gegeven nivo.

    """
    def __init__(self, naam, omschrijving=None, lijsten=None, nivo=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijsten = lijsten
        self.datum_van = 0  # voor max(datum_van)
        self.nivo = nivo
        self.vrsn = []
        self.vrsn_temp = []

    def bepaal(self, p, einddatum):
        self.vrsn.clear()
        self.vrsn_temp.clear()

        for lijst in self.lijsten:
            lijst.bepaal(p, einddatum)  # TODO ontwijk tussen lijsten
            self.vrsn_temp.extend(lijst.vrsn)
        self.vrsn_temp.sort(key=lambda v: v.datum)

        vrsn = self.vrsn_temp

        if vrsn:
            if self.nivo and len(vrsn) > 1:
                nivo = self.nivo
                if nivo == 'geneesmiddelgroep':
                    nivo = None
                vrsn = vrs_correctie(vrsn, nivo)

            self.vrsn.extend(vrsn)


class PatientCriterium:
    """
    base klasse voor patient criteria (geeft ja/nee voor een gegeven patient)

    """
    def setup_einddatum(self, einddatum):  # pragma: nocover
        pass

    def __call__(self, p, einddatum):
        raise NotImplementedError  # pragma: nocover

    def lengte(self):  # pragma: nocover
        return -1


class PatientEigenschappen(PatientCriterium):
    """
    patient criterium dat kijkt naar de eigenschappen van een patient.

    """
    def __init__(self, naam=None, omschrijving=None, passant=None, fout=None, leeftijd_min=-1, leeftijd_max=-1, zv_soort='recent', geslacht=None, recent=None):  # TODO zv_soort?
        self.naam = naam
        self.omschrijving = omschrijving
        self.passant = passant
        self.fout = fout
        self.geslacht = geslacht
        self.leeftijd_min = leeftijd_min
        self.leeftijd_max = leeftijd_max
        self.recent = recent

        self.passant_ja = (passant == 'ja')
        self.passant_nee = (passant == 'nee')
        self.fout_ja = (fout == 'ja')
        self.fout_nee = (fout == 'nee')
        self.recent_ja = (recent == 'ja')
        self.recent_nee = (recent == 'nee')

        self.geslacht_check = (geslacht is not None)
        self.leeftijd_check = (leeftijd_min != -1 or leeftijd_max != -1)
        self.or_check = (passant is not None or fout is not None or recent is not None)

    def lengte(self):
        if self.passant_ja or self.passant_nee:
            return 24
        elif self.fout_ja or self.fout_nee:
            return 12
        elif self.recent_ja or self.recent_nee:
            return 4
        else:
            return -1

    def __call__(self, p, einddatum):
        if self.leeftijd_check:
            leeftijd = p.leeftijd(einddatum)
            if not 0 <= leeftijd < 120:
                return False
            if self.leeftijd_min != -1 and leeftijd < self.leeftijd_min:
                return False
            if self.leeftijd_max != -1 and leeftijd >= self.leeftijd_max:
                return False

        if self.geslacht_check and p.geslacht != self.geslacht:
            return False

        if self.or_check:
            if self.passant_nee and not p.is_passant(einddatum):
                return True
            if self.passant_ja and p.is_passant(einddatum):
                return True

            if self.fout_nee and not p.is_fout(einddatum):
                return True
            if self.fout_ja and p.is_fout(einddatum):
                return True

            if self.recent_nee and not p.is_recent(einddatum):
                return True
            if self.recent_ja and p.is_recent(einddatum):
                return True

            return False

        return True


class PatientLogisch(PatientCriterium):
    """
    logisch patient criterium (en/of van patient logisch termen)

    bijv. "NIET gebruiker snoepjes EN WEL overlap jam met pindakaas"

    """
    def __init__(self, naam, omschrijving=None, enof=None, termen=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.of = (enof == 'OF')
        self.termen = termen

    def __call__(self, p, einddatum):
        if self.of:
            for crit in self.termen:
                if crit(p, einddatum):
                    return True
            return False
        else:
            for crit in self.termen:
                if not crit(p, einddatum):
                    return False
            return True


class PatientLogischTerm(PatientCriterium):
    """
    logisch patient criterium term (wel/niet patient criterium)

    bijv. "NIET: gebruiker snoepjes"
    """

    def __init__(self, naam=None, omschrijving=None, welniet=None, criterium=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.welniet = (welniet == 'WEL')
        self.criterium = criterium

    def __call__(self, p, einddatum):
        if self.criterium is None:
            return False
        if self.welniet:
            return self.criterium(p, einddatum)
        else:
            return not self.criterium(p, einddatum)


class PatientAfleveringen(PatientCriterium):
    """
    patient criterium dat kijkt naar (totaal aantal) afleveringen binnen de gegeven periode.

    in plaats van totaal aantal kan er ook totale stuks/ddds worden gekeken.

    er kan ook een verstrekking criterium filter worden meegegeven, dat voor alles of
    alleen de eerste/laatste verstrekking wordt gechecked.

    er kan ook alleen gekeken worden naar patienten die 'recent' een aflevering/gebruik hebben.

    """
    def __init__(self, naam, omschrijving=None, verstrekking=None, afleveringen_min=-1, afleveringen_max=-1, datum_van=-1, datum_tot=0,
                 recent=-1, stuks_min=-1.0, stuks_max=-1.0, ddd_min=-1.0, ddd_max=-1.0, recent_soort=None, vrs_crit=None, vrs_opties=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.verstrekking = verstrekking
        self.afleveringen_min = afleveringen_min
        self.afleveringen_max = afleveringen_max
        self.datum_tot = datum_tot
        self.datum_van = datum_van
        self.stuks_min = stuks_min
        self.stuks_max = stuks_max
        self.ddd_min = ddd_min
        self.ddd_max = ddd_max
        self.vrs_crit = vrs_crit
        self.vrs_opties = vrs_opties
        self.recent_soort = recent_soort
        self.recent = recent

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        if not self.verstrekking:
            return False

        self.verstrekking.bepaal(p, einddatum)
        vrsn = self.verstrekking.vrsn

        aantal = 0
        sum_ddd = 0.0
        sum_stuks = 0.0
        recent_gevonden = False

        if vrsn:
            i1 = vrs_index(vrsn, self.start)
            i2 = vrs_index(vrsn, self.eind)

            for i in range(i1, i2):
                vrs = vrsn[i]

                if self.vrs_crit and not self.vrs_crit(vrs):
                    continue

                aantal += 1
                sum_ddd += vrs.ddd
                sum_stuks += vrs.recept.hoeveelheid

                if self.recent_soort:
                    recent_van = shift_months(einddatum, -self.recent)
                    if self.recent_soort == 'aflevering':
                        if recent_van <= vrs.datum < self.eind:
                            recent_gevonden = True
                    elif self.recent_soort == 'gebruik':
                        if vrs.datum < self.eind and vrs.einddatum > recent_van:  # TODO lijkt bug, niet alleen binnen start/eind kijken?
                            recent_gevonden = True
                    else:
                        raise ValueError(f'ongeldige recent_soort: "{self.recent_soort}"')

            if i1 != i2 and self.vrs_crit:
                if self.vrs_opties == 'eerste' and not self.vrs_crit(vrsn[i1]):
                    return False
                elif self.vrs_opties == 'laatste' and not self.vrs_crit(vrsn[i2-1]):
                    return False

        if self.afleveringen_min != -1 and aantal < self.afleveringen_min:  # TODO naar helpers
            return False
        if self.afleveringen_max != -1 and aantal >= self.afleveringen_max:
            return False

        if self.stuks_min != -1.0 and sum_stuks < self.stuks_min:
            return False
        if self.stuks_max != -1.0 and sum_stuks >= self.stuks_max:
            return False

        if self.ddd_min != -1.0 and sum_ddd < self.ddd_min:
            return False
        if self.ddd_max != -1.0 and sum_ddd >= self.ddd_max:
            return False

        if self.recent_soort and not recent_gevonden:
            return False

        return True


class PatientAfleverContext(PatientCriterium):
    """
    patient criterium dat kijkt naar aantal afleveringen binnen de gegeven periode
    waarvoor de gegeven context geldt.

    de context kan zijn: wel/niet een bepaalde aflevering of gebruik vlak er voor/na.

    er kan ook een PatientEU criterium worden doorgegeven, om de context hiervan
    te bekijken (het te evalueren aantal is dan 1 of 0).

    """

    def __init__(self, naam, omschrijving=None, lijst=None, datum_van=-1, datum_tot=0, aantal_van=-1, aantal_tot=-1,
                 welniet=None, wat=None, dagen_voor=-1, dagen_na=-1, lijst_van=None, van=-1, criterium=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijst = lijst
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.aantal_van = aantal_van
        self.aantal_tot = aantal_tot
        self.welniet = (welniet == 'WEL')
        self.wat = wat
        self.van = van
        self.criterium = criterium
        self.dagen_voor = dagen_voor
        self.dagen_na = dagen_na
        self.lijst_van = lijst_van

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        if self.lijst_van is None:
            return False
        vrsn = []
        if self.criterium:
            if self.criterium(p, einddatum):
                vrsn = [self.criterium.vrs]
        else:
            if self.lijst is None:
                return False
            self.lijst.bepaal(p, einddatum)
            vrsn = self.lijst.vrsn

        i3 = vrs_index(vrsn, self.start)
        i4 = vrs_index(vrsn, self.eind)

        self.lijst_van.bepaal(p, einddatum)
        vrsn_van = self.lijst_van.vrsn

        dagen_voor = self.dagen_voor if self.dagen_voor != -1 else 1000000
        dagen_na = self.dagen_na if self.dagen_na != -1 else 1000000

        aantal = 0
        for i in range(i3, i4):
            vrs = vrsn[i]

            datum_voor = shift_days(vrs.datum, -dagen_voor)
            datum_na = shift_days(vrs.datum, dagen_na)

            i1 = vrs_index(vrsn_van, datum_voor)
            i2 = vrs_index(vrsn_van, datum_na)

            if self.wat == 'aflevering':
                gevonden = (i1 != i2)
            else:
                prdn_van = vrs_gebruik(vrsn_van, datum_voor, datum_na)
                gevonden = len(prdn_van) > 0

            if gevonden and self.welniet:
                aantal += 1
            elif not gevonden and not self.welniet:
                aantal += 1

        avan = self.aantal_van  # TODO helper
        if avan == -1:
            avan = 0
        atot = self.aantal_tot
        if atot == -1:
            atot = sys.maxsize

        return avan <= aantal < atot


class PatientGaten(PatientCriterium):
    """
    patient criterium dat kijkt naar gaten in het gebruik van de gegeven
    verstrekkingen.

    vervolgens kan er worden gefilterd op het aantal gaten (van bepaalde
    lengtes), en het (totaal of onafgebroken) aantal dagen van deze
    gaten.

    """
    def __init__(self, naam, omschrijving=None, vrs_lijst=None, datum_van=-1, datum_tot=0, totaal_onafgebroken=None, lengte_van=-1, lengte_tot=-1, gaten_van=-1, gaten_tot=-1):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrs_lijst = vrs_lijst
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.totaal_onafgebroken = totaal_onafgebroken
        self.lengte_van = lengte_van
        self.lengte_tot = lengte_tot
        self.gaten_van = gaten_van
        self.gaten_tot = gaten_tot

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        if not self.vrs_lijst:
            return False

        self.vrs_lijst.bepaal(p, einddatum)
        vrsn = self.vrs_lijst.vrsn

        gaten_van = self.gaten_van if self.gaten_van != -1 else 0
        gaten_tot = self.gaten_tot if self.gaten_tot != -1 else sys.maxsize

        lengte_van = self.lengte_van if self.lengte_van != -1 else 0
        lengte_tot = self.lengte_tot if self.lengte_tot != -1 else sys.maxsize

        prdn = vrs_gebruik(vrsn, self.start, self.eind)
        if not prdn:
            return gaten_van <= 0 < gaten_tot
        gaten = []
        for i in range(len(prdn) - 1):  # tussenstukjes
            gaten.append(Period(prdn[i].eind, prdn[i + 1].start))

        lengte_totaal = sum([get_days(gat.eind) - get_days(gat.start) for gat in gaten])
        if self.totaal_onafgebroken == "totaal":
            if not lengte_van <= lengte_totaal < lengte_tot:
                return False
        else:
            gaten = [gat for gat in gaten if lengte_van <= (get_days(gat.eind) - get_days(gat.start)) < lengte_tot]

        return gaten_van <= len(gaten) < gaten_tot


class PatientDosering(PatientCriterium):
    """
    patient criterium dat kijkt naar gemiddelde 'dosering' (ddd/eenheid/gebruiksdagen).

    het gemiddelde kan per verstrekking zijn of per dag.

    dit wordt berekend door de totale 'dosering' te delen door het aantal dagen tussen
    eerste en laatste verstrekking (of dag).

    gebruikt vrs_gemiddeld voor deze berekening.

    """
    def __init__(self, naam, omschrijving=None, lijst=None, datum_van=-1, datum_tot=0, soort_dosering=None, van=-1.0, tot=-1.0,
                 soort_berekening=None, vrs_of_dag=None, totaal_onafgebroken=None, soort_periode=None, aantalvrs=-1,
                 leeftijd_min=-1, leeftijd_max=-1, dagen_van=-1, dagen_tot=-1):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijst = lijst
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.soort_dosering = soort_dosering
        self.van = van
        self.tot = tot
        self.soort_berekening = soort_berekening
        self.vrs_of_dag = vrs_of_dag
        self.totaal_onafgebroken = totaal_onafgebroken
        self.soort_periode = soort_periode
        self.aantalvrs = aantalvrs
        self.leeftijd_min = leeftijd_min
        self.leeftijd_max = leeftijd_max
        self.dagen_van = dagen_van
        self.dagen_tot = dagen_tot

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        self.info_dosering = -1.0

        if not self.lijst:
            return False

        self.lijst.bepaal(p, einddatum)
        vrsn = self.lijst.vrsn

#        if self.geslacht.value and patient.geslacht != self.geslacht.value:
#            return False

        if self.leeftijd_min != -1 or self.leeftijd_max != -1:
            leeftijd = p.leeftijd(einddatum)
            if self.leeftijd_min != -1 and leeftijd < self.leeftijd_min:
                return False
            if self.leeftijd_max != -1 and leeftijd >= self.leeftijd_max:
                return False

        i1 = vrs_index(vrsn, self.start)
        i2 = vrs_index(vrsn, self.eind)
        vrsn = vrsn[i1:i2]

        assert self.soort_berekening == 'gemiddeld'

        # gemiddeld
        if not vrsn:
            return False

        totaal_dagen = vrs_gemiddeld(
            vrsn,
            self.soort_dosering,
            self.aantalvrs,
            self.vrs_of_dag or 'verstrekkingen',
            self.soort_periode,
            self.start,
            self.eind,
        )

        if totaal_dagen is not None:
            totaal, dagen = totaal_dagen
            dosering = totaal / float(dagen)
        else:
            return False

        self.info_dosering = dosering

        if self.van != -1.0 and dosering < self.van:
            return False
        if self.tot != -1.0 and dosering >= self.tot:
            return False

        return True


class PatientPolyfarmacie(PatientCriterium):
    """
    patient criterium dat kijkt naar het aantal groepen op een gegeven nivo,
    waarbinnen een bepaald aantal afleveringen of (totaal/onafgebroken) gebruik is.

    bijv.:

    'op atc-2 nivo minimaal 2 groepen waarbinnen tussen 5 en 10 dagen onafgebroken gebruik'

    groepen aangegeven met 'dubbelgroepen' tellen hierbij voor 2.

    """

    def __init__(self, naam, omschrijving=None, vrs_lijsten=None, datum_van=-1, datum_tot=0, vrs_van=-1, vrs_tot=-1,
                 gebr_van=-1, gebr_tot=-1, totaal_onafgebroken=None, dubbelgroepen=None,
                 min_van=-1, min_tot=0, groepen_van=-1, groepen_tot=-1, nivo=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrs_lijsten = vrs_lijsten
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.vrs_van = vrs_van
        self.vrs_tot = vrs_tot
        self.gebr_van = gebr_van
        self.gebr_tot = gebr_tot
        self.totaal_onafgebroken = totaal_onafgebroken
        self.dubbelen = set()
        if dubbelgroepen:
            self.dubbelen = set(dubbelgroepen.split())
        self.min_van = min_van
        self.min_tot = min_tot
        self.groepen_van = groepen_van
        self.groepen_tot = groepen_tot
        self.nivo = nivo

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        self.info_groepen = -1

        assert self.nivo != 'verstrekking lijst'

        vrsn = []
        if self.vrs_lijsten:
            for vrs_lijst in self.vrs_lijsten:
                vrs_lijst.bepaal(p, einddatum)
                vrsn.extend(vrs_lijst.vrsn)
        vrsn.sort(key=lambda v: v.datum)
        key_vrsn = vrs_split(vrsn, self.nivo)

        if self.min_van != -1:
            min_van = shift_months(einddatum, -self.min_van)
            min_tot = shift_months(einddatum, -self.min_tot)

            key_vrsn = {
                key: vrsn
                for key, vrsn in key_vrsn.items()
                if vrs_aantal(vrsn, min_van, min_tot)
            }

        groepen = []
        for key, vrsn in key_vrsn.items():
            if self.vrs_van != -1 or self.vrs_tot != -1:
                vrs_van = self.vrs_van if self.vrs_van != -1 else 0
                vrs_tot = self.vrs_tot if self.vrs_tot != -1 else sys.maxsize
                afleveringen = vrs_aantal(vrsn, self.start, self.eind)
                if vrs_van <= afleveringen < vrs_tot:
                    groepen.append(key)
                    continue

            if self.gebr_van != -1 or self.gebr_tot != -1:
                gebr_van = self.gebr_van if self.gebr_van != -1 else 0
                gebr_tot = self.gebr_tot if self.gebr_tot != -1 else sys.maxsize
                match = False
                prdn = vrs_gebruik(vrsn, self.start, self.eind)
                if self.totaal_onafgebroken == 'totaal':
                    totaal = 0
                    for per in prdn:
                        totaal += get_days(per.eind) - get_days(per.start)
                    if gebr_van <= totaal < gebr_tot:
                        match = True
                else:
                    for per in prdn:
                        if gebr_van <= get_days(per.eind) - get_days(per.start) < gebr_tot:
                            match = True
                            break
                if match:
                    groepen.append(key)
                    continue

        teller = sum([2 if groep in self.dubbelen else 1 for groep in groepen])
        self.info_groepen = teller

        groepenvan = self.groepen_van if self.groepen_van != -1 else 0
        groepentot = self.groepen_tot if self.groepen_tot != -1 else sys.maxsize

        return groepenvan <= teller < groepentot


class PatientTherapietrouw2(PatientCriterium):
    """
    patient criterium dat kijkt naar 'therapietrouwheid'.

    therapietrouwheid wordt bepaald als een gemiddeld percentage over groepen op het
    aangegeven nivo.


    """
    def __init__(self, naam, omschrijving, vrs_lijsten, nivo, datum_van=-1, datum_tot=0, perc_van=-1.0, perc_tot=-1.0):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrs_lijsten = vrs_lijsten
        self.nivo = nivo
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.perc_van = perc_van
        self.perc_tot = perc_tot

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        self.info_percentage = -1.0

        if self.nivo == 'verstrekking lijst':
            key_vrsn = {}
            for vrs_lijst in self.vrs_lijsten:
                vrs_lijst.bepaal(p, einddatum)
                key_vrsn[vrs_lijst.naam] = vrs_lijst.vrsn  # TODO op naam is meh
        else:
            verstrekkingen = []
            atc_wissels = []
            for vrs_lijst in self.vrs_lijsten:
                vrs_lijst.bepaal(p, einddatum)
                if vrs_lijst.correctie is not None and vrs_lijst.correctie.atc_wissel is not None:
                    atc_wissels.append(vrs_lijst.correctie.atc_wissel)  # TODO expliciet niet beter dan overnemen?
                verstrekkingen.extend(vrs_lijst.vrsn)
            verstrekkingen.sort(key=lambda v: v.datum)
            key_vrsn = vrs_split(verstrekkingen, self.nivo, ' '.join(atc_wissels))

        percentages = []
        berekening = {}

        for key, vrsn in key_vrsn.items():
            prdn = vrs_gebruik(vrsn, self.start, self.eind)
            if prdn:
                teller = sum([get_days(p.eind) - get_days(p.start) for p in prdn])
                noemer = get_days(einddatum) - get_days(prdn[0].start)  # TODO bug in orig: pakt einddatum ipv datum_tot!?
                perc = (100.0 * teller) / noemer
                percentages.append(perc)
                berekening[key] = perc

        if not percentages:
            return False

        gemiddeld_percentage = sum(percentages) / len(percentages)
        self.info_percentage = gemiddeld_percentage
        if self.perc_van != -1.0 and gemiddeld_percentage < self.perc_van:
            return False
        if self.perc_tot != -1.0 and gemiddeld_percentage >= self.perc_tot:
            return False

        return True


class PatientGebruik(PatientCriterium):
    """
    patient criterium dat kijkt naar totaal/onafgebroken gebruik en eventueel
    totaal ddd's.

    het maakt indirect gebruik van vrs_interactie, wat niet het meest
    efficient is misschien.

    """
    def __init__(self, naam, omschrijving=None, verstrekking=None, totaal_onafgebroken=None, dagen_van=-1, dagen_tot=-1, datum_van=-1, datum_tot=0, welniet=None, ddd_van=-1.0, ddd_tot=-1.0):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrs_lijst = verstrekking
        self.totaal = (totaal_onafgebroken == 'totaal')
        self.welniet = (welniet == 'WEL')
        if not self.welniet:
            raise ValueError(f'ongeldige patient gebruik wel/niet: "{welniet}"')
        self.dagen_van = dagen_van
        self.dagen_tot = dagen_tot
        self.ddd_van = ddd_van
        self.ddd_tot = ddd_tot
        self.datum_van = datum_van
        self.datum_tot = datum_tot

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        if not self.vrs_lijst:
            return False
        self.vrs_lijst.bepaal(p, einddatum)
        vrsn = self.vrs_lijst.vrsn

        prdn = vrs_gebruik(vrsn, self.start, self.eind)

        # gebruik totaal/onafgebroken
        if self.totaal:
            totaal = 0
            for per in prdn:
                totaal += get_days(per.eind) - get_days(per.start)

            if self.dagen_van != -1 and totaal < self.dagen_van:
                return False
            if self.dagen_tot != -1 and totaal >= self.dagen_tot:
                return False

        else:
            for per in prdn:
                if get_days(per.eind) - get_days(per.start) >= self.dagen_van:  # TODO dagen_tot
                    break
            else:
                return False

        # totaal ddd in periode
        if self.ddd_van != -1.0 or self.ddd_tot != -1.0:
            totaal_ddd = 0.0
            for vrs in vrsn:
                if vrs.datum < self.eind and vrs.einddatum > self.start:
                    duur = get_days(vrs.einddatum) - get_days(vrs.datum)
                    duur_in_periode = get_days(min(vrs.einddatum, self.eind)) - get_days(max(vrs.datum, self.start))
                    totaal_ddd += vrs.ddd * (duur_in_periode / duur)

            if self.ddd_van != -1.0 and totaal_ddd < self.ddd_van:  # TODO helpers helpers
                return False
            if self.ddd_tot != -1.0 and totaal_ddd >= self.ddd_tot:
                return False

        return True


class PatientInteractie2(PatientCriterium):
    """
    patient criterium dat kijkt naar overlappend gebruik.

    zie vrs_interactie voor de mogelijke parameters.

    """
    def __init__(self, naam, omschrijving=None, lijsten_verplicht=None, lijsten=None, dagen_van=-1, dagen_tot=-1, datum_van=-1, datum_tot=0,
                 nivo=None, totaal_onafgebroken=None, minimum=-1):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijsten_verplicht = lijsten_verplicht
        self.lijsten = lijsten
        self.dagen_van = dagen_van
        self.dagen_tot = dagen_tot
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.minimum = minimum

        self.vrsnn_verplicht = []
        self.vrsnn = []

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        self.info_perioden = None

        self.vrsnn_verplicht.clear()
        self.vrsnn.clear()

        if self.lijsten_verplicht:
            for vlijst in self.lijsten_verplicht:
                vlijst.bepaal(p, einddatum)
                self.vrsnn_verplicht.append(vlijst.vrsn)

        if self.lijsten:
            for vlijst in self.lijsten:
                vlijst.bepaal(p, einddatum)
                self.vrsnn.append(vlijst.vrsn)

        prdn = vrs_interactie(self.vrsnn, self.start, self.eind, self.minimum, vrsnn_verplicht=self.vrsnn_verplicht)
        self.info_perioden = prdn
        for per in prdn:
            dagen = get_days(per.eind) - get_days(per.start)
            if (
                (self.dagen_van == -1 or self.dagen_van <= dagen)
                and (self.dagen_tot == -1 or dagen < self.dagen_tot)  # TODO totaal/onafgebroken?
            ):
                return True

        return False


class PatientEU(PatientCriterium):
    """
    patient criterium dat kijkt naar eerste/vervolg uitgiften
    (resp. met minimale/maximale voorloop periode).

    complicatie is wat te doen bij verstrekkingen op dezelfde dag
    (hierbij kijken we bijv. ook naar modulaire tariefcode).

    """
    def __init__(self, naam, omschrijving=None, verstrekking=None, datum_van=-1, datum_tot=0, voorloop=-1, soort=None, modtarief=None, startmet=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrs_lijst = verstrekking
        self.soort = soort
        self.voorloop = voorloop
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.modtarief = modtarief
        self.startmet = startmet

    def setup_einddatum(self, einddatum):
        self.start = shift_months(einddatum, -self.datum_van)
        self.eind = shift_months(einddatum, -self.datum_tot)

    def __call__(self, p, einddatum):
        self.vrs = None
        if self.vrs_lijst is None:
            return False
        self.vrs_lijst.bepaal(p, einddatum)
        vrsn = self.vrs_lijst.vrsn
        if vrsn:
            i1 = vrs_index(vrsn, self.start)
            i2 = vrs_index(vrsn, self.eind)

            for i in range(i1, i2):
                vrs = vrsn[i]

                terug = shift_months(vrs.datum, -self.voorloop)

                if self.soort == 'vervolg uitgifte':
                    if (
                        i > 0
                        and vrsn[i-1].datum >= terug
                        and vrsn[i-1].datum != vrs.datum
                    ):
                        hebbes = self.check_zelfde_dag(vrsn, i, True)
                        if hebbes:
                            self.vrs = vrs
                            return True
                else:
                    if (
                        i == 0
                        or vrsn[i-1].datum < terug
                    ):
                        hebbes = self.check_zelfde_dag(vrsn, i, False)
                        if hebbes:
                            self.vrs = vrs
                            return True
        return False

    def check_zelfde_dag(self, vrsn, i, vervolg_uitgifte):
        datum = vrsn[i].datum
        while i < len(vrsn) and vrsn[i].datum == datum:
            vrs = vrsn[i]
            if not self.startmet or self.startmet(vrs):
                code = vrs.recept.modulaire_tariefcode
                if vervolg_uitgifte:
                    if (not self.modtarief or self.modtarief == 'nee' or code == 0 or code in CODES_VERVOLGUITGIFTE):

                        return vrs
                else:
                    if (not self.modtarief or self.modtarief == 'nee' or code == 0 or code not in CODES_VERVOLGUITGIFTE):
                        return vrs
            i += 1


class PatientPuntenTerm:
    """
    patient punten criterium term: hiermee hangen we een aantal
    punten aan een patient criterium.

    """
    def __init__(self, naam, omschrijving, criterium, aantal_punten):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium
        self.aantal_punten = aantal_punten

    def __call__(self, p, einddatum):
        if self.criterium is not None and self.criterium(p, einddatum):
            return self.aantal_punten
        return 0


class PatientPunten(PatientCriterium):
    """
    patient punten criterium. hiermee checken we het totaal aantal punten
    voor gegeven patient criteria, waarbij elk criterium een aantal punten
    krijgt toegewezen (indien waar voor een gegeven patient).

    """
    def __init__(self, naam, omschrijving, termen, punten_min=-1, punten_max=-1):
        self.naam = naam
        self.omschrijving = omschrijving
        self.termen = termen
        self.punten_min = punten_min
        self.punten_max = punten_max

    def __call__(self, p, einddatum):
        totaal = sum([term(p, einddatum) for term in self.termen])  # TODO termen is None check?
        pmin, pmax = self.punten_min, self.punten_max  # TODO naar helper, zie wokkel3utils aantal_van_tot
        if pmin == -1:
            pmin = 0
        if pmax == -1:
            pmax = sys.maxsize
        return pmin <= totaal < pmax


# TODO info.clear() in patcrits -> None?

class PatientInfo:
    """
    base klasse voor informatie componenten.

    met een informatie component kun je voor een patient
    specifieke informatie bepalen.

    """
    def __call__(self, p, einddatum):
        raise NotImplementedError  # pragma: nocover


class PatientInformatieInfo:
    """
    container voor meerdere informatie componenten

    """
    def __init__(self, naam, omschrijving=None, lijst=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.lijst = lijst


class PatientPatientInfo(PatientInfo):
    """
    geef J/N voor een gegeven patient criterium

    """
    def __init__(self, naam, omschrijving=None, criterium=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium

    def __call__(self, p, einddatum):
        if self.criterium:
            if self.criterium(p, einddatum):
                return 'J'
            else:
                return 'N'


class PatientPatientenInfo(PatientInfo):  # deprecated, want zelfde als PatientPatientInfo?
    """
    zelfde als PatientPatientInfo

    """
    def __init__(self, naam, omschrijving=None, criterium=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium

    def __call__(self, p, einddatum):
        if self.criterium:
            if self.criterium(p, einddatum):
                return 'J'
            else:
                return 'N'


class PatientPolyfarmacieInfo(PatientInfo):
    """
    voor het gegeven polyfarmacie criterium, neem het berekende aantal
    groepen over.

    """
    def __init__(self, naam, omschrijving=None, criterium=None, wat=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium
        self.wat = wat

    def __call__(self, p, einddatum):
        if self.criterium:
            self.criterium(p, einddatum)
            if self.wat == 'groepen':
                info_groepen = self.criterium.info_groepen
                if info_groepen > 0:
                    return str(info_groepen)
            else:
                raise ValueError(f'ongeldige polyfarmacie info: "{self.wat}"')


class PatientTherapietrouwNieuwInfo(PatientInfo):
    """
    voor het gegeven therapietrouw criterium, neem het berekende
    percentage over

    """
    def __init__(self, naam, omschrijving=None, criterium=None, wat=None, decimalen=2):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium
        self.wat = wat
        self.decimalen = decimalen

    def __call__(self, p, einddatum):
        if self.criterium:
            self.criterium(p, einddatum)
            if self.wat == 'percentage':
                percentage = self.criterium.info_percentage
                if percentage != -1.0:
                    return format_float(percentage, self.decimalen)
            else:
                raise ValueError(f'ongeldige therapietrouw info: "{self.wat}"')


class PatientVerstrekkingenInfo(PatientInfo):
    """
    voor de gegeven verstrekking lijst, bepaal het totaal aantal/stuks/ddd.

    er kan eventueel ook op een patient criterium en/of verstrekking criterium
    worden gefilterd.

    """
    def __init__(self, naam, omschrijving=None, vrs=None, criterium=None, tellen=None, datum_van=-1, datum_tot=0, vrs_enkel=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrslijst = vrs
        self.criterium = criterium
        self.tellen = tellen
        self.vrs_enkel = vrs_enkel
        self.datum_van = datum_van
        self.datum_tot = datum_tot

    def __call__(self, p, einddatum):
        if self.vrslijst is None:
            return
        if self.criterium is not None and not self.criterium(p, einddatum):
            return
        self.vrslijst.bepaal(p, einddatum)
        vrsn = self.vrslijst.vrsn
        start = shift_months(einddatum, -self.datum_van)
        eind = shift_months(einddatum, -self.datum_tot)
        i1 = vrs_index(vrsn, start)
        i2 = vrs_index(vrsn, eind)
        aantal = 0
        ddd = 0.0
        stuks = 0.0
        for i in range(i1, i2):
            vrs = vrsn[i]
            if self.vrs_enkel is None or self.vrs_enkel(vrs):
                aantal += 1
                ddd += vrs.recept.ddd
                stuks += vrs.recept.hoeveelheid
        if self.tellen == 'aantal':
            if aantal > 0:
                return str(aantal)
        elif self.tellen == 'ddd':
            if ddd > 0.0:
                return str(ddd)
        elif self.tellen == 'stuks':
            if stuks > 0.0:
                return str(stuks)
        else:
            raise ValueError(f'ongeldige verstrekkingen info: "{self.tellen}"')


class PatientPeriodenInfo(PatientInfo):
    """
    voor de gegeven verstrekking lijst, bepaal gebruiks perioden.

    de perioden kunnen op meerdere manier worden geformateerd (aantal dagen/intervallen).

    er kan evunteel ook op een patient criterium worden gefilterd.

    """
    def __init__(self, naam, omschrijving=None, pat=None, vrs=None, wat=None, hoe=None, datum_van=-1, datum_tot=0):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = pat
        self.vrslijst = vrs
        self.wat = wat
        self.hoe = hoe
        self.datum_van = datum_van
        self.datum_tot = datum_tot

    def __call__(self, p, einddatum):
        if self.vrslijst is None:
            return
        if self.criterium is not None and not self.criterium(p, einddatum):
            return

        self.vrslijst.bepaal(p, einddatum)
        vrsn = self.vrslijst.vrsn

        start = shift_months(einddatum, -self.datum_van)
        eind = shift_months(einddatum, -self.datum_tot)
        prdn = vrs_interactie([vrsn], start, eind)

        if self.wat != 'alle perioden':
            raise ValueError(f'ongeldig perioden info selectie: "{self.wat}"')

        if prdn:
            if self.hoe == 'dagen':
                return ', '.join([str(get_days(p.eind) - get_days(p.start)) for p in prdn])
            elif self.hoe == 'van - tot':
                return ', '.join([datum_fmt(p.start) + ' - ' + datum_fmt(p.eind) for p in prdn])
            else:
                raise ValueError(f'ongeldig perioden info formaat: "{self.hoe}"')


def vrs_info(vrs, wat):
    """
    voor gegeven verstrekking, bepaal gegeven eigenschap.

    """
    if wat == 'afleverdatum':
        return datum_fmt(vrs.datum)
    elif wat == 'einddatum':
        return datum_fmt(vrs.einddatum)
    elif wat == 'atc5-code':
        return vrs.atc.code
    elif wat == 'atc5-naam':
        return g_atc5_naam[vrs.atc.code]
    elif wat == 'ddd':
        return format_float(vrs.ddd)
    elif wat == "pdd":
        return format_float((vrs.ddd / (get_days(vrs.einddatum) - get_days(vrs.datum))))
    elif wat == 'voorschrijver-agb':
        return str(vrs.recept.agb)
    elif wat == "voorschrijversoort":
        return str(vrs.recept.sv)
    elif wat == "dagen":
        return str(get_days(vrs.einddatum) - get_days(vrs.datum))
    elif wat == 'gpk':
        return str(vrs.recept.artikel.gpk)
    elif wat == 'hpk':
        return str(vrs.recept.artikel.hpk)
    elif wat == 'zorgverzekeraar':
        return str(vrs.recept.zorgverzekeraar)
    elif wat == 'artikelnaam':
        return vrs.recept.artikel.naam
    else:
        raise ValueError(f'ongeldige verstrekking info: "{wat}"')


class PatientEUInfo(PatientInfo):
    """
    voor gegeven PatientEU criterium, bepaal gegeven
    verstrekking eigenschap voor eventuele eerste uitgifte.

    """
    def __init__(self, naam, omschrijving=None, criterium=None, wat=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.criterium = criterium
        self.wat = wat

    def __call__(self, p, einddatum):
        if self.criterium is None:
            return
        self.criterium(p, einddatum)
        if self.criterium.vrs is None:
            return
        return vrs_info(self.criterium.vrs, self.wat)


class PatientLUInfo(PatientInfo):
    """
    voor gegeven verstrekking lijst, bepaal gegeven
    verstrekking eigenschap voor eerste/laatste verstrekking.

    """
    def __init__(self, naam, omschrijving=None, vrs=None, datum_van=-1, welke=None, wat=None, datum_tot=0):
        self.naam = naam
        self.omschrijving = omschrijving
        self.vrslijst = vrs
        self.datum_van = datum_van
        self.datum_tot = datum_tot
        self.welke = welke
        self.wat = wat

    def __call__(self, p, einddatum):
        if self.vrslijst is None:
            return
        self.vrslijst.bepaal(p, einddatum)
        vrsn = self.vrslijst.vrsn
        start = shift_months(einddatum, -self.datum_van)
        eind = shift_months(einddatum, -self.datum_tot)
        i1 = vrs_index(vrsn, start)
        i2 = vrs_index(vrsn, eind)
        if i1 != i2:
            if self.welke == 'eerste':
                vrs = vrsn[i1]
            elif self.welke == 'laatste':
                vrs = vrsn[i2-1]
            else:
                raise ValueError(f'ongeldige lu info selectie: "{self.welke}"')
            return vrs_info(vrs, self.wat)


class PatientInteractieInfo(PatientInfo):
    """
    voor gegeven PatientInteractie2 criterium, bepaal
    maximale overlap in dagen.

    """
    def __init__(self, naam, omschrijving=None, pat=None, criterium=None, wens=None, uniek=None):
        self.naam = naam
        self.omschrijving = omschrijving
        self.pat = pat
        self.criterium = criterium
        self.wens = wens
        self.uniek = uniek

    def __call__(self, p, einddatum):
        patcrit = self.pat or self.criterium  # TODO pat/criterium weg?
        if patcrit is None or not patcrit(p, einddatum):
            return
        if self.wens != 'maximale lengte':
            raise ValueError(f'ongeldige interactie info wens: "{self.wens}"')
        if self.uniek != 'nee':
            raise ValueError(f'ongeldige interactie info uniek: "{self.uniek}"')
        prdn = patcrit.info_perioden
        return str(max([get_days(p.eind) - get_days(p.start) for p in prdn]))


class PatientDoseringInfo(PatientInfo):
    """
    voor gegeven PatientDosering criterium, neem berekende
    gemiddelde dosering over.

    """
    def __init__(self, naam, omschrijving=None, pat=None, criterium=None, wat=None, decimalen=2):  # TODO pat/criterium zelfde?
        self.naam = naam
        self.omschrijving = omschrijving
        self.wat = wat
        self.decimalen = decimalen
        self.criterium = criterium

    def __call__(self, p, einddatum):
        if self.criterium:
            self.criterium(p, einddatum)
            if self.wat == 'dosering':
                return format_float(self.criterium.info_dosering, self.decimalen)
            else:
                raise ValueError(f'ongeldige dosering informatie: "{self.wat}"')


if __name__ == '__main__':  # pragma: nocover
    # onderstaande is nodig voor shedskin's type analyse:
    # alles moet (indirect) worden aangeroepen, want anders kan de analyse niet volledig zijn.
    # abstracte ("base") types moeten ook voorkomen, anders kan het deze niet genereren.

    set_atcs(['C10'])
    set_pref_beleid({(1, 2): [(1, 2)]})
    set_atc5_naam({'': ''})
    set_codes_vervolguitgifte([1])

    a = Artikel(1, 'C10', 12, 13, 14, 15, 16, 1.0, 1, 'xx')
    r = Recept(a, 20200101, 20200101, 1, True, 1, 1, 1, 1.0, 1, 1.0, 1.0, 1.0, 1)

    v = Verstrekking(r)
    p = Patient(260100, '123', 'V', 1990, [v], 20240101)
    g = Groep({(1, '2'): p})

    mg = MiddelGroep('', '', atc_wel='', atc_niet='', farm_vorm='', niet_farm_vorm='', toedieningsweg='',
                     niet_toedieningsweg='', prk='', prk_niet='', gpk='', gpk_niet='', hpk='', hpk_niet='')

    atc = ATC('B10')
    atc.add_mgroep(mg)
    atc.clear_mgroepen()

    veig = VerstrekkingEigenschappen('', '', wmg='ja', voorschrijver='huisarts', modulairetariefcode='', middelgroep=mg, zorgverzekeraar='', inkoopkanaal_naam='', preferente_middelen='ja')
    vlterm = VerstrekkingLogischTerm('', '', 'NIET', veig)
    veig = VerstrekkingLogisch('', '', 'OF', [vlterm])

    correctie_term = CorrectieTerm('', '', opties='atc', waarden='A10B C10')
    correctie = Correctie('', '', 'nivo', atc_wissel='', correctietermen=[correctie_term])

    vcrits = []
    vcrit = VerstrekkingLijstEigenschappen('', '', mg, correctie=correctie, verstrekking=veig)
    vcrit = VerstrekkingLijstSamengesteld('', '', [vcrit], nivo='')
    vcrit.setup_einddatum(1234)
    vcrits.append(vcrit)

    ttcrit = PatientTherapietrouw2('', '', vcrits, nivo='')
    intcrit = PatientInteractie2('', '', lijsten=vcrits, lijsten_verplicht=vcrits, nivo='', totaal_onafgebroken='totaal')
    polycrit = PatientPolyfarmacie('', '', vcrits, dubbelgroepen='', nivo='', totaal_onafgebroken='totaal')
    eucrit = PatientEU('', '', vcrit, datum_van=12, voorloop=12, soort='', modtarief='ja', startmet=veig)
    doscrit = PatientDosering('', '', vcrit, soort_dosering='', soort_berekening='', vrs_of_dag='', totaal_onafgebroken='', soort_periode='')

    eig = PatientEigenschappen(naam='', omschrijving='', geslacht='M', passant='ja', fout='ja', recent='ja', zv_soort='recent')
    eig = eucrit
    eig = PatientGebruik('', '', vcrit, totaal_onafgebroken='totaal', welniet='WEL')
    eig = intcrit
    eig = PatientAfleveringen('', '', vcrit, vrs_crit=veig, recent_soort='', vrs_opties='')
    eig = PatientLogischTerm('', '', 'WEL', eig)
    eig = PatientLogisch('', '', 'OF', [eig])
    eig = ttcrit
    eig = PatientGaten('', '', vrs_lijst=vcrit, totaal_onafgebroken='totaal')
    eig = PatientPunten('', '', [PatientPuntenTerm('', '', eig, 2)], 6, 8)
    eig = PatientAfleverContext('', '', vcrit, welniet='WEL', wat='aflevering', lijst_van=vcrit, criterium=eucrit)
    eig = doscrit
    eig = polycrit
    eig.setup_einddatum(4321)

    patinfo = PatientPatientInfo('', '', criterium=eig)
    patinfo = PatientPatientenInfo('', '', criterium=eig)
    patinfo = PatientPolyfarmacieInfo('', '', criterium=polycrit, wat='')
    patinfo = PatientTherapietrouwNieuwInfo('', '', criterium=ttcrit, wat='')
    patinfo = PatientVerstrekkingenInfo('', '', criterium=eig, vrs=vcrit, tellen='', vrs_enkel=veig)
    patinfo = PatientPeriodenInfo('', '', pat=eig, vrs=vcrit, wat='', hoe='')
    patinfo = PatientEUInfo('', '', criterium=eucrit, wat='')
    patinfo = PatientLUInfo('', '', vrs=vcrit, welke='', wat='')
    patinfo = PatientInteractieInfo('', '', criterium=intcrit, pat=eig, wens='', uniek='')
    patinfo = PatientDoseringInfo('', '', criterium=doscrit, pat=eig, wat='')
    info = PatientInformatieInfo('', '', [patinfo])

    ind = Indicator('', '', eig, eig, tonen='')
    inds = Indicatoren('', '', lijst=[ind])
    ovz = IndicatorLijst('', '', indicatoren=inds, patient_keuze=eig, uitsluiten=eig, verhaal='', info=info)
    ovz = PatientOverzicht('', '', eig, eig, info=info, verhaal='')
    ovz.setup([mg], vcrits, [eig])
    ovz.lengte()

    ovz(g, 20240101)
