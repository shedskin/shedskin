#include "builtin.hpp"
#include "collections.hpp"
#include "sys.hpp"
#include "wokl.hpp"

namespace __wokl__ {

str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_2, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_26, *const_27, *const_28, *const_29, *const_3, *const_30, *const_31, *const_32, *const_33, *const_34, *const_35, *const_36, *const_37, *const_38, *const_39, *const_4, *const_40, *const_41, *const_42, *const_43, *const_44, *const_45, *const_46, *const_47, *const_48, *const_49, *const_5, *const_50, *const_51, *const_52, *const_53, *const_54, *const_55, *const_56, *const_57, *const_58, *const_59, *const_6, *const_60, *const_61, *const_62, *const_63, *const_64, *const_65, *const_66, *const_67, *const_68, *const_69, *const_7, *const_70, *const_71, *const_72, *const_73, *const_74, *const_75, *const_76, *const_77, *const_78, *const_79, *const_8, *const_80, *const_81, *const_82, *const_83, *const_84, *const_9;


str *__name__;
list<__ss_int> *CODES_VERVOLGUITGIFTE, *DAYS_YMD, *MONTH_DAYS;
list<void *> *NO_PERIODS;
Artikel *a;
Recept *r;
Verstrekking *v;
Patient *p;
Groep *g;
Middel *m;
MiddelGroep *mg;
ATC *atc;
VerstrekkingCriterium *veig;
VerstrekkingLogischTerm *vlterm;
CorrectieTerm *correctie_term;
Correctie *correctie;
list<VerstrekkingLijstCriterium *> *vcrits;
VerstrekkingLijstCriterium *vcrit;
PatientTherapietrouw2 *ttcrit;
PatientInteractie2 *intcrit;
PatientPolyfarmacie *polycrit;
PatientEU *eucrit;
PatientDosering *doscrit;
PatientCriterium *eig;
PatientInfo *patinfo;
PatientInformatieInfo *info;
Indicator *ind;
Indicatoren *inds;
Rapportage *ovz;
tuple<list<__ss_int> *> *__13;
dict<str *, ATC *> *g_atcs;
__collections__::defaultdict<str *, set<ATC *> *> *g_code_atcs;
dict<tuple<__ss_int> *, list<tuple<__ss_int> *> *> *g_pref_beleid;
dict<str *, str *> *g_atc5_naam;


str * default_0;
str * default_1;
str * default_2;
str * default_3;
str * default_4;
str * default_5;
str * default_6;
str * default_7;
str * default_8;
str * default_9;
str * default_10;
str * default_11;
str * default_12;
str * default_13;
str * default_14;
str * default_15;
list<Middel *> * default_16;
list<list<Verstrekking *> *> * default_17;
str * default_18;
str * default_19;
void * default_20;
__ss_int  default_21;
__ss_int  default_22;
str * default_23;
PatientCriterium * default_24;
PatientCriterium * default_25;
str * default_26;
str * default_27;
list<Indicator *> * default_28;
PatientCriterium * default_29;
PatientCriterium * default_30;
str * default_31;
PatientInformatieInfo * default_32;
str * default_33;
PatientCriterium * default_34;
PatientCriterium * default_35;
PatientInformatieInfo * default_36;
str * default_37;
str * default_38;
str * default_39;
str * default_40;
str * default_41;
str * default_42;
str * default_43;
str * default_44;
list<CorrectieTerm *> * default_45;
str * default_46;
str * default_47;
str * default_48;
str * default_49;
MiddelGroep * default_50;
str * default_51;
str * default_52;
str * default_53;
str * default_54;
MiddelGroep * default_55;
Correctie * default_56;
VerstrekkingCriterium * default_57;
str * default_58;
str * default_59;
str * default_60;
str * default_61;
str * default_62;
str * default_63;
str * default_64;
str * default_65;
str * default_66;
str * default_67;
list<PatientCriterium *> * default_68;
str * default_69;
str * default_70;
str * default_71;
PatientCriterium * default_72;
str * default_73;
VerstrekkingLijstCriterium * default_74;
str * default_75;
VerstrekkingCriterium * default_76;
str * default_77;
str * default_78;
str * default_79;
VerstrekkingLijstCriterium * default_80;
PatientCriterium * default_81;
VerstrekkingLijstCriterium * default_82;
str * default_83;
str * default_84;
str * default_85;
str * default_86;
str * default_87;
str * default_88;
str * default_89;
str * default_90;
str * default_91;
str * default_92;
VerstrekkingLijstCriterium * default_93;
str * default_94;
str * default_95;
list<VerstrekkingLijstCriterium *> * default_96;
list<VerstrekkingLijstCriterium *> * default_97;
str * default_98;
str * default_99;
str * default_100;
VerstrekkingLijstCriterium * default_101;
str * default_102;
str * default_103;
VerstrekkingCriterium * default_104;
str * default_105;
list<PatientInfo *> * default_106;
str * default_107;
PatientCriterium * default_108;
PatientCriterium * default_109;
PatientPolyfarmacie * default_110;
str * default_111;
PatientTherapietrouw2 * default_112;
str * default_113;
VerstrekkingLijstCriterium * default_114;
PatientCriterium * default_115;
str * default_116;
VerstrekkingCriterium * default_117;
PatientCriterium * default_118;
VerstrekkingLijstCriterium * default_119;
str * default_120;
str * default_121;
PatientEU * default_122;
str * default_123;
VerstrekkingLijstCriterium * default_124;
str * default_125;
str * default_126;
PatientCriterium * default_127;
PatientInteractie2 * default_128;
str * default_129;
str * default_130;
PatientCriterium * default_131;
PatientDosering * default_132;
str * default_133;
static inline list<__ss_int> *list_comp_0(__ss_int year, __ss_int length, __ss_int m);
static inline list<__ss_int> *list_comp_1(__ss_int einddatum, list<Verstrekking *> *vrsn);
static inline list<__ss_int> *list_comp_2(str *farm_vorm);
static inline list<__ss_int> *list_comp_3(str *niet_farm_vorm);
static inline list<__ss_int> *list_comp_4(str *toedieningsweg);
static inline list<__ss_int> *list_comp_5(str *niet_toedieningsweg);
static inline list<__ss_int> *list_comp_6(str *hpk);
static inline list<__ss_int> *list_comp_7(str *hpk_niet);
static inline list<__ss_int> *list_comp_8(str *prk);
static inline list<__ss_int> *list_comp_9(str *prk_niet);
static inline list<__ss_int> *list_comp_10(str *gpk);
static inline list<__ss_int> *list_comp_11(str *gpk_niet);
static inline list<__ss_float> *list_comp_12(list<tuple2<__ss_int, __ss_float> *> *dos_per_iets);
static inline list<__ss_int> *list_comp_13(list<Verstrekking *> *_vrsn);
static inline list<__ss_float> *list_comp_14(list<tuple2<__ss_int, __ss_float> *> *dos_per_iets);
static inline list<__ss_int> *list_comp_15(list<VerstrekkingLijstCriterium *> *vrslijsten);
static inline list<__ss_int> *list_comp_16(str *modulairetariefcode);
static inline list<__ss_int> *list_comp_17(str *zorgverzekeraar);
static inline list<str *> *list_comp_18(list<str *> *waarden, str *atc5);
static inline list<__ss_int> *list_comp_19(list<str *> *waarden);
static inline list<__ss_int> *list_comp_20(list<str *> *waarden);
static inline list<__ss_int> *list_comp_21(list<str *> *waarden);
static inline list<Verstrekking *> *list_comp_22(VerstrekkingLijstEigenschappen *self, list<Verstrekking *> *vrsn);
static inline list<__ss_int> *list_comp_23(list<Period *> *gaten);
static inline list<Period *> *list_comp_24(__ss_int lengte_van, __ss_int lengte_tot, list<Period *> *gaten);
static inline dict<str *, list<Verstrekking *> *> *list_comp_25(dict<str *, list<Verstrekking *> *> *key_vrsn, __ss_int min_tot, __ss_int min_van);
static inline list<__ss_int> *list_comp_26(list<str *> *groepen, PatientPolyfarmacie *self);
static inline list<__ss_int> *list_comp_27(list<Period *> *prdn);
static inline list<__ss_int> *list_comp_28(Patient *p, __ss_int einddatum, PatientPunten *self);
static inline list<str *> *list_comp_29(list<Period *> *prdn);
static inline list<str *> *list_comp_30(list<Period *> *prdn);
static inline list<__ss_int> *list_comp_31(list<Period *> *prdn);
static inline list<__ss_int> *list_comp_32(list<VerstrekkingLijstCriterium *> *vrslijsten);
static inline list<__ss_int> *list_comp_33(list<VerstrekkingLijstCriterium *> *vrslijsten);
static inline set<ATC *> *__lambda0__();
static inline __ss_int __lambda1__(Marker *m);
static inline __ss_int __lambda2__(Verstrekking *v);
static inline __ss_int __lambda6__(Verstrekking *v);
static inline __ss_int __lambda8__(Verstrekking *v);
static inline __ss_int __lambda9__(Verstrekking *v);

static inline list<__ss_int> *list_comp_0(__ss_int year, __ss_int length, __ss_int m) {
    __ss_int __11, __12, d;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FAST_FOR(d,0,length,1,11,12)
        __ss_result->append(((((year*__ss_int(10000))+((m+__ss_int(1))*__ss_int(100)))+d)+__ss_int(1)));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_1(__ss_int einddatum, list<Verstrekking *> *vrsn) {
    __ss_int __27, __28, i;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(79);
    FAST_FOR(i,0,__ss_int(79),1,27,28)
        __ss_result->units[__27] = vrs_index(vrsn, shift_months(einddatum, (-i)));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_2(str *farm_vorm) {
    str *__41, *fv;
    list<str *> *__36;
    __iter<str *> *__37;
    __ss_int __38;
    list<str *>::for_in_loop __39;
    void *__40;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __36 = farm_vorm->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__36));
    FOR_IN(fv,__36,36,38,39)
        __ss_result->units[__38] = __int(fv);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_3(str *niet_farm_vorm) {
    str *__47, *fv;
    list<str *> *__42;
    __iter<str *> *__43;
    __ss_int __44;
    list<str *>::for_in_loop __45;
    void *__46;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __42 = niet_farm_vorm->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__42));
    FOR_IN(fv,__42,42,44,45)
        __ss_result->units[__44] = __int(fv);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_4(str *toedieningsweg) {
    str *__53, *t;
    list<str *> *__48;
    __iter<str *> *__49;
    __ss_int __50;
    list<str *>::for_in_loop __51;
    void *__52;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __48 = toedieningsweg->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__48));
    FOR_IN(t,__48,48,50,51)
        __ss_result->units[__50] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_5(str *niet_toedieningsweg) {
    str *__59, *t;
    list<str *> *__54;
    __iter<str *> *__55;
    __ss_int __56;
    list<str *>::for_in_loop __57;
    void *__58;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __54 = niet_toedieningsweg->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__54));
    FOR_IN(t,__54,54,56,57)
        __ss_result->units[__56] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_6(str *hpk) {
    str *__65, *t;
    list<str *> *__60;
    __iter<str *> *__61;
    __ss_int __62;
    list<str *>::for_in_loop __63;
    void *__64;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __60 = hpk->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__60));
    FOR_IN(t,__60,60,62,63)
        __ss_result->units[__62] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_7(str *hpk_niet) {
    str *__71, *t;
    list<str *> *__66;
    __iter<str *> *__67;
    __ss_int __68;
    list<str *>::for_in_loop __69;
    void *__70;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __66 = hpk_niet->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__66));
    FOR_IN(t,__66,66,68,69)
        __ss_result->units[__68] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_8(str *prk) {
    str *__77, *t;
    list<str *> *__72;
    __iter<str *> *__73;
    __ss_int __74;
    list<str *>::for_in_loop __75;
    void *__76;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __72 = prk->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__72));
    FOR_IN(t,__72,72,74,75)
        __ss_result->units[__74] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_9(str *prk_niet) {
    str *__83, *t;
    list<str *> *__78;
    __iter<str *> *__79;
    __ss_int __80;
    list<str *>::for_in_loop __81;
    void *__82;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __78 = prk_niet->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__78));
    FOR_IN(t,__78,78,80,81)
        __ss_result->units[__80] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_10(str *gpk) {
    str *__89, *t;
    list<str *> *__84;
    __iter<str *> *__85;
    __ss_int __86;
    list<str *>::for_in_loop __87;
    void *__88;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __84 = gpk->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__84));
    FOR_IN(t,__84,84,86,87)
        __ss_result->units[__86] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_11(str *gpk_niet) {
    str *__95, *t;
    list<str *> *__90;
    __iter<str *> *__91;
    __ss_int __92;
    list<str *>::for_in_loop __93;
    void *__94;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __90 = gpk_niet->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__90));
    FOR_IN(t,__90,90,92,93)
        __ss_result->units[__92] = __int(t);
    END_FOR

    return __ss_result;
}

static inline list<__ss_float> *list_comp_12(list<tuple2<__ss_int, __ss_float> *> *dos_per_iets) {
    tuple2<__ss_int, __ss_float> *d;
    list<tuple2<__ss_int, __ss_float> *> *__221;
    __iter<tuple2<__ss_int, __ss_float> *> *__222;
    __ss_int __223;
    list<tuple2<__ss_int, __ss_float> *>::for_in_loop __224;

    list<__ss_float> *__ss_result = new list<__ss_float>();

    __ss_result->resize(len(dos_per_iets));
    FOR_IN(d,dos_per_iets,221,223,224)
        __ss_result->units[__223] = d->__getsecond__();
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_13(list<Verstrekking *> *_vrsn) {
    Verstrekking *vrs;
    list<Verstrekking *> *__225;
    __iter<Verstrekking *> *__226;
    __ss_int __227;
    list<Verstrekking *>::for_in_loop __228;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(_vrsn));
    FOR_IN(vrs,_vrsn,225,227,228)
        __ss_result->units[__227] = vrs->einddatum;
    END_FOR

    return __ss_result;
}

static inline list<__ss_float> *list_comp_14(list<tuple2<__ss_int, __ss_float> *> *dos_per_iets) {
    tuple2<__ss_int, __ss_float> *d;
    list<tuple2<__ss_int, __ss_float> *> *__229;
    __iter<tuple2<__ss_int, __ss_float> *> *__230;
    __ss_int __231;
    list<tuple2<__ss_int, __ss_float> *>::for_in_loop __232;

    list<__ss_float> *__ss_result = new list<__ss_float>();

    __229 = dos_per_iets->__slice__(__ss_int(2), __ss_int(0), (-__ss_int(1)), __ss_int(0));
    __ss_result->resize(len(__229));
    FOR_IN(d,__229,229,231,232)
        __ss_result->units[__231] = d->__getsecond__();
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_15(list<VerstrekkingLijstCriterium *> *vrslijsten) {
    VerstrekkingLijstCriterium *v;
    list<VerstrekkingLijstCriterium *> *__237;
    __iter<VerstrekkingLijstCriterium *> *__238;
    __ss_int __239;
    list<VerstrekkingLijstCriterium *>::for_in_loop __240;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(vrslijsten));
    FOR_IN(v,vrslijsten,237,239,240)
        __ss_result->units[__239] = v->datum_van;
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_16(str *modulairetariefcode) {
    str *__304, *mtc;
    list<str *> *__299;
    __iter<str *> *__300;
    __ss_int __301;
    list<str *>::for_in_loop __302;
    void *__303;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __299 = modulairetariefcode->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__299));
    FOR_IN(mtc,__299,299,301,302)
        __ss_result->units[__301] = __int(mtc);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_17(str *zorgverzekeraar) {
    str *__310, *zv;
    list<str *> *__305;
    __iter<str *> *__306;
    __ss_int __307;
    list<str *>::for_in_loop __308;
    void *__309;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __305 = zorgverzekeraar->split(NULL, (-__ss_int(1)));
    __ss_result->resize(len(__305));
    FOR_IN(zv,__305,305,307,308)
        __ss_result->units[__307] = __int(zv);
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_18(list<str *> *waarden, str *atc5) {
    str *atc;
    list<str *> *__377;
    __iter<str *> *__378;
    __ss_int __379;
    list<str *>::for_in_loop __380;

    list<str *> *__ss_result = new list<str *>();

    __ss_result->units.reserve(4);
    FOR_IN(atc,waarden,377,379,380)
        if (atc5->startswith(atc)) {
            __ss_result->append(atc);
        }
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_19(list<str *> *waarden) {
    str *w;
    list<str *> *__381;
    __iter<str *> *__382;
    __ss_int __383;
    list<str *>::for_in_loop __384;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(waarden));
    FOR_IN(w,waarden,381,383,384)
        __ss_result->units[__383] = __int(w);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_20(list<str *> *waarden) {
    str *w;
    list<str *> *__385;
    __iter<str *> *__386;
    __ss_int __387;
    list<str *>::for_in_loop __388;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(waarden));
    FOR_IN(w,waarden,385,387,388)
        __ss_result->units[__387] = __int(w);
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_21(list<str *> *waarden) {
    str *w;
    list<str *> *__389;
    __iter<str *> *__390;
    __ss_int __391;
    list<str *>::for_in_loop __392;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(waarden));
    FOR_IN(w,waarden,389,391,392)
        __ss_result->units[__391] = __int(w);
    END_FOR

    return __ss_result;
}

static inline list<Verstrekking *> *list_comp_22(VerstrekkingLijstEigenschappen *self, list<Verstrekking *> *vrsn) {
    Verstrekking *vrs;
    list<Verstrekking *> *__406;
    __iter<Verstrekking *> *__407;
    __ss_int __408;
    list<Verstrekking *>::for_in_loop __409;

    list<Verstrekking *> *__ss_result = new list<Verstrekking *>();

    __ss_result->units.reserve(4);
    FOR_IN(vrs,vrsn,406,408,409)
        if (self->verstrekking->__call__(vrs)) {
            __ss_result->append(vrs);
        }
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_23(list<Period *> *gaten) {
    Period *gat;
    list<Period *> *__483;
    __iter<Period *> *__484;
    __ss_int __485;
    list<Period *>::for_in_loop __486;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->units.reserve(4);
    FOR_IN(gat,gaten,483,485,486)
        if ((gat->eind!=NULL)) {
            __ss_result->append((get_days(gat->eind)-get_days(gat->start)));
        }
    END_FOR

    return __ss_result;
}

static inline list<Period *> *list_comp_24(__ss_int lengte_van, __ss_int lengte_tot, list<Period *> *gaten) {
    Period *gat;
    list<Period *> *__487;
    __iter<Period *> *__488;
    __ss_int __489, __492;
    list<Period *>::for_in_loop __490;
    __ss_bool __491, __493;

    list<Period *> *__ss_result = new list<Period *>();

    __ss_result->units.reserve(4);
    FOR_IN(gat,gaten,487,489,490)
        if (((gat->eind!=NULL) and (lengte_van<=(__492=(get_days(gat->eind)-get_days(gat->start))))&&(__492<lengte_tot))) {
            __ss_result->append(gat);
        }
    END_FOR

    return __ss_result;
}

static inline dict<str *, list<Verstrekking *> *> *list_comp_25(dict<str *, list<Verstrekking *> *> *key_vrsn, __ss_int min_tot, __ss_int min_van) {
    tuple2<str *, list<Verstrekking *> *> *__512;
    str *key;
    list<Verstrekking *> *vrsn;
    __iter<tuple2<str *, list<Verstrekking *> *> *> *__513, *__514;
    __ss_int __515;
    __iter<tuple2<str *, list<Verstrekking *> *> *>::for_in_loop __516;
    __GC_DICT<str *, list<Verstrekking *> *>::iterator __517;
    dict<str *, list<Verstrekking *> *> *__518;

    dict<str *, list<Verstrekking *> *> *__ss_result = new dict<str *, list<Verstrekking *> *>();

    FOR_IN_DICT(key_vrsn,518,517,515)
        key = (*__517).first;
        vrsn = (*__517).second;
        __517++;
        if (vrs_aantal(vrsn, min_van, min_tot)) {
            __ss_result->__setitem__(key,vrsn);
        }
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_26(list<str *> *groepen, PatientPolyfarmacie *self) {
    str *groep;
    list<str *> *__539;
    __iter<str *> *__540;
    __ss_int __541;
    list<str *>::for_in_loop __542;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(groepen));
    FOR_IN(groep,groepen,539,541,542)
        __ss_result->units[__541] = (((self->dubbelen)->__contains__(groep))?(__ss_int(2)):(__ss_int(1)));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_27(list<Period *> *prdn) {
    Period *p;
    list<Period *> *__560;
    __iter<Period *> *__561;
    __ss_int __562;
    list<Period *>::for_in_loop __563;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(prdn));
    FOR_IN(p,prdn,560,562,563)
        __ss_result->units[__562] = (get_days(p->eind)-get_days(p->start));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_28(Patient *p, __ss_int einddatum, PatientPunten *self) {
    PatientPuntenTerm *term;
    list<PatientPuntenTerm *> *__630;
    __iter<PatientPuntenTerm *> *__631;
    __ss_int __632;
    list<PatientPuntenTerm *>::for_in_loop __633;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __630 = self->termen;
    __ss_result->resize(len(__630));
    FOR_IN(term,__630,630,632,633)
        __ss_result->units[__632] = term->__call__(p, einddatum);
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_29(list<Period *> *prdn) {
    Period *p;
    list<Period *> *__644;
    __iter<Period *> *__645;
    __ss_int __646;
    list<Period *>::for_in_loop __647;

    list<str *> *__ss_result = new list<str *>();

    __ss_result->resize(len(prdn));
    FOR_IN(p,prdn,644,646,647)
        __ss_result->units[__646] = __str((get_days(p->eind)-get_days(p->start)));
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_30(list<Period *> *prdn) {
    Period *p;
    list<Period *> *__648;
    __iter<Period *> *__649;
    __ss_int __650;
    list<Period *>::for_in_loop __651;

    list<str *> *__ss_result = new list<str *>();

    __ss_result->resize(len(prdn));
    FOR_IN(p,prdn,648,650,651)
        __ss_result->units[__650] = __add_strs(3, datum_fmt(p->start), const_60, datum_fmt(p->eind));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_31(list<Period *> *prdn) {
    Period *p;
    list<Period *> *__656;
    __iter<Period *> *__657;
    __ss_int __658;
    list<Period *>::for_in_loop __659;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(prdn));
    FOR_IN(p,prdn,656,658,659)
        __ss_result->units[__658] = (get_days(p->eind)-get_days(p->start));
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_32(list<VerstrekkingLijstCriterium *> *vrslijsten) {
    VerstrekkingLijstCriterium *v;
    list<VerstrekkingLijstCriterium *> *__237;
    __iter<VerstrekkingLijstCriterium *> *__665;
    __ss_int __239;
    list<VerstrekkingLijstCriterium *>::for_in_loop __667;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(vrslijsten));
    FOR_IN(v,vrslijsten,237,239,667)
        __ss_result->units[__239] = v->datum_van;
    END_FOR

    return __ss_result;
}

static inline list<__ss_int> *list_comp_33(list<VerstrekkingLijstCriterium *> *vrslijsten) {
    VerstrekkingLijstCriterium *v;
    list<VerstrekkingLijstCriterium *> *__237;
    __iter<VerstrekkingLijstCriterium *> *__705;
    __ss_int __239;
    list<VerstrekkingLijstCriterium *>::for_in_loop __707;

    list<__ss_int> *__ss_result = new list<__ss_int>();

    __ss_result->resize(len(vrslijsten));
    FOR_IN(v,vrslijsten,237,239,707)
        __ss_result->units[__239] = v->datum_van;
    END_FOR

    return __ss_result;
}

static inline set<ATC *> *__lambda0__() {
    return (new set<ATC *>());
}

static inline __ss_int __lambda1__(Marker *m) {
    return m->datum;
}

static inline __ss_int __lambda2__(Verstrekking *v) {
    return v->datum;
}

static inline __ss_int __lambda6__(Verstrekking *v) {
    return v->datum;
}

static inline __ss_int __lambda8__(Verstrekking *v) {
    return v->datum;
}

static inline __ss_int __lambda9__(Verstrekking *v) {
    return v->datum;
}

tuple<list<__ss_int> *> *_month_days() {
    list<__ss_int> *__9, *days_ymd, *month_days, *month_lengths;
    __ss_int __3, __4, __8, days, length, m, year;
    tuple<__ss_int> *__5;
    __iter<tuple<__ss_int> *> *__6, *__7;
    __iter<tuple<__ss_int> *>::for_in_loop __10;

    month_days = (__ss_list<__ss_int>());
    days_ymd = (__ss_list<__ss_int>());
    days = __ss_int(0);

    FAST_FOR(year,__ss_int(2000),__ss_int(2035),1,3,4)
        month_lengths = (new list<__ss_int>(12,__ss_int(31),__ss_int(28),__ss_int(31),__ss_int(30),__ss_int(31),__ss_int(30),__ss_int(31),__ss_int(31),__ss_int(30),__ss_int(31),__ss_int(30),__ss_int(31)));
        if ((__mods(year, __ss_int(4))==__ss_int(0))) {
            month_lengths->__setitem__(__ss_int(1), __ss_int(29));
        }

        FOR_IN_ENUMERATE(length,month_lengths,9,8)
            m = __8;
            month_days->append(days);
            days_ymd->extend(list_comp_0(year, length, m));
            days = (days+length);
        END_FOR

    END_FOR

    return (new tuple<list<__ss_int> *>(2,month_days,days_ymd));
}

__ss_int get_days(__ss_int ymd) {
    __ss_int d, m, y;

    y = (__floordiv(ymd,__ss_int(10000))-__ss_int(2000));
    m = (__mods(__floordiv(ymd,__ss_int(100)), __ss_int(100))-__ss_int(1));
    d = (__mods(ymd, __ss_int(100))-__ss_int(1));
    return (__wokl__::MONTH_DAYS->__getfast__(((__ss_int(12)*y)+m))+d);
}

__ss_int get_ymd(__ss_int days) {
    if ((days<len(__wokl__::DAYS_YMD))) {
        return __wokl__::DAYS_YMD->__getfast__(days);
    }
    else {
        return __wokl__::DAYS_YMD->__getfast__((-__ss_int(1)));
    }
    return 0;
}

__ss_int shift_months(__ss_int ymd, __ss_int n) {
    __ss_int d, m, maanden, month, y, year;

    y = __floordiv(ymd,__ss_int(10000));
    m = __mods(__floordiv(ymd,__ss_int(100)), __ss_int(100));
    d = __mods(ymd, __ss_int(100));
    maanden = (((__ss_int(12)*y)+(m-__ss_int(1)))+n);
    year = __floordiv(maanden,__ss_int(12));
    month = (__mods(maanden, __ss_int(12))+__ss_int(1));
    return (((__ss_int(10000)*year)+(__ss_int(100)*month))+d);
}

__ss_int shift_days(__ss_int ymd, __ss_int n) {
    return get_ymd((get_days(ymd)+n));
}

/**
class Groep
*/

class_ *cl_Groep;

void *Groep::__init__(dict<tuple2<__ss_int, str *> *, Patient *> *dikkie) {
    this->data = dikkie;
    return NULL;
}

/**
class ATC
*/

class_ *cl_ATC;

void *ATC::__init__(str *code) {
    this->code = code;
    this->atc1 = code->__slice__(__ss_int(2), __ss_int(0), __ss_int(1), __ss_int(0));
    this->atc2 = code->__slice__(__ss_int(2), __ss_int(0), __ss_int(3), __ss_int(0));
    this->atc3 = code->__slice__(__ss_int(2), __ss_int(0), __ss_int(4), __ss_int(0));
    this->atc4 = code->__slice__(__ss_int(2), __ss_int(0), __ss_int(5), __ss_int(0));
    this->mgroepen = (__ss_list<MiddelGroep *>());
    return NULL;
}

void *ATC::add_mgroep(MiddelGroep *mgroep) {
    (this->mgroepen)->append(mgroep);
    return NULL;
}

void *ATC::clear_mgroepen() {
    (this->mgroepen)->clear();
    return NULL;
}

void *set_atcs(list<str *> *codes) {
    str *code;
    ATC *atc;
    __ss_int __16, __21, __25, __26, i;
    list<str *> *__14;
    __iter<str *> *__15;
    list<str *>::for_in_loop __17;
    tuple2<str *, ATC *> *__18;
    __iter<tuple2<str *, ATC *> *> *__19, *__20;
    __iter<tuple2<str *, ATC *> *>::for_in_loop __22;
    __GC_DICT<str *, ATC *>::iterator __23;
    dict<str *, ATC *> *__24;

    g_atcs = (new dict<str *, ATC *>());

    FOR_IN(code,codes,14,16,17)
        __wokl__::g_atcs->__setitem__(code, (new ATC(code)));
    END_FOR

    g_code_atcs = (new __collections__::defaultdict<str *, set<ATC *> *>(__lambda0__));

    FOR_IN_DICT(__wokl__::g_atcs,24,23,21)
        code = (*__23).first;
        atc = (*__23).second;
        __23++;

        FAST_FOR(i,__ss_int(1),(len(code)+__ss_int(1)),1,25,26)
            (__wokl__::g_code_atcs->__getitem__(code->__slice__(__ss_int(2), __ss_int(0), i, __ss_int(0))))->add(atc);
        END_FOR

    END_FOR

    return NULL;
}

void *set_pref_beleid(dict<tuple<__ss_int> *, list<tuple<__ss_int> *> *> *pref) {
    g_pref_beleid = pref;
    return NULL;
}

void *set_atc5_naam(dict<str *, str *> *atc5_naam) {
    g_atc5_naam = atc5_naam;
    return NULL;
}

/**
class Artikel
*/

class_ *cl_Artikel;

void *Artikel::__init__(__ss_int nr, str *atc, __ss_int farmaceutische_vorm_code, __ss_int toedieningsweg_code, __ss_int prk, __ss_int gpk, __ss_int hpk, __ss_float ddd, __ss_int inkoopkanaal, str *naam) {
    this->nr = nr;
    this->_atc = __wokl__::g_atcs->get(atc);
    this->farmaceutische_vorm_code = farmaceutische_vorm_code;
    this->toedieningsweg_code = toedieningsweg_code;
    this->prk = prk;
    this->gpk = gpk;
    this->hpk = hpk;
    this->ddd = ddd;
    this->inkoopkanaal = inkoopkanaal;
    this->naam = naam;
    return NULL;
}

/**
class Recept
*/

class_ *cl_Recept;

void *Recept::__init__(Artikel *artikel, __ss_int datum, __ss_int einddatum, __ss_int aantaldagen, __ss_bool standaard_periode, __ss_int modulaire_tariefcode, __ss_int zorgverzekeraar, __ss_int statuswtg, __ss_float hoeveelheid, __ss_int sv, __ss_float ddd, __ss_float hoeveelheidperdag, __ss_float pufjes, __ss_int agb) {
    this->artikel = artikel;
    this->datum = datum;
    this->einddatum = einddatum;
    this->standaard_periode = standaard_periode;
    this->modulaire_tariefcode = modulaire_tariefcode;
    this->zorgverzekeraar = zorgverzekeraar;
    this->statuswtg = statuswtg;
    this->hoeveelheid = hoeveelheid;
    this->sv = sv;
    this->ddd = ddd;
    this->hoeveelheidperdag = hoeveelheidperdag;
    this->aantaldagen = aantaldagen;
    this->pufjes = pufjes;
    this->agb = agb;
    return NULL;
}

/**
class Verstrekking
*/

class_ *cl_Verstrekking;

void *Verstrekking::__init__(Recept *recept) {
    this->recept = recept;
    this->_atc = (recept->artikel)->_atc;
    this->datum = recept->datum;
    this->einddatum = recept->einddatum;
    this->ddd = recept->ddd;
    return NULL;
}

/**
class Patient
*/

class_ *cl_Patient;

void *Patient::__init__(__ss_int nawnr, str *patientnr, str *geslacht, __ss_int geboortejaar, list<Verstrekking *> *vrsn, __ss_int einddatum) {
    this->nawnr = nawnr;
    this->patientnr = patientnr;
    this->geslacht = geslacht;
    this->geboortejaar = geboortejaar;
    this->vrsn = vrsn;
    this->month_idx = list_comp_1(einddatum, vrsn);
    this->indexed = False;
    this->_passant_cache = (new dict<__ss_int, __ss_int>());
    this->_fout_cache = (new dict<__ss_int, __ss_int>());
    return NULL;
}

__ss_bool Patient::is_passant(__ss_int einddatum) {
    /**
    let op, 2 jaar aan data benodigd!
    */
    __ss_int datum_a, datum_b, i1, i2, result;
    dict<__ss_int, __ss_int> *__29;

    result = (this->_passant_cache)->get(einddatum, (-__ss_int(1)));
    if ((result!=(-__ss_int(1)))) {
        return ___bool(result);
    }
    if (__eq(this->patientnr, const_1)) {
        return True;
    }
    i1 = (this->month_idx)->__getfast__(__ss_int(24));
    i2 = (this->month_idx)->__getfast__(__ss_int(0));
    if ((i1==i2)) {
        result = __ss_int(0);
    }
    else {
        datum_a = ((this->vrsn)->__getfast__((i2-__ss_int(1))))->datum;
        datum_b = ((this->vrsn)->__getfast__(i1))->datum;
        result = __int(___bool(((get_days(datum_a)-get_days(datum_b))<=__ss_int(4))));
    }
    this->_passant_cache->__setitem__(einddatum, result);
    return ___bool(result);
}

__ss_bool Patient::is_fout(__ss_int einddatum) {
    /**
    let op, 1 jaar aan data benodigd!
    */
    __ss_int __32, __33, __34, i, idx_eind, idx_jaar, idx_maand, result, year;
    __ss_bool __30, __31, ongeldige_zorgverzekeraar;
    Verstrekking *vrs;
    dict<__ss_int, __ss_int> *__35;

    result = (this->_fout_cache)->get(einddatum, (-__ss_int(1)));
    if ((result!=(-__ss_int(1)))) {
        return ___bool(result);
    }
    result = __ss_int(0);
    year = __floordiv(einddatum,__ss_int(10000));
    if (__eq(this->geslacht, const_3)) {
        result = __ss_int(1);
    }
    else if ((((year-this->geboortejaar)>__ss_int(110)) or ((year-this->geboortejaar)<__ss_int(0)))) {
        result = __ss_int(1);
    }
    else {
        idx_eind = (this->month_idx)->__getfast__(__ss_int(0));
        idx_maand = (this->month_idx)->__getfast__(__ss_int(1));
        idx_jaar = (this->month_idx)->__getfast__(__ss_int(12));
        ongeldige_zorgverzekeraar = True;

        FAST_FOR(i,idx_jaar,idx_eind,1,32,33)
            vrs = (this->vrsn)->__getfast__(i);
            if ((!__eq(__34=(vrs->recept)->zorgverzekeraar,__ss_int(9999)) && !__eq(__34,__ss_int(9998)))) {
                ongeldige_zorgverzekeraar = False;
                break;
            }
        END_FOR

        if (ongeldige_zorgverzekeraar) {
            result = __ss_int(1);
        }
        else if (((idx_eind-idx_maand)>__ss_int(100))) {
            result = __ss_int(1);
        }
        else if (((idx_eind-idx_jaar)>__ss_int(1000))) {
            result = __ss_int(1);
        }
    }
    this->_fout_cache->__setitem__(einddatum, result);
    return ___bool(result);
}

__ss_bool Patient::is_recent(__ss_int einddatum) {
    return ___bool(((this->month_idx)->__getfast__(__ss_int(4))!=(this->month_idx)->__getfast__(__ss_int(0))));
}

__ss_int Patient::leeftijd(__ss_int einddatum) {
    __ss_int year;

    year = __floordiv(einddatum,__ss_int(10000));
    if ((__mods(einddatum, __ss_int(1000))==__ss_int(101))) {
        year = (year-__ss_int(1));
    }
    return (year-this->geboortejaar);
}

/**
class Middel
*/

class_ *cl_Middel;

void *Middel::__init__(str *naam, str *omschrijving, str *atc_wel, str *atc_niet, str *farm_vorm, str *niet_farm_vorm, str *toedieningsweg, str *niet_toedieningsweg, str *prk, str *prk_niet, str *gpk, str *gpk_niet, str *hpk, str *hpk_niet) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->atc_wel = ((___bool(atc_wel))?((atc_wel->upper())->split(NULL, (-__ss_int(1)))):(NULL));
    this->atc_niet = ((___bool(atc_niet))?((atc_niet->upper())->split(NULL, (-__ss_int(1)))):(NULL));
    this->farm_vorm = ((___bool(farm_vorm))?(list_comp_2(farm_vorm)):(NULL));
    this->niet_farm_vorm = ((___bool(niet_farm_vorm))?(list_comp_3(niet_farm_vorm)):(NULL));
    this->toedieningsweg = ((___bool(toedieningsweg))?(list_comp_4(toedieningsweg)):(NULL));
    this->niet_toedieningsweg = ((___bool(niet_toedieningsweg))?(list_comp_5(niet_toedieningsweg)):(NULL));
    this->hpk = ((___bool(hpk))?(list_comp_6(hpk)):(NULL));
    this->niet_hpk = ((___bool(hpk_niet))?(list_comp_7(hpk_niet)):(NULL));
    this->prk = ((___bool(prk))?(list_comp_8(prk)):(NULL));
    this->niet_prk = ((___bool(prk_niet))?(list_comp_9(prk_niet)):(NULL));
    this->gpk = ((___bool(gpk))?(list_comp_10(gpk)):(NULL));
    this->niet_gpk = ((___bool(gpk_niet))?(list_comp_11(gpk_niet)):(NULL));
    return NULL;
}

/**
class MiddelGroep
*/

class_ *cl_MiddelGroep;

void *MiddelGroep::__init__(str *naam, str *omschrijving, list<Middel *> *middelen) {
    Middel *middel;
    list<__ss_int> *__100, *__101, *__102, *__103, *__104, *__105, *__96, *__97, *__98, *__99;

    this->naam = naam;
    this->omschrijving = omschrijving;
    this->middelen = middelen;
    this->vrsn = (__ss_list<Verstrekking *>());
    ASSERT(___bool((len(middelen)==__ss_int(1))), 0);
    middel = middelen->__getfast__(__ss_int(0));
    this->fast_contains = True;
    if ((___bool(middel->hpk) or ___bool(middel->niet_hpk) or ___bool(middel->prk) or ___bool(middel->niet_prk) or ___bool(middel->gpk) or ___bool(middel->niet_gpk) or ___bool(middel->farm_vorm) or ___bool(middel->niet_farm_vorm) or ___bool(middel->toedieningsweg) or ___bool(middel->niet_toedieningsweg))) {
        this->fast_contains = False;
    }
    this->atc_wel = middel->atc_wel;
    this->atc_niet = middel->atc_niet;
    this->farm_vorm = middel->farm_vorm;
    this->niet_farm_vorm = middel->niet_farm_vorm;
    this->toedieningsweg = middel->toedieningsweg;
    this->niet_toedieningsweg = middel->niet_toedieningsweg;
    this->hpk = middel->hpk;
    this->niet_hpk = middel->niet_hpk;
    this->prk = middel->prk;
    this->niet_prk = middel->niet_prk;
    this->gpk = middel->gpk;
    this->niet_gpk = middel->niet_gpk;
    return NULL;
}

__ss_bool MiddelGroep::__contains__(Verstrekking *vrs) {
    str *code;
    __ss_bool match;
    pyobj *__106, *__107, *__108, *__109, *__110, *__111, *__112, *__113, *__114, *__115, *__120, *__121, *__122, *__123, *__124, *__125, *__130, *__131, *__136, *__137, *__138, *__139, *__140, *__141;
    list<str *> *__116, *__132;
    __iter<str *> *__117, *__133;
    __ss_int __118, __134;
    list<str *>::for_in_loop __119, __135;
    list<pyobj *> *__126, *__127, *__128, *__129;

    if ((___bool(this->farm_vorm) and (!(this->farm_vorm)->__contains__(((vrs->recept)->artikel)->farmaceutische_vorm_code)))) {
        return False;
    }
    if ((___bool(this->niet_farm_vorm) and (this->niet_farm_vorm)->__contains__(((vrs->recept)->artikel)->farmaceutische_vorm_code))) {
        return False;
    }
    if ((___bool(this->toedieningsweg) and (!(this->toedieningsweg)->__contains__(((vrs->recept)->artikel)->toedieningsweg_code)))) {
        return False;
    }
    if ((___bool(this->niet_toedieningsweg) and (this->niet_toedieningsweg)->__contains__(((vrs->recept)->artikel)->toedieningsweg_code))) {
        return False;
    }
    if ((___bool(this->atc_niet) and ___bool(vrs->_atc))) {

        FOR_IN(code,this->atc_niet,116,118,119)
            if (((vrs->_atc)->code)->startswith(code)) {
                return False;
            }
        END_FOR

    }
    if ((___bool(this->niet_gpk) and (this->niet_gpk)->__contains__(((vrs->recept)->artikel)->gpk))) {
        return False;
    }
    if ((___bool(this->niet_prk) and (this->niet_prk)->__contains__(((vrs->recept)->artikel)->prk))) {
        return False;
    }
    if ((___bool(this->niet_hpk) and (this->niet_hpk)->__contains__(((vrs->recept)->artikel)->hpk))) {
        return False;
    }
    if ((___bool(this->atc_wel) or ___bool(this->hpk) or ___bool(this->prk) or ___bool(this->gpk))) {
        match = False;
        if ((___bool(this->atc_wel) and ___bool(vrs->_atc))) {

            FOR_IN(code,this->atc_wel,132,134,135)
                if (((vrs->_atc)->code)->startswith(code)) {
                    match = True;
                }
            END_FOR

        }
        if ((___bool(this->hpk) and (this->hpk)->__contains__(((vrs->recept)->artikel)->hpk))) {
            match = True;
        }
        if ((___bool(this->prk) and (this->prk)->__contains__(((vrs->recept)->artikel)->prk))) {
            match = True;
        }
        if ((___bool(this->gpk) and (this->gpk)->__contains__(((vrs->recept)->artikel)->gpk))) {
            match = True;
        }
        if (__NOT(match)) {
            return False;
        }
    }
    return True;
}

/**
class Marker
*/

class_ *cl_Marker;

void *Marker::__init__(__ss_int i, __ss_int datum, __ss_int add, __ss_int add_verplicht) {
    this->i = i;
    this->datum = datum;
    this->add = add;
    this->add_verplicht = add_verplicht;
    return NULL;
}

/**
class Period
*/

class_ *cl_Period;

void *Period::__init__(__ss_int start, __ss_int eind) {
    this->start = start;
    this->eind = eind;
    return NULL;
}

list<Period *> *vrs_gebruik(list<Verstrekking *> *vrsn, __ss_int start, __ss_int eind) {
    if (__NOT(___bool(vrsn))) {
        return ((list<Period *> *)(__wokl__::NO_PERIODS));
    }
    return vrs_interactie((new list<list<Verstrekking *> *>(1,vrsn)), start, eind, (-__ss_int(1)), default_17);
}

list<Period *> *vrs_interactie(list<list<Verstrekking *> *> *vrsnn, __ss_int startdatum, __ss_int einddatum, __ss_int minimum, list<list<Verstrekking *> *> *vrsnn_verplicht) {
    __ss_int __144, __148, __153, __158, __163, __165, __166, __167, count, count_verplicht, datum, eind, i, iets, j, start, total;
    list<Verstrekking *> *__156, *vrsn;
    list<Period *> *periods;
    list<Marker *> *markers;
    __ss_bool __160, __161, __168, __169, __170, __171, __172, __173, __174, __175, nu_overlap, overlap, verplicht;
    Verstrekking *vrs;
    list<__ss_int> *__162, *__164, *counts, *counts_verplicht;
    list<list<Verstrekking *> *> *__142, *__146, *__154;
    __iter<list<Verstrekking *> *> *__143, *__147;
    list<list<Verstrekking *> *>::for_in_loop __145, __149;
    tuple2<__ss_int, list<Verstrekking *> *> *__150;
    __iter<tuple2<__ss_int, list<Verstrekking *> *> *> *__151, *__152;
    __iter<tuple2<__ss_int, list<Verstrekking *> *> *>::for_in_loop __155;
    __iter<Verstrekking *> *__157;
    list<Verstrekking *>::for_in_loop __159;

    total = (len(vrsnn)+len(vrsnn_verplicht));
    if ((minimum==(-__ss_int(1)))) {
        minimum = total;
    }
    iets = __ss_int(0);

    FOR_IN(vrsn,vrsnn,142,144,145)
        if (___bool(vrsn)) {
            iets = (iets+__ss_int(1));
        }
    END_FOR


    FOR_IN(vrsn,vrsnn_verplicht,146,148,149)
        if (___bool(vrsn)) {
            iets = (iets+__ss_int(1));
        }
        else {
            return ((list<Period *> *)(__wokl__::NO_PERIODS));
        }
    END_FOR

    if ((iets<minimum)) {
        return ((list<Period *> *)(__wokl__::NO_PERIODS));
    }
    periods = (__ss_list<Period *>());
    vrsnn = (vrsnn_verplicht)->__add__(vrsnn);
    markers = (__ss_list<Marker *>());

    FOR_IN_ENUMERATE(vrsn,vrsnn,154,153)
        i = __153;
        verplicht = ___bool((i<len(vrsnn_verplicht)));

        FOR_IN(vrs,vrsn,156,158,159)
            markers->append((new Marker(i, vrs->datum, __ss_int(1), ((verplicht)?(__ss_int(1)):(__ss_int(0))))));
            markers->append((new Marker(i, vrs->einddatum, (-__ss_int(1)), ((verplicht)?((-__ss_int(1))):(__ss_int(0))))));
        END_FOR

    END_FOR

    markers->sort(__ss_int(0), __lambda1__, __ss_int(0));
    counts = ((new list<__ss_int>(1,__ss_int(0))))->__mul__(total);
    counts_verplicht = ((new list<__ss_int>(1,__ss_int(0))))->__mul__(total);
    i = __ss_int(0);
    overlap = False;

    while ((i<len(markers))) {
        datum = (markers->__getfast__(i))->datum;

        while (((i<len(markers)) and ((markers->__getfast__(i))->datum==datum))) {
            __162 = counts;
            __163 = (markers->__getfast__(i))->i;
            __162->__setitem__(__163, (__162->__getfast__(__163)+(markers->__getfast__(i))->add));
            __164 = counts_verplicht;
            __165 = (markers->__getfast__(i))->i;
            __164->__setitem__(__165, (__164->__getfast__(__165)+(markers->__getfast__(i))->add_verplicht));
            i = (i+__ss_int(1));
        }
        count = __ss_int(0);
        count_verplicht = __ss_int(0);

        FAST_FOR(j,0,total,1,166,167)
            if ((counts->__getfast__(j)>__ss_int(0))) {
                count = (count+__ss_int(1));
            }
            if ((counts_verplicht->__getfast__(j)>__ss_int(0))) {
                count_verplicht = (count_verplicht+__ss_int(1));
            }
        END_FOR

        nu_overlap = __AND(___bool((count>=minimum)), ___bool((count_verplicht==len(vrsnn_verplicht))), 168);
        if ((__NOT(overlap) and nu_overlap)) {
            start = datum;
        }
        else if ((overlap and __NOT(nu_overlap))) {
            if (((datum>startdatum) and (start<einddatum))) {
                start = ___max(2, __ss_int(0), start, startdatum);
                eind = ___min(2, __ss_int(0), datum, einddatum);
                periods->append((new Period(start, eind)));
            }
        }
        overlap = nu_overlap;
    }
    return periods;
}

__ss_int vrs_index(list<Verstrekking *> *recepten, __ss_int datum) {
    __ss_int __176, _hi, _lo, mid;

    __176 = len(recepten);
    _lo = __ss_int(0);
    _hi = __176;

    while ((_lo<_hi)) {
        mid = __floordiv((_lo+_hi),__ss_int(2));
        if (((recepten->__getfast__(mid))->datum<datum)) {
            _lo = (mid+__ss_int(1));
        }
        else {
            _hi = mid;
        }
    }
    return _lo;
}

list<Verstrekking *> *vrs_schuiven(list<Verstrekking *> *vrsn) {
    list<Verstrekking *> *__181, *result;
    __ss_int __180, days, i, laatst;
    Verstrekking *vrs, *vrs2;
    tuple2<__ss_int, Verstrekking *> *__177;
    __iter<tuple2<__ss_int, Verstrekking *> *> *__178, *__179;
    __iter<tuple2<__ss_int, Verstrekking *> *>::for_in_loop __182;
    __ss_bool __183, __184;

    result = vrsn->__slice__(__ss_int(0), __ss_int(0), __ss_int(0), __ss_int(0));

    FOR_IN_ENUMERATE(vrs,vrsn,181,180)
        i = __180;
        if (((i>__ss_int(0)) and (vrs->datum<laatst))) {
            vrs2 = (new Verstrekking(vrs->recept));
            days = (get_days(laatst)-get_days(vrs->datum));
            vrs2->datum = shift_days(vrs->datum, days);
            vrs2->einddatum = shift_days(vrs->einddatum, days);
            result->__setitem__(i, vrs2);
        }
        else {
            vrs2 = vrs;
        }
        laatst = vrs2->einddatum;
    END_FOR

    return result;
}

list<Verstrekking *> *vrs_correctie(list<Verstrekking *> *vrsn, str *nivo, str *atc_wissel) {
    dict<str *, list<Verstrekking *> *> *__191, *key_vrsn;
    list<Verstrekking *> *result;
    str *key;
    tuple2<str *, list<Verstrekking *> *> *__185;
    __iter<tuple2<str *, list<Verstrekking *> *> *> *__186, *__187;
    __ss_int __188;
    __iter<tuple2<str *, list<Verstrekking *> *> *>::for_in_loop __189;
    __GC_DICT<str *, list<Verstrekking *> *>::iterator __190;

    if ((nivo==NULL)) {
        return vrs_schuiven(vrsn);
    }
    key_vrsn = vrs_split(vrsn, nivo, atc_wissel);
    result = (__ss_list<Verstrekking *>());

    FOR_IN_DICT(key_vrsn,191,190,188)
        key = (*__190).first;
        vrsn = (*__190).second;
        __190++;
        result->extend(vrs_schuiven(vrsn));
    END_FOR

    result->sort(__ss_int(0), __lambda2__, __ss_int(0));
    return result;
}

dict<str *, list<Verstrekking *> *> *vrs_split(list<Verstrekking *> *vrsn, str *nivo, str *atc_wissel) {
    dict<str *, list<Verstrekking *> *> *key_vrsn;
    dict<str *, str *> *atc_map;
    str *__197, *atcs_term, *code;
    list<str *> *__192, *__198, *atcs;
    Verstrekking *vrs;
    ATC *atc;
    __iter<str *> *__193, *__199;
    __ss_int __194, __200, __204;
    list<str *>::for_in_loop __195, __201;
    void *__196;
    list<Verstrekking *> *__202;
    __iter<Verstrekking *> *__203;
    list<Verstrekking *>::for_in_loop __205;

    key_vrsn = (new dict<str *, list<Verstrekking *> *>());
    atc_map = NULL;
    if (___bool(atc_wissel)) {
        atc_map = (new dict<str *, str *>());

        FOR_IN(atcs_term,atc_wissel->split(NULL, (-__ss_int(1))),192,194,195)
            atcs = (atcs_term->upper())->split(const_4, (-__ss_int(1)));

            FOR_IN(code,atcs->__slice__(__ss_int(1), __ss_int(1), __ss_int(0), __ss_int(0)),198,200,201)
                atc_map->__setitem__(code, atcs->__getfast__(__ss_int(0)));
            END_FOR

        END_FOR

    }

    FOR_IN(vrs,vrsn,202,204,205)
        atc = ((vrs->recept)->artikel)->_atc;
        if (__eq(nivo, const_5)) {
            code = atc->atc1;
        }
        else if (__eq(nivo, const_6)) {
            code = atc->atc2;
        }
        else if (__eq(nivo, const_7)) {
            code = atc->atc3;
        }
        else if (__eq(nivo, const_8)) {
            code = atc->atc4;
        }
        else if (__eq(nivo, const_9)) {
            code = atc->code;
        }
        else {
            print(const_10, nivo);
            throw (new ValueError());
        }
        if (___bool(atc_wissel)) {
            code = atc_map->get(code, code);
        }
        if ((key_vrsn)->__contains__(code)) {
            (key_vrsn->__getitem__(code))->append(vrs);
        }
        else {
            key_vrsn->__setitem__(code, (new list<Verstrekking *>(1,vrs)));
        }
    END_FOR

    return key_vrsn;
}

__ss_int vrs_aantal(list<Verstrekking *> *_vrsn, __ss_int datum_begin, __ss_int datum_eind) {
    return (vrs_index(_vrsn, datum_eind)-vrs_index(_vrsn, datum_begin));
}

__ss_float vrs_gemiddeld_hulp(Verstrekking *vrs, str *soort_dosering) {
    if (__eq(soort_dosering, const_11)) {
        return vrs->ddd;
    }
    else if (__eq(soort_dosering, const_12)) {
        if (((((vrs->recept)->artikel)->_atc)->code)->startswith(const_13)) {
            return (vrs->recept)->pufjes;
        }
        return (vrs->recept)->hoeveelheid;
    }
    else if (__eq(soort_dosering, const_14)) {
        return ((__ss_float)((get_days(vrs->einddatum)-get_days(vrs->datum))));
    }
    else {
        ASSERT(False, 0);
    }
    return 0;
}

tuple2<__ss_float, __ss_int> *vrs_gemiddeld(list<Verstrekking *> *_vrsn, str *soort_dosering, __ss_int aantal_iets, str *vrs_of_dag, void *soort_periode, __ss_int start_periode, __ss_int eind_periode) {
    /**
    berekent gemiddelde van 'iets' tussen afleverdatum eerste en laatste voorschrift,
    met veel opties. correspondeert 1 op 1 met wokkel patient dosering criterium.
    */
    list<tuple2<__ss_int, __ss_float> *> *dos_per_iets;
    Verstrekking *vrs;
    __ss_float hoeveel, totaal;
    dict<__ss_int, __ss_float> *__214, *dag_totaal;
    __ss_int __208, __212, __215, __219, _dagen, dag;
    list<Verstrekking *> *__206, *__210;
    __iter<Verstrekking *> *__207, *__211;
    list<Verstrekking *>::for_in_loop __209, __213;
    list<__ss_int> *__217;
    __iter<__ss_int> *__218;
    list<__ss_int>::for_in_loop __220;

    dos_per_iets = (__ss_list<tuple2<__ss_int, __ss_float> *>());
    if (__eq(vrs_of_dag, const_16)) {

        FOR_IN(vrs,_vrsn,206,208,209)
            hoeveel = vrs_gemiddeld_hulp(vrs, soort_dosering);
            dos_per_iets->append((new tuple2<__ss_int, __ss_float>(2,vrs->datum,hoeveel)));
        END_FOR

    }
    else {
        dag_totaal = (new dict<__ss_int, __ss_float>());

        FOR_IN(vrs,_vrsn,210,212,213)
            hoeveel = vrs_gemiddeld_hulp(vrs, soort_dosering);
            try {
                dag_totaal->__addtoitem__(vrs->datum, hoeveel);
            } catch (KeyError *) {
                dag_totaal->__setitem__(vrs->datum, hoeveel);
            }
        END_FOR


        FOR_IN(dag,sorted(dag_totaal, __ss_int(0), __ss_int(0), __ss_int(0)),217,219,220)
            dos_per_iets->append((new tuple2<__ss_int, __ss_float>(2,dag,dag_totaal->__getitem__(dag))));
        END_FOR

    }
    if ((aantal_iets!=(-__ss_int(1)))) {
        if ((len(dos_per_iets)<aantal_iets)) {
            return NULL;
        }
        dos_per_iets = dos_per_iets->__slice__(__ss_int(1), (-aantal_iets), __ss_int(0), __ss_int(0));
    }
    totaal = __sum(list_comp_12(dos_per_iets));
    if (__eq(((str *)(soort_periode)), const_17)) {
        _dagen = (get_days(eind_periode)-get_days(dos_per_iets->__getfast__(__ss_int(0))->__getfirst__()));
    }
    else if (__eq(((str *)(soort_periode)), const_18)) {
        _dagen = (get_days(___max(1, __ss_int(0), list_comp_13(_vrsn)))-get_days(start_periode));
    }
    else {
        totaal = __sum(list_comp_14(dos_per_iets));
        _dagen = (get_days(dos_per_iets->__getfast__((-__ss_int(1)))->__getfirst__())-get_days(dos_per_iets->__getfast__(__ss_int(0))->__getfirst__()));
    }
    if ((_dagen==__ss_int(0))) {
        return NULL;
    }
    return (new tuple2<__ss_float, __ss_int>(2,totaal,_dagen));
}

/**
class Rapportage
*/

class_ *cl_Rapportage;

void *Rapportage::setup(list<MiddelGroep *> *mgroepen, list<VerstrekkingLijstCriterium *> *vrslijsten) {
    VerstrekkingLijstCriterium *vcrit;
    list<VerstrekkingLijstCriterium *> *__233;
    __iter<VerstrekkingLijstCriterium *> *__234;
    __ss_int __235;
    list<VerstrekkingLijstCriterium *>::for_in_loop __236;

    this->mgroepen = mgroepen;
    this->vrslijsten = vrslijsten;

    FOR_IN(vcrit,vrslijsten,233,235,236)
        vcrit->rapportage = this;
    END_FOR

    this->maanden = ___max(1, __ss_int(0), list_comp_15(vrslijsten));
    return NULL;
}

void *Rapportage::maak_index() {
    ATC *atc;
    set<ATC *> *__259, *niet, *wel;
    MiddelGroep *mgroep;
    str *atc_niet, *atc_wel;
    __iter<ATC *> *__241, *__242, *__260;
    __ss_int __243, __249, __253, __257, __261;
    __iter<ATC *>::for_in_loop __244;
    __GC_DICT<str *, ATC *>::iterator __245;
    dict<str *, ATC *> *__246;
    list<MiddelGroep *> *__247;
    __iter<MiddelGroep *> *__248;
    list<MiddelGroep *>::for_in_loop __250;
    list<str *> *__251, *__255;
    __iter<str *> *__252, *__256;
    list<str *>::for_in_loop __254, __258;
    set<ATC *>::for_in_loop __262;


    FOR_IN(atc,__wokl__::g_atcs->values(),241,243,244)
        atc->clear_mgroepen();
    END_FOR

    wel = (new set<ATC *>());
    niet = (new set<ATC *>());

    FOR_IN(mgroep,this->mgroepen,247,249,250)
        wel->clear();
        niet->clear();
        if (___bool(mgroep->atc_wel)) {

            FOR_IN(atc_wel,mgroep->atc_wel,251,253,254)
                wel->update(1, __wokl__::g_code_atcs->__getitem__(atc_wel));
            END_FOR

        }
        if (___bool(mgroep->atc_niet)) {

            FOR_IN(atc_niet,mgroep->atc_niet,255,257,258)
                niet->update(1, __wokl__::g_code_atcs->__getitem__(atc_niet));
            END_FOR

        }

        FOR_IN(atc,wel,259,261,262)
            if ((!(niet)->__contains__(atc))) {
                atc->add_mgroep(mgroep);
            }
        END_FOR

    END_FOR

    return NULL;
}

void *Rapportage::indexeer(Patient *p, __ss_int i1, __ss_int i2) {
    MiddelGroep *mgroep;
    __ss_int __265, __267, __268, __271, i;
    Verstrekking *vrs;
    list<MiddelGroep *> *__263, *__269, *mgroepen;
    __iter<MiddelGroep *> *__264, *__270;
    list<MiddelGroep *>::for_in_loop __266, __272;


    FOR_IN(mgroep,this->mgroepen,263,265,266)
        (mgroep->vrsn)->clear();
    END_FOR


    FAST_FOR(i,i1,i2,1,267,268)
        vrs = (p->vrsn)->__getfast__(i);
        if ((vrs->_atc!=NULL)) {
            mgroepen = (vrs->_atc)->mgroepen;

            FOR_IN(mgroep,mgroepen,269,271,272)
                (mgroep->vrsn)->append(vrs);
            END_FOR

        }
    END_FOR

    return NULL;
}

/**
class Indicator
*/

class_ *cl_Indicator;

void *Indicator::__init__(str *naam, str *omschrijving, PatientCriterium *teller_criterium, PatientCriterium *noemer_criterium, str *tonen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->teller = teller_criterium;
    this->noemer = noemer_criterium;
    return NULL;
}

/**
class Indicatoren
*/

class_ *cl_Indicatoren;

void *Indicatoren::__init__(str *naam, str *omschrijving, list<Indicator *> *lijst) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijst = lijst;
    return NULL;
}

/**
class IndicatorLijst
*/

class_ *cl_IndicatorLijst;

void *IndicatorLijst::__init__(str *naam, str *omschrijving, Indicatoren *indicatoren, PatientCriterium *patient_keuze, PatientCriterium *uitsluiten, str *verhaal, PatientInformatieInfo *info) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->patient_keuze = patient_keuze;
    this->uitsluiten = uitsluiten;
    ASSERT(___bool((len(indicatoren->lijst)==__ss_int(1))), 0);
    this->indicatoren = indicatoren;
    return NULL;
}

list<dict<str *, str *> *> *IndicatorLijst::__call__(Groep *groep, __ss_int einddatum) {
    list<dict<str *, str *> *> *result;
    __ss_int __275, patient_in_teller, terug;
    Patient *p;
    Indicator *indicator;
    __iter<Patient *> *__273, *__274;
    __iter<Patient *>::for_in_loop __276;
    __GC_DICT<tuple2<__ss_int, str *> *, Patient *>::iterator __277;
    dict<tuple2<__ss_int, str *> *, Patient *> *__278;
    __ss_bool __279, __280, __281, __282;

    result = (__ss_list<dict<str *, str *> *>());
    this->maak_index();
    terug = shift_months(einddatum, (-this->maanden));

    FOR_IN(p,(groep->data)->values(),273,275,276)
        p->indexed = False;
        if (((this->uitsluiten!=NULL) and this->uitsluiten->__call__(p, einddatum))) {
            continue;
        }
        if (((this->patient_keuze!=NULL) and __NOT(this->patient_keuze->__call__(p, einddatum)))) {
            continue;
        }
        indicator = ((this->indicatoren)->lijst)->__getfast__(__ss_int(0));
        if (indicator->noemer->__call__(p, einddatum)) {
            patient_in_teller = __ss_int(0);
            if (indicator->teller->__call__(p, einddatum)) {
                patient_in_teller = __ss_int(1);
            }
            result->append((new dict<str *, str *>(2, (new tuple<str *>(2,const_19,p->patientnr)),(new tuple<str *>(2,const_20,__str(patient_in_teller))))));
        }
    END_FOR

    return result;
}

/**
class PatientOverzicht
*/

class_ *cl_PatientOverzicht;

void *PatientOverzicht::__init__(str *naam, str *omschrijving, PatientCriterium *selectie, PatientCriterium *exclusie, PatientInformatieInfo *info) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->selectie = selectie;
    this->exclusie = exclusie;
    this->_info = info;
    return NULL;
}

list<dict<str *, str *> *> *PatientOverzicht::__call__(Groep *groep, __ss_int einddatum) {
    list<dict<str *, str *> *> *result;
    Patient *p;
    PatientInfo *info;
    __iter<Patient *> *__283, *__284;
    __ss_int __285, __295;
    __iter<Patient *>::for_in_loop __286;
    __GC_DICT<tuple2<__ss_int, str *> *, Patient *>::iterator __287;
    dict<tuple2<__ss_int, str *> *, Patient *> *__288;
    __ss_bool __289, __290, __291, __292;
    list<PatientInfo *> *__293;
    __iter<PatientInfo *> *__294;
    list<PatientInfo *>::for_in_loop __296;
    str *__297, *__298;

    result = (__ss_list<dict<str *, str *> *>());
    this->maak_index();

    FOR_IN(p,(groep->data)->values(),283,285,286)
        p->indexed = False;
        if (((this->exclusie!=NULL) and this->exclusie->__call__(p, einddatum))) {
            continue;
        }
        if (((this->selectie!=NULL) and __NOT(this->selectie->__call__(p, einddatum)))) {
            continue;
        }

        FOR_IN(info,(this->_info)->lijst,293,295,296)
            result->append((new dict<str *, str *>(4, (new tuple<str *>(2,const_21,__str(p->nawnr))),(new tuple<str *>(2,const_19,p->patientnr)),(new tuple<str *>(2,const_22,info->naam)),(new tuple<str *>(2,const_23,__OR(info->__call__(p, einddatum), const_24, 297))))));
        END_FOR

    END_FOR

    return result;
}

/**
class CorrectieTerm
*/

class_ *cl_CorrectieTerm;

void *CorrectieTerm::__init__(str *naam, str *omschrijving, str *opties, str *waarden, __ss_int vaste_periode, __ss_float ddd_factor) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->opties = opties;
    this->waarden = ((___bool(waarden))?((waarden->upper())->split(NULL, (-__ss_int(1)))):(NULL));
    this->vaste_periode = vaste_periode;
    this->ddd_factor = ddd_factor;
    return NULL;
}

/**
class Correctie
*/

class_ *cl_Correctie;

void *Correctie::__init__(str *naam, str *omschrijving, str *nivo, __ss_int standaard_periode, __ss_float ddd_factor, __ss_int vaste_periode, __ss_int vaste_verlenging, __ss_float gmddd_van, __ss_float gmddd_tot, str *atc_wissel, list<CorrectieTerm *> *correctietermen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->nivo = nivo;
    this->standaard_periode = standaard_periode;
    this->ddd_factor = ddd_factor;
    this->vaste_periode = vaste_periode;
    this->vaste_verlenging = vaste_verlenging;
    this->gmddd_van = gmddd_van;
    this->gmddd_tot = gmddd_tot;
    this->atc_wissel = atc_wissel;
    this->correctietermen = correctietermen;
    return NULL;
}

/**
class VerstrekkingCriterium
*/

class_ *cl_VerstrekkingCriterium;

/**
class VerstrekkingEigenschappen
*/

class_ *cl_VerstrekkingEigenschappen;

void *VerstrekkingEigenschappen::__init__(str *naam, str *omschrijving, str *wmg, str *voorschrijver, str *modulairetariefcode, MiddelGroep *middelgroep, __ss_float ddd_van, __ss_float ddd_tot, __ss_float ddd_per_dag_van, __ss_float ddd_per_dag_tot, __ss_int dagen_van, __ss_int dagen_tot, str *zorgverzekeraar, str *inkoopkanaal_naam, str *preferente_middelen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->wmg = wmg;
    this->voorschrijver = voorschrijver;
    this->middelgroep = middelgroep;
    this->modulaire_tariefcode = ((___bool(modulairetariefcode))?(list_comp_16(modulairetariefcode)):(NULL));
    this->ddd_van = ddd_van;
    this->ddd_tot = ddd_tot;
    this->ddd_per_dag_van = ddd_per_dag_van;
    this->ddd_per_dag_tot = ddd_per_dag_tot;
    this->dagen_van = dagen_van;
    this->dagen_tot = dagen_tot;
    this->zorgverzekeraar = ((___bool(zorgverzekeraar))?(list_comp_17(zorgverzekeraar)):(NULL));
    this->inkoopkanaal_naam = inkoopkanaal_naam;
    this->preferente_middelen = preferente_middelen;
    return NULL;
}

__ss_bool VerstrekkingEigenschappen::__call__(Verstrekking *vrs) {
    __ss_int __321, __345, artikelnr, dagen, jaar, maand;
    __ss_float __333, __334, ddd_per_dag;
    pyobj *__311, *__312;
    __ss_bool __313, __314, __315, __316, __317, __318, __319, __320, __322, __323, __324, __325, __326, __327, __328, __329, __330, __331, __332, __335, __336, __337, __338, __339, __340, __341, __342, __343, __344;

    if ((___bool(this->middelgroep) and (!(this->middelgroep)->__contains__(vrs)))) {
        return False;
    }
    if (___bool(this->wmg)) {
        if ((__eq(this->wmg, const_25) and ((vrs->recept)->statuswtg!=__ss_int(1)))) {
            return False;
        }
        else if ((__eq(this->wmg, const_26) and ((vrs->recept)->statuswtg==__ss_int(1)))) {
            return False;
        }
    }
    if (___bool(this->voorschrijver)) {
        if (((__eq(this->voorschrijver, const_27) and ((vrs->recept)->sv!=__ss_int(1))) or (__eq(this->voorschrijver, const_28) and (!__eq(__321=(vrs->recept)->sv,__ss_int(3)) && !__eq(__321,__ss_int(6)) && !__eq(__321,__ss_int(9)))) or (__eq(this->voorschrijver, const_29) and ((vrs->recept)->sv==__ss_int(1))))) {
            return False;
        }
    }
    if (___bool(this->modulaire_tariefcode)) {
        if ((!(this->modulaire_tariefcode)->__contains__((vrs->recept)->modulaire_tariefcode))) {
            return False;
        }
    }
    if (___bool(this->zorgverzekeraar)) {
        if ((!(this->zorgverzekeraar)->__contains__((vrs->recept)->zorgverzekeraar))) {
            return False;
        }
    }
    if (((this->ddd_van!=((__ss_float)((-__ss_int(1))))) and (vrs->ddd<this->ddd_van))) {
        return False;
    }
    if (((this->ddd_tot!=((__ss_float)((-__ss_int(1))))) and (vrs->ddd>=this->ddd_tot))) {
        return False;
    }
    if (((this->ddd_per_dag_van!=((__ss_float)((-__ss_int(1))))) or (this->ddd_per_dag_tot!=((__ss_float)((-__ss_int(1))))))) {
        dagen = (get_days(vrs->einddatum)-get_days(vrs->datum));
        if ((dagen and ___bool(vrs->ddd))) {
            ddd_per_dag = (vrs->ddd/dagen);
            if (((this->ddd_per_dag_van!=(-__ss_float(1.0))) and (ddd_per_dag<this->ddd_per_dag_van))) {
                return False;
            }
            if (((this->ddd_per_dag_tot!=(-__ss_float(1.0))) and (ddd_per_dag>=this->ddd_per_dag_tot))) {
                return False;
            }
        }
        else {
            return False;
        }
    }
    if (((this->dagen_van!=(-__ss_int(1))) or (this->dagen_tot!=(-__ss_int(1))))) {
        dagen = (get_days(vrs->einddatum)-get_days(vrs->datum));
        if (((this->dagen_van!=(-__ss_int(1))) and (dagen<this->dagen_van))) {
            return False;
        }
        if (((this->dagen_tot!=(-__ss_int(1))) and (dagen>=this->dagen_tot))) {
            return False;
        }
    }
    if (___bool(this->inkoopkanaal_naam)) {
        ASSERT(___bool(__eq(this->inkoopkanaal_naam, const_30)), 0);
        if ((!__eq(__345=((vrs->recept)->artikel)->inkoopkanaal,__ss_int(2)) && !__eq(__345,__ss_int(4)))) {
            return False;
        }
    }
    if (___bool(this->preferente_middelen)) {
        ASSERT(___bool(__eq(this->preferente_middelen, const_25)), 0);
        jaar = __floordiv(vrs->datum,__ss_int(10000));
        maand = __mods(__floordiv(vrs->datum,__ss_int(100)), __ss_int(100));
        artikelnr = ((vrs->recept)->artikel)->nr;
        if (__NOT((__wokl__::g_pref_beleid->__getitem__((__ss_tuple_int(2,jaar,maand))))->__contains__((__ss_tuple_int(2,artikelnr,(vrs->recept)->zorgverzekeraar))))) {
            return False;
        }
    }
    return True;
}

/**
class VerstrekkingLogischTerm
*/

class_ *cl_VerstrekkingLogischTerm;

void *VerstrekkingLogischTerm::__init__(str *naam, str *omschrijving, str *welniet, VerstrekkingCriterium *criterium) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->welniet = ___bool(__eq(welniet, const_31));
    this->criterium = criterium;
    return NULL;
}

__ss_bool VerstrekkingLogischTerm::__call__(Verstrekking *vrs) {
    if (this->welniet) {
        return this->criterium->__call__(vrs);
    }
    else {
        return __NOT(this->criterium->__call__(vrs));
    }
    return False;
}

/**
class VerstrekkingLogisch
*/

class_ *cl_VerstrekkingLogisch;

void *VerstrekkingLogisch::__init__(str *naam, str *omschrijving, str *enof, list<VerstrekkingLogischTerm *> *termen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->of = ___bool(__eq(enof, const_32));
    this->termen = termen;
    return NULL;
}

__ss_bool VerstrekkingLogisch::__call__(Verstrekking *vrs) {
    VerstrekkingLogischTerm *term;
    list<VerstrekkingLogischTerm *> *__346, *__350;
    __iter<VerstrekkingLogischTerm *> *__347, *__351;
    __ss_int __348, __352;
    list<VerstrekkingLogischTerm *>::for_in_loop __349, __353;

    if (this->of) {

        FOR_IN(term,this->termen,346,348,349)
            if (term->__call__(vrs)) {
                return True;
            }
        END_FOR

        return False;
    }
    else {

        FOR_IN(term,this->termen,350,352,353)
            if (__NOT(term->__call__(vrs))) {
                return False;
            }
        END_FOR

        return True;
    }
    return False;
}

/**
class VerstrekkingLijstCriterium
*/

class_ *cl_VerstrekkingLijstCriterium;

void *VerstrekkingLijstCriterium::setup_einddatum(__ss_int einddatum) {
    return NULL;
}

/**
class VerstrekkingLijstEigenschappen
*/

class_ *cl_VerstrekkingLijstEigenschappen;

void *VerstrekkingLijstEigenschappen::__init__(str *naam, str *omschrijving, MiddelGroep *middelgroep, Correctie *correctie, __ss_int datum_tot, __ss_int datum_van, VerstrekkingCriterium *verstrekking) {
    __ss_bool __354, __355, __356, __357, __358, __359;

    this->naam = naam;
    this->omschrijving = omschrijving;
    this->middelgroep = middelgroep;
    this->datum_tot = datum_tot;
    this->datum_van = datum_van;
    this->_correctie = correctie;
    this->verstrekking = verstrekking;
    this->vrsn = (__ss_list<Verstrekking *>());
    this->vrsn_temp = (__ss_list<Verstrekking *>());
    this->slow_check = __AND(___bool(middelgroep), __OR(__NOT(___bool(middelgroep->atc_wel)), __OR(___bool(middelgroep->hpk), __OR(___bool(middelgroep->prk), ___bool(middelgroep->gpk), 357), 356), 355), 354);
    return NULL;
}

void *VerstrekkingLijstEigenschappen::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

Verstrekking *VerstrekkingLijstEigenschappen::corrigeer(Verstrekking *vrs) {
    Correctie *correctie;
    __ss_float __360, __361, __371, __372, ddd, gmddd_tot, gmddd_van;
    __ss_int __375, aantaldagen, einddatum;
    list<CorrectieTerm *> *__373, *correctietermen;
    CorrectieTerm *term;
    __ss_bool __362, __363, __364, __365, __366, __367, __368, __369, __370, __393, __394, uitzondering;
    list<str *> *waarden;
    str *atc5, *opties;
    __iter<CorrectieTerm *> *__374;
    list<CorrectieTerm *>::for_in_loop __376;

    correctie = this->_correctie;
    __360 = correctie->gmddd_van;
    __361 = correctie->gmddd_tot;
    gmddd_van = __360;
    gmddd_tot = __361;
    aantaldagen = (vrs->recept)->aantaldagen;
    if (((gmddd_van!=(-__ss_float(1.0))) or (gmddd_tot!=(-__ss_float(1.0))))) {
        if ((__NOT(___bool((vrs->recept)->hoeveelheidperdag)) or ((gmddd_van!=(-__ss_float(1.0))) and __NOT((gmddd_van<=(vrs->recept)->hoeveelheidperdag))) or ((gmddd_tot!=(-__ss_float(1.0))) and __NOT(((vrs->recept)->hoeveelheidperdag<=gmddd_tot))))) {
            aantaldagen = __int(((vrs->recept)->hoeveelheid*__OR(((vrs->recept)->artikel)->ddd, ((__ss_float)(__ss_int(1))), 371)));
        }
    }
    if ((correctie->vaste_periode!=(-__ss_int(1)))) {
        aantaldagen = correctie->vaste_periode;
    }
    else if (aantaldagen) {
    }
    else if ((correctie->standaard_periode!=(-__ss_int(1)))) {
        aantaldagen = correctie->standaard_periode;
    }
    else {
        aantaldagen = __ss_int(1);
    }
    if ((correctie->vaste_verlenging!=(-__ss_int(1)))) {
        aantaldagen = (aantaldagen+correctie->vaste_verlenging);
    }
    ddd = (vrs->ddd*correctie->ddd_factor);
    correctietermen = correctie->correctietermen;
    if (___bool(correctietermen)) {

        FOR_IN(term,correctietermen,373,375,376)
            uitzondering = False;
            waarden = term->waarden;
            if (__NOT(___bool(waarden))) {
                continue;
            }
            opties = term->opties;
            if (__eq(opties, const_33)) {
                atc5 = (((vrs->recept)->artikel)->_atc)->code;
                uitzondering = ___bool(list_comp_18(waarden, atc5));
            }
            else if (__eq(opties, const_34)) {
                uitzondering = ___bool((list_comp_19(waarden))->__contains__(((vrs->recept)->artikel)->hpk));
            }
            else if (__eq(opties, const_35)) {
                uitzondering = ___bool((list_comp_20(waarden))->__contains__(((vrs->recept)->artikel)->prk));
            }
            else if (__eq(opties, const_36)) {
                uitzondering = ___bool((list_comp_21(waarden))->__contains__(((vrs->recept)->artikel)->gpk));
            }
            if (uitzondering) {
                if ((term->vaste_periode!=(-__ss_int(1)))) {
                    aantaldagen = term->vaste_periode;
                }
                ddd = (term->ddd_factor*(vrs->recept)->ddd);
            }
        END_FOR

    }
    einddatum = shift_days(vrs->datum, aantaldagen);
    if (((einddatum!=vrs->einddatum) or (ddd!=vrs->ddd))) {
        vrs = (new Verstrekking(vrs->recept));
        vrs->einddatum = einddatum;
        vrs->ddd = ddd;
    }
    return vrs;
}

void *VerstrekkingLijstEigenschappen::bepaal(Patient *p, __ss_int einddatum) {
    MiddelGroep *middelgroep;
    __ss_int __395, __396, __397, __398, __399, __400, i, i1, i2;
    Verstrekking *vrs;
    list<Verstrekking *> *vrsn;
    Correctie *correctie;
    str *atc_wissel, *nivo;
    __ss_bool __401, __402;
    pyobj *__403, *__404, *__405;

    (this->vrsn)->clear();
    (this->vrsn_temp)->clear();
    middelgroep = this->middelgroep;
    if ((middelgroep==NULL)) {
        i1 = (p->month_idx)->__getfast__(this->datum_van);
        i2 = (p->month_idx)->__getfast__(this->datum_tot);

        FAST_FOR(i,i1,i2,1,395,396)
            vrs = (p->vrsn)->__getfast__(i);
            (this->vrsn_temp)->append(this->corrigeer(vrs));
        END_FOR

    }
    else {
        if (__NOT(p->indexed)) {
            i1 = (p->month_idx)->__getfast__((this->rapportage)->maanden);
            i2 = (p->month_idx)->__getfast__(__ss_int(0));
            (this->rapportage)->indexeer(p, i1, i2);
            p->indexed = True;
        }
        if (this->slow_check) {
            i1 = (p->month_idx)->__getfast__(this->datum_van);
            i2 = (p->month_idx)->__getfast__(this->datum_tot);

            FAST_FOR(i,i1,i2,1,397,398)
                vrs = (p->vrsn)->__getfast__(i);
                if ((middelgroep)->__contains__(vrs)) {
                    (this->vrsn_temp)->append(this->corrigeer(vrs));
                }
            END_FOR

        }
        else {
            i1 = vrs_index(middelgroep->vrsn, this->start);
            i2 = vrs_index(middelgroep->vrsn, this->eind);

            FAST_FOR(i,i1,i2,1,399,400)
                vrs = (middelgroep->vrsn)->__getfast__(i);
                if ((middelgroep->fast_contains or (middelgroep)->__contains__(vrs))) {
                    (this->vrsn_temp)->append(this->corrigeer(vrs));
                }
            END_FOR

        }
    }
    if (___bool(this->vrsn_temp)) {
        vrsn = this->vrsn_temp;
        correctie = this->_correctie;
        if (((correctie!=NULL) and ___bool(correctie->nivo) and (len(vrsn)>__ss_int(1)))) {
            nivo = correctie->nivo;
            if (__eq(nivo, const_37)) {
                nivo = NULL;
            }
            atc_wissel = correctie->atc_wissel;
            vrsn = vrs_correctie(vrsn, nivo, atc_wissel);
        }
        if ((this->verstrekking!=NULL)) {
            vrsn = list_comp_22(this, vrsn);
        }
        (this->vrsn)->extend(vrsn);
    }
    return NULL;
}

/**
class VerstrekkingLijstSamengesteld
*/

class_ *cl_VerstrekkingLijstSamengesteld;

void *VerstrekkingLijstSamengesteld::__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten, str *nivo) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijsten = lijsten;
    this->datum_van = __ss_int(0);
    this->nivo = nivo;
    this->vrsn = (__ss_list<Verstrekking *>());
    this->vrsn_temp = (__ss_list<Verstrekking *>());
    return NULL;
}

void *VerstrekkingLijstSamengesteld::bepaal(Patient *p, __ss_int einddatum) {
    VerstrekkingLijstCriterium *lijst;
    list<Verstrekking *> *vrsn;
    str *nivo;
    list<VerstrekkingLijstCriterium *> *__410;
    __iter<VerstrekkingLijstCriterium *> *__411;
    __ss_int __412;
    list<VerstrekkingLijstCriterium *>::for_in_loop __413;
    pyobj *__414, *__415;

    (this->vrsn)->clear();
    (this->vrsn_temp)->clear();

    FOR_IN(lijst,this->lijsten,410,412,413)
        lijst->bepaal(p, einddatum);
        (this->vrsn_temp)->extend(lijst->vrsn);
    END_FOR

    (this->vrsn_temp)->sort(__ss_int(0), __lambda6__, __ss_int(0));
    vrsn = this->vrsn_temp;
    if (___bool(vrsn)) {
        if ((___bool(this->nivo) and (len(vrsn)>__ss_int(1)))) {
            nivo = this->nivo;
            if (__eq(nivo, const_37)) {
                nivo = NULL;
            }
            vrsn = vrs_correctie(vrsn, nivo, NULL);
        }
        (this->vrsn)->extend(vrsn);
    }
    return NULL;
}

/**
class PatientCriterium
*/

class_ *cl_PatientCriterium;

void *PatientCriterium::setup_einddatum(__ss_int einddatum) {
    return NULL;
}

/**
class PatientEigenschappen
*/

class_ *cl_PatientEigenschappen;

void *PatientEigenschappen::__init__(str *naam, str *omschrijving, str *passant, str *fout, __ss_int leeftijd_min, __ss_int leeftijd_max, str *zv_soort, str *geslacht, str *recent) {
    __ss_bool __416, __417, __418, __419;

    this->naam = naam;
    this->omschrijving = omschrijving;
    this->passant = passant;
    this->fout = fout;
    this->geslacht = geslacht;
    this->leeftijd_min = leeftijd_min;
    this->leeftijd_max = leeftijd_max;
    this->recent = recent;
    this->passant_ja = ___bool(__eq(passant, const_25));
    this->passant_nee = ___bool(__eq(passant, const_26));
    this->fout_ja = ___bool(__eq(fout, const_25));
    this->fout_nee = ___bool(__eq(fout, const_26));
    this->recent_ja = ___bool(__eq(recent, const_25));
    this->recent_nee = ___bool(__eq(recent, const_26));
    this->geslacht_check = ___bool((geslacht!=NULL));
    this->leeftijd_check = __OR(___bool((leeftijd_min!=(-__ss_int(1)))), ___bool((leeftijd_max!=(-__ss_int(1)))), 416);
    this->or_check = __OR(___bool((passant!=NULL)), ___bool((fout!=NULL)), 418);
    return NULL;
}

__ss_bool PatientEigenschappen::__call__(Patient *p, __ss_int einddatum) {
    __ss_int leeftijd;
    __ss_bool __420, __421, __422, __423, __424, __425, __426, __427, __428, __429, __430, __431, __432, __433, __434, __435, __436, __437;

    if (this->leeftijd_check) {
        leeftijd = p->leeftijd(einddatum);
        if (__NOT((__ss_int(0)<=leeftijd)&&(leeftijd<__ss_int(120)))) {
            return False;
        }
        if (((this->leeftijd_min!=(-__ss_int(1))) and (leeftijd<this->leeftijd_min))) {
            return False;
        }
        if (((this->leeftijd_max!=(-__ss_int(1))) and (leeftijd>=this->leeftijd_max))) {
            return False;
        }
    }
    if ((this->geslacht_check and __ne(p->geslacht, this->geslacht))) {
        return False;
    }
    if (this->or_check) {
        if ((this->passant_nee and __NOT(p->is_passant(einddatum)))) {
            return True;
        }
        if ((this->passant_ja and p->is_passant(einddatum))) {
            return True;
        }
        if ((this->fout_nee and __NOT(p->is_fout(einddatum)))) {
            return True;
        }
        if ((this->fout_ja and p->is_fout(einddatum))) {
            return True;
        }
        if ((this->recent_nee and __NOT(p->is_recent(einddatum)))) {
            return True;
        }
        if ((this->recent_ja and p->is_recent(einddatum))) {
            return True;
        }
        return False;
    }
    return True;
}

/**
class PatientLogisch
*/

class_ *cl_PatientLogisch;

void *PatientLogisch::__init__(str *naam, str *omschrijving, str *enof, list<PatientCriterium *> *termen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->of = ___bool(__eq(enof, const_32));
    this->termen = termen;
    return NULL;
}

__ss_bool PatientLogisch::__call__(Patient *p, __ss_int einddatum) {
    PatientCriterium *crit;
    list<PatientCriterium *> *__438, *__442;
    __iter<PatientCriterium *> *__439, *__443;
    __ss_int __440, __444;
    list<PatientCriterium *>::for_in_loop __441, __445;

    if (this->of) {

        FOR_IN(crit,this->termen,438,440,441)
            if (crit->__call__(p, einddatum)) {
                return True;
            }
        END_FOR

        return False;
    }
    else {

        FOR_IN(crit,this->termen,442,444,445)
            if (__NOT(crit->__call__(p, einddatum))) {
                return False;
            }
        END_FOR

        return True;
    }
    return False;
}

/**
class PatientLogischTerm
*/

class_ *cl_PatientLogischTerm;

void *PatientLogischTerm::__init__(str *naam, str *omschrijving, str *welniet, PatientCriterium *criterium) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->welniet = ___bool(__eq(welniet, const_31));
    this->criterium = criterium;
    return NULL;
}

__ss_bool PatientLogischTerm::__call__(Patient *p, __ss_int einddatum) {
    if (this->welniet) {
        return this->criterium->__call__(p, einddatum);
    }
    else {
        return __NOT(this->criterium->__call__(p, einddatum));
    }
    return False;
}

/**
class PatientAfleveringen
*/

class_ *cl_PatientAfleveringen;

void *PatientAfleveringen::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int afleveringen_min, __ss_int afleveringen_max, __ss_int datum_van, __ss_int datum_tot, __ss_int recent, __ss_float stuks_min, __ss_float stuks_max, __ss_float ddd_min, __ss_float ddd_max, str *recent_soort, VerstrekkingCriterium *vrs_crit, str *vrs_opties) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->verstrekking = verstrekking;
    this->afleveringen_min = afleveringen_min;
    this->afleveringen_max = afleveringen_max;
    this->datum_tot = datum_tot;
    this->datum_van = datum_van;
    this->stuks_min = stuks_min;
    this->stuks_max = stuks_max;
    this->ddd_min = ddd_min;
    this->ddd_max = ddd_max;
    this->vrs_crit = vrs_crit;
    this->vrs_opties = vrs_opties;
    this->recent_soort = recent_soort;
    this->recent = recent;
    return NULL;
}

void *PatientAfleveringen::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientAfleveringen::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int __446, __447, __451, aantal, i, i1, i2, recent_van;
    __ss_float sum_ddd, sum_stuks;
    __ss_bool __450, __452, __453, __454, __457, __458, __459, __460, __461, __462, __463, __464, __465, __466, __467, __468, __469, __470, __471, __472, recent_gevonden;
    Verstrekking *vrs;
    pyobj *__448, *__449, *__455, *__456, *__473, *__474;

    if (__NOT(___bool(this->verstrekking))) {
        return False;
    }
    (this->verstrekking)->bepaal(p, einddatum);
    vrsn = (this->verstrekking)->vrsn;
    aantal = __ss_int(0);
    sum_ddd = __ss_float(0.0);
    sum_stuks = __ss_float(0.0);
    recent_gevonden = False;
    if (___bool(vrsn)) {
        i1 = vrs_index(vrsn, this->start);
        i2 = vrs_index(vrsn, this->eind);

        FAST_FOR(i,i1,i2,1,446,447)
            vrs = vrsn->__getfast__(i);
            if ((___bool(this->vrs_crit) and __NOT(this->vrs_crit->__call__(vrs)))) {
                continue;
            }
            aantal = (aantal+__ss_int(1));
            sum_ddd = (sum_ddd+vrs->ddd);
            sum_stuks = (sum_stuks+(vrs->recept)->hoeveelheid);
            if (___bool(this->recent_soort)) {
                recent_van = shift_months(einddatum, (-this->recent));
                if ((__eq(this->recent_soort, const_39) and (recent_van<=(__451=vrs->datum))&&(__451<this->eind))) {
                    recent_gevonden = True;
                }
                else if (((vrs->datum<this->eind) and (vrs->einddatum>recent_van))) {
                    recent_gevonden = True;
                }
            }
        END_FOR

        if (((i1!=i2) and ___bool(this->vrs_crit))) {
            if ((__eq(this->vrs_opties, const_40) and __NOT(this->vrs_crit->__call__(vrsn->__getfast__(i1))))) {
                return False;
            }
            else if ((__eq(this->vrs_opties, const_41) and __NOT(this->vrs_crit->__call__(vrsn->__getfast__((i2-__ss_int(1))))))) {
                return False;
            }
        }
    }
    if (((this->afleveringen_min!=(-__ss_int(1))) and (aantal<this->afleveringen_min))) {
        return False;
    }
    if (((this->afleveringen_max!=(-__ss_int(1))) and (aantal>=this->afleveringen_max))) {
        return False;
    }
    if (((this->stuks_min!=(-__ss_float(1.0))) and (sum_stuks<this->stuks_min))) {
        return False;
    }
    if (((this->stuks_max!=(-__ss_float(1.0))) and (sum_stuks>=this->stuks_max))) {
        return False;
    }
    if (((this->ddd_min!=(-__ss_float(1.0))) and (sum_ddd<this->ddd_min))) {
        return False;
    }
    if (((this->ddd_max!=(-__ss_float(1.0))) and (sum_ddd>=this->ddd_max))) {
        return False;
    }
    if ((___bool(this->recent_soort) and __NOT(recent_gevonden))) {
        return False;
    }
    return True;
}

/**
class PatientAfleverContext
*/

class_ *cl_PatientAfleverContext;

void *PatientAfleverContext::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, __ss_int aantal_van, __ss_int aantal_tot, str *welniet, str *wat, __ss_int dagen_voor, __ss_int dagen_na, VerstrekkingLijstCriterium *lijst_van, __ss_int van, PatientCriterium *criterium) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijst = lijst;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->aantal_van = aantal_van;
    this->aantal_tot = aantal_tot;
    this->welniet = ___bool(__eq(welniet, const_31));
    this->wat = wat;
    this->van = van;
    this->criterium = criterium;
    this->dagen_voor = dagen_voor;
    this->dagen_na = dagen_na;
    this->lijst_van = lijst_van;
    return NULL;
}

void *PatientAfleverContext::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientAfleverContext::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn, *vrsn_van;
    __ss_int __475, __476, aantal, atot, avan, dagen_na, dagen_voor, datum_na, datum_voor, i, i1, i2, i3, i4;
    Verstrekking *vrs;
    __ss_bool __477, __478, __479, __480, gevonden;
    list<Period *> *prdn_van;

    vrsn = (__ss_list<Verstrekking *>());
    if (___bool(this->criterium)) {
        if (this->criterium->__call__(p, einddatum)) {
            vrsn = (new list<Verstrekking *>(1,(this->criterium)->vrs));
        }
    }
    else {
        (this->lijst)->bepaal(p, einddatum);
        vrsn = (this->lijst)->vrsn;
    }
    i3 = vrs_index(vrsn, this->start);
    i4 = vrs_index(vrsn, this->eind);
    (this->lijst_van)->bepaal(p, einddatum);
    vrsn_van = (this->lijst_van)->vrsn;
    dagen_voor = (((this->dagen_voor!=(-__ss_int(1))))?(this->dagen_voor):(__ss_int(1000000)));
    dagen_na = (((this->dagen_na!=(-__ss_int(1))))?(this->dagen_na):(__ss_int(1000000)));
    aantal = __ss_int(0);

    FAST_FOR(i,i3,i4,1,475,476)
        vrs = vrsn->__getfast__(i);
        datum_voor = shift_days(vrs->datum, (-dagen_voor));
        datum_na = shift_days(vrs->datum, dagen_na);
        i1 = vrs_index(vrsn_van, datum_voor);
        i2 = vrs_index(vrsn_van, datum_na);
        if (__eq(this->wat, const_39)) {
            gevonden = ___bool((i1!=i2));
        }
        else {
            prdn_van = vrs_gebruik(vrsn_van, datum_voor, datum_na);
            gevonden = ___bool((len(prdn_van)>__ss_int(0)));
        }
        if ((gevonden and this->welniet)) {
            aantal = (aantal+__ss_int(1));
        }
        else if ((__NOT(gevonden) and __NOT(this->welniet))) {
            aantal = (aantal+__ss_int(1));
        }
    END_FOR

    avan = this->aantal_van;
    if ((avan==(-__ss_int(1)))) {
        avan = __ss_int(0);
    }
    atot = this->aantal_tot;
    if ((atot==(-__ss_int(1)))) {
        atot = __sys__::maxsize;
    }
    return ___bool((avan<=aantal)&&(aantal<atot));
}

list<Period *> *prd_invert(list<Period *> *prdn, __ss_int start, __ss_int eind) {
    /**
    inverteer perioden tussen start- en einddatum 
    */
    list<Period *> *result;
    __ss_int __481, __482, i;

    if (__NOT(___bool(prdn))) {
        return (new list<Period *>(1,(new Period(start, eind))));
    }
    result = (__ss_list<Period *>());
    if (((prdn->__getfast__(__ss_int(0)))->start>start)) {
        result->append((new Period(start, (prdn->__getfast__(__ss_int(0)))->start)));
    }

    FAST_FOR(i,0,(len(prdn)-__ss_int(1)),1,481,482)
        result->append((new Period((prdn->__getfast__(i))->eind, (prdn->__getfast__((i+__ss_int(1))))->start)));
    END_FOR

    if (((prdn->__getfast__((-__ss_int(1))))->eind<eind)) {
        result->append((new Period((prdn->__getfast__((-__ss_int(1))))->eind, eind)));
    }
    return result;
}

/**
class PatientGaten
*/

class_ *cl_PatientGaten;

void *PatientGaten::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs_lijst, __ss_int datum_van, __ss_int datum_tot, str *totaal_onafgebroken, __ss_int lengte_van, __ss_int lengte_tot, __ss_int gaten_van, __ss_int gaten_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->vrs_lijst = vrs_lijst;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->totaal_onafgebroken = totaal_onafgebroken;
    this->lengte_van = lengte_van;
    this->lengte_tot = lengte_tot;
    this->gaten_van = gaten_van;
    this->gaten_tot = gaten_tot;
    return NULL;
}

void *PatientGaten::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientGaten::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int __494, gaten_tot, gaten_van, lengte_tot, lengte_totaal, lengte_van;
    list<Period *> *gaten, *prdn;

    if (__NOT(___bool(this->vrs_lijst))) {
        return False;
    }
    (this->vrs_lijst)->bepaal(p, einddatum);
    vrsn = (this->vrs_lijst)->vrsn;
    gaten_van = (((this->gaten_van!=(-__ss_int(1))))?(this->gaten_van):(__ss_int(0)));
    gaten_tot = (((this->gaten_tot!=(-__ss_int(1))))?(this->gaten_tot):(__sys__::maxsize));
    lengte_van = (((this->lengte_van!=(-__ss_int(1))))?(this->lengte_van):(__ss_int(0)));
    lengte_tot = (((this->lengte_tot!=(-__ss_int(1))))?(this->lengte_tot):(__sys__::maxsize));
    prdn = vrs_gebruik(vrsn, this->start, this->eind);
    if (__NOT(___bool(prdn))) {
        return ___bool((gaten_van<=__ss_int(0))&&(__ss_int(0)<gaten_tot));
    }
    prdn->__getfast__(__ss_int(0))->start = this->start;
    prdn->__getfast__((-__ss_int(1)))->eind = this->eind;
    gaten = prd_invert(prdn, this->start, this->eind);
    lengte_totaal = __sum(list_comp_23(gaten));
    if (__eq(this->totaal_onafgebroken, const_43)) {
        if (__NOT((lengte_van<=lengte_totaal)&&(lengte_totaal<lengte_tot))) {
            return False;
        }
    }
    else {
        gaten = list_comp_24(lengte_van, lengte_tot, gaten);
    }
    return ___bool((gaten_van<=(__494=len(gaten)))&&(__494<gaten_tot));
}

/**
class PatientDosering
*/

class_ *cl_PatientDosering;

void *PatientDosering::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *lijst, __ss_int datum_van, __ss_int datum_tot, str *soort_dosering, __ss_float van, __ss_float tot, str *soort_berekening, str *vrs_of_dag, str *totaal_onafgebroken, str *soort_periode, __ss_int aantalvrs, __ss_int leeftijd_min, __ss_int leeftijd_max, __ss_int dagen_van, __ss_int dagen_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijst = lijst;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->soort_dosering = soort_dosering;
    this->van = van;
    this->tot = tot;
    this->soort_berekening = soort_berekening;
    this->vrs_of_dag = vrs_of_dag;
    this->totaal_onafgebroken = totaal_onafgebroken;
    this->soort_periode = NULL;
    this->aantalvrs = aantalvrs;
    this->leeftijd_min = leeftijd_min;
    this->leeftijd_max = leeftijd_max;
    this->dagen_van = dagen_van;
    this->dagen_tot = dagen_tot;
    return NULL;
}

void *PatientDosering::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientDosering::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int dagen, i1, i2, leeftijd;
    tuple2<__ss_float, __ss_int> *__503, *totaal_dagen;
    __ss_float dosering, totaal;
    __ss_bool __495, __496, __497, __498, __499, __500, __504, __505, __506, __507;
    str *__501, *__502;

    if (__NOT(___bool(this->lijst))) {
        return False;
    }
    (this->lijst)->bepaal(p, einddatum);
    vrsn = (this->lijst)->vrsn;
    if (((this->leeftijd_min!=(-__ss_int(1))) or (this->leeftijd_max!=(-__ss_int(1))))) {
        leeftijd = p->leeftijd(einddatum);
        if (((this->leeftijd_min!=(-__ss_int(1))) and (leeftijd<this->leeftijd_min))) {
            return False;
        }
        if (((this->leeftijd_max!=(-__ss_int(1))) and (leeftijd>=this->leeftijd_max))) {
            return False;
        }
    }
    i1 = vrs_index(vrsn, this->start);
    i2 = vrs_index(vrsn, this->eind);
    vrsn = vrsn->__slice__(__ss_int(3), i1, i2, __ss_int(0));
    ASSERT(___bool(__eq(this->soort_berekening, const_44)), 0);
    if (__NOT(___bool(vrsn))) {
        return False;
    }
    totaal_dagen = vrs_gemiddeld(vrsn, this->soort_dosering, this->aantalvrs, __OR(this->vrs_of_dag, const_16, 501), this->soort_periode, this->start, this->eind);
    if ((totaal_dagen!=NULL)) {
        __503 = totaal_dagen;
        __SS_UNPACK_CHECK(__503, 2);
        totaal = __503->__getfirst__();
        dagen = __503->__getsecond__();
        dosering = (totaal/__float(dagen));
    }
    else {
        return False;
    }
    if (((this->van!=(-__ss_float(1.0))) and (dosering<this->van))) {
        return False;
    }
    if (((this->tot!=(-__ss_float(1.0))) and (dosering>=this->tot))) {
        return False;
    }
    return True;
}

/**
class PatientPolyfarmacie
*/

class_ *cl_PatientPolyfarmacie;

void *PatientPolyfarmacie::__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, __ss_int datum_van, __ss_int datum_tot, __ss_int vrs_van, __ss_int vrs_tot, __ss_int gebr_van, __ss_int gebr_tot, str *totaal_onafgebroken, str *dubbelgroepen, __ss_int min_van, __ss_int min_tot, __ss_int groepen_van, __ss_int groepen_tot, str *nivo) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->vrs_lijsten = vrs_lijsten;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->vrs_van = vrs_van;
    this->vrs_tot = vrs_tot;
    this->gebr_van = gebr_van;
    this->gebr_tot = gebr_tot;
    this->totaal_onafgebroken = totaal_onafgebroken;
    this->dubbelen = (new set<str *>());
    if (___bool(dubbelgroepen)) {
        this->dubbelen = (new set<str *>(dubbelgroepen->split(NULL, (-__ss_int(1)))));
    }
    this->min_van = min_van;
    this->min_tot = min_tot;
    this->groepen_van = groepen_van;
    this->groepen_tot = groepen_tot;
    this->nivo = nivo;
    return NULL;
}

void *PatientPolyfarmacie::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientPolyfarmacie::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    VerstrekkingLijstCriterium *vrs_lijst;
    dict<str *, list<Verstrekking *> *> *__525, *key_vrsn;
    __ss_int __510, __522, __532, __536, __538, afleveringen, gebr_tot, gebr_van, groepentot, groepenvan, min_tot, min_van, teller, totaal, vrs_tot, vrs_van;
    list<str *> *groepen;
    str *key;
    __ss_bool __526, __527, __528, __529, match;
    list<Period *> *__530, *__534, *prdn;
    Period *per;
    list<VerstrekkingLijstCriterium *> *__508;
    __iter<VerstrekkingLijstCriterium *> *__509;
    list<VerstrekkingLijstCriterium *>::for_in_loop __511;
    tuple2<str *, list<Verstrekking *> *> *__519;
    __iter<tuple2<str *, list<Verstrekking *> *> *> *__520, *__521;
    __iter<tuple2<str *, list<Verstrekking *> *> *>::for_in_loop __523;
    __GC_DICT<str *, list<Verstrekking *> *>::iterator __524;
    __iter<Period *> *__531, *__535;
    list<Period *>::for_in_loop __533, __537;

    this->info_groepen = (-__ss_int(1));
    ASSERT(___bool(__ne(this->nivo, const_45)), 0);
    vrsn = (__ss_list<Verstrekking *>());
    if (___bool(this->vrs_lijsten)) {

        FOR_IN(vrs_lijst,this->vrs_lijsten,508,510,511)
            vrs_lijst->bepaal(p, einddatum);
            vrsn->extend(vrs_lijst->vrsn);
        END_FOR

    }
    vrsn->sort(__ss_int(0), __lambda8__, __ss_int(0));
    key_vrsn = vrs_split(vrsn, this->nivo, NULL);
    if ((this->min_van!=(-__ss_int(1)))) {
        min_van = shift_months(einddatum, (-this->min_van));
        min_tot = shift_months(einddatum, (-this->min_tot));
        key_vrsn = list_comp_25(key_vrsn, min_tot, min_van);
    }
    groepen = (__ss_list<str *>());

    FOR_IN_DICT(key_vrsn,525,524,522)
        key = (*__524).first;
        vrsn = (*__524).second;
        __524++;
        if (((this->vrs_van!=(-__ss_int(1))) or (this->vrs_tot!=(-__ss_int(1))))) {
            vrs_van = (((this->vrs_van!=(-__ss_int(1))))?(this->vrs_van):(__ss_int(0)));
            vrs_tot = (((this->vrs_tot!=(-__ss_int(1))))?(this->vrs_tot):(__sys__::maxsize));
            afleveringen = vrs_aantal(vrsn, this->start, this->eind);
            if ((vrs_van<=afleveringen)&&(afleveringen<vrs_tot)) {
                groepen->append(key);
                continue;
            }
        }
        if (((this->gebr_van!=(-__ss_int(1))) or (this->gebr_tot!=(-__ss_int(1))))) {
            gebr_van = (((this->gebr_van!=(-__ss_int(1))))?(this->gebr_van):(__ss_int(0)));
            gebr_tot = (((this->gebr_tot!=(-__ss_int(1))))?(this->gebr_tot):(__sys__::maxsize));
            match = False;
            prdn = vrs_gebruik(vrsn, this->start, this->eind);
            if (__eq(this->totaal_onafgebroken, const_43)) {
                totaal = __ss_int(0);

                FOR_IN(per,prdn,530,532,533)
                    totaal = (totaal+(get_days(per->eind)-get_days(per->start)));
                END_FOR

                if ((gebr_van<=totaal)&&(totaal<gebr_tot)) {
                    match = True;
                }
            }
            else {

                FOR_IN(per,prdn,534,536,537)
                    if ((gebr_van<=(__538=(get_days(per->eind)-get_days(per->start))))&&(__538<gebr_tot)) {
                        match = True;
                        break;
                    }
                END_FOR

            }
            if (match) {
                groepen->append(key);
                continue;
            }
        }
    END_FOR

    teller = __sum(list_comp_26(groepen, this));
    this->info_groepen = teller;
    groepenvan = (((this->groepen_van!=(-__ss_int(1))))?(this->groepen_van):(__ss_int(0)));
    groepentot = (((this->groepen_tot!=(-__ss_int(1))))?(this->groepen_tot):(__sys__::maxsize));
    return ___bool((groepenvan<=teller)&&(teller<groepentot));
}

/**
class PatientTherapietrouw2
*/

class_ *cl_PatientTherapietrouw2;

void *PatientTherapietrouw2::__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *vrs_lijsten, str *nivo, __ss_int datum_van, __ss_int datum_tot, __ss_float perc_van, __ss_float perc_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->vrs_lijsten = vrs_lijsten;
    this->nivo = nivo;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->perc_van = perc_van;
    this->perc_tot = perc_tot;
    return NULL;
}

void *PatientTherapietrouw2::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientTherapietrouw2::__call__(Patient *p, __ss_int einddatum) {
    dict<str *, list<Verstrekking *> *> *__559, *key_vrsn;
    VerstrekkingLijstCriterium *vrs_lijst;
    list<Verstrekking *> *verstrekkingen, *vrsn;
    list<str *> *atc_wissels;
    list<__ss_float> *percentages;
    dict<str *, __ss_float> *berekening;
    str *key;
    list<Period *> *prdn;
    __ss_int __545, __549, __556, noemer, teller;
    __ss_float gemiddeld_percentage, perc;
    list<VerstrekkingLijstCriterium *> *__543, *__547;
    __iter<VerstrekkingLijstCriterium *> *__544, *__548;
    list<VerstrekkingLijstCriterium *>::for_in_loop __546, __550;
    __ss_bool __551, __552, __564, __565, __566, __567;
    tuple2<str *, list<Verstrekking *> *> *__553;
    __iter<tuple2<str *, list<Verstrekking *> *> *> *__554, *__555;
    __iter<tuple2<str *, list<Verstrekking *> *> *>::for_in_loop __557;
    __GC_DICT<str *, list<Verstrekking *> *>::iterator __558;

    this->info_percentage = (-__ss_float(1.0));
    if (__eq(this->nivo, const_45)) {
        key_vrsn = (new dict<str *, list<Verstrekking *> *>());

        FOR_IN(vrs_lijst,this->vrs_lijsten,543,545,546)
            vrs_lijst->bepaal(p, einddatum);
            key_vrsn->__setitem__(vrs_lijst->naam, vrs_lijst->vrsn);
        END_FOR

    }
    else {
        verstrekkingen = (__ss_list<Verstrekking *>());
        atc_wissels = (__ss_list<str *>());

        FOR_IN(vrs_lijst,this->vrs_lijsten,547,549,550)
            vrs_lijst->bepaal(p, einddatum);
            if (((vrs_lijst->_correctie!=NULL) and ((vrs_lijst->_correctie)->atc_wissel!=NULL))) {
                atc_wissels->append((vrs_lijst->_correctie)->atc_wissel);
            }
            verstrekkingen->extend(vrs_lijst->vrsn);
        END_FOR

        verstrekkingen->sort(__ss_int(0), __lambda9__, __ss_int(0));
        key_vrsn = vrs_split(verstrekkingen, this->nivo, (const_46)->join(atc_wissels));
    }
    percentages = (__ss_list<__ss_float>());
    berekening = (new dict<str *, __ss_float>());

    FOR_IN_DICT(key_vrsn,559,558,556)
        key = (*__558).first;
        vrsn = (*__558).second;
        __558++;
        prdn = vrs_gebruik(vrsn, this->start, this->eind);
        if (___bool(prdn)) {
            teller = __sum(list_comp_27(prdn));
            noemer = (get_days(einddatum)-get_days((prdn->__getfast__(__ss_int(0)))->start));
            perc = ((__ss_float(100.0)*teller)/noemer);
            percentages->append(perc);
            berekening->__setitem__(key, perc);
        }
    END_FOR

    if (__NOT(___bool(percentages))) {
        return False;
    }
    gemiddeld_percentage = (__sum(percentages)/len(percentages));
    this->info_percentage = gemiddeld_percentage;
    if (((this->perc_van!=(-__ss_float(1.0))) and (gemiddeld_percentage<this->perc_van))) {
        return False;
    }
    if (((this->perc_tot!=(-__ss_float(1.0))) and (gemiddeld_percentage>=this->perc_tot))) {
        return False;
    }
    return True;
}

/**
class PatientGebruik
*/

class_ *cl_PatientGebruik;

void *PatientGebruik::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, str *totaal_onafgebroken, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *welniet, __ss_float ddd_van, __ss_float ddd_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->verstrekking = verstrekking;
    this->totaal = ___bool(__eq(totaal_onafgebroken, const_43));
    this->welniet = ___bool(__eq(welniet, const_31));
    ASSERT(this->welniet, 0);
    this->dagen_van = dagen_van;
    this->dagen_tot = dagen_tot;
    this->ddd_van = ddd_van;
    this->ddd_tot = ddd_tot;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    return NULL;
}

void *PatientGebruik::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientGebruik::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *__583, *vrsn;
    list<Period *> *__568, *__576, *prdn;
    __ss_int __570, __578, __580, __585, duur, duur_in_periode, totaal;
    Period *per;
    __ss_float totaal_ddd;
    Verstrekking *vrs;
    __iter<Period *> *__569, *__577;
    list<Period *>::for_in_loop __571, __579;
    __ss_bool __572, __573, __574, __575, __581, __582, __587, __588, __589, __590, __591, __592;
    __iter<Verstrekking *> *__584;
    list<Verstrekking *>::for_in_loop __586;

    (this->verstrekking)->bepaal(p, einddatum);
    vrsn = (this->verstrekking)->vrsn;
    prdn = vrs_gebruik(vrsn, this->start, this->eind);
    if (this->totaal) {
        totaal = __ss_int(0);

        FOR_IN(per,prdn,568,570,571)
            totaal = (totaal+(get_days(per->eind)-get_days(per->start)));
        END_FOR

        if (((this->dagen_van!=(-__ss_int(1))) and (totaal<this->dagen_van))) {
            return False;
        }
        if (((this->dagen_tot!=(-__ss_int(1))) and (totaal>=this->dagen_tot))) {
            return False;
        }
    }
    else {

        __580 = 0;
        FOR_IN(per,prdn,576,578,579)
            if (((get_days(per->eind)-get_days(per->start))>=this->dagen_van)) {
                __580 = 1;
                break;
            }
        END_FOR
        if (!__580) {
            return False;
        }

    }
    if (((this->ddd_van!=(-__ss_float(1.0))) or (this->ddd_tot!=(-__ss_float(1.0))))) {
        totaal_ddd = __ss_float(0.0);

        FOR_IN(vrs,vrsn,583,585,586)
            if (((vrs->datum<this->eind) and (vrs->einddatum>this->start))) {
                duur = (get_days(vrs->einddatum)-get_days(vrs->datum));
                duur_in_periode = (get_days(___min(2, __ss_int(0), vrs->einddatum, this->eind))-get_days(___max(2, __ss_int(0), vrs->datum, this->start)));
                totaal_ddd = (totaal_ddd+(vrs->ddd*__divs(duur_in_periode, duur)));
            }
        END_FOR

        if (((this->ddd_van!=(-__ss_float(1.0))) and (totaal_ddd<this->ddd_van))) {
            return False;
        }
        if (((this->ddd_tot!=(-__ss_float(1.0))) and (totaal_ddd>=this->ddd_tot))) {
            return False;
        }
    }
    return True;
}

/**
class PatientInteractie2
*/

class_ *cl_PatientInteractie2;

void *PatientInteractie2::__init__(str *naam, str *omschrijving, list<VerstrekkingLijstCriterium *> *lijsten_verplicht, list<VerstrekkingLijstCriterium *> *lijsten, __ss_int dagen_van, __ss_int dagen_tot, __ss_int datum_van, __ss_int datum_tot, str *nivo, str *totaal_onafgebroken, __ss_int minimum) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijsten_verplicht = lijsten_verplicht;
    this->lijsten = lijsten;
    this->dagen_van = dagen_van;
    this->dagen_tot = dagen_tot;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->minimum = minimum;
    this->vrsnn_verplicht = (__ss_list<list<Verstrekking *> *>());
    this->vrsnn = (__ss_list<list<Verstrekking *> *>());
    return NULL;
}

void *PatientInteractie2::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientInteractie2::__call__(Patient *p, __ss_int einddatum) {
    VerstrekkingLijstCriterium *vlijst;
    list<Period *> *__601, *prdn;
    Period *per;
    __ss_int __595, __599, __603, dagen;
    list<VerstrekkingLijstCriterium *> *__593, *__597;
    __iter<VerstrekkingLijstCriterium *> *__594, *__598;
    list<VerstrekkingLijstCriterium *>::for_in_loop __596, __600;
    __iter<Period *> *__602;
    list<Period *>::for_in_loop __604;
    __ss_bool __605, __606, __607, __608, __609, __610;

    this->info_perioden = NULL;
    (this->vrsnn_verplicht)->clear();
    (this->vrsnn)->clear();
    if (___bool(this->lijsten_verplicht)) {

        FOR_IN(vlijst,this->lijsten_verplicht,593,595,596)
            vlijst->bepaal(p, einddatum);
            if (___bool(vlijst->vrsn)) {
                (this->vrsnn_verplicht)->append(vlijst->vrsn);
            }
            else {
                return False;
            }
        END_FOR

    }
    if (___bool(this->lijsten)) {

        FOR_IN(vlijst,this->lijsten,597,599,600)
            vlijst->bepaal(p, einddatum);
            (this->vrsnn)->append(vlijst->vrsn);
        END_FOR

    }
    prdn = vrs_interactie(this->vrsnn, this->start, this->eind, this->minimum, this->vrsnn_verplicht);
    this->info_perioden = prdn;

    FOR_IN(per,prdn,601,603,604)
        dagen = (get_days(per->eind)-get_days(per->start));
        if ((((this->dagen_van==(-__ss_int(1))) or (this->dagen_van<=dagen)) and ((this->dagen_tot==(-__ss_int(1))) or (dagen<this->dagen_tot)))) {
            return True;
        }
    END_FOR

    return False;
}

/**
class PatientEU
*/

class_ *cl_PatientEU;

void *PatientEU::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *verstrekking, __ss_int datum_van, __ss_int datum_tot, __ss_int voorloop, str *soort, str *modtarief, VerstrekkingCriterium *startmet) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->verstrekking = verstrekking;
    this->soort = soort;
    this->voorloop = voorloop;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->modtarief = modtarief;
    this->startmet = startmet;
    return NULL;
}

void *PatientEU::setup_einddatum(__ss_int einddatum) {
    this->start = shift_months(einddatum, (-this->datum_van));
    this->eind = shift_months(einddatum, (-this->datum_tot));
    return NULL;
}

__ss_bool PatientEU::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int __611, __612, code, i, i1, i2, terug;
    Verstrekking *hebbes, *vrs;
    __ss_bool __613, __614, __615, __616, __617;

    this->vrs = NULL;
    (this->verstrekking)->bepaal(p, einddatum);
    vrsn = (this->verstrekking)->vrsn;
    if (___bool(vrsn)) {
        i1 = vrs_index(vrsn, this->start);
        i2 = vrs_index(vrsn, this->eind);

        FAST_FOR(i,i1,i2,1,611,612)
            vrs = vrsn->__getfast__(i);
            code = (vrs->recept)->modulaire_tariefcode;
            terug = shift_months(vrs->datum, (-this->voorloop));
            if (__eq(this->soort, const_47)) {
                if (((i>__ss_int(0)) and ((vrsn->__getfast__((i-__ss_int(1))))->datum>=terug) and ((vrsn->__getfast__((i-__ss_int(1))))->datum!=vrs->datum))) {
                    hebbes = this->check_zelfde_dag(vrsn, i, True);
                    if (___bool(hebbes)) {
                        this->vrs = vrs;
                        return True;
                    }
                }
            }
            else if (((i==__ss_int(0)) or ((vrsn->__getfast__((i-__ss_int(1))))->datum<terug))) {
                hebbes = this->check_zelfde_dag(vrsn, i, False);
                if (___bool(hebbes)) {
                    this->vrs = vrs;
                    return True;
                }
            }
        END_FOR

    }
    return False;
}

Verstrekking *PatientEU::check_zelfde_dag(list<Verstrekking *> *vrsn, __ss_int i, __ss_bool vervolg_uitgifte) {
    __ss_int code, datum;
    Verstrekking *vrs;
    __ss_bool __618, __619, __620, __621, __622, __623, __624, __625, __626, __627, __628, __629;

    datum = (vrsn->__getfast__(i))->datum;

    while (((i<len(vrsn)) and ((vrsn->__getfast__(i))->datum==datum))) {
        vrs = vrsn->__getfast__(i);
        if ((__NOT(___bool(this->startmet)) or this->startmet->__call__(vrs))) {
            code = (vrs->recept)->modulaire_tariefcode;
            if (vervolg_uitgifte) {
                if ((__NOT(___bool(this->modtarief)) or __eq(this->modtarief, const_26) or (code==__ss_int(0)) or (__wokl__::CODES_VERVOLGUITGIFTE)->__contains__(code))) {
                    return vrs;
                }
            }
            else if ((__NOT(___bool(this->modtarief)) or __eq(this->modtarief, const_26) or (code==__ss_int(0)) or (!(__wokl__::CODES_VERVOLGUITGIFTE)->__contains__(code)))) {
                return vrs;
            }
        }
        i = (i+__ss_int(1));
    }
    return 0;
}

/**
class PatientPuntenTerm
*/

class_ *cl_PatientPuntenTerm;

void *PatientPuntenTerm::__init__(str *naam, str *omschrijving, PatientCriterium *criterium, __ss_int aantal_punten) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    this->aantal_punten = aantal_punten;
    return NULL;
}

__ss_int PatientPuntenTerm::__call__(Patient *p, __ss_int einddatum) {
    if (this->criterium->__call__(p, einddatum)) {
        return this->aantal_punten;
    }
    return __ss_int(0);
}

/**
class PatientPunten
*/

class_ *cl_PatientPunten;

void *PatientPunten::__init__(str *naam, str *omschrijving, list<PatientPuntenTerm *> *termen, __ss_int punten_min, __ss_int punten_max) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->termen = termen;
    this->punten_min = punten_min;
    this->punten_max = punten_max;
    return NULL;
}

__ss_bool PatientPunten::__call__(Patient *p, __ss_int einddatum) {
    __ss_int __634, __635, pmax, pmin, totaal;

    totaal = __sum(list_comp_28(p, einddatum, this));
    __634 = this->punten_min;
    __635 = this->punten_max;
    pmin = __634;
    pmax = __635;
    if ((pmin==(-__ss_int(1)))) {
        pmin = __ss_int(0);
    }
    if ((pmax==(-__ss_int(1)))) {
        pmax = __sys__::maxsize;
    }
    return ___bool((pmin<=totaal)&&(totaal<pmax));
}

/**
class PatientInformatieInfo
*/

class_ *cl_PatientInformatieInfo;

void *PatientInformatieInfo::__init__(str *naam, str *omschrijving, list<PatientInfo *> *lijst) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->lijst = lijst;
    return NULL;
}

/**
class PatientInfo
*/

class_ *cl_PatientInfo;

/**
class PatientPatientInfo
*/

class_ *cl_PatientPatientInfo;

void *PatientPatientInfo::__init__(str *naam, str *omschrijving, PatientCriterium *criterium) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    return NULL;
}

str *PatientPatientInfo::__call__(Patient *p, __ss_int einddatum) {
    if (___bool(this->criterium)) {
        if (this->criterium->__call__(p, einddatum)) {
            return const_48;
        }
        else {
            return const_49;
        }
    }
    return 0;
}

/**
class PatientPatientenInfo
*/

class_ *cl_PatientPatientenInfo;

void *PatientPatientenInfo::__init__(str *naam, str *omschrijving, PatientCriterium *criterium) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    return NULL;
}

str *PatientPatientenInfo::__call__(Patient *p, __ss_int einddatum) {
    if (___bool(this->criterium)) {
        if (this->criterium->__call__(p, einddatum)) {
            return const_48;
        }
        else {
            return const_49;
        }
    }
    return 0;
}

/**
class PatientPolyfarmacieInfo
*/

class_ *cl_PatientPolyfarmacieInfo;

void *PatientPolyfarmacieInfo::__init__(str *naam, str *omschrijving, PatientPolyfarmacie *criterium, str *wat) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    this->wat = wat;
    return NULL;
}

str *PatientPolyfarmacieInfo::__call__(Patient *p, __ss_int einddatum) {
    __ss_int info_groepen;

    if (___bool(this->criterium)) {
        this->criterium->__call__(p, einddatum);
        if (__eq(this->wat, const_50)) {
            info_groepen = (this->criterium)->info_groepen;
            if ((info_groepen>__ss_int(0))) {
                return __str(info_groepen);
            }
        }
        else {
            ASSERT(False, 0);
        }
    }
    return 0;
}

/**
class PatientTherapietrouwNieuwInfo
*/

class_ *cl_PatientTherapietrouwNieuwInfo;

void *PatientTherapietrouwNieuwInfo::__init__(str *naam, str *omschrijving, PatientTherapietrouw2 *criterium, str *wat, __ss_int decimalen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    this->wat = wat;
    this->decimalen = decimalen;
    return NULL;
}

str *PatientTherapietrouwNieuwInfo::__call__(Patient *p, __ss_int einddatum) {
    __ss_float percentage;

    if (___bool(this->criterium)) {
        this->criterium->__call__(p, einddatum);
        if (__eq(this->wat, const_51)) {
            percentage = (this->criterium)->info_percentage;
            if ((percentage!=(-__ss_float(1.0)))) {
                if ((this->decimalen==__ss_int(0))) {
                    return __str(__int(percentage));
                }
                else if ((this->decimalen==__ss_int(2))) {
                    return __mod6(const_52, 1, percentage);
                }
                else {
                    ASSERT(False, 0);
                }
            }
        }
        else {
            ASSERT(False, 0);
        }
    }
    return 0;
}

/**
class PatientVerstrekkingenInfo
*/

class_ *cl_PatientVerstrekkingenInfo;

void *PatientVerstrekkingenInfo::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, PatientCriterium *criterium, str *tellen, __ss_int datum_van, __ss_int datum_tot, VerstrekkingCriterium *vrs_enkel) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->vrslijst = vrs;
    this->criterium = criterium;
    this->tellen = tellen;
    this->vrs_enkel = vrs_enkel;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    return NULL;
}

str *PatientVerstrekkingenInfo::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int __638, __639, aantal, eind, i, i1, i2, start;
    __ss_float ddd, stuks;
    Verstrekking *vrs;
    __ss_bool __636, __637, __640, __641;

    if (((this->criterium!=NULL) and __NOT(this->criterium->__call__(p, einddatum)))) {
        return NULL;
    }
    if ((this->vrslijst==NULL)) {
        return NULL;
    }
    (this->vrslijst)->bepaal(p, einddatum);
    vrsn = (this->vrslijst)->vrsn;
    start = shift_months(einddatum, (-this->datum_van));
    eind = shift_months(einddatum, (-this->datum_tot));
    i1 = vrs_index(vrsn, start);
    i2 = vrs_index(vrsn, eind);
    aantal = __ss_int(0);
    ddd = __ss_float(0.0);
    stuks = __ss_float(0.0);

    FAST_FOR(i,i1,i2,1,638,639)
        vrs = vrsn->__getfast__(i);
        if (((this->vrs_enkel==NULL) or this->vrs_enkel->__call__(vrs))) {
            aantal = (aantal+__ss_int(1));
            ddd = (ddd+(vrs->recept)->ddd);
            stuks = (stuks+(vrs->recept)->hoeveelheid);
        }
    END_FOR

    if (__eq(this->tellen, const_53)) {
        if ((aantal>__ss_int(0))) {
            return __str(aantal);
        }
    }
    else if (__eq(this->tellen, const_54)) {
        if ((ddd>__ss_float(0.0))) {
            return __str(ddd);
        }
    }
    else if (__eq(this->tellen, const_55)) {
        if ((stuks>__ss_float(0.0))) {
            return __str(stuks);
        }
    }
    else {
        ASSERT(False, 0);
    }
    return 0;
}

/**
class PatientPeriodenInfo
*/

class_ *cl_PatientPeriodenInfo;

void *PatientPeriodenInfo::__init__(str *naam, str *omschrijving, PatientCriterium *pat, VerstrekkingLijstCriterium *vrs, str *wat, str *hoe, __ss_int datum_van, __ss_int datum_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = pat;
    this->vrslijst = vrs;
    this->wat = wat;
    this->hoe = hoe;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    return NULL;
}

str *PatientPeriodenInfo::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int eind, start;
    list<Period *> *prdn;
    __ss_bool __642, __643;

    if (((this->criterium!=NULL) and __NOT(this->criterium->__call__(p, einddatum)))) {
        return NULL;
    }
    if ((this->vrslijst==NULL)) {
        return NULL;
    }
    (this->vrslijst)->bepaal(p, einddatum);
    vrsn = (this->vrslijst)->vrsn;
    start = shift_months(einddatum, (-this->datum_van));
    eind = shift_months(einddatum, (-this->datum_tot));
    prdn = vrs_interactie((new list<list<Verstrekking *> *>(1,vrsn)), start, eind, (-__ss_int(1)), default_17);
    ASSERT(___bool(__eq(this->wat, const_56)), 0);
    if (___bool(prdn)) {
        if (__eq(this->hoe, const_57)) {
            return (const_58)->join(list_comp_29(prdn));
        }
        else if (__eq(this->hoe, const_59)) {
            return (const_58)->join(list_comp_30(prdn));
        }
        else {
            ASSERT(False, 0);
        }
    }
    return 0;
}

str *datum_fmt(__ss_int ymd) {
    __ss_int d, m, y;

    y = __floordiv(ymd,__ss_int(10000));
    m = __mods(__floordiv(ymd,__ss_int(100)), __ss_int(100));
    d = __mods(ymd, __ss_int(100));
    return __mod6(const_61, 3, d, m, y);
}

str *vrs_info(Verstrekking *vrs, str *wat) {
    if (__eq(wat, const_62)) {
        return datum_fmt(vrs->datum);
    }
    else if (__eq(wat, const_63)) {
        return datum_fmt(vrs->einddatum);
    }
    else if (__eq(wat, const_64)) {
        return (vrs->_atc)->code;
    }
    else if (__eq(wat, const_65)) {
        return __wokl__::g_atc5_naam->__getitem__((vrs->_atc)->code);
    }
    else if (__eq(wat, const_54)) {
        return __mod6(const_66, 1, vrs->ddd);
    }
    else if (__eq(wat, const_67)) {
        return __mod6(const_66, 1, (vrs->ddd/(get_days(vrs->einddatum)-get_days(vrs->datum))));
    }
    else if (__eq(wat, const_62)) {
        return datum_fmt(vrs->datum);
    }
    else if (__eq(wat, const_68)) {
        return __str((vrs->recept)->agb);
    }
    else if (__eq(wat, const_69)) {
        return __str((vrs->recept)->sv);
    }
    else if (__eq(wat, const_57)) {
        return __str((get_days(vrs->einddatum)-get_days(vrs->datum)));
    }
    else if (__eq(wat, const_36)) {
        return __str(((vrs->recept)->artikel)->gpk);
    }
    else if (__eq(wat, const_34)) {
        return __str(((vrs->recept)->artikel)->hpk);
    }
    else if (__eq(wat, const_70)) {
        return __str((vrs->recept)->zorgverzekeraar);
    }
    else if (__eq(wat, const_71)) {
        return ((vrs->recept)->artikel)->naam;
    }
    else {
        print(const_72, wat);
        ASSERT(False, 0);
    }
    return 0;
}

/**
class PatientEUInfo
*/

class_ *cl_PatientEUInfo;

void *PatientEUInfo::__init__(str *naam, str *omschrijving, PatientEU *criterium, str *wat) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->criterium = criterium;
    this->wat = wat;
    return NULL;
}

str *PatientEUInfo::__call__(Patient *p, __ss_int einddatum) {
    if ((this->criterium==NULL)) {
        return NULL;
    }
    this->criterium->__call__(p, einddatum);
    if (((this->criterium)->vrs==NULL)) {
        return NULL;
    }
    return vrs_info((this->criterium)->vrs, this->wat);
}

/**
class PatientLUInfo
*/

class_ *cl_PatientLUInfo;

void *PatientLUInfo::__init__(str *naam, str *omschrijving, VerstrekkingLijstCriterium *vrs, __ss_int datum_van, str *welke, str *wat, __ss_int datum_tot) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->vrslijst = vrs;
    this->datum_van = datum_van;
    this->datum_tot = datum_tot;
    this->welke = welke;
    this->wat = wat;
    return NULL;
}

str *PatientLUInfo::__call__(Patient *p, __ss_int einddatum) {
    list<Verstrekking *> *vrsn;
    __ss_int eind, i1, i2, start;
    Verstrekking *vrs;

    (this->vrslijst)->bepaal(p, einddatum);
    vrsn = (this->vrslijst)->vrsn;
    start = shift_months(einddatum, (-this->datum_van));
    eind = shift_months(einddatum, (-this->datum_tot));
    i1 = vrs_index(vrsn, start);
    i2 = vrs_index(vrsn, eind);
    if ((i1!=i2)) {
        if (__eq(this->welke, const_40)) {
            vrs = vrsn->__getfast__(i1);
        }
        else if (__eq(this->welke, const_41)) {
            vrs = vrsn->__getfast__((i2-__ss_int(1)));
        }
        else {
            ASSERT(False, 0);
        }
        return vrs_info(vrs, this->wat);
    }
    return 0;
}

/**
class PatientInteractieInfo
*/

class_ *cl_PatientInteractieInfo;

void *PatientInteractieInfo::__init__(str *naam, str *omschrijving, PatientCriterium *pat, PatientInteractie2 *criterium, str *wens, str *uniek) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    this->pat = pat;
    this->criterium = criterium;
    this->wens = wens;
    this->uniek = uniek;
    return NULL;
}

str *PatientInteractieInfo::__call__(Patient *p, __ss_int einddatum) {
    list<Period *> *prdn;
    __ss_bool __652, __653, __654, __655;

    if (((this->pat!=NULL) and __NOT(this->pat->__call__(p, einddatum)))) {
        return NULL;
    }
    if (((this->criterium!=NULL) and __NOT(this->criterium->__call__(p, einddatum)))) {
        return NULL;
    }
    ASSERT(___bool(__eq(this->wens, const_73)), 0);
    ASSERT(___bool(__eq(this->uniek, const_26)), 0);
    prdn = (this->criterium)->info_perioden;
    return __str(___max(1, __ss_int(0), list_comp_31(prdn)));
}

/**
class PatientDoseringInfo
*/

class_ *cl_PatientDoseringInfo;

void *PatientDoseringInfo::__init__(str *naam, str *omschrijving, PatientCriterium *pat, PatientDosering *criterium, str *wat, __ss_int decimalen) {
    this->naam = naam;
    this->omschrijving = omschrijving;
    return NULL;
}

str *PatientDoseringInfo::__call__(Patient *p, __ss_int einddatum) {
    ASSERT(False, 0);
    return const_24;
}

void __init() {
    __name__ = new str("__main__");

    const_0 = new str("let op, 2 jaar aan data benodigd!");
    const_1 = new str("9999999999");
    const_2 = new str("let op, 1 jaar aan data benodigd!");
    const_3 = __char_cache[79];
    const_4 = __char_cache[43];
    const_5 = new str("atc1");
    const_6 = new str("atc2");
    const_7 = new str("atc3");
    const_8 = new str("atc4");
    const_9 = new str("atc5");
    const_10 = new str("VRS SPLIT NIVO:");
    const_11 = new str("DDD");
    const_12 = new str("eenheid");
    const_13 = new str("R03");
    const_14 = new str("gebruiksdagen");
    const_15 = new str("berekent gemiddelde van 'iets' tussen afleverdatum eerste en laatste voorschrift,\012    met veel opties. correspondeert 1 op 1 met wokkel patient dosering criterium.");
    const_16 = new str("verstrekkingen");
    const_17 = new str("starter");
    const_18 = new str("stopper");
    const_19 = new str("patientnr");
    const_20 = new str("patient_in_teller");
    const_21 = new str("nawnr");
    const_22 = new str("info");
    const_23 = new str("waarde");
    const_24 = new str("");
    const_25 = new str("ja");
    const_26 = new str("nee");
    const_27 = new str("huisarts");
    const_28 = new str("specialist");
    const_29 = new str("specialist of overig");
    const_30 = new str("generiek");
    const_31 = new str("WEL");
    const_32 = new str("OF");
    const_33 = new str("atc");
    const_34 = new str("hpk");
    const_35 = new str("prk");
    const_36 = new str("gpk");
    const_37 = new str("geneesmiddelgroep");
    const_38 = new str("recent");
    const_39 = new str("aflevering");
    const_40 = new str("eerste");
    const_41 = new str("laatste");
    const_42 = new str(" inverteer perioden tussen start- en einddatum ");
    const_43 = new str("totaal");
    const_44 = new str("gemiddeld");
    const_45 = new str("verstrekking lijst");
    const_46 = __char_cache[32];
    const_47 = new str("vervolg uitgifte");
    const_48 = __char_cache[74];
    const_49 = __char_cache[78];
    const_50 = new str("groepen");
    const_51 = new str("percentage");
    const_52 = new str("%.2f");
    const_53 = new str("aantal");
    const_54 = new str("ddd");
    const_55 = new str("stuks");
    const_56 = new str("alle perioden");
    const_57 = new str("dagen");
    const_58 = new str(", ");
    const_59 = new str("van - tot");
    const_60 = new str(" - ");
    const_61 = new str("%02d-%02d-%04d");
    const_62 = new str("afleverdatum");
    const_63 = new str("einddatum");
    const_64 = new str("atc5-code");
    const_65 = new str("atc5-naam");
    const_66 = new str("%.3f");
    const_67 = new str("pdd");
    const_68 = new str("voorschrijver-agb");
    const_69 = new str("voorschrijversoort");
    const_70 = new str("zorgverzekeraar");
    const_71 = new str("artikelnaam");
    const_72 = new str("VRS INFO?");
    const_73 = new str("maximale lengte");
    const_74 = new str("__main__");
    const_75 = new str("C10");
    const_76 = new str("xx");
    const_77 = new str("123");
    const_78 = __char_cache[86];
    const_79 = __char_cache[50];
    const_80 = new str("B10");
    const_81 = new str("NIET");
    const_82 = new str("A10B C10");
    const_83 = new str("nivo");
    const_84 = __char_cache[77];

    CODES_VERVOLGUITGIFTE = (new list<__ss_int>(60,__ss_int(1),__ss_int(2),__ss_int(3),__ss_int(4),__ss_int(5),__ss_int(6),__ss_int(13),__ss_int(14),__ss_int(15),__ss_int(16),__ss_int(17),__ss_int(18),__ss_int(25),__ss_int(26),__ss_int(27),__ss_int(28),__ss_int(29),__ss_int(30),__ss_int(37),__ss_int(38),__ss_int(39),__ss_int(40),__ss_int(41),__ss_int(42),__ss_int(49),__ss_int(50),__ss_int(51),__ss_int(55),__ss_int(56),__ss_int(57),__ss_int(61),__ss_int(62),__ss_int(63),__ss_int(67),__ss_int(68),__ss_int(69),__ss_int(73),__ss_int(74),__ss_int(75),__ss_int(79),__ss_int(80),__ss_int(81),__ss_int(85),__ss_int(86),__ss_int(87),__ss_int(91),__ss_int(92),__ss_int(93),__ss_int(145),__ss_int(146),__ss_int(147),__ss_int(148),__ss_int(149),__ss_int(150),__ss_int(151),__ss_int(152),__ss_int(153),__ss_int(154),__ss_int(155),__ss_int(156)));
    __13 = _month_days();
    __SS_UNPACK_CHECK(__13, 2);
    MONTH_DAYS = __13->__getfirst__();
    DAYS_YMD = __13->__getsecond__();
    cl_Groep = new class_("Groep");
    cl_ATC = new class_("ATC");
    cl_Artikel = new class_("Artikel");
    cl_Recept = new class_("Recept");
    cl_Verstrekking = new class_("Verstrekking");
    cl_Patient = new class_("Patient");
    default_0 = NULL;
    default_1 = NULL;
    default_2 = NULL;
    default_3 = NULL;
    default_4 = NULL;
    default_5 = NULL;
    default_6 = NULL;
    default_7 = NULL;
    default_8 = NULL;
    default_9 = NULL;
    default_10 = NULL;
    default_11 = NULL;
    default_12 = NULL;
    default_13 = NULL;
    cl_Middel = new class_("Middel");
    default_14 = NULL;
    default_15 = NULL;
    default_16 = NULL;
    cl_MiddelGroep = new class_("MiddelGroep");
    cl_Marker = new class_("Marker");
    cl_Period = new class_("Period");
    NO_PERIODS = (__ss_list<void *>());
    default_17 = (__ss_list<list<Verstrekking *> *>());
    default_18 = NULL;
    default_19 = NULL;
    default_20 = NULL;
    default_21 = NULL;
    default_22 = NULL;
    cl_Rapportage = new class_("Rapportage");
    default_23 = NULL;
    default_24 = NULL;
    default_25 = NULL;
    default_26 = NULL;
    cl_Indicator = new class_("Indicator");
    default_27 = NULL;
    default_28 = NULL;
    cl_Indicatoren = new class_("Indicatoren");
    default_29 = NULL;
    default_30 = NULL;
    default_31 = NULL;
    default_32 = NULL;
    cl_IndicatorLijst = new class_("IndicatorLijst");
    default_33 = NULL;
    default_34 = NULL;
    default_35 = NULL;
    default_36 = NULL;
    cl_PatientOverzicht = new class_("PatientOverzicht");
    default_37 = NULL;
    default_38 = NULL;
    default_39 = NULL;
    default_40 = NULL;
    cl_CorrectieTerm = new class_("CorrectieTerm");
    default_41 = NULL;
    default_42 = NULL;
    default_43 = NULL;
    default_44 = NULL;
    default_45 = NULL;
    cl_Correctie = new class_("Correctie");
    cl_VerstrekkingCriterium = new class_("VerstrekkingCriterium");
    default_46 = NULL;
    default_47 = NULL;
    default_48 = NULL;
    default_49 = NULL;
    default_50 = NULL;
    default_51 = NULL;
    default_52 = NULL;
    default_53 = NULL;
    cl_VerstrekkingEigenschappen = new class_("VerstrekkingEigenschappen");
    cl_VerstrekkingLogischTerm = new class_("VerstrekkingLogischTerm");
    cl_VerstrekkingLogisch = new class_("VerstrekkingLogisch");
    cl_VerstrekkingLijstCriterium = new class_("VerstrekkingLijstCriterium");
    default_54 = NULL;
    default_55 = NULL;
    default_56 = NULL;
    default_57 = NULL;
    cl_VerstrekkingLijstEigenschappen = new class_("VerstrekkingLijstEigenschappen");
    default_58 = NULL;
    cl_VerstrekkingLijstSamengesteld = new class_("VerstrekkingLijstSamengesteld");
    cl_PatientCriterium = new class_("PatientCriterium");
    default_59 = NULL;
    default_60 = NULL;
    default_61 = NULL;
    default_62 = NULL;
    default_63 = const_38;
    default_64 = NULL;
    default_65 = NULL;
    cl_PatientEigenschappen = new class_("PatientEigenschappen");
    default_66 = NULL;
    default_67 = NULL;
    default_68 = NULL;
    cl_PatientLogisch = new class_("PatientLogisch");
    default_69 = NULL;
    default_70 = NULL;
    default_71 = NULL;
    default_72 = NULL;
    cl_PatientLogischTerm = new class_("PatientLogischTerm");
    default_73 = NULL;
    default_74 = NULL;
    default_75 = NULL;
    default_76 = NULL;
    default_77 = NULL;
    cl_PatientAfleveringen = new class_("PatientAfleveringen");
    default_78 = NULL;
    default_79 = NULL;
    default_80 = NULL;
    default_81 = NULL;
    cl_PatientAfleverContext = new class_("PatientAfleverContext");
    default_82 = NULL;
    default_83 = NULL;
    cl_PatientGaten = new class_("PatientGaten");
    default_84 = NULL;
    default_85 = NULL;
    default_86 = NULL;
    default_87 = NULL;
    default_88 = NULL;
    cl_PatientDosering = new class_("PatientDosering");
    default_89 = NULL;
    default_90 = NULL;
    default_91 = NULL;
    cl_PatientPolyfarmacie = new class_("PatientPolyfarmacie");
    cl_PatientTherapietrouw2 = new class_("PatientTherapietrouw2");
    default_92 = NULL;
    default_93 = NULL;
    default_94 = NULL;
    default_95 = NULL;
    cl_PatientGebruik = new class_("PatientGebruik");
    default_96 = NULL;
    default_97 = NULL;
    default_98 = NULL;
    default_99 = NULL;
    cl_PatientInteractie2 = new class_("PatientInteractie2");
    default_100 = NULL;
    default_101 = NULL;
    default_102 = NULL;
    default_103 = NULL;
    default_104 = NULL;
    cl_PatientEU = new class_("PatientEU");
    cl_PatientPuntenTerm = new class_("PatientPuntenTerm");
    cl_PatientPunten = new class_("PatientPunten");
    default_105 = NULL;
    default_106 = NULL;
    cl_PatientInformatieInfo = new class_("PatientInformatieInfo");
    cl_PatientInfo = new class_("PatientInfo");
    default_107 = NULL;
    default_108 = NULL;
    cl_PatientPatientInfo = new class_("PatientPatientInfo");
    default_109 = NULL;
    cl_PatientPatientenInfo = new class_("PatientPatientenInfo");
    default_110 = NULL;
    default_111 = NULL;
    cl_PatientPolyfarmacieInfo = new class_("PatientPolyfarmacieInfo");
    default_112 = NULL;
    default_113 = NULL;
    cl_PatientTherapietrouwNieuwInfo = new class_("PatientTherapietrouwNieuwInfo");
    default_114 = NULL;
    default_115 = NULL;
    default_116 = NULL;
    default_117 = NULL;
    cl_PatientVerstrekkingenInfo = new class_("PatientVerstrekkingenInfo");
    default_118 = NULL;
    default_119 = NULL;
    default_120 = NULL;
    default_121 = NULL;
    cl_PatientPeriodenInfo = new class_("PatientPeriodenInfo");
    default_122 = NULL;
    default_123 = NULL;
    cl_PatientEUInfo = new class_("PatientEUInfo");
    default_124 = NULL;
    default_125 = NULL;
    default_126 = NULL;
    cl_PatientLUInfo = new class_("PatientLUInfo");
    default_127 = NULL;
    default_128 = NULL;
    default_129 = NULL;
    default_130 = NULL;
    cl_PatientInteractieInfo = new class_("PatientInteractieInfo");
    default_131 = NULL;
    default_132 = NULL;
    default_133 = NULL;
    cl_PatientDoseringInfo = new class_("PatientDoseringInfo");
    if (__eq(__wokl__::__name__, const_74)) {
        set_atcs((new list<str *>(1,const_75)));
        set_pref_beleid((new dict<tuple<__ss_int> *, list<tuple<__ss_int> *> *>(1, (new tuple2<tuple<__ss_int> *, list<tuple<__ss_int> *> *>(2,(__ss_tuple_int(2,__ss_int(1),__ss_int(2))),(new list<tuple<__ss_int> *>(1,(__ss_tuple_int(2,__ss_int(1),__ss_int(2))))))))));
        set_atc5_naam((new dict<str *, str *>(1, (new tuple<str *>(2,const_24,const_24)))));
        a = (new Artikel(__ss_int(1), const_75, __ss_int(12), __ss_int(13), __ss_int(14), __ss_int(15), __ss_int(16), __ss_float(1.0), __ss_int(1), const_76));
        r = (new Recept(__wokl__::a, __ss_int(20200101), __ss_int(20200101), __ss_int(1), True, __ss_int(1), __ss_int(1), __ss_int(1), __ss_float(1.0), __ss_int(1), __ss_float(1.0), __ss_float(1.0), __ss_float(1.0), __ss_int(1)));
        v = (new Verstrekking(__wokl__::r));
        p = (new Patient(__ss_int(260100), const_77, const_78, __ss_int(1990), (new list<Verstrekking *>(1,__wokl__::v)), __ss_int(20240101)));
        g = (new Groep((new dict<tuple2<__ss_int, str *> *, Patient *>(1, (new tuple2<tuple2<__ss_int, str *> *, Patient *>(2,(new tuple2<__ss_int, str *>(2,__ss_int(1),const_79)),__wokl__::p))))));
        m = (new Middel(const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24, const_24));
        mg = (new MiddelGroep(const_24, const_24, (new list<Middel *>(1,__wokl__::m))));
        atc = (new ATC(const_80));
        __wokl__::atc->add_mgroep(__wokl__::mg);
        __wokl__::atc->clear_mgroepen();
        veig = ((VerstrekkingCriterium *)((new VerstrekkingEigenschappen(const_24, const_24, const_25, const_27, const_24, __wokl__::mg, (-__ss_float(1.0)), (-__ss_float(1.0)), (-__ss_float(1.0)), (-__ss_float(1.0)), (-__ss_int(1)), (-__ss_int(1)), const_24, const_24, const_25))));
        vlterm = (new VerstrekkingLogischTerm(const_24, const_24, const_81, __wokl__::veig));
        veig = ((VerstrekkingCriterium *)((new VerstrekkingLogisch(const_24, const_24, const_32, (new list<VerstrekkingLogischTerm *>(1,__wokl__::vlterm))))));
        correctie_term = (new CorrectieTerm(const_24, const_24, const_33, const_82, (-__ss_int(1)), __ss_float(1.0)));
        correctie = (new Correctie(const_24, const_24, const_83, __ss_int(1), __ss_float(1.0), (-__ss_int(1)), (-__ss_int(1)), (-__ss_float(1.0)), (-__ss_float(1.0)), const_24, (new list<CorrectieTerm *>(1,__wokl__::correctie_term))));
        vcrits = (__ss_list<VerstrekkingLijstCriterium *>());
        vcrit = ((VerstrekkingLijstCriterium *)((new VerstrekkingLijstEigenschappen(const_24, const_24, __wokl__::mg, __wokl__::correctie, __ss_int(0), (-__ss_int(1)), __wokl__::veig))));
        vcrit = ((VerstrekkingLijstCriterium *)((new VerstrekkingLijstSamengesteld(const_24, const_24, (new list<VerstrekkingLijstCriterium *>(1,__wokl__::vcrit)), const_24))));
        __wokl__::vcrit->setup_einddatum(__ss_int(1234));
        __wokl__::vcrits->append(__wokl__::vcrit);
        ttcrit = (new PatientTherapietrouw2(const_24, const_24, __wokl__::vcrits, const_24, (-__ss_int(1)), __ss_int(0), (-__ss_float(1.0)), (-__ss_float(1.0))));
        intcrit = (new PatientInteractie2(const_24, const_24, __wokl__::vcrits, __wokl__::vcrits, (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), __ss_int(0), const_24, const_43, (-__ss_int(1))));
        polycrit = (new PatientPolyfarmacie(const_24, const_24, __wokl__::vcrits, (-__ss_int(1)), __ss_int(0), (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), const_43, const_24, (-__ss_int(1)), __ss_int(0), (-__ss_int(1)), (-__ss_int(1)), const_24));
        eucrit = (new PatientEU(const_24, const_24, __wokl__::vcrit, __ss_int(12), __ss_int(0), __ss_int(12), const_24, const_25, __wokl__::veig));
        doscrit = (new PatientDosering(const_24, const_24, __wokl__::vcrit, (-__ss_int(1)), __ss_int(0), const_24, (-__ss_float(1.0)), (-__ss_float(1.0)), const_24, const_24, const_24, const_24, (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1))));
        eig = ((PatientCriterium *)((new PatientEigenschappen(const_24, const_24, const_25, const_25, (-__ss_int(1)), (-__ss_int(1)), const_38, const_84, const_25))));
        eig = ((PatientCriterium *)(__wokl__::eucrit));
        eig = ((PatientCriterium *)((new PatientGebruik(const_24, const_24, __wokl__::vcrit, const_43, (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), __ss_int(0), const_31, (-__ss_float(1.0)), (-__ss_float(1.0))))));
        eig = ((PatientCriterium *)(__wokl__::intcrit));
        eig = ((PatientCriterium *)((new PatientAfleveringen(const_24, const_24, __wokl__::vcrit, (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), __ss_int(0), (-__ss_int(1)), (-__ss_float(1.0)), (-__ss_float(1.0)), (-__ss_float(1.0)), (-__ss_float(1.0)), const_24, __wokl__::veig, const_24))));
        eig = ((PatientCriterium *)((new PatientLogischTerm(const_24, const_24, const_31, __wokl__::eig))));
        eig = ((PatientCriterium *)((new PatientLogisch(const_24, const_24, const_32, (new list<PatientCriterium *>(1,__wokl__::eig))))));
        eig = ((PatientCriterium *)(__wokl__::ttcrit));
        eig = ((PatientCriterium *)((new PatientGaten(const_24, const_24, __wokl__::vcrit, (-__ss_int(1)), __ss_int(0), const_43, (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1)), (-__ss_int(1))))));
        eig = ((PatientCriterium *)((new PatientPunten(const_24, const_24, (new list<PatientPuntenTerm *>(1,(new PatientPuntenTerm(const_24, const_24, __wokl__::eig, __ss_int(2))))), __ss_int(6), __ss_int(8)))));
        eig = ((PatientCriterium *)((new PatientAfleverContext(const_24, const_24, __wokl__::vcrit, (-__ss_int(1)), __ss_int(0), (-__ss_int(1)), (-__ss_int(1)), const_31, const_39, (-__ss_int(1)), (-__ss_int(1)), __wokl__::vcrit, (-__ss_int(1)), __wokl__::eig))));
        eig = ((PatientCriterium *)(__wokl__::doscrit));
        eig = ((PatientCriterium *)(__wokl__::polycrit));
        __wokl__::eig->setup_einddatum(__ss_int(4321));
        patinfo = ((PatientInfo *)((new PatientPatientInfo(const_24, const_24, __wokl__::eig))));
        patinfo = ((PatientInfo *)((new PatientPatientenInfo(const_24, const_24, __wokl__::eig))));
        patinfo = ((PatientInfo *)((new PatientPolyfarmacieInfo(const_24, const_24, __wokl__::polycrit, const_24))));
        patinfo = ((PatientInfo *)((new PatientTherapietrouwNieuwInfo(const_24, const_24, __wokl__::ttcrit, const_24, __ss_int(2)))));
        patinfo = ((PatientInfo *)((new PatientVerstrekkingenInfo(const_24, const_24, __wokl__::vcrit, __wokl__::eig, const_24, (-__ss_int(1)), __ss_int(0), __wokl__::veig))));
        patinfo = ((PatientInfo *)((new PatientPeriodenInfo(const_24, const_24, __wokl__::eig, __wokl__::vcrit, const_24, const_24, (-__ss_int(1)), __ss_int(0)))));
        patinfo = ((PatientInfo *)((new PatientEUInfo(const_24, const_24, __wokl__::eucrit, const_24))));
        patinfo = ((PatientInfo *)((new PatientLUInfo(const_24, const_24, __wokl__::vcrit, (-__ss_int(1)), const_24, const_24, __ss_int(0)))));
        patinfo = ((PatientInfo *)((new PatientInteractieInfo(const_24, const_24, __wokl__::eig, __wokl__::intcrit, const_24, const_24))));
        patinfo = ((PatientInfo *)((new PatientDoseringInfo(const_24, const_24, __wokl__::eig, __wokl__::doscrit, const_24, __ss_int(2)))));
        info = (new PatientInformatieInfo(const_24, const_24, (new list<PatientInfo *>(1,__wokl__::patinfo))));
        ind = (new Indicator(const_24, const_24, __wokl__::eig, __wokl__::eig, const_24));
        inds = (new Indicatoren(const_24, const_24, (new list<Indicator *>(1,__wokl__::ind))));
        ovz = ((Rapportage *)((new IndicatorLijst(const_24, const_24, __wokl__::inds, __wokl__::eig, __wokl__::eig, const_24, __wokl__::info))));
        ovz = ((Rapportage *)((new PatientOverzicht(const_24, const_24, __wokl__::eig, __wokl__::eig, __wokl__::info))));
        __wokl__::ovz->setup((new list<MiddelGroep *>(1,__wokl__::mg)), __wokl__::vcrits);
        __wokl__::ovz->__call__(__wokl__::g, __ss_int(20240101));
    }
}

} // module namespace

int main(int __ss_argc, char **__ss_argv) {
    __shedskin__::__init();
    __collections__::__init();
    __sys__::__init(__ss_argc, __ss_argv);
    __shedskin__::__start(__wokl__::__init);
}
