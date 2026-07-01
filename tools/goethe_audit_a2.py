#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Аудит словаря против официального Goethe A2 (Goethe-Zertifikat A2) Wortliste.
Проверяет: (1) артикли имеющихся слов совпадают с документом,
(2) все подходящие существительные из документа попали в словарь,
и печатает статистику. Запуск:  python tools/goethe_audit_a2.py

Слова, уже проверяемые в goethe_audit.py (A1), здесь не дублируются.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Существительные из Goethe A2 Wortliste (2016), НЕ входящие в A1-аудит ---
# Источник: алфавитный список (стр. 8–31) + Wortgruppen (стр. 5–7).
FULL = {
    # A
    "Ampel": "die", "Angebot": "das", "Ankunft": "die",
    "Anmeldung": "die", "Anschluss": "der", "Anzug": "der",
    "Apparat": "der", "Aufzug": "der", "Ausgang": "der",
    "Auskunft": "die", "Ausstellung": "die", "Autobahn": "die",
    "Ausweis": "der",
    # B
    "Bäcker": "der", "Bäckerei": "die", "Bäckerin": "die",
    "Bahnsteig": "der", "Balkon": "der", "Baustelle": "die",
    "Bescheid": "der", "Besuch": "der", "Bewerbung": "die",
    "Birne": "die", "Briefmarke": "die", "Brücke": "die",
    "Büro": "das",
    # C
    "Café": "das", "Cafeteria": "die", "Chef": "der", "Creme": "die",
    # D
    "Dame": "die", "Datei": "die", "Datum": "das",
    "Direktor": "der", "Doktor": "der", "Doktorin": "die",
    "Doppelzimmer": "das", "Dorf": "das", "Drucker": "der",
    # E
    "E-Book": "das", "Ecke": "die", "Ehefrau": "die", "Ehemann": "der",
    "Eingang": "der", "Einkaufszentrum": "das", "Einzelzimmer": "das",
    "Empfänger": "der", "Erdgeschoss": "das",
    "Erfahrung": "die", "Erlaubnis": "die", "Ermäßigung": "die",
    # F
    "Fahrer": "der", "Fahrerin": "die",
    "Fan": "der", "Farbe": "die", "Feier": "die",
    "Fernseher": "der", "Festival": "das", "Fieber": "das",
    "Firma": "die", "Flohmarkt": "der", "Flug": "der",
    "Freizeit": "die", "Friseur": "der", "Friseurin": "die",
    "Führerschein": "der", "Führung": "die",
    # G
    "Gabel": "die", "Garage": "die",
    "Gast": "der", "Gegenteil": "das", "Gehalt": "das",
    "Geldbörse": "die", "Gerät": "das", "Gericht": "das",
    "Gewitter": "das", "Gitarre": "die",
    "Gruppe": "die",
    # H
    "Halle": "die", "Hamburger": "der", "Hand": "die",
    "Handtuch": "das", "Handwerker": "der", "Handwerkerin": "die",
    "Haushalt": "der", "Hauptstadt": "die", "Heimat": "die",
    "Heizung": "die", "Hemd": "das", "Herd": "der",
    "Hilfe": "die", "Hose": "die",
    # I
    "Instrument": "das", "Interesse": "das", "Interview": "das",
    # J
    "Job": "der", "Jugendherberge": "die",
    # K
    "Kalender": "der", "Kasse": "die", "Kaufhaus": "das",
    "Keller": "der", "Kette": "die", "Kirche": "die",
    "Kleidung": "die", "Koch": "der", "Köchin": "die",
    "Koffer": "der", "Kollege": "der", "Kollegin": "die",
    "Kontakt": "der", "Konto": "das", "Körper": "der",
    "Krankenkasse": "die", "Krankenpfleger": "der", "Krankenschwester": "die",
    "Kredit": "der", "Krimi": "der", "Kultur": "die",
    "Kunde": "der", "Kundin": "die", "Kunst": "die",
    # L
    "Laden": "der", "Landschaft": "die", "Lied": "das",
    "Löffel": "der",
    # M
    "Magen": "der", "Mannschaft": "die", "Maschine": "die",
    "Mechaniker": "der", "Mechanikerin": "die", "Meinung": "die",
    "Menge": "die", "Mensch": "der", "Messe": "die",
    "Miete": "die", "Mittagessen": "das", "Mitternacht": "die",
    "Mobiltelefon": "das", "Mode": "die", "Moment": "der",
    "Motor": "der", "Motorroller": "der", "Müll": "der",
    "Museum": "das", "Musikerin": "die", "Musiker": "der",
    "Mütze": "die",
    # N
    "Nachbar": "der", "Nachbarin": "die", "Natur": "die",
    # O
    "Öl": "das",
    # P
    "Paar": "das", "Parfüm": "das", "Party": "die",
    "Pass": "der", "Passwort": "das", "Pflanze": "die",
    "Plan": "der", "Plakat": "das", "Polizei": "die",
    "Polizist": "der", "Polizistin": "die", "Portion": "die",
    "Postleitzahl": "die", "Praktikum": "das", "Praxis": "die",
    "Produkt": "das", "Programm": "das", "Projekt": "das",
    "Prospekt": "der",
    # Q
    "Qualität": "die",
    # R
    "Rathaus": "das", "Rechnung": "die", "Reinigung": "die",
    "Reihe": "die", "Reisebüro": "das", "Reiseführer": "der",
    "Rentner": "der", "Rentnerin": "die", "Reparatur": "die",
    "Rezeption": "die", "Rock": "der", "Rose": "die",
    "Ruhe": "die", "Rundgang": "der",
    # S
    "Sänger": "der", "Sängerin": "die",
    "Schalter": "der", "Schere": "die", "Schild": "das",
    "Schirm": "der", "Schlafzimmer": "das", "Schloss": "das",
    "Schuh": "der", "Schüler": "der", "Schweiz": "die",
    "Sehenswürdigkeit": "die", "Seife": "die", "Sekretariat": "das",
    "Sekunde": "die", "Sendung": "die", "Service": "der",
    "Situation": "die", "Ski": "der", "Sofa": "das",
    "Speisekarte": "die", "Spaziergang": "der", "Sprechstunde": "die",
    "Stadtplan": "der", "Star": "der",
    "Stelle": "die", "Stiefel": "der", "Stift": "der",
    "Stock": "der", "Stockwerk": "das", "Straßenbahn": "die",
    "Stress": "der", "Student": "der", "Studentin": "die",
    "Studium": "das", "Stundenplan": "der",
    # T
    "Tablet": "das", "Tablette": "die", "Tafel": "die",
    "Taxi": "das", "Team": "das", "Tennis": "das",
    "Termin": "der", "Ticket": "das", "Tipp": "der",
    "Titel": "der", "Topf": "der", "Torte": "die",
    "Tour": "die", "Tourist": "der", "Touristin": "die",
    "Training": "das",
    # U
    "Umzug": "der", "Universität": "die", "Unterkunft": "die",
    # V
    "Veranstaltung": "die", "Verein": "der", "Verkehr": "der",
    "Verkäufer": "der", "Verkäuferin": "die",
    "Verkehrsmittel": "das", "Verspätung": "die", "Vertrag": "der",
    "Vorschlag": "der",
    # W
    "Wagen": "der", "Wäsche": "die", "Webseite": "die",
    "Werkstatt": "die", "Wettbewerb": "der", "Witz": "der",
    "Wolke": "die", "Workshop": "der", "Wunsch": "der",
    # Z
    "Zahnarzt": "der", "Zeitschrift": "die", "Zelt": "das",
    "Zeugnis": "das", "Ziel": "das", "Zirkus": "der",
    "Zitrone": "die", "Zoo": "der",
    # Wortgruppen — Schulfächer (нет в A1-аудите)
    "Abitur": "das", "Biologie": "die", "Direktor": "der",
    "Französisch": "das", "Klassenfahrt": "die", "Latein": "das",
    "Religion": "die", "Sekretariat": "das",
    # Wortgruppen — Familienmitglieder
    "Cousin": "der", "Cousine": "die", "Enkel": "der", "Enkelin": "die",
    # Wortgruppen — Berufe (только те, кого нет в A1)
    "Bäcker": "der", "Bäckerin": "die",
}

# --- Особые случаи ---

# Гомографы: в A1-аудите уже есть See (der), Band (die), Erwachsene, Jugendliche,
# Angestellte, Teil, Cola, Comic. Здесь только новые для A2.
MULTI = {
    "Bekannte": {"der", "die"},   # der/die Bekannte (субстантивированное прил.)
}

# Только множественное число — новые относительно A1
PLURAL_EXPECTED_A2 = ["Fundsachen", "Kenntnisse", "Lebensmittel", "Möbel",
                      "Papiere", "Pommes frites"]

# Школьные предметы без артикля в документе — фактический род (новые для A2)
ARTICLED_SUBJECTS = {
    "Biologie": "die",
    "Französisch": "das",
    "Geschichte": "die",   # в A2 явно в алфавитном разделе
    "Latein": "das",
    "Religion": "die",
}


def main():
    words = json.load(open(os.path.join(ROOT, "public", "words.json"), encoding="utf-8"))
    present = {}
    for w in words:
        present.setdefault(w["word"], set()).add(w["article"])

    single = {w: a for w, a in FULL.items() if w not in MULTI}
    single.update(ARTICLED_SUBJECTS)

    missing, mismatch = [], []

    for w, a in single.items():
        arts = present.get(w)
        if not arts:
            missing.append(f"{a} {w}")
        elif a not in arts:
            mismatch.append((w, a, "/".join(sorted(arts))))

    for w, allowed in MULTI.items():
        if not (present.get(w, set()) & allowed):
            missing.append(f"{'/'.join(sorted(allowed))} {w}")

    for w in PLURAL_EXPECTED_A2:
        if "Plural" not in present.get(w, set()):
            missing.append(f"Plural {w}")

    total_single = len(single)
    total_multi = len(MULTI)
    total_plural = len(PLURAL_EXPECTED_A2)
    total = total_single + total_multi + total_plural

    print("=" * 64)
    print("АУДИТ ПРОТИВ Goethe A2 (Goethe-Zertifikat A2) Wortliste")
    print("(только слова, не входящие в A1-аудит)")
    print("=" * 64)
    print(f"Существительных с однозначным родом               : {total_single}")
    print(f"Гомографы / субстантивированные (несколько родов) : {total_multi}")
    print(f"Только множественное число (ответ «Plural»)       : {total_plural}")
    print(f"ИТОГО существительных из документа                : {total}")
    print(f"Всего записей в словаре (включая гомографы)       : {len(words)}")
    print("-" * 64)

    ok = True
    if mismatch:
        ok = False
        print(f"!!! НЕСОВПАДЕНИЯ АРТИКЛЕЙ ({len(mismatch)}):")
        for w, doc, cur in mismatch:
            print(f"    {w}: документ={doc}, словарь={cur}")
    else:
        print("Несовпадений артиклей с документом: НЕТ ✓")

    if missing:
        ok = False
        print(f"!!! НЕ ПОПАЛИ В СЛОВАРЬ ({len(missing)}): {sorted(missing)}")
    else:
        print("Все существительные из документа присутствуют ✓")

    print("=" * 64)
    print("ИТОГ:", "ВСЁ ОК ✓" if ok else "ЕСТЬ ПРОБЛЕМЫ — см. выше")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
