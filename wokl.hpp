#ifndef __WOKL_HPP
#define __WOKL_HPP

using namespace __shedskin__;
namespace __wokl__ {

extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_54, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_73, *const_74, *const_75, *const_76, *const_77, *const_78, *const_79, *const_8, *const_80, *const_81, *const_82, *const_83, *const_84, *const_9;

class Groep;
class ATC;
class Artikel;
class Recept;
class Verstrekking;
class Patient;
class Middel;
class MiddelGroep;
class Marker;
class Period;
class Rapportage;
class Indicator;
class Indicatoren;
class IndicatorLijst;
class PatientOverzicht;
class CorrectieTerm;
class Correctie;
class VerstrekkingCriterium;
class VerstrekkingEigenschappen;
class VerstrekkingLogischTerm;
class VerstrekkingLogisch;
class VerstrekkingLijstCriterium;
class VerstrekkingLijstEigenschappen;
class VerstrekkingLijstSamengesteld;
class PatientCriterium;
class PatientEigenschappen;
class PatientLogisch;
class PatientLogischTerm;
class PatientAfleveringen;
class PatientAfleverContext;
class PatientGaten;
class PatientDosering;
class PatientPolyfarmacie;
class PatientTherapietrouw2;
class PatientGebruik;
class PatientInteractie2;
class PatientEU;
class PatientPuntenTerm;
class PatientPunten;
class PatientInformatieInfo;
class PatientInfo;
class PatientPatientInfo;
class PatientPatientenInfo;
class PatientPolyfarmacieInfo;
class PatientTherapietrouwNieuwInfo;
class PatientVerstrekkingenInfo;
class PatientPeriodenInfo;
class PatientEUInfo;
class PatientLUInfo;
class PatientInteractieInfo;
class PatientDoseringInfo;

typedef set<ATC *> *(*lambda0)();
typedef __ss_int (*lambda1)(Marker *);
typedef __ss_int (*lambda2)(Verstrekking *);
typedef void *(*lambda3)(void *, void *, void *, void *, void *);
typedef void *(*lambda4)(void *, void *, void *, void *, void *);
typedef void *(*lambda5)(void *, void *, void *, void *, void *);
typedef __ss_int (*lambda6)(Verstrekking *);
typedef void *(*lambda7)(void *, void *, void *, void *, void *);
typedef __ss_int (*lambda8)(Verstrekking *);
typedef __ss_int (*lambda9)(Verstrekking *);
typedef void *(*lambda10)(void *, void *, void *, void *, void *);
typedef void *(*lambda11)(void *, void *, void *, void *, void *);
typedef void *(*lambda12)(void *, void *, void *, void *, void *);
typedef void *(*lambda13)(void *, void *, void *, void *, void *);
typedef void *(*lambda14)(void *, void *, void *, void *, void *);
typedef void *(*lambda15)(void *, void *, void *, void *, void *);
typedef void *(*lambda16)(void *, void *, void *, void *, void *);
typedef void *(*lambda17)(void *, void *, void *, void *, void *);
typedef void *(*lambda18)(void *, void *, void *, void *, void *);
typedef void *(*lambda19)(void *, void *, void *, void *, void *);
typedef void *(*lambda20)(void *, void *, void *, void *, void *);
typedef void *(*lambda21)(void *, void *, void *, void *, void *);
typedef void *(*lambda22)(void *, void *, void *, void *, void *);
typedef void *(*lambda23)(void *, void *, void *, void *, void *);
typedef void *(*lambda24)(void *, void *, void *, void *, void *);
typedef void *(*lambda25)(void *, void *, void *, void *, void *);
typedef void *(*lambda26)(void *, void *, void *, void *, void *);
typedef void *(*lambda27)(void *, void *, void *, void *, void *);
typedef void *(*lambda28)(void *, void *, void *, void *, void *);
typedef void *(*lambda29)(void *, void *, void *, void *, void *);
typedef void *(*lambda30)(void *, void *, void *, void *, void *);
typedef void *(*lambda31)(void *, void *, void *, void *, void *);
typedef void *(*lambda32)(void *, void *, void *, void *, void *);
typedef void *(*lambda33)(void *, void *, void *, void *, void *);
typedef void *(*lambda34)(void *, void *, void *, void *, void *);
typedef void *(*lambda35)(void *, void *, void *, void *, void *);
typedef void *(*lambda36)(void *, void *, void *, void *, void *);
typedef void *(*lambda37)(void *, void *, void *, void *, void *);
typedef void *(*lambda38)(void *, void *, void *, void *, void *);

extern str *__name__;
extern list<__ss_int> *CODES_VERVOLGUITGIFTE, *DAYS_YMD, *MONTH_DAYS;
extern list<void *> *NO_PERIODS;
extern Artikel *a;
extern Recept *r;
extern Verstrekking *v;
extern Patient *p;
extern Groep *g;
extern Middel *m;
extern MiddelGroep *mg;
extern ATC *atc;
extern VerstrekkingCriterium *veig;
extern VerstrekkingLogischTerm *vlterm;
extern CorrectieTerm *correctie_term;
extern Correctie *correctie;
extern list<VerstrekkingLijstCriterium *> *vcrits;
extern VerstrekkingLijstCriterium *vcrit;
extern PatientTherapietrouw2 *ttcrit;
extern PatientInteractie2 *intcrit;
extern PatientPolyfarmacie *polycrit;
extern PatientEU *eucrit;
extern PatientDosering *doscrit;
extern PatientCriterium *eig;
extern PatientInfo *patinfo;
extern PatientInformatieInfo *info;
extern Indicator *ind;
extern Indicatoren *inds;
extern Rapportage *ovz;
extern tuple<list<__ss_int> *> *__13;
extern dict<str *, ATC *> *g_atcs;
extern __collections__::defaultdict<str *, set<ATC *> *> *g_code_atcs;
extern dict<tuple<__ss_int> *, list<tuple<__ss_int> *> *> *g_pref_beleid;
extern dict<str *, str *> *g_atc5_naam;


extern class_ *cl_Groep;
class Groep : public pyobj {
public:
    dict<tuple2<__ss_int, str *> *, Patient *> *data;

    Groep() {}
    Groep(dict<tuple2<__ss_int, str *> *, Patient *> *dikkie) {
        this->__class__ = cl_Groep;
        __init__(dikkie);
    }
    void *__init__(dict<tuple2<__ss_int, str *> *, Patient *> *dikkie);
};

extern class_ *cl_ATC;
class ATC : public pyobj {
public:
    str *code;
    list<MiddelGroep *> *mgroepen;
    str *atc3;
    str *atc1;
    str *atc4;
    str *atc2;

    ATC() {}
    ATC(str *code) {
        this->__class__ = cl_ATC;
        __init__(code);
    }
    void *__init__(str *code);
    void *add_mgroep(MiddelGroep *mgroep);
    void *clear_mgroepen();
};

extern class_ *cl_Artikel;
class Artikel : public pyobj {
public:
    __ss_float ddd;
    __ss_int toedieningsweg_code;
    __ss_int inkoopkanaal;
    __ss_int nr;
    __ss_int prk;
    str *naam;
    __ss_int gpk;
    __ss_int hpk;
    __ss_int farmaceutische_vorm_code;
    ATC *_atc;

    Artikel() {}
    Artikel(__ss_int nr, str *atc, __ss_int farmaceutische_vorm_code, __ss_int toedieningsweg_code, __ss_int prk, __ss_int gpk, __ss_int hpk, __ss_float ddd, __ss_int inkoopkanaal, str *naam) {
        this->__class__ = cl_Artikel;
        __init__(nr, atc, farmaceutische_vorm_code, toedieningsweg_code, prk, gpk, hpk, ddd, inkoopkanaal, naam);
    }
    void *__init__(__ss_int nr, str *atc, __ss_int farmaceutische_vorm_code, __ss_int toedieningsweg_code, __ss_int prk, __ss_int gpk, __ss_int hpk, __ss_float ddd, __ss_int inkoopkanaal, str *naam);
};

extern class_ *cl_Recept;
class Recept : public pyobj {
public:
    __ss_int datum;
    __ss_float hoeveelheidperdag;
    __ss_int statuswtg;
    __ss_int einddatum;
    __ss_int aantaldagen;
    __ss_float hoeveelheid;
    __ss_bool standaard_periode;
    __ss_float pufjes;
    __ss_int sv;
    __ss_int modulaire_tariefcode;
    Artikel *artikel;
    __ss_int agb;
    __ss_float ddd;
    __ss_int zorgverzekeraar;

    Recept() {}
    Recept(Artikel *artikel, __ss_int datum, __ss_int einddatum, __ss_int aantaldagen, __ss_bool standaard_periode, __ss_int modulaire_tariefcode, __ss_int zorgverzekeraar, __ss_int statuswtg, __ss_float hoeveelheid, __ss_int sv, __ss_float ddd, __ss_float hoeveelheidperdag, __ss_float pufjes, __ss_int agb) {
        this->__class__ = cl_Recept;
        __init__(artikel, datum, einddatum, aantaldagen, standaard_periode, modulaire_tariefcode, zorgverzekeraar, statuswtg, hoeveelheid, sv, ddd, hoeveelheidperdag, pufjes, agb);
    }
    void *__init__(Artikel *artikel, __ss_int datum, __ss_int einddatum, __ss_int aantaldagen, __ss_bool standaard_periode, __ss_int modulaire_tariefcode, __ss_int zorgverzekeraar, __ss_int statuswtg, __ss_float hoeveelheid, __ss_int sv, __ss_float ddd, __ss_float hoeveelheidperdag, __ss_float pufjes, __ss_int agb);
};

extern class_ *cl_Verstrekking;
class Verstrekking : public pyobj {
public:
    Recept *recept;
    __ss_int einddatum;
    __ss_float ddd;
    __ss_int datum;
    ATC *_atc;

    Verstrekking() {}
    Verstrekking(Recept *recept) {
        this->__class__ = cl_Verstrekking;
        __init__(recept);
    }
    void *__init__(Recept *recept);
};

extern class_ *cl_Patient;
class Patient : public pyobj {
public:
    __ss_int geboortejaar;
    list<Verstrekking *> *vrsn;
    __ss_int nawnr;
    __ss_bool indexed;
    list<__ss_int> *month_idx;
    str *patientnr;
    str *geslacht;
    dict<__ss_int, __ss_int> *_passant_cache;
    dict<__ss_int, __ss_int> *_fout_cache;

    Patient() {}
    Patient(__ss_int nawnr, str *patientnr, str *geslacht, __ss_int geboortejaar, list<Verstrekking *> *vrsn, __ss_int einddatum) {
        this->__class__ = cl_Patient;
        __init__(nawnr, patientnr, geslacht, geboortejaar, vrsn, einddatum);
    }
    void *__init__(__ss_int nawnr, str *patientnr, str *geslacht, __ss_int geboortejaar, list<Verstrekking *> *vrsn, __ss_int einddatum);
    __ss_bool is_passant(__ss_int einddatum);
    __ss_bool is_fout(__ss_int einddatum);
    __ss_bool is_recent(__ss_int einddatum);
    __ss_int leeftijd(__ss_int einddatum);
};

extern class_ *cl_Middel;
class Middel : public pyobj {
public:
    list<str *> *atc_niet;
    list<__ss_int> *farm_vorm;
    list<__ss_int> *toedieningsweg;
    list<__ss_int> *hpk;
    list<__ss_int> *gpk;
    list<__ss_int> *niet_hpk;
    list<__ss_int> *niet_gpk;
    list<__ss_int> *prk;
    str *naam;
    str *omschrijving;
    list<str *> *atc_wel;
    list<__ss_int> *niet_farm_vorm;
    list<__ss_int> *niet_toedieningsweg;
    list<__ss_int> *niet_prk;

    Middel() {}
    Middel(str *naam, str *omschrijving, str *atc_wel, str *atc_niet, str *farm_vorm, str *niet_farm_vorm, str *toedieningsweg, str *niet_toedieningsweg, str *prk, str *prk_niet, str *gpk, str *gpk_niet, str *hpk, str *hpk_niet) {
        this->__class__ = cl_Middel;
        __init__(naam, omschrijving, atc_wel, atc_niet, farm_vorm, niet_farm_vorm, toedieningsweg, niet_toedieningsweg, prk, prk_niet, gpk, gpk_niet, hpk, hpk_niet);
    }
    void *__init__(str *naam, str *omschrijving, str *atc_wel, str *atc_niet, str *farm_vorm, str *niet_farm_vorm, str *toedieningsweg, str *niet_toedieningsweg, str *prk, str *prk_niet, str *gpk, str *gpk_niet, str *hpk, str *hpk_niet);
};

extern class_ *cl_MiddelGroep;
class MiddelGroep : public pyobj {
public:
    str *omschrijving;
    __ss_bool fast_contains;
    list<Middel *> *middelen;
    str *naam;
    list<Verstrekking *> *vrsn;
    list<__ss_int> *hpk;
    list<str *> *atc_wel;
    list<__ss_int> *farm_vorm;
    list<__ss_int> *niet_prk;
    list<__ss_int> *gpk;
    list<__ss_int> *niet_farm_vorm;
    list<__ss_int> *niet_gpk;
    list<__ss_int> *niet_hpk;
    list<__ss_int> *toedieningsweg;
    list<__ss_int> *prk;
    list<__ss_int> *niet_toedieningsweg;
    list<str *> *atc_niet;

    MiddelGroep() {}
    MiddelGroep(str *naam, str *omschrijving, list<Middel *> *middelen) {
        this->__class__ = cl_MiddelGroep;
        __init__(naam, omschrijving, middelen);
    }
    void *__init__(str *naam, str *omschrijving, list<Middel *> *middelen);
    __ss_bool __contains__(Verstrekking *vrs);
};

extern class_ *cl_Marker;
class Marker : public pyobj {
public:
    __ss_int add_verplicht;
    __ss_int datum;
    __ss_int add;
    __ss_int i;

    Marker() {}
    Marker(__ss_int i, __ss_int datum, __ss_int add, __ss_int add_verplicht) {
        this->__class__ = cl_Marker;
        __init__(i, datum, add, add_verplicht);
    }
    void *__init__(__ss_int i, __ss_int datum, __ss_int add, __ss_int add_verplicht);
};

extern class_ *cl_Period;
class Period : public pyobj {
public:
    __ss_int start;
    __ss_int eind;

    Period() {}
    Period(__ss_int start, __ss_int eind) {
        this->__class__ = cl_Period;
        __init__(start, eind);
    }
    void *__init__(__ss_int start, __ss_int eind);
};

extern class_ *cl_Rapportage;
class Rapportage : public pyobj {
public:
    list<MiddelGroep *> *mgroepen;
    list<VerstrekkingLijstCriterium *> *vrslijsten;
    __ss_int maanden;

    Rapportage() { this->__class__ = cl_Rapportage; }
    virtual list<dict<str *, str *> *> *__call__(Groep *groep, __ss_int  einddatum) { return 0; };
    void *setup(list<MiddelGroep *> *mgroepen, list<VerstrekkingLijstCriterium *> *vrslijsten);
    void *maak_index();
    void *indexeer(Patient *p, __ss_int i1, __ss_int i2);
};

extern class_ *cl_Indicator;
class Indicator : public pyobj {
public:
    str *naam;
    PatientCriterium *noemer;
    str *omschrijving;
    PatientCriterium *teller;

    Indicator() {}
    Indicator(str *naam, str *omschrijving, PatientCriterium *teller_criterium, PatientCriterium *noemer_criterium, str *tonen) {
        this->__class__ = cl_Indicator;
        __init__(naam, omschrijving, teller_criterium, noemer_criterium, tonen);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *teller_criterium, PatientCriterium *noemer_criterium, str *tonen);
};

extern class_ *cl_Indicatoren;
class Indicatoren : public pyobj {
public:
    str *omschrijving;
    str *naam;
    list<Indicator *> *lijst;

    Indicatoren() {}
    Indicatoren(str *naam, str *omschrijving, list<Indicator *> *lijst) {
        this->__class__ = cl_Indicatoren;
        __init__(naam, omschrijving, lijst);
    }
    void *__init__(str *naam, str *omschrijving, list<Indicator *> *lijst);
};

extern class_ *cl_IndicatorLijst;
class IndicatorLijst : public Rapportage {
public:
    PatientCriterium *patient_keuze;
    Indicatoren *indicatoren;
    PatientCriterium *uitsluiten;
    str *omschrijving;
    str *naam;

    IndicatorLijst() {}
    IndicatorLijst(str *naam, str *omschrijving, Indicatoren *indicatoren, PatientCriterium *patient_keuze, PatientCriterium *uitsluiten, str *verhaal, PatientInformatieInfo *info) {
        this->__class__ = cl_IndicatorLijst;
        __init__(naam, omschrijving, indicatoren, patient_keuze, uitsluiten, verhaal, info);
    }
    void *__init__(str *naam, str *omschrijving, Indicatoren *indicatoren, PatientCriterium *patient_keuze, PatientCriterium *uitsluiten, str *verhaal, PatientInformatieInfo *info);
    list<dict<str *, str *> *> *__call__(Groep *groep, __ss_int einddatum);
};

extern class_ *cl_PatientOverzicht;
class PatientOverzicht : public Rapportage {
public:
    PatientCriterium *exclusie;
    PatientCriterium *selectie;
    PatientInformatieInfo *_info;
    str *omschrijving;
    str *naam;

    PatientOverzicht() {}
    PatientOverzicht(str *naam, str *omschrijving, PatientCriterium *selectie, PatientCriterium *exclusie, PatientInformatieInfo *info) {
        this->__class__ = cl_PatientOverzicht;
        __init__(naam, omschrijving, selectie, exclusie, info);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *selectie, PatientCriterium *exclusie, PatientInformatieInfo *info);
    list<dict<str *, str *> *> *__call__(Groep *groep, __ss_int einddatum);
};

extern class_ *cl_CorrectieTerm;
class CorrectieTerm : public pyobj {
public:
    __ss_float ddd_factor;
    list<str *> *waarden;
    __ss_int vaste_periode;
    str *opties;
    str *omschrijving;
    str *naam;

    CorrectieTerm() {}
    CorrectieTerm(str *naam, str *omschrijving, str *opties, str *waarden, __ss_int vaste_periode, __ss_float ddd_factor) {
        this->__class__ = cl_CorrectieTerm;
        __init__(naam, omschrijving, opties, waarden, vaste_periode, ddd_factor);
    }
    void *__init__(str *naam, str *omschrijving, str *opties, str *waarden, __ss_int vaste_periode, __ss_float ddd_factor);
};

extern class_ *cl_Correctie;
class Correctie : public pyobj {
public:
    __ss_int vaste_verlenging;
    str *nivo;
    __ss_float gmddd_van;
    __ss_int standaard_periode;
    __ss_float gmddd_tot;
    __ss_float ddd_factor;
    str *naam;
    str *atc_wissel;
    __ss_int vaste_periode;
    str *omschrijving;
    list<CorrectieTerm *> *correctietermen;

    Correctie() {}
    Correctie(str *naam, str *omschrijving, str *nivo, __ss_int standaard_periode, __ss_float ddd_factor, __ss_int vaste_periode, __ss_int vaste_verlenging, __ss_float gmddd_van, __ss_float gmddd_tot, str *atc_wissel, list<CorrectieTerm *> *correctietermen) {
        this->__class__ = cl_Correctie;
        __init__(naam, omschrijving, nivo, standaard_periode, ddd_factor, vaste_periode, vaste_verlenging, gmddd_van, gmddd_tot, atc_wissel, correctietermen);
    }
    void *__init__(str *naam, str *omschrijving, str *nivo, __ss_int standaard_periode, __ss_float ddd_factor, __ss_int vaste_periode, __ss_int vaste_verlenging, __ss_float gmddd_van, __ss_float gmddd_tot, str *atc_wissel, list<CorrectieTerm *> *correctietermen);
};

extern class_ *cl_VerstrekkingCriterium;
class VerstrekkingCriterium : public pyobj {
public:
    VerstrekkingCriterium() { this->__class__ = cl_VerstrekkingCriterium; }
    virtual __ss_bool  __call__(Verstrekking *vrs) { return False; };
};

extern class_ *cl_VerstrekkingEigenschappen;
class VerstrekkingEigenschappen : public VerstrekkingCriterium {
public:
    str *preferente_middelen;
    __ss_float ddd_per_dag_tot;
    __ss_float ddd_per_dag_van;
    __ss_float ddd_tot;
    MiddelGroep *middelgroep;
    __ss_int dagen_van;
    str *naam;
    __ss_float ddd_van;
    list<__ss_int> *modulaire_tariefcode;
    str *omschrijving;
    __ss_int dagen_tot;
    str *wmg;
    str *voorschrijver;
    str *inkoopkanaal_naam;
    list<__ss_int> *zorgverzekeraar;

    VerstrekkingEigenschappen() {}
    VerstrekkingEigenschappen(str *naam, str *omschrijving, str *wmg, str *voorschrijver, str *modulairetariefcode, MiddelGroep *middelgroep, __ss_float ddd_van, __ss_float ddd_tot, __ss_float ddd_per_dag_van, __ss_float ddd_per_dag_tot, __ss_int dagen_van, __ss_int dagen_tot, str *zorgverzekeraar, str *inkoopkanaal_naam, str *preferente_middelen) {
        this->__class__ = cl_VerstrekkingEigenschappen;
        __init__(naam, omschrijving, wmg, voorschrijver, modulairetariefcode, middelgroep, ddd_van, ddd_tot, ddd_per_dag_van, ddd_per_dag_tot, dagen_van, dagen_tot, zorgverzekeraar, inkoopkanaal_naam, preferente_middelen);
    }
    void *__init__(str *naam, str *omschrijving, str *wmg, str *voorschrijver, str *modulairetariefcode, MiddelGroep *middelgroep, __ss_float ddd_van, __ss_float ddd_tot, __ss_float ddd_per_dag_van, __ss_float ddd_per_dag_tot, __ss_int dagen_van, __ss_int dagen_tot, str *zorgverzekeraar, str *inkoopkanaal_naam, str *preferente_middelen);
    __ss_bool __call__(Verstrekking *vrs);
};

extern class_ *cl_VerstrekkingLogischTerm;
class VerstrekkingLogischTerm : public VerstrekkingCriterium {
public:
    VerstrekkingCriterium *criterium;
    __ss_bool welniet;
    str *omschrijving;
    str *naam;

    VerstrekkingLogischTerm() {}
    VerstrekkingLogischTerm(str *naam, str *omschrijving, str *welniet, VerstrekkingCriterium *criterium) {
        this->__class__ = cl_VerstrekkingLogischTerm;
        __init__(naam, omschrijving, welniet, criterium);
    }
    void *__init__(str *naam, str *omschrijving, str *welniet, VerstrekkingCriterium *criterium);
    __ss_bool __call__(Verstrekking *vrs);
};

extern class_ *cl_VerstrekkingLogisch;
class VerstrekkingLogisch : public VerstrekkingCriterium {
public:
    list<VerstrekkingLogischTerm *> *termen;
    __ss_bool of;
    str *omschrijving;
    str *naam;

    VerstrekkingLogisch() {}
    VerstrekkingLogisch(str *naam, str *omschrijving, str *enof, list<VerstrekkingLogischTerm *> *termen) {
        this->__class__ = cl_VerstrekkingLogisch;
        __init__(naam, omschrijving, enof, termen);
    }
    void *__init__(str *naam, str *omschrijving, str *enof, list<VerstrekkingLogischTerm *> *termen);
    __ss_bool __call__(Verstrekking *vrs);
};

extern class_ *cl_VerstrekkingLijstCriterium;
class VerstrekkingLijstCriterium : public pyobj {
public:
    Rapportage *rapportage;
    __ss_int datum_van;
    list<Verstrekking *> *vrsn;
    str *naam;
    Correctie *_correctie;

    VerstrekkingLijstCriterium() { this->__class__ = cl_VerstrekkingLijstCriterium; }
    virtual void *bepaal(Patient *p, __ss_int  einddatum) { return 0; };
    virtual void *setup_einddatum(__ss_int  einddatum);
};

extern class_ *cl_VerstrekkingLijstEigenschappen;
class VerstrekkingLijstEigenschappen : public VerstrekkingLijstCriterium {
public:
    __ss_int datum_tot;
    __ss_bool slow_check;
    str *omschrijving;
    VerstrekkingCriterium *verstrekking;
    MiddelGroep *middelgroep;
    list<Verstrekking *> *vrsn_temp;
    __ss_int start;
    __ss_int eind;

    VerstrekkingLijstEigenschappen() {}
    VerstrekkingLijstEigenschappen(str *naam, str *omschrijving, MiddelGroep *middelgroep, Correctie *correctie, __ss_int datum_tot, __ss_int datum_van, VerstrekkingCriterium *verstrekking) {
        this->__class__ = cl_VerstrekkingLijstEigenschappen;
        __init__(naam, omschrijving, middelgroep, correctie, datum_tot, datum_van, verstrekking);
    }
    void *__init__(str *naam, str *omschrijving, MiddelGroep *middelgroep, Correctie *correctie, __ss_int datum_tot, __ss_int datum_van, VerstrekkingCriterium *verstrekking);
    void *setup_einddatum(__ss_int einddatum);
    Verstrekking *corrigeer(Verstrekking *vrs);
    void *bepaal(Patient *p, __ss_int einddatum);
};

extern class_ *cl_VerstrekkingLijstSamengesteld;
class VerstrekkingLijstSamengesteld : public VerstrekkingLijstCriterium {
public:
    str *omschrijving;
    str *nivo;
    list<VerstrekkingLijstCriterium *> *lijsten;
    list<Verstrekking *> *vrsn_temp;

    VerstrekkingLijstSamengesteld() {}
    VerstrekkingLijstSamengesteld(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten, str *nivo) {
        this->__class__ = cl_VerstrekkingLijstSamengesteld;
        __init__(naam, omschrijving, lijsten, nivo);
    }
    void *__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten, str *nivo);
    void *bepaal(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientCriterium;
class PatientCriterium : public pyobj {
public:
    Verstrekking *vrs;

    PatientCriterium() { this->__class__ = cl_PatientCriterium; }
    virtual __ss_bool  __call__(Patient *p, __ss_int  einddatum) { return False; };
    virtual void *setup_einddatum(__ss_int  einddatum);
};

extern class_ *cl_PatientEigenschappen;
class PatientEigenschappen : public PatientCriterium {
public:
    __ss_bool fout_nee;
    str *fout;
    str *naam;
    __ss_int leeftijd_min;
    __ss_bool geslacht_check;
    str *omschrijving;
    __ss_bool passant_nee;
    __ss_bool or_check;
    __ss_int leeftijd_max;
    __ss_bool recent_ja;
    __ss_bool recent_nee;
    __ss_bool leeftijd_check;
    str *passant;
    __ss_bool passant_ja;
    str *geslacht;
    str *recent;
    __ss_bool fout_ja;

    PatientEigenschappen() {}
    PatientEigenschappen(str *naam, str *omschrijving, str *passant, str *fout, __ss_int leeftijd_min, __ss_int leeftijd_max, str *zv_soort, str *geslacht, str *recent) {
        this->__class__ = cl_PatientEigenschappen;
        __init__(naam, omschrijving, passant, fout, leeftijd_min, leeftijd_max, zv_soort, geslacht, recent);
    }
    void *__init__(str *naam, str *omschrijving, str *passant, str *fout, __ss_int leeftijd_min, __ss_int leeftijd_max, str *zv_soort, str *geslacht, str *recent);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientLogisch;
class PatientLogisch : public PatientCriterium {
public:
    str *omschrijving;
    str *naam;
    list<PatientCriterium *> *termen;
    __ss_bool of;

    PatientLogisch() {}
    PatientLogisch(str *naam, str *omschrijving, str *enof, list<PatientCriterium *> *termen) {
        this->__class__ = cl_PatientLogisch;
        __init__(naam, omschrijving, enof, termen);
    }
    void *__init__(str *naam, str *omschrijving, str *enof, list<PatientCriterium *> *termen);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientLogischTerm;
class PatientLogischTerm : public PatientCriterium {
public:
    str *omschrijving;
    PatientCriterium *criterium;
    __ss_bool welniet;
    str *naam;

    PatientLogischTerm() {}
    PatientLogischTerm(str *naam, str *omschrijving, str *welniet, PatientCriterium *criterium) {
        this->__class__ = cl_PatientLogischTerm;
        __init__(naam, omschrijving, welniet, criterium);
    }
    void *__init__(str *naam, str *omschrijving, str *welniet, PatientCriterium *criterium);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientAfleveringen;
class PatientAfleveringen : public PatientCriterium {
public:
    __ss_int afleveringen_max;
    str *recent_soort;
    __ss_int afleveringen_min;
    str *vrs_opties;
    __ss_int datum_tot;
    __ss_int recent;
    __ss_int datum_van;
    __ss_float stuks_min;
    __ss_float stuks_max;
    str *naam;
    __ss_float ddd_min;
    str *omschrijving;
    __ss_float ddd_max;
    VerstrekkingLijstCriterium *verstrekking;
    VerstrekkingCriterium *vrs_crit;
    __ss_int eind;
    __ss_int start;

    PatientAfleveringen() {}
    PatientAfleveringen(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int afleveringen_min, __ss_int afleveringen_max, __ss_int datum_van, __ss_int datum_tot, __ss_int recent, __ss_float stuks_min, __ss_float stuks_max, __ss_float ddd_min, __ss_float ddd_max, str *recent_soort, VerstrekkingCriterium *vrs_crit, str *vrs_opties) {
        this->__class__ = cl_PatientAfleveringen;
        __init__(naam, omschrijving, verstrekking, afleveringen_min, afleveringen_max, datum_van, datum_tot, recent, stuks_min, stuks_max, ddd_min, ddd_max, recent_soort, vrs_crit, vrs_opties);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int afleveringen_min, __ss_int afleveringen_max, __ss_int datum_van, __ss_int datum_tot, __ss_int recent, __ss_float stuks_min, __ss_float stuks_max, __ss_float ddd_min, __ss_float ddd_max, str *recent_soort, VerstrekkingCriterium *vrs_crit, str *vrs_opties);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientAfleverContext;
class PatientAfleverContext : public PatientCriterium {
public:
    __ss_int datum_van;
    __ss_int datum_tot;
    __ss_int dagen_na;
    PatientCriterium *criterium;
    str *wat;
    __ss_int aantal_tot;
    __ss_int van;
    VerstrekkingLijstCriterium *lijst;
    __ss_int aantal_van;
    VerstrekkingLijstCriterium *lijst_van;
    str *naam;
    str *omschrijving;
    __ss_int dagen_voor;
    __ss_bool welniet;
    __ss_int start;
    __ss_int eind;

    PatientAfleverContext() {}
    PatientAfleverContext(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, __ss_int aantal_van, __ss_int aantal_tot, str *welniet, str *wat, __ss_int dagen_voor, __ss_int dagen_na, VerstrekkingLijstCriterium *lijst_van, __ss_int van, PatientCriterium *criterium) {
        this->__class__ = cl_PatientAfleverContext;
        __init__(naam, omschrijving, lijst, datum_van, datum_tot, aantal_van, aantal_tot, welniet, wat, dagen_voor, dagen_na, lijst_van, van, criterium);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, __ss_int aantal_van, __ss_int aantal_tot, str *welniet, str *wat, __ss_int dagen_voor, __ss_int dagen_na, VerstrekkingLijstCriterium *lijst_van, __ss_int van, PatientCriterium *criterium);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientGaten;
class PatientGaten : public PatientCriterium {
public:
    str *omschrijving;
    __ss_int gaten_van;
    __ss_int datum_tot;
    __ss_int lengte_van;
    VerstrekkingLijstCriterium *vrs_lijst;
    str *naam;
    __ss_int gaten_tot;
    __ss_int lengte_tot;
    __ss_int datum_van;
    str *totaal_onafgebroken;
    __ss_int eind;
    __ss_int start;

    PatientGaten() {}
    PatientGaten(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs_lijst, __ss_int datum_van, __ss_int datum_tot, str *totaal_onafgebroken, __ss_int lengte_van, __ss_int lengte_tot, __ss_int gaten_van, __ss_int gaten_tot) {
        this->__class__ = cl_PatientGaten;
        __init__(naam, omschrijving, vrs_lijst, datum_van, datum_tot, totaal_onafgebroken, lengte_van, lengte_tot, gaten_van, gaten_tot);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs_lijst, __ss_int datum_van, __ss_int datum_tot, str *totaal_onafgebroken, __ss_int lengte_van, __ss_int lengte_tot, __ss_int gaten_van, __ss_int gaten_tot);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientDosering;
class PatientDosering : public PatientCriterium {
public:
    __ss_int leeftijd_max;
    __ss_float van;
    VerstrekkingLijstCriterium *lijst;
    __ss_int dagen_van;
    __ss_int dagen_tot;
    void *soort_periode;
    __ss_int datum_tot;
    __ss_float tot;
    str *soort_dosering;
    __ss_int datum_van;
    __ss_int aantalvrs;
    str *soort_berekening;
    str *naam;
    str *vrs_of_dag;
    str *omschrijving;
    str *totaal_onafgebroken;
    __ss_int leeftijd_min;
    __ss_int eind;
    __ss_int start;

    PatientDosering() {}
    PatientDosering(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, str *soort_dosering, __ss_float van, __ss_float tot, str *soort_berekening, str *vrs_of_dag, str *totaal_onafgebroken, str *soort_periode, __ss_int aantalvrs, __ss_int leeftijd_min, __ss_int leeftijd_max, __ss_int dagen_van, __ss_int dagen_tot) {
        this->__class__ = cl_PatientDosering;
        __init__(naam, omschrijving, lijst, datum_van, datum_tot, soort_dosering, van, tot, soort_berekening, vrs_of_dag, totaal_onafgebroken, soort_periode, aantalvrs, leeftijd_min, leeftijd_max, dagen_van, dagen_tot);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, str *soort_dosering, __ss_float van, __ss_float tot, str *soort_berekening, str *vrs_of_dag, str *totaal_onafgebroken, str *soort_periode, __ss_int aantalvrs, __ss_int leeftijd_min, __ss_int leeftijd_max, __ss_int dagen_van, __ss_int dagen_tot);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientPolyfarmacie;
class PatientPolyfarmacie : public PatientCriterium {
public:
    __ss_int min_van;
    __ss_int vrs_tot;
    __ss_int groepen_van;
    str *naam;
    __ss_int datum_tot;
    list<VerstrekkingLijstCriterium *> *vrs_lijsten;
    str *totaal_onafgebroken;
    __ss_int vrs_van;
    __ss_int min_tot;
    __ss_int gebr_van;
    __ss_int groepen_tot;
    str *omschrijving;
    __ss_int datum_van;
    __ss_int gebr_tot;
    str *nivo;
    set<str *> *dubbelen;
    __ss_int start;
    __ss_int eind;
    __ss_int info_groepen;

    PatientPolyfarmacie() {}
    PatientPolyfarmacie(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, __ss_int datum_van, __ss_int datum_tot, __ss_int vrs_van, __ss_int vrs_tot, __ss_int gebr_van, __ss_int gebr_tot, str *totaal_onafgebroken, str *dubbelgroepen, __ss_int min_van, __ss_int min_tot, __ss_int groepen_van, __ss_int groepen_tot, str *nivo) {
        this->__class__ = cl_PatientPolyfarmacie;
        __init__(naam, omschrijving, vrs_lijsten, datum_van, datum_tot, vrs_van, vrs_tot, gebr_van, gebr_tot, totaal_onafgebroken, dubbelgroepen, min_van, min_tot, groepen_van, groepen_tot, nivo);
    }
    void *__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, __ss_int datum_van, __ss_int datum_tot, __ss_int vrs_van, __ss_int vrs_tot, __ss_int gebr_van, __ss_int gebr_tot, str *totaal_onafgebroken, str *dubbelgroepen, __ss_int min_van, __ss_int min_tot, __ss_int groepen_van, __ss_int groepen_tot, str *nivo);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientTherapietrouw2;
class PatientTherapietrouw2 : public PatientCriterium {
public:
    __ss_float perc_van;
    list<VerstrekkingLijstCriterium *> *vrs_lijsten;
    __ss_float perc_tot;
    str *nivo;
    __ss_int datum_van;
    str *naam;
    __ss_int datum_tot;
    str *omschrijving;
    __ss_int eind;
    __ss_int start;
    __ss_float info_percentage;

    PatientTherapietrouw2() {}
    PatientTherapietrouw2(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, str *nivo, __ss_int datum_van, __ss_int datum_tot, __ss_float perc_van, __ss_float perc_tot) {
        this->__class__ = cl_PatientTherapietrouw2;
        __init__(naam, omschrijving, vrs_lijsten, nivo, datum_van, datum_tot, perc_van, perc_tot);
    }
    void *__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, str *nivo, __ss_int datum_van, __ss_int datum_tot, __ss_float perc_van, __ss_float perc_tot);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientGebruik;
class PatientGebruik : public PatientCriterium {
public:
    __ss_bool welniet;
    str *omschrijving;
    __ss_float ddd_tot;
    VerstrekkingLijstCriterium *verstrekking;
    __ss_int datum_van;
    __ss_int dagen_van;
    __ss_bool totaal;
    __ss_int datum_tot;
    __ss_int dagen_tot;
    str *naam;
    __ss_float ddd_van;
    __ss_int start;
    __ss_int eind;

    PatientGebruik() {}
    PatientGebruik(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, str *totaal_onafgebroken, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *welniet, __ss_float ddd_van, __ss_float ddd_tot) {
        this->__class__ = cl_PatientGebruik;
        __init__(naam, omschrijving, verstrekking, totaal_onafgebroken, dagen_van, dagen_tot, datum_van, datum_tot, welniet, ddd_van, ddd_tot);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, str *totaal_onafgebroken, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *welniet, __ss_float ddd_van, __ss_float ddd_tot);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientInteractie2;
class PatientInteractie2 : public PatientCriterium {
public:
    __ss_int datum_tot;
    list<VerstrekkingLijstCriterium *> *lijsten;
    __ss_int datum_van;
    __ss_int minimum;
    list<VerstrekkingLijstCriterium *> *lijsten_verplicht;
    __ss_int dagen_van;
    str *naam;
    list<list<Verstrekking *> *> *vrsnn_verplicht;
    __ss_int dagen_tot;
    str *omschrijving;
    list<list<Verstrekking *> *> *vrsnn;
    __ss_int eind;
    __ss_int start;
    list<Period *> *info_perioden;

    PatientInteractie2() {}
    PatientInteractie2(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten_verplicht, list<VerstrekkingLijstCriterium *> *lijsten, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *nivo, str *totaal_onafgebroken, __ss_int minimum) {
        this->__class__ = cl_PatientInteractie2;
        __init__(naam, omschrijving, lijsten_verplicht, lijsten, dagen_van, dagen_tot, datum_van, datum_tot, nivo, totaal_onafgebroken, minimum);
    }
    void *__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten_verplicht, list<VerstrekkingLijstCriterium *> *lijsten, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *nivo, str *totaal_onafgebroken, __ss_int minimum);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientEU;
class PatientEU : public PatientCriterium {
public:
    VerstrekkingCriterium *startmet;
    VerstrekkingLijstCriterium *verstrekking;
    str *soort;
    str *modtarief;
    str *omschrijving;
    __ss_int voorloop;
    str *naam;
    __ss_int datum_tot;
    __ss_int datum_van;
    __ss_int start;
    __ss_int eind;

    PatientEU() {}
    PatientEU(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int datum_van, __ss_int datum_tot, __ss_int voorloop, str *soort, str *modtarief, VerstrekkingCriterium *startmet) {
        this->__class__ = cl_PatientEU;
        __init__(naam, omschrijving, verstrekking, datum_van, datum_tot, voorloop, soort, modtarief, startmet);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int datum_van, __ss_int datum_tot, __ss_int voorloop, str *soort, str *modtarief, VerstrekkingCriterium *startmet);
    void *setup_einddatum(__ss_int einddatum);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
    Verstrekking *check_zelfde_dag(list<Verstrekking *> *vrsn, __ss_int i, __ss_bool vervolg_uitgifte);
};

extern class_ *cl_PatientPuntenTerm;
class PatientPuntenTerm : public pyobj {
public:
    __ss_int aantal_punten;
    PatientCriterium *criterium;
    str *omschrijving;
    str *naam;

    PatientPuntenTerm() {}
    PatientPuntenTerm(str *naam, str *omschrijving, PatientCriterium *criterium, __ss_int aantal_punten) {
        this->__class__ = cl_PatientPuntenTerm;
        __init__(naam, omschrijving, criterium, aantal_punten);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *criterium, __ss_int aantal_punten);
    __ss_int __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientPunten;
class PatientPunten : public PatientCriterium {
public:
    __ss_int punten_max;
    __ss_int punten_min;
    list<PatientPuntenTerm *> *termen;
    str *omschrijving;
    str *naam;

    PatientPunten() {}
    PatientPunten(str *naam, str *omschrijving, list<PatientPuntenTerm *> *termen, __ss_int punten_min, __ss_int punten_max) {
        this->__class__ = cl_PatientPunten;
        __init__(naam, omschrijving, termen, punten_min, punten_max);
    }
    void *__init__(str *naam, str *omschrijving, list<PatientPuntenTerm *> *termen, __ss_int punten_min, __ss_int punten_max);
    __ss_bool __call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientInformatieInfo;
class PatientInformatieInfo : public pyobj {
public:
    list<PatientInfo *> *lijst;
    str *omschrijving;
    str *naam;

    PatientInformatieInfo() {}
    PatientInformatieInfo(str *naam, str *omschrijving, list<PatientInfo *> *lijst) {
        this->__class__ = cl_PatientInformatieInfo;
        __init__(naam, omschrijving, lijst);
    }
    void *__init__(str *naam, str *omschrijving, list<PatientInfo *> *lijst);
};

extern class_ *cl_PatientInfo;
class PatientInfo : public pyobj {
public:
    str *naam;

    PatientInfo() { this->__class__ = cl_PatientInfo; }
    virtual str *__call__(Patient *p, __ss_int  einddatum) { return 0; };
};

extern class_ *cl_PatientPatientInfo;
class PatientPatientInfo : public PatientInfo {
public:
    PatientCriterium *criterium;
    str *omschrijving;

    PatientPatientInfo() {}
    PatientPatientInfo(str *naam, str *omschrijving, PatientCriterium *criterium) {
        this->__class__ = cl_PatientPatientInfo;
        __init__(naam, omschrijving, criterium);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *criterium);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientPatientenInfo;
class PatientPatientenInfo : public PatientInfo {
public:
    PatientCriterium *criterium;
    str *omschrijving;

    PatientPatientenInfo() {}
    PatientPatientenInfo(str *naam, str *omschrijving, PatientCriterium *criterium) {
        this->__class__ = cl_PatientPatientenInfo;
        __init__(naam, omschrijving, criterium);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *criterium);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientPolyfarmacieInfo;
class PatientPolyfarmacieInfo : public PatientInfo {
public:
    str *wat;
    PatientPolyfarmacie *criterium;
    str *omschrijving;

    PatientPolyfarmacieInfo() {}
    PatientPolyfarmacieInfo(str *naam, str *omschrijving, PatientPolyfarmacie *criterium, str *wat) {
        this->__class__ = cl_PatientPolyfarmacieInfo;
        __init__(naam, omschrijving, criterium, wat);
    }
    void *__init__(str *naam, str *omschrijving, PatientPolyfarmacie *criterium, str *wat);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientTherapietrouwNieuwInfo;
class PatientTherapietrouwNieuwInfo : public PatientInfo {
public:
    __ss_int decimalen;
    str *wat;
    PatientTherapietrouw2 *criterium;
    str *omschrijving;

    PatientTherapietrouwNieuwInfo() {}
    PatientTherapietrouwNieuwInfo(str *naam, str *omschrijving, PatientTherapietrouw2 *criterium, str *wat, __ss_int decimalen) {
        this->__class__ = cl_PatientTherapietrouwNieuwInfo;
        __init__(naam, omschrijving, criterium, wat, decimalen);
    }
    void *__init__(str *naam, str *omschrijving, PatientTherapietrouw2 *criterium, str *wat, __ss_int decimalen);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientVerstrekkingenInfo;
class PatientVerstrekkingenInfo : public PatientInfo {
public:
    PatientCriterium *criterium;
    VerstrekkingCriterium *vrs_enkel;
    __ss_int datum_van;
    str *omschrijving;
    VerstrekkingLijstCriterium *vrslijst;
    __ss_int datum_tot;
    str *tellen;

    PatientVerstrekkingenInfo() {}
    PatientVerstrekkingenInfo(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, PatientCriterium *criterium, str *tellen, __ss_int datum_van, __ss_int datum_tot, VerstrekkingCriterium *vrs_enkel) {
        this->__class__ = cl_PatientVerstrekkingenInfo;
        __init__(naam, omschrijving, vrs, criterium, tellen, datum_van, datum_tot, vrs_enkel);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, PatientCriterium *criterium, str *tellen, __ss_int datum_van, __ss_int datum_tot, VerstrekkingCriterium *vrs_enkel);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientPeriodenInfo;
class PatientPeriodenInfo : public PatientInfo {
public:
    str *omschrijving;
    str *wat;
    __ss_int datum_van;
    PatientCriterium *criterium;
    __ss_int datum_tot;
    str *hoe;
    VerstrekkingLijstCriterium *vrslijst;

    PatientPeriodenInfo() {}
    PatientPeriodenInfo(str *naam, str *omschrijving, PatientCriterium *pat, VerstrekkingLijstCriterium *vrs, str *wat, str *hoe, __ss_int datum_van, __ss_int datum_tot) {
        this->__class__ = cl_PatientPeriodenInfo;
        __init__(naam, omschrijving, pat, vrs, wat, hoe, datum_van, datum_tot);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *pat, VerstrekkingLijstCriterium *vrs, str *wat, str *hoe, __ss_int datum_van, __ss_int datum_tot);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientEUInfo;
class PatientEUInfo : public PatientInfo {
public:
    str *wat;
    PatientEU *criterium;
    str *omschrijving;

    PatientEUInfo() {}
    PatientEUInfo(str *naam, str *omschrijving, PatientEU *criterium, str *wat) {
        this->__class__ = cl_PatientEUInfo;
        __init__(naam, omschrijving, criterium, wat);
    }
    void *__init__(str *naam, str *omschrijving, PatientEU *criterium, str *wat);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientLUInfo;
class PatientLUInfo : public PatientInfo {
public:
    str *wat;
    VerstrekkingLijstCriterium *vrslijst;
    __ss_int datum_van;
    __ss_int datum_tot;
    str *welke;
    str *omschrijving;

    PatientLUInfo() {}
    PatientLUInfo(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, __ss_int datum_van, str *welke, str *wat, __ss_int datum_tot) {
        this->__class__ = cl_PatientLUInfo;
        __init__(naam, omschrijving, vrs, datum_van, welke, wat, datum_tot);
    }
    void *__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, __ss_int datum_van, str *welke, str *wat, __ss_int datum_tot);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientInteractieInfo;
class PatientInteractieInfo : public PatientInfo {
public:
    PatientCriterium *pat;
    str *uniek;
    str *omschrijving;
    str *wens;
    PatientInteractie2 *criterium;

    PatientInteractieInfo() {}
    PatientInteractieInfo(str *naam, str *omschrijving, PatientCriterium *pat, PatientInteractie2 *criterium, str *wens, str *uniek) {
        this->__class__ = cl_PatientInteractieInfo;
        __init__(naam, omschrijving, pat, criterium, wens, uniek);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *pat, PatientInteractie2 *criterium, str *wens, str *uniek);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern class_ *cl_PatientDoseringInfo;
class PatientDoseringInfo : public PatientInfo {
public:
    str *omschrijving;

    PatientDoseringInfo() {}
    PatientDoseringInfo(str *naam, str *omschrijving, PatientCriterium *pat, PatientDosering *criterium, str *wat, __ss_int decimalen) {
        this->__class__ = cl_PatientDoseringInfo;
        __init__(naam, omschrijving, pat, criterium, wat, decimalen);
    }
    void *__init__(str *naam, str *omschrijving, PatientCriterium *pat, PatientDosering *criterium, str *wat, __ss_int decimalen);
    str *__call__(Patient *p, __ss_int einddatum);
};

extern str * default_0;
extern str * default_1;
extern str * default_2;
extern str * default_3;
extern str * default_4;
extern str * default_5;
extern str * default_6;
extern str * default_7;
extern str * default_8;
extern str * default_9;
extern str * default_10;
extern str * default_11;
extern str * default_12;
extern str * default_13;
extern str * default_14;
extern str * default_15;
extern list<Middel *> * default_16;
extern list<list<Verstrekking *> *> * default_17;
extern str * default_18;
extern str * default_19;
extern void * default_20;
extern __ss_int  default_21;
extern __ss_int  default_22;
extern str * default_23;
extern PatientCriterium * default_24;
extern PatientCriterium * default_25;
extern str * default_26;
extern str * default_27;
extern list<Indicator *> * default_28;
extern PatientCriterium * default_29;
extern PatientCriterium * default_30;
extern str * default_31;
extern PatientInformatieInfo * default_32;
extern str * default_33;
extern PatientCriterium * default_34;
extern PatientCriterium * default_35;
extern PatientInformatieInfo * default_36;
extern str * default_37;
extern str * default_38;
extern str * default_39;
extern str * default_40;
extern str * default_41;
extern str * default_42;
extern str * default_43;
extern str * default_44;
extern list<CorrectieTerm *> * default_45;
extern str * default_46;
extern str * default_47;
extern str * default_48;
extern str * default_49;
extern MiddelGroep * default_50;
extern str * default_51;
extern str * default_52;
extern str * default_53;
extern str * default_54;
extern MiddelGroep * default_55;
extern Correctie * default_56;
extern VerstrekkingCriterium * default_57;
extern str * default_58;
extern str * default_59;
extern str * default_60;
extern str * default_61;
extern str * default_62;
extern str * default_63;
extern str * default_64;
extern str * default_65;
extern str * default_66;
extern str * default_67;
extern list<PatientCriterium *> * default_68;
extern str * default_69;
extern str * default_70;
extern str * default_71;
extern PatientCriterium * default_72;
extern str * default_73;
extern VerstrekkingLijstCriterium * default_74;
extern str * default_75;
extern VerstrekkingCriterium * default_76;
extern str * default_77;
extern str * default_78;
extern str * default_79;
extern VerstrekkingLijstCriterium * default_80;
extern PatientCriterium * default_81;
extern VerstrekkingLijstCriterium * default_82;
extern str * default_83;
extern str * default_84;
extern str * default_85;
extern str * default_86;
extern str * default_87;
extern str * default_88;
extern str * default_89;
extern str * default_90;
extern str * default_91;
extern str * default_92;
extern VerstrekkingLijstCriterium * default_93;
extern str * default_94;
extern str * default_95;
extern list<VerstrekkingLijstCriterium *> * default_96;
extern list<VerstrekkingLijstCriterium *> * default_97;
extern str * default_98;
extern str * default_99;
extern str * default_100;
extern VerstrekkingLijstCriterium * default_101;
extern str * default_102;
extern str * default_103;
extern VerstrekkingCriterium * default_104;
extern str * default_105;
extern list<PatientInfo *> * default_106;
extern str * default_107;
extern PatientCriterium * default_108;
extern PatientCriterium * default_109;
extern PatientPolyfarmacie * default_110;
extern str * default_111;
extern PatientTherapietrouw2 * default_112;
extern str * default_113;
extern VerstrekkingLijstCriterium * default_114;
extern PatientCriterium * default_115;
extern str * default_116;
extern VerstrekkingCriterium * default_117;
extern PatientCriterium * default_118;
extern VerstrekkingLijstCriterium * default_119;
extern str * default_120;
extern str * default_121;
extern PatientEU * default_122;
extern str * default_123;
extern VerstrekkingLijstCriterium * default_124;
extern str * default_125;
extern str * default_126;
extern PatientCriterium * default_127;
extern PatientInteractie2 * default_128;
extern str * default_129;
extern str * default_130;
extern PatientCriterium * default_131;
extern PatientDosering * default_132;
extern str * default_133;
tuple<list<__ss_int> *> *_month_days();
__ss_int get_days(__ss_int ymd);
__ss_int get_ymd(__ss_int days);
__ss_int shift_months(__ss_int ymd, __ss_int n);
__ss_int shift_days(__ss_int ymd, __ss_int n);
void *set_atcs(list<str *> *codes);
void *set_pref_beleid(dict<tuple<__ss_int> *, list<tuple<__ss_int> *> *> *pref);
void *set_atc5_naam(dict<str *, str *> *atc5_naam);
list<Period *> *vrs_gebruik(list<Verstrekking *> *vrsn, __ss_int start, __ss_int eind);
list<Period *> *vrs_interactie(list<list<Verstrekking *> *> *vrsnn, __ss_int startdatum, __ss_int einddatum, __ss_int minimum, list<list<Verstrekking *> *> *vrsnn_verplicht);
__ss_int vrs_index(list<Verstrekking *> *recepten, __ss_int datum);
list<Verstrekking *> *vrs_schuiven(list<Verstrekking *> *vrsn);
list<Verstrekking *> *vrs_correctie(list<Verstrekking *> *vrsn, str *nivo, str *atc_wissel);
dict<str *, list<Verstrekking *> *> *vrs_split(list<Verstrekking *> *vrsn, str *nivo, str *atc_wissel);
__ss_int vrs_aantal(list<Verstrekking *> *_vrsn, __ss_int datum_begin, __ss_int datum_eind);
__ss_float vrs_gemiddeld_hulp(Verstrekking *vrs, str *soort_dosering);
tuple2<__ss_float, __ss_int> *vrs_gemiddeld(list<Verstrekking *> *_vrsn, str *soort_dosering, __ss_int aantal_iets, str *vrs_of_dag, void *soort_periode, __ss_int start_periode, __ss_int eind_periode);
list<Period *> *prd_invert(list<Period *> *prdn, __ss_int start, __ss_int eind);
str *datum_fmt(__ss_int ymd);
str *vrs_info(Verstrekking *vrs, str *wat);

} // module namespace
#endif
