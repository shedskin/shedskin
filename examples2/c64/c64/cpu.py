#!/usr/bin/env python
# I, Danny Milosavljevic, hereby place this file into the public domain.
# -*- coding: utf-8 -*-

# TODO wrap into zero page with IND addressing mode

import sys

from . import mmu
from . import tape
from .symbols import *

def err(message):
    print("error: %s" % message, file=sys.stderr)
    sys.exit(1)
    return 42

def to_signed_byte(value):
    return value if value < 0x80 else -(256 - value)

class Registers(object):
    def __init__(self): # FIXME default values...
        self.PC = 0
        self.SP = 0xFF
        self.X = 0
        self.Y = 0
        self.A = 0

known_routines = {
    0xE000: 'BASIC-Funktion EXP \xe2\x80\x93 Fortsetzung von $BFFF',
    0xE043: 'Polynomberechnung',
    0xE08D: '2 Konstanten f\xc3\xbcr RND',
    0xE097: 'BASIC-Funktion RND',
    0xE0F9: 'Fehlerauswertung nach I/O-Routinen in BASIC',
    0xE10C: 'PETSCII-Zeichen ausgeben mit CHROUT, Wert mu\xc3\x9f im Akku stehen',
    0xE112: 'PETSCII-Zeichen holen mit CHRIN (Eingabeger\xc3\xa4t w\xc3\xa4hlbar)',
    0xE118: 'Ausgabeger\xc3\xa4t setzen mit CHKOUT',
    0xE11E: 'Eingabeger\xc3\xa4t setzen mit CHKIN',
    0xE124: 'Zeichen aus Tastaturpuffer in Akku holen mit GETIN',
    0xE12A: 'BASIC-Befehl SYS',
    0xE156: 'BASIC-Befehl SAVE',
    0xE165: 'BASIC-Befehl VERIFY',
    0xE168: 'BASIC-Befehl LOAD',
    0xE1BE: 'BASIC-Befehl OPEN',
    0xE1C7: 'BASIC-Befehl CLOSE',
    0xE1D4: 'Parameter f\xc3\xbcr LOAD, SAVE und VERIFY aus BASIC-Text holen',
    0xE200: 'Pr\xc3\xbcft auf Komma und holt 1-Byte-Wert nach X',
    0xE206: 'Pr\xc3\xbcft auf weitere Zeichen',
    0xE20E: 'Pr\xc3\xbcft auf Komma und weitere Zeichen',
    0xE219: 'Parameter f\xc3\xbcr OPEN und CLOSE holen',
    0xE264: 'BASIC-Funktion COS',
    0xE26B: 'BASIC-Funktion SIN',
    0xE2B4: 'BASIC-Funktion TAN',
    0xE2E0: 'Trig. Konstante 1.570796327 = PI/2',
    0xE2E5: 'Trig. Konstante 6.28318531 = 2*PI',
    0xE2EA: 'Trig. Konstante 0.25',
    0xE2EF: 'Trig. Konstante 5 = Polynomgrad, dann 6 Koeffizienten',
    0xE2F0: 'Trig. Konstante -14.3813907',
    0xE2F5: 'Trig. Konstante 42.0077971',
    0xE2FA: 'Trig. Konstante -76.7041703',
    0xE2FF: 'Trig. Konstante 81.6052237',
    0xE304: 'Trig. Konstante -41.3417021',
    0xE309: 'Trig. Konstante 6.28318531 = 2*PI',
    0xE30E: 'BASIC-Funktion ATN',
    0xE33E: 'ATN Konstante 11 = Polynomgrad, dann 12 Koeffizienten',
    0xE33F: 'ATN Konstante -0.00068479391',
    0xE344: 'ATN Konstante 0.00485094216',
    0xE349: 'ATN Konstante -0.161117018',
    0xE34E: 'ATN Konstante 0.034209638',
    0xE353: 'ATN Konstante -0.0542791328',
    0xE358: 'ATN Konstante 0.0724571965',
    0xE35D: 'ATN Konstante -0.0898023954',
    0xE362: 'ATN Konstante 0.110932413',
    0xE367: 'ATN Konstante -0.142839808',
    0xE36C: 'ATN Konstante 0.19999912',
    0xE371: 'ATN Konstante -0.333333316',
    0xE376: 'ATN Konstante 1.00',
    0xE37B: 'BASIC-Warmstart nach RUNSTOP/RESTORE bzw. BRK',
    0xE394: 'BASIC-Kaltstart (Reset)',
    0xE3A2: 'Kopie der CHRGET-Routine f\xc3\xbcr die Zeropage',
    0xE3BA: 'Konstante 0.811635157 = Anfangswert f\xc3\xbcr RND-Funktion:',
    0xE3BF: 'RAM initialisieren f\xc3\xbcr BASIC',
    0xE422: 'Einschaltmeldung ausgeben',
    0xE447: 'Tabelle der BASIC-Vektoren (f\xc3\xbcr $0300)',
    0xE453: 'BASIC-Vektoren aus der Tabelle laden nach $0300 ff.',
    0xE45F: 'Text der Einschaltmeldungen',
    0xE4AD: 'BASIC-CHKOUT Routine',
    0xE4B7: 'Unbenutzter Bereich (ist mit $AA gef\xc3\xbcllt)',
    0xE4D3: 'Patch f\xc3\xbcr RS-232-Routinen',
    0xE4DA: 'Schreibt Hintergrundfarbe in Farbram (von CLR benutzt,',
    0xE4E0: 'Pause (8.5 Sec.), nachdem eine Datei auf der Kassette',
    0xE4EC: 'Timerkonstanten f\xc3\xbcr RS-232 Baud Rate, PAL-Version',
    0xE500: 'IOBASE: Gibt die Basisadresse des CIA in X/Y aus',
    0xE505: 'SCREEN: Bildschirmgr\xc3\xb6\xc3\x9fe einlesen: 40 Spalten in X, 25 Zeilen',
    0xE50A: 'PLOT: Setzt/holt Cursorposition: X = Zeile, Y = Spalte',
    0xE518: 'Initialisiert I/O (Bildschirm und Tastatur)',
    0xE544: 'L\xc3\xb6scht Bildschirmspeicher',
    0xE566: 'Cursor Home: bringt Cursor in Grundposition (oben links)',
    0xE56C: 'berechnet die Cursorposition, setzt Bildschirmzeiger',
    0xE59A: 'Videocontroller initialisieren und Cursor Home (wird nicht',
    0xE5A0: 'Videocontroller initialisieren',
    0xE5B4: 'Holt ein Zeichen aus dem Tastaturpuffer',
    0xE5CA: 'Wartet auf Tastatureingabe',
    0xE632: 'Holt ein Zeichen vom Bildschirm',
    0xE684: 'Testet auf Hochkomma und kehrt ggf. das Hochkomma-Flag $D4',
    0xE691: 'Gibt Zeichen auf Bildschirm aus',
    0xE6B6: 'Springt in neue Zeile bzw. f\xc3\xbcgt neue Zeile ein',
    0xE701: 'R\xc3\xbcckschritt in vorhergehende Zeile',
    0xE716: 'Ausgabe (des Zeichens in A) auf Bildschirm incl.',
    0xE87C: 'N\xc3\xa4chste Zeile setzen, ggf. Scrollen',
    0xE891: 'Aktion nach Taste RETURN',
    0xE8A1: 'Cursor zur vorigen Zeile, wenn er am Zeilenanfang r\xc3\xbcckw\xc3\xa4rts',
    0xE8B3: 'Cursor zur n\xc3\xa4chsten Zeile, wenn er am Zeilenende vorw\xc3\xa4rts',
    0xE8CB: 'pr\xc3\xbcft, ob Zeichen in A einer der 16 Farbcodes ist und setzt',
    0xE8DA: 'Tabelle der Farbcodes \xe2\x80\x93 16 Bytes',
    0xE8EA: 'Bildschirm scrollen, schiebt Bildschirm um eine Zeile nach',
    0xE965: 'F\xc3\xbcgt leere Fortsetzungzeile ein',
    0xE9C8: 'Schiebt Zeile nach oben',
    0xE9E0: 'Berechnet Zeiger auf Farbram und Startadresse des',
    0xE9F0: 'Setzt Zeiger auf Bildschirmspeicher f\xc3\xbcr Zeile X',
    0xE9FF: 'L\xc3\xb6scht eine Bildschirmzeile (Zeile in X)',
    0xEA13: 'Setzt Blinkz\xc3\xa4hler und Farbramzeiger',
    0xD2AC: 'Schreibt ein Zeichen mit Farbe auf dem Bildschirm',
    0xEA24: 'Berechnet den Farbram-Zeiger zur aktuellen Cursorposition',
    0xEA31: 'Interrupt-Routine, verarbeitet alle IRQ-Interrupts',
    0xEA81: 'Holt A/X/Y aus dem Stapel zur\xc3\xbcck und beendet IRQ',
    0xEA87: 'SCNKEY: Tastaturabfrage',
    0xEB48: 'Pr\xc3\xbcft auf Shift, Control, Commodore',
    0xEB79: 'Zeiger auf Tastatur-Dekodiertabelle f\xc3\xbcr Umwandlung der',
    0xEB81: 'Dekodiertabelle ungeshiftet',
    0xEBC2: 'Dekodiertabelle geshiftet',
    0xEC03: 'Dekodiertabelle mit Commodore-Taste',
    0xEC44: 'Pr\xc3\xbcft auf PETSCII-Codes f\xc3\xbcr Steuerzeichen',
    0xEC78: 'Dekodiertabelle mit Control-Taste',
    0xECB9: 'Konstanten f\xc3\xbcr Videocontroller',
    0xECE7: 'Text "LOAD"(CR)"RUN"(CR) f\xc3\xbcr den Tastaturpuffer nach Dr\xc3\xbccken',
    0xECF0: 'Tabelle der LSB der Bildschirmzeilen-Anf\xc3\xa4nge',
    0xED09: 'TALK: Sendet TALK auf seriellem Bus',
    0xED0C: 'LISTEN: Sendet LISTEN auf seriellen Bus',
    0xED40: 'Gibt ein Byte (aus $95) auf seriellen Bus aus',
    0xEDB9: 'SECOND: Sendet Sekund\xc3\xa4radresse nach LISTEN',
    0xEDBE: 'Gibt ATN frei',
    0xEDC7: 'TKSA: Gibt Sekund\xc3\xa4radresse nach TALK aus',
    0xEDDD: 'CIOUT: Gibt ein Byte auf seriellem Bus aus',
    0xEDEF: 'UNTLK: Sendet UNTALK auf seriellem Bus',
    0xEDFE: 'UNLSN: Sendet UNLISTEN auf seriellem Bus',
    0xEE13: 'ACPTR: Holt ein Zeichen vom seriellen Bus',
    0xEE85: 'Clock-Leitung low',
    0xEE8E: 'Clock-Leitung high',
    0xEE97: 'Data-Leitung low',
    0xEEA0: 'Data-Leitung high',
    0xEEA9: 'Holt Bit vom seriellen Bus ins Carry-Flag',
    0xEEB3: 'Verz\xc3\xb6gerung 1 ms',
    0xEEBB: 'RS-232 Ausgabe',
    0xEF06: 'Sendet ein Byte',
    0xEF2E: 'RS-232 Fehlerbehandlung',
    0xEF4A: 'Berechnet Anzahl der zu sendenden Bits +1',
    0xEF59: 'Sammelt Bits zu einem Byte',
    0xEF7E: 'Erm\xc3\xb6glicht den Empfang eines Bytes w\xc3\xa4hrend NMI',
    0xEF90: 'Testet Startbit nach Empfang',
    0xEFE1: 'Ausgabe auf RS-232',
    0xF017: 'Gibt ein RS-232-Zeichen aus',
    0xF04D: 'Initialisiert RS-232 f\xc3\xbcr Eingabe',
    0xF086: 'Liest ein RS-232-Zeichen ein',
    0xF0A4: 'Sch\xc3\xbctzt seriellen Bus und Bandbetrieb vor NMIs',
    0xF0BD: 'Tabelle der I/O-Meldungen',
    0xF12B: 'Gibt eine I/O-Meldung der Tabelle aus (Y als Offset)',
    0xF13E: 'GETIN: Holt ein Zeichen vom Eingabeger\xc3\xa4t',
    0xF157: 'CHRIN: Eingabe eines Zeichens',
    0xF199: 'Holt ein Zeichen vom Band / vom seriellen Bus / von RS-232',
    0xF1CA: 'CHROUT: Gibt ein Zeichen aus',
    0xF20E: 'CHKIN: \xc3\x96ffnet Eingabekanal',
    0xF250: 'CHKOUT: \xc3\x96ffnet Ausgabekanal',
    0xF291: 'CLOSE: Schlie\xc3\x9ft Datei, logische Dateinummer im Akku',
    0xF30F: 'Sucht logische Datei (Nummer in X)',
    0xF31F: 'Setzt Datei-Parameter',
    0xF32F: 'CLALL; Schlie\xc3\x9ft alle Ein-/Ausgabe-Kan\xc3\xa4le',
    0xF333: 'CLRCHN: Schlie\xc3\x9ft aktiven I/O-Kanal',
    0xF34A: 'OPEN: Datei \xc3\xb6ffnen (Dateinummer in $B8)',
    0xF3D5: 'Datei \xc3\xb6ffnen auf seriellem Bus',
    0xF409: 'Datei \xc3\xb6ffnen auf RS-232',
    0xF49E: 'LOAD: Daten ins RAM laden von Peripherieger\xc3\xa4ten, aber nicht',
    0xF4B8: 'Laden vom seriellen Bus',
    0xF539: 'Laden f\xc3\xbcr Band',
    0xF5AF: 'Gibt Meldung "SEARCHING" bzw. "SEARCHING FOR" aus',
    0xF5C1: 'Dateiname ausgeben',
    0xF5D2: '"LOADING" bzw. "VERIFYING" ausgeben',
    0xF5DD: 'SAVE: Daten vom RAM auf Peripherieger\xc3\xa4te sichern, aber nicht',
    0xF5FA: 'Speichern auf seriellen Bus',
    0xF659: 'Speichern auf Band',
    0xF68F: '"SAVING" ausgeben',
    0xF69B: 'UDTIM: Erh\xc3\xb6ht TIME und fragt STOP-Taste ab',
    0xF6DD: 'RDTIM: Uhrzeit lesen (TIME)',
    0xF6E4: 'SETTIM: Setzt Uhrzeit (TIME)',
    0xF6ED: 'STOP: Fragt STOP-Taste ab',
    0xF6FB: 'Ausgabe der Fehlermeldung "TOO MANY FILES"',
    0xF6FE: 'Ausgabe der Fehlermeldung "FILE OPEN"',
    0xF701: 'Ausgabe der Fehlermeldung "FILE NOT OPEN"',
    0xF704: 'Ausgabe der Fehlermeldung "FILE NOT FOUND"',
    0xF707: 'Ausgabe der Fehlermeldung "DEVICE NOT PRESENT"',
    0xF70A: 'Ausgabe der Fehlermeldung "NOT INPUT FILE"',
    0xF70D: 'Ausgabe der Fehlermeldung "NOT OUTPUT FILE"',
    0xF710: 'Ausgabe der Fehlermeldung "MISSING FILENAME"',
    0xF713: 'Ausgabe der Fehlermeldung "ILLEGAL DEVICE NUMBER"',
    0xF72C: 'L\xc3\xa4dt n\xc3\xa4chsten Kassettenvorspann',
    0xF76A: 'Schreibt Kassettenvorspann',
    0xF7D0: 'Holt Startadresse des Bandpuffers und pr\xc3\xbcft, ob g\xc3\xbcltig',
    0xF7D7: 'Setzt Start- und End-Zeiger des Bandpuffers',
    0xF7EA: 'L\xc3\xa4dt Kassettenvorspann zum angegebenen Dateinamen',
    0xF80D: 'Erh\xc3\xb6ht Bandpufferzeiger',
    0xF817: 'Fragt Bandtaste f\xc3\xbcr Lesen ab und gibt Meldungen aus',
    0xF82E: 'Pr\xc3\xbcft ob Bandtaste gedr\xc3\xbcckt',
    0xF838: 'Wartet auf Bandtaste f\xc3\xbcr Schreiben, gibt ggf. Meldung aus',
    0xF841: 'Liest Block vom Band',
    0xF84A: 'L\xc3\xa4dt vom Band',
    0xF864: 'Schreiben auf Band vorbereiten',
    0xF875: 'Allgemeine Routine f\xc3\xbcr Lesen und Schreiben vom/auf Band',
    0xF8D0: 'Pr\xc3\xbcft auf STOP-Taste w\xc3\xa4hrend Kassetten-Nutzung',
    0xF8E2: 'Band f\xc3\xbcr Lesen vorbereiten',
    0xF92C: 'Band lesen; IRQ-Routine',
    0xFA60: 'L\xc3\xa4dt/pr\xc3\xbcft Zeichen vom Band',
    0xFB8E: 'Setzt Bandzeiger auf Programmstart',
    0xFB97: 'Initialisiert Bitz\xc3\xa4hler f\xc3\xbcr serielle Ausgabe',
    0xFBA6: 'Schreiben auf Band',
    0xFBCD: 'Start der IRQ-Routine f\xc3\xbcr Band schreiben',
    0xFC93: 'Beendet Rekorderbetrieb',
    0xFCB8: 'Setzt IRQ-Vektor zur\xc3\xbcck auf Standard',
    0xFCCA: 'Schaltet Rekordermotor aus',
    0xFCD1: 'Pr\xc3\xbcft, ob Endadresse erreicht (Vergleich $AC/$AD mit',
    0xFCDB: 'Erh\xc3\xb6ht Adresszeiger',
    0xFCE2: 'RESET \xe2\x80\x93 Routine',
    0xFD02: 'Pr\xc3\xbcft auf Steckmodul',
    0xFD10: 'Text "CBM80" f\xc3\xbcr Modulerkennung',
    0xFD15: 'RESTOR: R\xc3\xbccksetzen der Ein- und Ausgabe-Vektoren auf',
    0xFD1A: 'VECTOR: Setzt Vektoren abh\xc3\xa4ngig von X/Y',
    0xFD30: 'Tabelle der Kernal-Vektoren f\xc3\xbcr $0314-$0333 (16-mal 2 Byte)',
    0xFD50: 'RAMTAS: Initialisiert Zeiger f\xc3\xbcr den Arbeitsspeicher',
    0xFD9B: 'Tabelle der IRQ-Vektoren (4-mal 2 Byte)',
    0xFDA3: 'IOINIT: Interrupt-Initialisierung',
    0xFDDD: 'Setzt Timer',
    0xFDF9: 'SETNAM: Setzt Parameter f\xc3\xbcr Dateinamen',
    0xFE00: 'SETLFS: Setzt Parameter f\xc3\xbcr aktive Datei',
    0xFE07: 'READST: Holt I/O-Status',
    0xFE18: 'SETMSG: Setzt Status als Flag f\xc3\xbcr Betriebssystem-Meldungen',
    0xFE21: 'SETTMO: Setzt Timeout f\xc3\xbcr seriellen Bus',
    0xFE25: 'Liest/setzt Obergrenze des BASIC-RAM (nach/von X/Y)',
    0xFE34: 'MEMBOT: Liest/setzt Untergrenze des BASIC-RAM (nach/von X/Y)',
    0xFE43: 'NMI Einsprung',
    0xFE47: 'Standard-NMI-Routine',
    0xFE66: 'Warmstart BASIC (BRK-Routine)',
    0xFEBC: 'Interrupt-Ende (holt Y, X, A vom Stack und RTI)',
    0xFEC2: 'Tabelle mit Timerkonstanten f\xc3\xbcr RS-232 Baudrate,',
    0xFED6: 'NMI-Routine f\xc3\xbcr RS-232 Eingabe',
    0xFF07: 'NMI-Routine f\xc3\xbcr RS-232 Ausgabe',
    0xFF43: 'IRQ-Einsprung aus Bandroutine',
    0xFF48: 'IRQ-Einsprung',
    0xFF5B: 'CINT: Video-Reset',
    0xFF80: 'Kernal Versions-Nummer',
    0xFF81: 'Kernal-Vektoren',
    0xFF81: 'CINT: Initalisierung Bildschirm-Editor',
    0xFF84: 'IOINIT: Initialiserung der Ein- und Ausgabe',
    0xFF87: 'RAMTAS: Initalisieren des RAMs, Kassettenpuffer einrichten,',
    0xFF8A: 'RESTOR: R\xc3\xbccksetzen der Ein- und Ausgabevektoren auf Standard',
    0xFF8D: 'VECTOR: Abspeichern von RAM bzw. Vektorverwaltung der',
    0xFF90: 'SETMSG: Steuerung von KERNAL-Meldungen',
    0xFF93: 'SECOND: \xc3\x9cbertragung der Sekund\xc3\xa4radresse nach LISTEN-Befehl',
    0xFF96: 'TKSA: \xc3\x9cbertragung der Sekund\xc3\xa4radresse nach TALK-Befehl',
    0xFF99: 'MEMTOP: Setzen oder Lesen des Zeigers auf BASIC-RAM-Ende',
    0xFF9C: 'MEMBOT: Setzen oder Lesen des Zeigers auf BASIC-RAM-Anfang',
    0xFF9F: 'SCNKEY: Abfrage der Tastatur',
    0xFFA2: 'SETTMO: Setzen der Zeitsperre f\xc3\xbcr seriellen Bus (nur f\xc3\xbcr',
    0xFFA5: 'ACPTR: Byte-Eingabe (serieller Port)',
    0xFFA8: 'CIOUT: Byte-Ausgabe (serieller Bus)',
    0xFFAB: 'UNTLK: Senden des UNTALK-Befehls f\xc3\xbcr seriellen Bus',
    0xFFAE: 'UNLSN: Senden des UNLISTEN-Befehls f\xc3\xbcr seriellen Bus zur',
    0xFFB1: 'LISTEN: Befehl LISTEN f\xc3\xbcr Ger\xc3\xa4te am seriellen Bus (Start',
    0xFFB4: 'TALK: TALK auf den seriellen Bus senden',
    0xFFB7: 'READST: Lesen des Ein-/Ausgabestatusworts, also',
    0xFFBA: 'SETLFS: Setzen der Ger\xc3\xa4teadressen (logische, Prim\xc3\xa4r- und',
    0xFFBD: 'SETNAM: Festlegen des Dateinamens',
    0xFFC0: 'OPEN: Logische Datei \xc3\xb6ffnen (vergl. BASIC-Befehl OPEN)',
    0xFFC3: 'CLOSE: Logische Datei schlie\xc3\x9fen (vergl. BASIC-Befehl CLOSE)',
    0xFFC6: 'CHKIN: Eingabe-Kanal \xc3\xb6ffnen',
    0xFFC9: 'CHKOUT: Ausgabe-Kanal \xc3\xb6ffnen',
    0xFFCC: 'CLRCHN: Schlie\xc3\x9ft Ein- und Ausgabekanal',
    0xFFCF: 'CHRIN: Zeicheneingabe',
    0xFFD2: 'CHROUT: Zeichenausgabe',
    0xFFD5: 'LOAD: Daten ins RAM laden von Peripherieger\xc3\xa4ten, aber nicht',
    0xFFD8: 'SAVE: Daten vom RAM auf Peripherieger\xc3\xa4te sichern, aber nicht',
    0xFFDB: 'SETTIM: Setzen der Uhrzeit (vergl. BASIC-Systemvariable',
    0xFFDE: 'RDTIM: Uhrzeit lesen (vergl. BASIC-Systemvariablen TIME/TI',
    0xFFE1: 'STOP: Abfrage der Taste',
    0xFFE4: 'GETIN: Zeichen vom Eingabeger\xc3\xa4t einlesen',
    0xFFE7: 'CLALL: Schlie\xc3\x9fen alle Kan\xc3\xa4le und Dateien',
    0xFFEA: 'UDTIM: Weiterstellen der Uhrzeit',
    0xFFED: 'SCREEN: Anzahl der Bildschirmspalten und -zeilen ermitteln',
    0xFFF0: 'PLOT: Setzen oder Lesen der Cursorpostion (X-/Y-Position)',
    0xFFF3: 'IOBASE: R\xc3\xbcckmeldung der Basisadressen f\xc3\xbcr Ein- und',
}

class CPU(object):
    def __init__(self):
        self.B_disasm = False
        self.B_debug_stack = False
        CPU.opcode_to_mnem.append("XXX") # ShedSkin
        CPU.opcode_to_mnem = CPU.opcode_to_mnem[:-1] # ShedSkin
        assert len(CPU.opcode_to_mnem) == 0x100, "CPU opcode map covers all 256 possible opcodes"
        self.B_in_interrupt = False
        self.registers = Registers()
        self.MMU = mmu.MMU()
        self.flags = set() # of N, V, B, D, I, Z, C.
        self.flags.add("I")
        self.flags.discard("C")
        self.flags.add("Z")
        #for mnem in set(CPU.opcode_to_mnem):
        #    if not hasattr(self, mnem) and mnem not in CPU.exotic_opcodes:
        #        raise NotImplementedError("warning: instruction %r not implemented")
        if False: # ShedSkin
            value = self.load_value_unadvancing(S_Z)
            value = self.load_value_advancing(S_Z)
            self.update_flags_by_number(value)                 

    def write_register(self, name, value):
        assert isinstance(value, int), "CPU.write_register: value is an integer"
        if name == S_PC:
            self.registers.PC = value
        elif name == S_A:
            self.registers.A = value
        elif name == S_X:
            self.registers.X = value
        elif name == S_Y:
            self.registers.Y = value
        elif name == S_SP:
            self.registers.SP = value
        else:
            assert False, "CPU.write_register: register is known"
        #print("registers", self.registers)
        #if self.B_disasm:
        #    print("%r:=%r" % (chr(name), value))

    def read_register(self, name):
        r = self.registers
        return r.PC if name == S_PC else \
               r.A if name == S_A else \
               r.X if name == S_X else \
               r.Y if name == S_Y else \
               r.SP if name == S_SP else \
               err("unknown register")

    def disasm(self, PC):
        opcode = self.MMU.read_memory(PC)
        mnem = CPU.opcode_to_mnem[opcode]
        addressing_modes = CPU.LDX_addressing_modes if mnem == "LDX" else \
            CPU.LDY_addressing_modes if mnem == "LDY" else \
            CPU.LDA_addressing_modes if mnem == "LDA" else \
            CPU.CMP_addressing_modes if mnem == "CMP" else \
            CPU.CPX_addressing_modes if mnem == "CPX" else \
            CPU.CPY_addressing_modes if mnem == "CPY" else \
            CPU.ADC_addressing_modes if mnem == "ADC" else \
            CPU.SBC_addressing_modes if mnem == "SBC" else \
            CPU.BIT_addressing_modes if mnem == "BIT" else \
            CPU.AND_addressing_modes if mnem == "AND" else \
            CPU.EOR_addressing_modes if mnem == "EOR" else \
            CPU.ORA_addressing_modes if mnem == "ORA" else \
            CPU.INC_addressing_modes if mnem == "INC" else \
            CPU.DEC_addressing_modes if mnem == "DEC" else \
            CPU.ASL_addressing_modes if mnem == "ASL" else \
            CPU.LSR_addressing_modes if mnem == "LSR" else \
            CPU.ROL_addressing_modes if mnem == "ROL" else \
            CPU.ROR_addressing_modes if mnem == "ROR" else \
            CPU.STX_addressing_modes if mnem == "STX" else \
            CPU.STY_addressing_modes if mnem == "STY" else \
            CPU.STA_addressing_modes if mnem == "STA" else \
            CPU.NOP_addressing_modes if mnem == "NOP" else \
            CPU.LAX_addressing_modes if mnem == "LAX" else \
            CPU.DCP_addressing_modes if mnem == "DCP" else \
            {42: S_XXX}
        addressing_mode = addressing_modes[opcode] if opcode in addressing_modes else S_NONE
        #addressing_mode = addressing_modes.get(opcode) or S_NONE
        # EQ addressing_mode = getattr(self.__class__, mnem + "_addressing_modes")[opcode]

        args = ""
        if addressing_mode == S_HASH:
            args = "#%r" % self.MMU.read_memory(PC + 1, 1)
        elif addressing_mode == S_ABS_X:
            base = (self.MMU.read_memory(PC + 1, 2))
            args = "$%04X+X" % base
        elif addressing_mode == S_ABS:
            v = self.MMU.read_memory(PC + 1, 2)
            base = v
            args = "$%04X ABS ; %s" % (base, known_routines[v] if v in known_routines else "")
        elif addressing_mode == S_ABS_Y:
            base = (self.MMU.read_memory(PC + 1, 2))
            args = "$%04X+Y" % base
        elif addressing_mode == S_Z:
            base = (self.MMU.read_memory(PC + 1, 1))
            args = "[$%02X]" % base
        elif addressing_mode == S_Z_X:
            base = (self.MMU.read_memory(PC + 1, 1))
            args = "[$%02X+X]" % base
        elif addressing_mode == S_Z_Y:
            base = (self.MMU.read_memory(PC + 1, 1))
            args = "[$%02X+Y]" % base
        elif addressing_mode == S_IND_X:
            base = (self.MMU.read_memory(PC + 1, 1))
            args = "[[$%02X]+X]" % base
        elif addressing_mode == S_IND_Y:
            base = (self.MMU.read_memory(PC + 1, 1))
            args = "[[$%02X]+Y]" % base
        elif addressing_mode == S_A:
            args = "A"
        elif addressing_mode != S_NONE:
            print("error: unknown addressing mode %r." % addressing_mode, file=sys.stderr)
            assert False, "CPU.disasm: addressing mode is known"
        else:
            if mnem in ["BNE", "BEQ", "BVS", "BVC", "BCC", "BCS", "BPL", "BMI"]:
                offset = to_signed_byte(self.MMU.read_memory(PC + 1, 1))
                args = "%r ; $%X" % (offset, PC + offset + 2)
            elif mnem in ["JSR", "JMP"]:
                # FIXME other modes for JMP
                address = (self.MMU.read_memory(PC + 1, 2))
                args = "$%X" % address
                if opcode == 0x6C:
                    args = "[%s]" % args

        print("A %02X, X %02X, Y %02X, SP %04X, PC %04X %02X %s %s" % (self.registers.A, self.registers.X, self.registers.Y, self.registers.SP | 0x100, PC, opcode, mnem, args))

    def step(self):
        PC = self.read_register(S_PC)
        opcode = self.MMU.read_memory(PC)
        #if PC == 0xE43D:  #FIXME
        #    self.B_disasm = False
        if self.B_disasm:
            self.disasm(PC)
        # TODO maybe use set_PC so we notice when someone walks into our hooks.
        self.write_register(S_PC, PC + 1)
        #sys.stdout.write("\t" + mnem)
        #print(hex(opcode))
        if opcode == 0x0:
            return self.BRK(opcode)
        elif opcode == 0x1:
            return self.ORA(opcode)
        elif opcode == 0x2:
            return self.KIL(opcode)
        elif opcode == 0x3:
            return self.SLO(opcode)
        elif opcode == 0x4:
            return self.NOP(opcode)
        elif opcode == 0x5:
            return self.ORA(opcode)
        elif opcode == 0x6:
            return self.ASL(opcode)
        elif opcode == 0x7:
            return self.SLO(opcode)
        elif opcode == 0x8:
            return self.PHP(opcode)
        elif opcode == 0x9:
            return self.ORA(opcode)
        elif opcode == 0xA:
            return self.ASL(opcode)
        elif opcode == 0xB:
            return self.ANC(opcode)
        elif opcode == 0xC:
            return self.NOP(opcode)
        elif opcode == 0xD:
            return self.ORA(opcode)
        elif opcode == 0xE:
            return self.ASL(opcode)
        elif opcode == 0xF:
            return self.SLO(opcode)
        elif opcode == 0x10:
            return self.BPL(opcode)
        elif opcode == 0x11:
            return self.ORA(opcode)
        elif opcode == 0x12:
            return self.KIL(opcode)
        elif opcode == 0x13:
            return self.SLO(opcode)
        elif opcode == 0x14:
            return self.NOP(opcode)
        elif opcode == 0x15:
            return self.ORA(opcode)
        elif opcode == 0x16:
            return self.ASL(opcode)
        elif opcode == 0x17:
            return self.SLO(opcode)
        elif opcode == 0x18:
            return self.CLC(opcode)
        elif opcode == 0x19:
            return self.ORA(opcode)
        elif opcode == 0x1A:
            return self.NOP(opcode)
        elif opcode == 0x1B:
            return self.SLO(opcode)
        elif opcode == 0x1C:
            return self.NOP(opcode)
        elif opcode == 0x1D:
            return self.ORA(opcode)
        elif opcode == 0x1E:
            return self.ASL(opcode)
        elif opcode == 0x1F:
            return self.SLO(opcode)
        elif opcode == 0x20:
            return self.JSR(opcode)
        elif opcode == 0x21:
            return self.AND(opcode)
        elif opcode == 0x22:
            return self.KIL(opcode)
        elif opcode == 0x23:
            return self.RLA(opcode)
        elif opcode == 0x24:
            return self.BIT(opcode)
        elif opcode == 0x25:
            return self.AND(opcode)
        elif opcode == 0x26:
            return self.ROL(opcode)
        elif opcode == 0x27:
            return self.RLA(opcode)
        elif opcode == 0x28:
            return self.PLP(opcode)
        elif opcode == 0x29:
            return self.AND(opcode)
        elif opcode == 0x2A:
            return self.ROL(opcode)
        elif opcode == 0x2B:
            return self.ANC(opcode)
        elif opcode == 0x2C:
            return self.BIT(opcode)
        elif opcode == 0x2D:
            return self.AND(opcode)
        elif opcode == 0x2E:
            return self.ROL(opcode)
        elif opcode == 0x2F:
            return self.RLA(opcode)
        elif opcode == 0x30:
            return self.BMI(opcode)
        elif opcode == 0x31:
            return self.AND(opcode)
        elif opcode == 0x32:
            return self.KIL(opcode)
        elif opcode == 0x33:
            return self.RLA(opcode)
        elif opcode == 0x34:
            return self.NOP(opcode)
        elif opcode == 0x35:
            return self.AND(opcode)
        elif opcode == 0x36:
            return self.ROL(opcode)
        elif opcode == 0x37:
            return self.RLA(opcode)
        elif opcode == 0x38:
            return self.SEC(opcode)
        elif opcode == 0x39:
            return self.AND(opcode)
        elif opcode == 0x3A:
            return self.NOP(opcode)
        elif opcode == 0x3B:
            return self.RLA(opcode)
        elif opcode == 0x3C:
            return self.NOP(opcode)
        elif opcode == 0x3D:
            return self.AND(opcode)
        elif opcode == 0x3E:
            return self.ROL(opcode)
        elif opcode == 0x3F:
            return self.RLA(opcode)
        elif opcode == 0x40:
            return self.RTI(opcode)
        elif opcode == 0x41:
            return self.EOR(opcode)
        elif opcode == 0x42:
            return self.KIL(opcode)
        elif opcode == 0x43:
            return self.SRE(opcode)
        elif opcode == 0x44:
            return self.NOP(opcode)
        elif opcode == 0x45:
            return self.EOR(opcode)
        elif opcode == 0x46:
            return self.LSR(opcode)
        elif opcode == 0x47:
            return self.SRE(opcode)
        elif opcode == 0x48:
            return self.PHA(opcode)
        elif opcode == 0x49:
            return self.EOR(opcode)
        elif opcode == 0x4A:
            return self.LSR(opcode)
        elif opcode == 0x4B:
            return self.ALR(opcode)
        elif opcode == 0x4C:
            return self.JMP(opcode)
        elif opcode == 0x4D:
            return self.EOR(opcode)
        elif opcode == 0x4E:
            return self.LSR(opcode)
        elif opcode == 0x4F:
            return self.SRE(opcode)
        elif opcode == 0x50:
            return self.BVC(opcode)
        elif opcode == 0x51:
            return self.EOR(opcode)
        elif opcode == 0x52:
            return self.KIL(opcode)
        elif opcode == 0x53:
            return self.SRE(opcode)
        elif opcode == 0x54:
            return self.NOP(opcode)
        elif opcode == 0x55:
            return self.EOR(opcode)
        elif opcode == 0x56:
            return self.LSR(opcode)
        elif opcode == 0x57:
            return self.SRE(opcode)
        elif opcode == 0x58:
            return self.CLI(opcode)
        elif opcode == 0x59:
            return self.EOR(opcode)
        elif opcode == 0x5A:
            return self.NOP(opcode)
        elif opcode == 0x5B:
            return self.SRE(opcode)
        elif opcode == 0x5C:
            return self.NOP(opcode)
        elif opcode == 0x5D:
            return self.EOR(opcode)
        elif opcode == 0x5E:
            return self.LSR(opcode)
        elif opcode == 0x5F:
            return self.SRE(opcode)
        elif opcode == 0x60:
            return self.RTS(opcode)
        elif opcode == 0x61:
            return self.ADC(opcode)
        elif opcode == 0x62:
            return self.KIL(opcode)
        elif opcode == 0x63:
            return self.RRA(opcode)
        elif opcode == 0x64:
            return self.NOP(opcode)
        elif opcode == 0x65:
            return self.ADC(opcode)
        elif opcode == 0x66:
            return self.ROR(opcode)
        elif opcode == 0x67:
            return self.RRA(opcode)
        elif opcode == 0x68:
            return self.PLA(opcode)
        elif opcode == 0x69:
            return self.ADC(opcode)
        elif opcode == 0x6A:
            return self.ROR(opcode)
        elif opcode == 0x6B:
            return self.ARR(opcode)
        elif opcode == 0x6C:
            return self.JMP(opcode)
        elif opcode == 0x6D:
            return self.ADC(opcode)
        elif opcode == 0x6E:
            return self.ROR(opcode)
        elif opcode == 0x6F:
            return self.RRA(opcode)
        elif opcode == 0x70:
            return self.BVS(opcode)
        elif opcode == 0x71:
            return self.ADC(opcode)
        elif opcode == 0x72:
            return self.KIL(opcode)
        elif opcode == 0x73:
            return self.RRA(opcode)
        elif opcode == 0x74:
            return self.NOP(opcode)
        elif opcode == 0x75:
            return self.ADC(opcode)
        elif opcode == 0x76:
            return self.ROR(opcode)
        elif opcode == 0x77:
            return self.RRA(opcode)
        elif opcode == 0x78:
            return self.SEI(opcode)
        elif opcode == 0x79:
            return self.ADC(opcode)
        elif opcode == 0x7A:
            return self.NOP(opcode)
        elif opcode == 0x7B:
            return self.RRA(opcode)
        elif opcode == 0x7C:
            return self.NOP(opcode)
        elif opcode == 0x7D:
            return self.ADC(opcode)
        elif opcode == 0x7E:
            return self.ROR(opcode)
        elif opcode == 0x7F:
            return self.RRA(opcode)
        elif opcode == 0x80:
            return self.NOP(opcode)
        elif opcode == 0x81:
            return self.STA(opcode)
        elif opcode == 0x82:
            return self.NOP(opcode)
        elif opcode == 0x83:
            return self.SAX(opcode)
        elif opcode == 0x84:
            return self.STY(opcode)
        elif opcode == 0x85:
            return self.STA(opcode)
        elif opcode == 0x86:
            return self.STX(opcode)
        elif opcode == 0x87:
            return self.SAX(opcode)
        elif opcode == 0x88:
            return self.DEY(opcode)
        elif opcode == 0x89:
            return self.NOP(opcode)
        elif opcode == 0x8A:
            return self.TXA(opcode)
        elif opcode == 0x8B:
            return self.XAA(opcode)
        elif opcode == 0x8C:
            return self.STY(opcode)
        elif opcode == 0x8D:
            return self.STA(opcode)
        elif opcode == 0x8E:
            return self.STX(opcode)
        elif opcode == 0x8F:
            return self.SAX(opcode)
        elif opcode == 0x90:
            return self.BCC(opcode)
        elif opcode == 0x91:
            return self.STA(opcode)
        elif opcode == 0x92:
            return self.KIL(opcode)
        elif opcode == 0x93:
            return self.AHX(opcode)
        elif opcode == 0x94:
            return self.STY(opcode)
        elif opcode == 0x95:
            return self.STA(opcode)
        elif opcode == 0x96:
            return self.STX(opcode)
        elif opcode == 0x97:
            return self.SAX(opcode)
        elif opcode == 0x98:
            return self.TYA(opcode)
        elif opcode == 0x99:
            return self.STA(opcode)
        elif opcode == 0x9A:
            return self.TXS(opcode)
        elif opcode == 0x9B:
            return self.TAS(opcode)
        elif opcode == 0x9C:
            return self.SHY(opcode)
        elif opcode == 0x9D:
            return self.STA(opcode)
        elif opcode == 0x9E:
            return self.SHX(opcode)
        elif opcode == 0x9F:
            return self.AHX(opcode)
        elif opcode == 0xA0:
            return self.LDY(opcode)
        elif opcode == 0xA1:
            return self.LDA(opcode)
        elif opcode == 0xA2:
            return self.LDX(opcode)
        elif opcode == 0xA3:
            return self.LAX(opcode)
        elif opcode == 0xA4:
            return self.LDY(opcode)
        elif opcode == 0xA5:
            return self.LDA(opcode)
        elif opcode == 0xA6:
            return self.LDX(opcode)
        elif opcode == 0xA7:
            return self.LAX(opcode)
        elif opcode == 0xA8:
            return self.TAY(opcode)
        elif opcode == 0xA9:
            return self.LDA(opcode)
        elif opcode == 0xAA:
            return self.TAX(opcode)
        elif opcode == 0xAB:
            return self.LAX(opcode)
        elif opcode == 0xAC:
            return self.LDY(opcode)
        elif opcode == 0xAD:
            return self.LDA(opcode)
        elif opcode == 0xAE:
            return self.LDX(opcode)
        elif opcode == 0xAF:
            return self.LAX(opcode)
        elif opcode == 0xB0:
            return self.BCS(opcode)
        elif opcode == 0xB1:
            return self.LDA(opcode)
        elif opcode == 0xB2:
            return self.KIL(opcode)
        elif opcode == 0xB3:
            return self.LAX(opcode)
        elif opcode == 0xB4:
            return self.LDY(opcode)
        elif opcode == 0xB5:
            return self.LDA(opcode)
        elif opcode == 0xB6:
            return self.LDX(opcode)
        elif opcode == 0xB7:
            return self.LAX(opcode)
        elif opcode == 0xB8:
            return self.CLV(opcode)
        elif opcode == 0xB9:
            return self.LDA(opcode)
        elif opcode == 0xBA:
            return self.TSX(opcode)
        elif opcode == 0xBB:
            return self.LAS(opcode)
        elif opcode == 0xBC:
            return self.LDY(opcode)
        elif opcode == 0xBD:
            return self.LDA(opcode)
        elif opcode == 0xBE:
            return self.LDX(opcode)
        elif opcode == 0xBF:
            return self.LAX(opcode)
        elif opcode == 0xC0:
            return self.CPY(opcode)
        elif opcode == 0xC1:
            return self.CMP(opcode)
        elif opcode == 0xC2:
            return self.NOP(opcode)
        elif opcode == 0xC3:
            return self.DCP(opcode)
        elif opcode == 0xC4:
            return self.CPY(opcode)
        elif opcode == 0xC5:
            return self.CMP(opcode)
        elif opcode == 0xC6:
            return self.DEC(opcode)
        elif opcode == 0xC7:
            return self.DCP(opcode)
        elif opcode == 0xC8:
            return self.INY(opcode)
        elif opcode == 0xC9:
            return self.CMP(opcode)
        elif opcode == 0xCA:
            return self.DEX(opcode)
        elif opcode == 0xCB:
            return self.AXS(opcode)
        elif opcode == 0xCC:
            return self.CPY(opcode)
        elif opcode == 0xCD:
            return self.CMP(opcode)
        elif opcode == 0xCE:
            return self.DEC(opcode)
        elif opcode == 0xCF:
            return self.DCP(opcode)
        elif opcode == 0xD0:
            return self.BNE(opcode)
        elif opcode == 0xD1:
            return self.CMP(opcode)
        elif opcode == 0xD2:
            return self.KIL(opcode)
        elif opcode == 0xD3:
            return self.DCP(opcode)
        elif opcode == 0xD4:
            return self.NOP(opcode)
        elif opcode == 0xD5:
            return self.CMP(opcode)
        elif opcode == 0xD6:
            return self.DEC(opcode)
        elif opcode == 0xD7:
            return self.DCP(opcode)
        elif opcode == 0xD8:
            return self.CLD(opcode)
        elif opcode == 0xD9:
            return self.CMP(opcode)
        elif opcode == 0xDA:
            return self.NOP(opcode)
        elif opcode == 0xDB:
            return self.DCP(opcode)
        elif opcode == 0xDC:
            return self.NOP(opcode)
        elif opcode == 0xDD:
            return self.CMP(opcode)
        elif opcode == 0xDE:
            return self.DEC(opcode)
        elif opcode == 0xDF:
            return self.DCP(opcode)
        elif opcode == 0xE0:
            return self.CPX(opcode)
        elif opcode == 0xE1:
            return self.SBC(opcode)
        elif opcode == 0xE2:
            return self.NOP(opcode)
        elif opcode == 0xE3:
            return self.ISC(opcode)
        elif opcode == 0xE4:
            return self.CPX(opcode)
        elif opcode == 0xE5:
            return self.SBC(opcode)
        elif opcode == 0xE6:
            return self.INC(opcode)
        elif opcode == 0xE7:
            return self.ISC(opcode)
        elif opcode == 0xE8:
            return self.INX(opcode)
        elif opcode == 0xE9:
            return self.SBC(opcode)
        elif opcode == 0xEA:
            return self.NOP(opcode)
        elif opcode == 0xEB:
            return self.SBC(opcode)
        elif opcode == 0xEC:
            return self.CPX(opcode)
        elif opcode == 0xED:
            return self.SBC(opcode)
        elif opcode == 0xEE:
            return self.INC(opcode)
        elif opcode == 0xEF:
            return self.ISC(opcode)
        elif opcode == 0xF0:
            return self.BEQ(opcode)
        elif opcode == 0xF1:
            return self.SBC(opcode)
        elif opcode == 0xF2:
            return self.KIL(opcode)
        elif opcode == 0xF3:
            return self.ISC(opcode)
        elif opcode == 0xF4:
            return self.NOP(opcode)
        elif opcode == 0xF5:
            return self.SBC(opcode)
        elif opcode == 0xF6:
            return self.INC(opcode)
        elif opcode == 0xF7:
            return self.ISC(opcode)
        elif opcode == 0xF8:
            return self.SED(opcode)
        elif opcode == 0xF9:
            return self.SBC(opcode)
        elif opcode == 0xFA:
            return self.NOP(opcode)
        elif opcode == 0xFB:
            return self.ISC(opcode)
        elif opcode == 0xFC:
            return self.NOP(opcode)
        elif opcode == 0xFD:
            return self.SBC(opcode)
        elif opcode == 0xFE:
            return self.INC(opcode)
        elif opcode == 0xFF:
            return self.ISC(opcode)
        #fn = self.opcode_to_fn[opcode]
        #fn(self, opcode)
        #print("done")

    # TODO DCP {adr} = DEC {adr} + CMP {adr}

    def update_flags_by_number(self, value):
        """ assumes 8 bit number, be careful. """
        assert isinstance(value, int), "CPU.update_flags_by_number: value is a number"
        if value < 0 or ((value & 128) != 0):
            self.flags.add("N")
        else:
            self.flags.discard("N")
        if value == 0:
            self.flags.add("Z")
        else:
            self.flags.discard("Z")
        return value

    def consume_operand(self, size):
        PC = self.read_register(S_PC)
        value = self.MMU.read_memory(PC, size)
        self.write_register(S_PC, PC + size)
        return value

    def consume_unsigned_operand(self, size):
        """ returns the operand as an integer, not as a buffer """
        value = self.consume_operand(size)
        return value

    def consume_signed_operand(self, size):
        """ returns the operand as an integer, not as a buffer """
        value = to_signed_byte(self.consume_operand(size))
        #value = (endian.unpack_signed_16_bit if size == 2 else endian.unpack_signed if size == 1 else err("invalid operand size"))(value)
        #print(value)
        return value

    def read_zero_page_memory(self, address, size = 1):
        assert size < 3, "CPU.read_zero_page_memory: size<3"
        assert size > 0, "CPU.read_zero_page_memory: size>0"
        if size == 2 and address == 0xFF:
            return self.MMU.read_memory(address, 1) | (self.MMU.read_memory(0, 1) << 8)
        else:
            return self.MMU.read_memory(address, size)

    def store_value(self, addressing_mode, value, size = 1):
        #print("MODE", addressing_mode)
        if addressing_mode == S_Z:
            self.MMU.write_memory(self.consume_unsigned_operand(1), value, size)
        elif addressing_mode == S_Z_Y:
            # FIXME unsigned?
            self.MMU.write_memory((self.consume_unsigned_operand(1) + (self.read_register(S_Y)) & 0xFF), value, size)
        elif addressing_mode == S_Z_X:
            # FIXME unsigned?
            self.MMU.write_memory((self.consume_unsigned_operand(1) + (self.read_register(S_X)) & 0xFF), value, size)
        elif addressing_mode == S_ABS:
            self.MMU.write_memory(self.consume_unsigned_operand(2), value, size)
        elif addressing_mode == S_ABS_Y:
            # FIXME unsigned.
            self.MMU.write_memory((self.consume_unsigned_operand(2) + self.read_register(S_Y)) & 0xFFFF, value, size)
        elif addressing_mode == S_ABS_X:
            # FIXME unsigned.
            self.MMU.write_memory((self.consume_unsigned_operand(2) + self.read_register(S_X)) & 0xFFFF, value, size)
        elif addressing_mode == S_IND_X:
            base = self.consume_unsigned_operand(1)
            # FIXME signed?
            offset = (self.read_register(S_X))
            address = self.MMU.read_memory((base + offset) & 0xFF, 2)
            assert address != 0, "CPU.store_value: debugging sentinel to avoid dereferencing a 0 pointer on IND."
            self.MMU.write_memory(address, value, size)
        elif addressing_mode == S_IND_Y: # [[$a]+X]
            base = self.consume_unsigned_operand(1)
            #print("base would be $%X" % base)
            address = self.read_zero_page_memory(base, 2)
            # FIXME signed?
            offset = (self.read_register(S_Y))
            #print("address would be $%X+$%X" % (address, offset))
            assert address != 0, "CPU.store_value: debugging sentinel to avoid dereferencing a 0 pointer on IND."
            #print("offset %r" % offset)
            self.MMU.write_memory((address + offset) & 0xFFFF, value, size)
        elif addressing_mode == S_A:
            self.write_register(S_A, value)
        else:
            print("error", addressing_mode)
            assert False, "CPU.store_value: addressing mode is known"

    def load_value_unadvancing(self, addressing_mode): # mostly INC and shift instructions...
        old_PC = self.read_register(S_PC)
        result = self.load_value_advancing(addressing_mode)
        self.write_register(S_PC, old_PC)
        return result

    def load_value_advancing(self, addressing_mode):
        # mask_addressing_modes = [S_HASH, S_Z, S_Z_X, S_Z_Y, S_ABS, S_ABS_X, S_ABS_Y, S_IND_X, S_IND_Y]
        #sys.stdout.write({
        #    0: S_HASH,
        #    0x1C: S_ABS_Y,
        #}.get(addressing_mode) or str(addressing_mode))
        # FIXME is unsigned correct?
        #print(addressing_mode)
        return    self.read_register(S_A) if addressing_mode == S_A else \
                self.consume_unsigned_operand(1) if addressing_mode == S_HASH else \
            self.MMU.read_zero_page(self.consume_unsigned_operand(1)) if addressing_mode == S_Z else \
            self.MMU.read_zero_page((self.consume_unsigned_operand(1) + self.read_register(S_X)) & 0xFF) if addressing_mode == S_Z_X else \
            self.MMU.read_zero_page((self.consume_unsigned_operand(1) + self.read_register(S_Y)) & 0xFF) if addressing_mode == S_Z_Y else \
            self.MMU.read_memory(self.consume_unsigned_operand(2)) if addressing_mode == S_ABS else \
            self.MMU.read_memory((self.consume_unsigned_operand(2) + self.read_register(S_X)) & 0xFFFF) if addressing_mode == S_ABS_X else \
            self.MMU.read_memory((self.consume_unsigned_operand(2) + self.read_register(S_Y)) & 0xFFFF) if addressing_mode == S_ABS_Y else \
            self.MMU.read_memory(self.MMU.read_memory((self.consume_unsigned_operand(1) + self.read_register(S_X)) & 0xFF, 2)) if addressing_mode == S_IND_X else \
            self.MMU.read_memory(self.read_zero_page_memory(self.consume_unsigned_operand(1), 2) + self.read_register(S_Y)) if addressing_mode == S_IND_Y else \
            err("invalid addressing mode %r" % addressing_mode)

    LDX_addressing_modes = {
            0xA2: S_HASH,
            0xA6: S_Z,
            0xB6: S_Z_Y,
            0xAE: S_ABS,
            0xBE: S_ABS_Y,
        }
    def LDX(self, opcode = 0xA2):
        addressing_mode = CPU.LDX_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        self.write_register(S_X, value)
        self.update_flags_by_number(value)

    LDY_addressing_modes = {
            0xA0: S_HASH,
            0xA4: S_Z,
            0xB4: S_Z_X,
            0xAC: S_ABS,
            0xBC: S_ABS_X,
    }
    def LDY(self, opcode):
        addressing_mode = CPU.LDY_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        self.write_register(S_Y, value)
        self.update_flags_by_number(value)

    LDA_addressing_modes = {
            0xA9: S_HASH,
            0xA5: S_Z,
            0xB5: S_Z_X,
            0xAD: S_ABS,
            0xBD: S_ABS_X,
            0xB9: S_ABS_Y,
            0xA1: S_IND_X,
            0xB1: S_IND_Y,
    }
    def LDA(self, opcode):
        addressing_mode = CPU.LDA_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        #if value is None:
        #    print("ADR", CPU.LDA_addressing_modes[opcode])
        #print("LDA result is %r" % value)
        self.write_register(S_A, value)
        self.update_flags_by_number(value)

    def compare(self, value, reference_value):
        result = reference_value - value
        self.update_flags_by_number(result)
        #print("CMP RES", result)
        if reference_value >= value:
            self.flags.add("C")
        else:
            self.flags.discard("C")
            assert "N" in self.flags, "CPU.compare: N is in flags"

    CMP_addressing_modes = {
            0xC9: S_HASH,
            0xC5: S_Z,
            0xD5: S_Z_X,
            0xCD: S_ABS,
            0xDD: S_ABS_X,
            0xD9: S_ABS_Y,
            0xC1: S_IND_X,
            0xD1: S_IND_Y,
        }
    def CMP(self, opcode):
        """ compare with A """
        # FIXME negative numbers?
        assert opcode in [0xC1, 0xC5, 0xC9, 0xCD, 0xD1, 0xD5, 0xD9, 0xDD], "CPU.CMP opcode is in known set"
        reference_value = self.read_register(S_A)
        addressing_mode = CPU.CMP_addressing_modes[opcode]
        return self.compare(self.load_value_advancing(addressing_mode), reference_value)

    CPX_addressing_modes = {
            0xE0: S_HASH,
            0xE4: S_Z,
            0xEC: S_ABS,
    }
    def CPX(self, opcode):
        """ compare with X """
        reference_value = self.read_register(S_X)
        addressing_mode = CPU.CPX_addressing_modes[opcode]
        return self.compare(self.load_value_advancing(addressing_mode), reference_value)

    CPY_addressing_modes = {
            0xC0: S_HASH,
            0xC4: S_Z,
            0xCC: S_ABS,
    }
    def CPY(self, opcode):
        """ compare with Y """
        # FIXME negative numbers?
        reference_value = self.read_register(S_Y)
        addressing_mode = CPU.CPY_addressing_modes[opcode]
        return self.compare(self.load_value_advancing(addressing_mode), reference_value)

    def add_BCD(self, a, b): # unsigned
        carry = 1 if "C" in self.flags else 0  
        # N and Z are invalid on 6502
        a0 = a & 0xF
        a1 = a >> 4
        b0 = b & 0xF
        b1 = b >> 4
        r0 = a0 + b0 + carry
        r1 = a1 + b1 + (1 if r0 > 9 else 0)
        if r0 > 9:
            r0 = r0 - 10
        if r1 > 9:
            r1 = r1 - 10
            self.flags.add("C")
        else:
            self.flags.discard("C")
        # TODO overflow.
        value = (r1 << 4) | r0
        self.write_register(S_A, value)
        self.update_flags_by_number(value)
        return value
    def subtract_BCD(self, a, b):
        uncarry = 0 if "C" in self.flags else 1
        # N and Z are invalid on 6502
        a0 = a & 0xF
        a1 = a >> 4
        b0 = b & 0xF
        b1 = b >> 4
        r0 = a0 - b0 - uncarry
        r1 = a1 - b1 - (1 if r0 < 0 else 0)
        if r0 < 0:
            r0 = 10 + r0
        if r1 < 0:
            r1 = 10 + r1
            self.flags.discard("C")
        else:
            self.flags.add("C")
        # TODO overflow.
        value = (r1 << 4) | r0
        self.write_register(S_A, value)
        self.update_flags_by_number(value)
        return value
    def add(self, operand_0, operand_1):
        carry = 1 if "C" in self.flags else 0
        value = (operand_0 + operand_1 + carry)
        B_overflow_1 = False
        a_value = value
        if (value & 0xFF) != value: # that is, value>0xFF.
            self.flags.add("C")
            B_overflow_1 = True
        else:
            self.flags.discard("C")
        value = value & 0xFF
        # 0x7F+1 overflow
        # 0x80+0xFF overflow
        B_overflow = ((operand_0 ^ operand_1) & 0x80) == 0 and ((operand_0 ^ value) & 0x80) != 0
        #((operand_0 ^ operand_1) & (operand_0 ^ (value & 0xFF)) & 0x80) != 0
        #B_overflow = ((operand_1 & 0x80) == 0 and (operand_0 & 0x80) == 0 and (value & 0x80) != 0) or \
        #             ((operand_1 & 0x80) != 0 and (operand_0 & 0x80) != 0 and (value & 0x80) == 0)
        if B_overflow:
            self.flags.add("V")
        else:
            #if B_overflow_1 != False:
            #    print("whoops") # , a_value, operand_0, operand_1)
            # FIXME assert(B_overflow_1 == False)
            self.flags.discard("V")
        #self.store_value(addressing_mode, value)
        self.write_register(S_A, value)
        self.update_flags_by_number(value)
        return value
    ADC_addressing_modes = {
        0x69: S_HASH,
        0x65: S_Z,
        0x75: S_Z_X,
        0x6D: S_ABS,
        0x7D: S_ABS_X,
        0x79: S_ABS_Y,
        0x61: S_IND_X,
        0x71: S_IND_Y,
    }
    def ADC(self, opcode):
        """ add with carry """
        # TODO BCD arithmetic.
        addressing_mode = CPU.ADC_addressing_modes[opcode]
        operand_0 = self.read_register(S_A)
        operand_1 = self.load_value_advancing(addressing_mode)
        #print("ADC", operand_0, operand_1)
        if "D" in self.flags:
            self.add_BCD(operand_0, operand_1)
        else:
            self.add(operand_0, operand_1)
        # for BCD: carry:=result>$99
        # for BCD: N:=value of bit 7

    SBC_addressing_modes = {
        0xE9: S_HASH,
        0xE5: S_Z,
        0xF5: S_Z_X,
        0xED: S_ABS,
        0xFD: S_ABS_X,
        0xF9: S_ABS_Y,
        0xE1: S_IND_X,
        0xF1: S_IND_Y,
    }
    def SBC(self, opcode):
        """ subtract with carry """
        # TODO BCD arithmetic.
        addressing_mode = CPU.SBC_addressing_modes[opcode]
        operand_0 = self.read_register(S_A)
        operand_1 = self.load_value_advancing(addressing_mode)
        if "D" in self.flags:
            self.subtract_BCD(operand_0, operand_1)
        else:
            self.add(operand_0, operand_1 ^ 0xFF)
        #B_overflow = ((operand_0 ^ operand_1) & (operand_0 ^ (result & 0xFF)) & 0x80) != 0
        #if B_overflow:
        #    self.flags.add("V")
        #else:
        #    self.flags.discard("V")
        #if result < 0 or (result & 128) != 0:
        #    self.flags.add("C")
        #else:
        #    self.flags.discard("C") # FIXME test.
        #self.store_value(addressing_mode, value)

    def test_bits(self, addressing_mode):
        reference_value = self.read_register(S_A)
        value = self.load_value_advancing(addressing_mode)
        result = value & reference_value
        return result, value

    BIT_addressing_modes = {
        0x24: S_Z,
        0x2C: S_ABS,
    }
    def BIT(self, opcode = 0x24):
        """ like AND, but does not store the result (but just the flags). """
        reference_value = self.read_register(S_A)
        result, operand = self.test_bits(CPU.BIT_addressing_modes[opcode])
        self.update_flags_by_number(result)
        if (operand & 64) != 0:
            self.flags.add("V")
        else:
            self.flags.discard("V")
        if (operand & 128) != 0:
            self.flags.add("N")
        else:
            self.flags.discard("N")
        #return result

    AND_addressing_modes = {
            0x29: S_HASH,
            0x25: S_Z,
            0x35: S_Z_X,
            0x2D: S_ABS,
            0x3D: S_ABS_X,
            0x39: S_ABS_Y,
            0x21: S_IND_X,
            0x31: S_IND_Y,
        }
    def AND(self, opcode):
        """ AND with A """
        value, operand = self.test_bits(CPU.AND_addressing_modes[opcode])
        self.write_register(S_A, value)
        self.update_flags_by_number(value)

    EOR_addressing_modes = {
            0x49: S_HASH,
            0x45: S_Z,
            0x55: S_Z_X,
            0x4D: S_ABS,
            0x5D: S_ABS_X,
            0x59: S_ABS_Y,
            0x41: S_IND_X,
            0x51: S_IND_Y,
    }

    def EOR(self, opcode):
        """ exclusive OR """
        reference_value = self.read_register(S_A)
        addressing_mode = CPU.EOR_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        result = value ^ reference_value
        self.write_register(S_A, result)
        self.update_flags_by_number(result)

    ORA_addressing_modes = {
            0x09: S_HASH,
            0x05: S_Z,
            0x15: S_Z_X,
            0x0D: S_ABS,
            0x1D: S_ABS_X,
            0x19: S_ABS_Y,
            0x01: S_IND_X,
            0x11: S_IND_Y,
    }
    def ORA(self, opcode = 0x1):
        """ ORA with A """
        reference_value = self.read_register(S_A)
        addressing_mode = CPU.ORA_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        result = value | reference_value
        self.write_register(S_A, result)
        self.update_flags_by_number(result)

    def TXS(self, opcode = 0x9A):
        """ transfer X to stack pointer """
        # does NOT set negative flag!
        self.write_register(S_SP, self.read_register(S_X))

    def TAY(self, opcode = 0xA8):
        """ transfer A to Y """
        self.write_register(S_Y, self.update_flags_by_number(self.read_register(S_A)))

    def TYA(self, opcode = 0x98):
        """ transfer Y to A """
        self.write_register(S_A, self.update_flags_by_number(self.read_register(S_Y)))

    def TAX(self, opcode = 0xAA):
        """ transfer A to X """
        self.write_register(S_X, self.update_flags_by_number(self.read_register(S_A)))

    def TSX(self, opcode = 0xBA):
        """ transfer SP to X """
        value = self.update_flags_by_number(self.read_register(S_SP))
        self.write_register(S_X, value)

    def TXA(self, opcode = 0x8A):
        """ transfer X to A """
        self.write_register(S_A, self.update_flags_by_number(self.read_register(S_X)))

    def CLD(self, opcode = 0xD8):
        """ Clear Decimal """
        self.flags.discard("D")

    def SED(self, opcode = 0xF8):
        """ Set Decimal """
        self.flags.add("D")

    NOP_addressing_modes = {
            0xEA: S_A,
            0x1A: S_A,
            0x3A: S_A,
            0x5A: S_A,
            0x7A: S_A,
            0xDA: S_A,
            0xFA: S_A,
            0x04: S_Z,
            0x44: S_Z,
            0x64: S_Z,
            0x0C: S_ABS,
            0x1C: S_ABS_X,
            0x3C: S_ABS_X,
            0x5C: S_ABS_X,
            0x7C: S_ABS_X,
            0xDC: S_ABS_X,
            0xFC: S_ABS_X,
            0x9B: S_ABS_Y, # C64DTV
            0x14: S_Z_X,
            0x34: S_Z_X,
            0x54: S_Z_X,
            0x74: S_Z_X,
            0xD4: S_Z_X,
            0xF4: S_Z_X,
            0x80: S_HASH,
            0x82: S_HASH,
            0x89: S_HASH,
            0xC2: S_HASH,
            0xE2: S_HASH,
    }
    def NOP(self, opcode):
        """ No operation """
        addressing_mode = CPU.NOP_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        #self.consume_operand(1) # dummy so you can replace any 1-arg instruction's opcode by BRK.

    def DEX(self, opcode):
        result = (self.read_register(S_X) - 1) & 0xFF
        self.write_register(S_X, result)
        self.update_flags_by_number(result)

    def INX(self, opcode = 0xE8):
        result = ((self.read_register(S_X)) + 1) & 0xFF
        self.write_register(S_X, result)
        self.update_flags_by_number(result)

    def DEY(self, opcode = 0x88):
        result = (self.read_register(S_Y) - 1) & 0xFF
        self.write_register(S_Y, result)
        self.update_flags_by_number(result)

    def INY(self, opcode = 0xC8):
        result = ((self.read_register(S_Y)) + 1) & 0xFF
        self.write_register(S_Y, result)
        self.update_flags_by_number(result)

    DEC_addressing_modes = {
            0xC6: S_Z,
            0xD6: S_Z_X,
            0xCE: S_ABS,
            0xDE: S_ABS_X,
    }
    def DEC(self, opcode = 0xC6):
        addressing_mode = CPU.DEC_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        result = (value - 1) & 0xFF
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)

    DCP_addressing_modes = {
            0xC7: S_Z,
            0xD7: S_Z_X,
            0xCF: S_ABS,
            0xDF: S_ABS_X,
            0xDB: S_ABS_Y,
            0xC3: S_IND_X,
            0xD3: S_IND_Y,
    }
    def DCP(self, opcode = 0xC3):
        addressing_mode = CPU.DCP_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        result = (value - 1) & 0xFF
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)
        self.compare(result, self.read_register(S_A))

    INC_addressing_modes = {
            0xE6: S_Z,
            0xF6: S_Z_X,
            0xEE: S_ABS,
            0xFE: S_ABS_X,
    }
    def INC(self, opcode):
        addressing_mode = CPU.INC_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        result = (value + 1) & 0xFF
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)

    ASL_addressing_modes = {
            0x0A: S_A,
            0x06: S_Z,
            0x16: S_Z_X,
            0x0E: S_ABS,
            0x1E: S_ABS_X,
    }
    def ASL(self, opcode):
        addressing_mode = CPU.ASL_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        if (value & 128) != 0:
            self.flags.add("C")
        else:
            self.flags.discard("C")
        result = (value << 1) & 0xFF
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)

    LSR_addressing_modes = {
            0x4A: S_A,
            0x46: S_Z,
            0x56: S_Z_X,
            0x4E: S_ABS,
            0x5E: S_ABS_X,
    }
    def LSR(self, opcode):
        addressing_mode = CPU.LSR_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        if (value & 1) != 0:
            self.flags.add("C")
        else:
            self.flags.discard("C")
        result = (value >> 1) & 0xFF
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)

    ROL_addressing_modes = {
            0x2A: S_A,
            0x26: S_Z,
            0x36: S_Z_X,
            0x2E: S_ABS,
            0x3E: S_ABS_X,
    }
    def ROL(self, opcode):
        addressing_mode = CPU.ROL_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        value = ((value << 1) | (1 if "C" in self.flags else 0))
        result = value & 0xFF
        if (value & 0x100) != 0:
            self.flags.add("C")
        else:
            self.flags.discard("C")
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)
        
    ROR_addressing_modes = {
            0x6A: S_A,
            0x66: S_Z,
            0x76: S_Z_X,
            0x6E: S_ABS,
            0x7E: S_ABS_X,
    }
    def ROR(self, opcode = 0x66):
        addressing_mode = CPU.ROR_addressing_modes[opcode]
        value = self.load_value_unadvancing(addressing_mode)
        result = ((value >> 1) | (128 if "C" in self.flags else 0))  & 0xFF
        if (value & 1) != 0:
            self.flags.add("C")
        else:
            self.flags.discard("C")
        #(self.flags.add if value & 1 else self.flags.discard)("C") # yes, the old value!
        self.store_value(addressing_mode, result)
        self.update_flags_by_number(result)
    
    status_positions = ["C", "Z", "I", "D", "B", "5", "V", "N"]

    def pop_status(self):
        flags_bin = self.stack_pop(1)
        self.flags = set([(flag_name if (flags_bin & (1 << flag_bit)) != 0 else "") for flag_bit, flag_name in enumerate(CPU.status_positions)])
        self.flags.discard("")

    def push_status(self):
        flags_bin = sum([((1 << flag_bit) if flag_name in self.flags else 0) for flag_bit, flag_name in enumerate(CPU.status_positions)])
        self.stack_push(flags_bin, 1)

    def stack_push(self, value, size):
        """
        actually:
        RAM[sp+256] = value >> 8
        sp_1=sp-1
        sp_1&=255
        RAM[sp-1+256] = value & 0xFF
        sp_2=sp_1-1
        sp_2&=255
        """
        assert isinstance(value, int), "CPU.stack_push: value is an integer"
        SP = self.read_register(S_SP)
        base = 0x100
        for i in range(size): # easier debugging when it doesn't skip slots.
            SP -= 1
            self.write_register(S_SP, SP)
        #SP -= size
        #self.write_register(S_SP, SP)
        address = base + SP + 1
        self.MMU.write_memory(address, value, size)
        if self.B_debug_stack:
            print("stack push %r at $%X" % (value, address))

    def stack_peek(self, size):
        SP = self.read_register(S_SP)
        base = 0x100
        value_bin = self.MMU.read_memory(base + SP + 1, size)
        return value_bin

    def stack_pop(self, size):
        value_bin = self.stack_peek(size)
        SP = self.read_register(S_SP)
        self.write_register(S_SP, SP + size)
        base = 0x100
        if self.B_debug_stack:
            print("stack pop %r at $%X" % (value_bin, base + SP + 1))
        #print("stack peek %r" % self.stack_peek(2))
        return value_bin

    def set_PC(self, new_PC):
        self.write_register(S_PC, new_PC)

    def BNE(self, opcode):
        assert opcode == 0xD0, "CPU.BNE: opcode is known"
        offset = self.consume_signed_operand(1)
        if "Z" not in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BEQ(self, opcode):
        offset = self.consume_signed_operand(1)
        if "Z" in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BPL(self, opcode = 0x10):
        offset = self.consume_signed_operand(1)
        if "N" not in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BMI(self, opcode = 0x30):
        offset = self.consume_signed_operand(1)
        if "N" in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BCS(self, opcode = 0xB0):
        offset = self.consume_signed_operand(1)
        if "C" in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BCC(self, opcode):
        offset = self.consume_signed_operand(1)
        if "C" not in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BVS(self, opcode):
        offset = self.consume_signed_operand(1)
        if "V" in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)

    def BVC(self, opcode):
        offset = self.consume_signed_operand(1)
        if "V" not in self.flags:
            #print("OFFSET", offset)
            self.set_PC((self.read_register(S_PC) + offset) & 0xFFFF)


    def JMP(self, opcode = 0x4C):
        address = self.consume_unsigned_operand(2)
        if opcode == 0x6C: # indirect jump
            address = self.MMU.read_memory(address, 2)
        self.set_PC(address)


    def JSR(self, opcode = 0x20):
        assert opcode == 0x20, "CPU.JSR: opcode is known"
        #self.push_status()
        new_PC = self.consume_unsigned_operand(2)
        self.stack_push(self.read_register(S_PC) - 1, 2)
        self.set_PC(new_PC)

    STX_addressing_modes = {
        0x86: S_Z,
        0x96: S_Z_Y,
        0x8E: S_ABS,
    }
    def STX(self, opcode):
        """ store X into memory """
        self.store_value(CPU.STX_addressing_modes[opcode], self.read_register(S_X))

    STY_addressing_modes = {
        0x84: S_Z,
        0x94: S_Z_X,
        0x8C: S_ABS,
    }
    def STY(self, opcode):
        """ store Y into memory """
        self.store_value(CPU.STY_addressing_modes[opcode], self.read_register(S_Y))

    STA_addressing_modes = {
        0x85: S_Z,
        0x95: S_Z_X,
        0x8D: S_ABS,
        0x9D: S_ABS_X,
        0x99: S_ABS_Y,
        0x81: S_IND_X,
        0x91: S_IND_Y,
    }
    def STA(self, opcode = 0x81):
        """ store A into memory """
        self.store_value(CPU.STA_addressing_modes[opcode], self.read_register(S_A))

    def RTS(self, opcode = 0x60):
        """ return from subroutine """
        PC = (self.stack_pop(2))
        self.set_PC(PC + 1)
        #self.pop_status()

    def RTI(self, opcode = 0x40):
        """ return from interrupt """
        self.pop_status()
        PC = (self.stack_pop(2))
        self.B_in_interrupt = False
        self.set_PC(PC)

    def SEI(self, opcode = 0x78):
        """ Set Interrupt Disable """
        self.flags.add("I")

    def CLI(self, opcode = 0x58):
        """ Clear Interrupt Disable """
        self.flags.discard("I")

    def clear_Z(self): # mostly for unit tests.
        self.flags.discard("Z")

#    def set_Z(self): # mostly for unit tests.
#        self.flags.add("Z")

#    def clear_N(self): # mostly for unit tests.
#        self.flags.discard("N")

#    def set_N(self): # mostly for unit tests.
#        self.flags.add("N")

#    def set_V(self): # mostly for unit tests.
#        self.flags.add("V")

    def CLC(self, opcode = 0x18):
        """ Clear Carry """
        self.flags.discard("C")

    def SEC(self, opcode = 0x38):
        """ Set Carry """
        self.flags.add("C")

    def CLV(self, opcode = 0xB8):
        """ Clear Overflow """
        self.flags.discard("V")

    def BRK(self, opcode):
        """ software debugging (NMI) """
        self.consume_operand(1) # dummy so you can replace any 1-arg instruction's opcode by BRK.
        old_PC = self.read_register(S_PC)
        if old_PC - 2 == 0xF8A1 or old_PC - 2 == 0xF7BE or old_PC - 2 == 0xF72F: # tape
            tape.call_hook(self, self.MMU, old_PC - 2)
        else:
            self.cause_interrupt(True)

    def cause_interrupt(self, B_BRK):  # IRQ and BRK.
        if self.B_in_interrupt:
            return
        if self.B_disasm:
            print("causing interrupt")
        self.B_in_interrupt = True
        address = 0xFFFE
        old_PC = self.read_register(S_PC)
        self.stack_push(old_PC, 2)
        new_PC = self.MMU.read_memory(address, 2)
        self.push_status()
        self.SEI(0x78)
        #print("NEW PC $%X" % new_PC)
        if B_BRK:
            self.flags.add("B")
        self.set_PC(new_PC)

    def PHP(self, opcode):
        """ push processor status """
        self.push_status()

    def PLP(self, opcode):
        """ pull processor status """
        self.pop_status()

    def PHA(self, opcode):
        """ push A """
        self.stack_push(self.read_register(S_A), 1)

    def PLA(self, opcode):
        """ pull A """
        value = self.stack_pop(1)
        self.write_register(S_A, value)
        self.update_flags_by_number(value)

    opcode_to_mnem = [
        "BRK", 
        "ORA",
        "KIL", 
        "SLO",
        "NOP",
        "ORA",
        "ASL",
        "SLO",
        "PHP",
        "ORA",
        "ASL",
        "ANC",
        "NOP",
        "ORA",
        "ASL",
        "SLO",
        "BPL",
        "ORA",
        "KIL",
        "SLO",
        "NOP",
        "ORA",
        "ASL",
        "SLO",
        "CLC",
        "ORA",
        "NOP",
        "SLO",
        "NOP",
        "ORA",
        "ASL",
        "SLO",
        "JSR",
        "AND",
        "KIL",
        "RLA",
        "BIT",
        "AND",
        "ROL",
        "RLA",
        "PLP",
        "AND",
        "ROL",
        "ANC",
        "BIT",
        "AND",
        "ROL",
        "RLA",
        "BMI",
        "AND",
        "KIL",
        "RLA",
        "NOP",
        "AND",
        "ROL",
        "RLA",
        "SEC",
        "AND",
        "NOP",
        "RLA",
        "NOP",
        "AND",
        "ROL",
        "RLA",
        "RTI",
        "EOR",
        "KIL",
        "SRE",
        "NOP",
        "EOR",
        "LSR",
        "SRE",
        "PHA",
        "EOR",
        "LSR",
        "ALR",
        "JMP",
        "EOR",
        "LSR",
        "SRE",
        "BVC",
        "EOR",
        "KIL",
        "SRE",
        "NOP",
        "EOR",
        "LSR",
        "SRE",
        "CLI",
        "EOR",
        "NOP",
        "SRE",
        "NOP",
        "EOR",
        "LSR",
        "SRE",
        "RTS",
        "ADC",
        "KIL",
        "RRA", # ROR then ADC
        "NOP",
        "ADC",
        "ROR",
        "RRA",
        "PLA",
        "ADC",
        "ROR",
        "ARR",
        "JMP",
        "ADC",
        "ROR",
        "RRA",
        "BVS",
        "ADC",
        "KIL",
        "RRA",
        "NOP",
        "ADC",
        "ROR",
        "RRA",
        "SEI",
        "ADC",
        "NOP",
        "RRA",
        "NOP",
        "ADC",
        "ROR",
        "RRA",
        "NOP",
        "STA",
        "NOP",
        "SAX",
        "STY",
        "STA",
        "STX",
        "SAX",
        "DEY",
        "NOP",
        "TXA",
        "XAA",
        "STY",
        "STA",
        "STX",
        "SAX",
        "BCC",
        "STA",
        "KIL",
        "AHX",
        "STY",
        "STA",
        "STX",
        "SAX",
        "TYA",
        "STA",
        "TXS",
        "TAS", # unstable.
        "SHY",
        "STA",
        "SHX",
        "AHX",
        "LDY",
        "LDA",    
        "LDX",
        "LAX",
        "LDY",
        "LDA",
        "LDX",
        "LAX",
        "TAY",
        "LDA",
        "TAX",
        "LAX",
        "LDY",
        "LDA",
        "LDX",
        "LAX",
        "BCS",
        "LDA",
        "KIL",
        "LAX",
        "LDY",
        "LDA",
        "LDX",
        "LAX",
        "CLV",
        "LDA",
        "TSX",
        "LAS",
        "LDY",
        "LDA",
        "LDX",
        "LAX",
        "CPY",
        "CMP",
        "NOP",
        "DCP",
        "CPY",
        "CMP",
        "DEC",
        "DCP",
        "INY",
        "CMP",
        "DEX",
        "AXS",
        "CPY",
        "CMP",
        "DEC",
        "DCP",
        "BNE",
        "CMP",
        "KIL",
        "DCP",
        "NOP",
        "CMP",
        "DEC",
        "DCP",
        "CLD",
        "CMP",
        "NOP",
        "DCP",
        "NOP",
        "CMP",
        "DEC",
        "DCP",
        "CPX",
        "SBC",
        "NOP",
        "ISC",
        "CPX",
        "SBC",
        "INC",
        "ISC",
        "INX",
        "SBC",
        "NOP",
        "SBC",
        "CPX",
        "SBC",
        "INC",
        "ISC",
        "BEQ",
        "SBC",
        "KIL",
        "ISC",
        "NOP",
        "SBC",
        "INC",
        "ISC", # INC then SBC
        "SED",
        "SBC",
        "NOP",
        "ISC",
        "NOP",
        "SBC",
        "INC",
        "ISC",
    ]

    def AHX(self, opcode):
        raise NotImplementedError("AHX not implemented")
        sys.exit(1)

    def ALR(self, opcode):
        raise NotImplementedError("ALR not implemented")
        sys.exit(1)

    def ANC(self, opcode):
        raise NotImplementedError("ANC not implemented")
        sys.exit(1)

    def ARR(self, opcode):
        raise NotImplementedError("ARR not implemented")
        sys.exit(1)

    def AXS(self, opcode = 0xCB):
        raise NotImplementedError("AXS not implemented")
        sys.exit(1)

    def ISC(self, opcode):
        PC = self.read_register(S_PC)
        print("PC")
        print(PC)
        sys.stdout.flush()
        raise NotImplementedError("ISC not implemented")
        sys.exit(1) # INC whatever; SBC whatever
        # EF abcd
        # FF abcd,X
        # FB abcd,Y
        # E7 ab
        # F7 ab,X
        # E3 (ab,X)
        # F3 (ab),Y
    def KIL(self, opcode):
        raise NotImplementedError("KIL not implemented")
        sys.exit(1)

    def LAS(self, opcode):
        raise NotImplementedError("LAS not implemented")
        sys.exit(1)

    LAX_addressing_modes = {
            0xA3: S_HASH,
            0xA7: S_Z,
            0xB7: S_Z_Y,
            0xAF: S_ABS,
            0xBF: S_ABS_Y,
        }
    def LAX(self, opcode):
        addressing_mode = CPU.LAX_addressing_modes[opcode]
        value = self.load_value_advancing(addressing_mode)
        #if value is None:
        #    print("ADR", CPU.LDA_addressing_modes[opcode])
        #print("LDA result is %r" % value)
        self.write_register(S_A, value)
        self.write_register(S_X, value)
        self.update_flags_by_number(value)

    def RLA(self, opcode):
        raise NotImplementedError("RLA not implemented")
        sys.exit(1)

    def RRA(self, opcode):
        raise NotImplementedError("RRA not implemented")
        sys.exit(1)

    def SAX(self, opcode):
        raise NotImplementedError("SAX not implemented")
        sys.exit(1)

    def SHX(self, opcode):
        raise NotImplementedError("SHX not implemented")
        sys.exit(1)

    def SHY(self, opcode):
        raise NotImplementedError("SHY not implemented")
        sys.exit(1)

    def SLO(self, opcode):
        raise NotImplementedError("SLO not implemented")
        sys.exit(1)

    def SRE(self, opcode):
        raise NotImplementedError("SRE not implemented")
        sys.exit(1)

    def TAS(self, opcode = 0x9B):
        raise NotImplementedError("TAS not implemented")
        sys.exit(1)

    def XAA(self, opcode):
        raise NotImplementedError("XAA not implemented")
        sys.exit(1)


    exotic_opcodes = set(["RRA", "TAS", "SRE", "SLO", "KIL", "SHX", "SHY", "SAX", "LAS", "XAS", "ALR", "RLA", "DCP", "AHX", "ARR", "LAX", "ANC", "ISC", "XAA", "AXS", ])

if __name__ == "__main__":
    CPU_1 = CPU()
    #CPU_1.write_register(S_PC, 0)
    #CPU_1.INC(0xE6)
    #print(CPU_1.read_register(S_PC))
    value = open(sys.argv[1], "rb").read()
    for i in range(len(value)):
        CPU_1.MMU.write_memory(i, value[i], 1)
    PC = 0
    CPU_1.B_disasm = True
    for i in range(100):
        CPU_1.step()
