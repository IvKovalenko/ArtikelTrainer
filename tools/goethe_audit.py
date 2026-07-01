#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Аудит словаря против официального Goethe A1 (Fit in Deutsch 1) Wortliste.
Проверяет: (1) артикли имеющихся слов совпадают с документом,
(2) все подходящие существительные из документа попали в словарь,
и печатает статистику. Запуск:  python tools/goethe_audit.py
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ВСЕ существительные с артиклем (r=der, e=die, s=das) из документа Goethe A1 ---
FULL = {
    # A
    "Achtung": "die", "Adresse": "die", "Ahnung": "die", "Alter": "das",
    "Anfang": "der", "Angst": "die", "Anruf": "der", "Anrufbeantworter": "der",
    "Antwort": "die", "Antwortbogen": "der", "Anzeige": "die", "Apfel": "der",
    "Apotheke": "die", "Appetit": "der", "Arbeit": "die", "Architekt": "der",
    "Architektin": "die", "Arm": "der", "Artikel": "der", "Arzt": "der",
    "Ärztin": "die", "Auge": "das", "Aufgabe": "die", "Ausflug": "der",
    "Ausland": "das", "Auto": "das", "Automat": "der",
    # B
    "Baby": "das", "Bad": "das", "Bahnhof": "der", "Bahnsteig": "der",
    "Ball": "der", "Banane": "die", "Band": "die", "Basketball": "der",
    "Bauch": "der", "Baum": "der", "Beispiel": "das", "Beruf": "der",
    "Bett": "das", "Bibliothek": "die", "Bleistift": "der", "Blog": "der",
    "Blume": "die", "Bluse": "die", "Brief": "der", "Brot": "das",
    "Brötchen": "das", "Bruder": "der", "Buch": "das", "Bus": "der",
    # C
    "CD": "die", "CD-Player": "der", "Chat": "der", "Cola": "die",
    "Comic": "der", "Computer": "der",
    # D
    "Dank": "der", "Disco": "die", "Durst": "der", "DVD": "die",
    # E
    "Ei": "das", "Einladung": "die", "Eins": "die", "Eis": "das", "Ende": "das",
    "Entschuldigung": "die", "Erwachsene": "der", "Essen": "das", "Euro": "der",
    # F
    "Fach": "das", "Fahrkarte": "die", "Fahrplan": "der", "Fahrrad": "das",
    "Familie": "die", "Familienname": "der", "Fax": "das", "Fehler": "der",
    "Fenster": "das", "Fernsehen": "das", "Film": "der", "Fisch": "der",
    "Flasche": "die", "Fleisch": "das", "Flughafen": "der", "Flugzeug": "das",
    "Fluss": "der", "Foto": "das", "Fotoapparat": "der", "Frage": "die",
    "Frau": "die", "Freund": "der", "Freundin": "die", "Frühling": "der",
    "Frühstück": "das", "Fuß": "der", "Fußball": "der",
    # G
    "Garten": "der", "Geburtstag": "der", "Geld": "das", "Gemüse": "das",
    "Gepäck": "das", "Geschäft": "das", "Geschenk": "das", "Geschichte": "die",
    "Gespräch": "das", "Glas": "das", "Gleis": "das", "Glück": "das",
    "Glückwunsch": "der", "Großmutter": "die", "Großvater": "der",
    "Grundschule": "die", "Gruß": "der", "Gymnasium": "das",
    # H
    "Haar": "das", "Hals": "der", "Haltestelle": "die", "Handy": "das",
    "Hauptschule": "die", "Haus": "das", "Hausaufgabe": "die", "Hausfrau": "die",
    "Hausmann": "der", "Heft": "das", "Herbst": "der", "Herr": "der",
    "Hobby": "das", "Hochzeit": "die", "Homepage": "die", "Hund": "der",
    "Hunger": "der",
    # I
    "Idee": "die", "Information": "die", "Ingenieur": "der", "Ingenieurin": "die",
    "Insel": "die", "Internet": "das",
    # J
    "Jacke": "die", "Jahr": "das", "Jugendliche": "der", "Junge": "der",
    # K
    "Kaffee": "der", "Kakao": "der", "Kamera": "die", "Karte": "die",
    "Kartoffel": "die", "Käse": "der", "Katze": "die", "Kauffrau": "die",
    "Kaufmann": "der", "Kind": "das", "Kino": "das", "Kiosk": "der",
    "Klasse": "die", "Klassenarbeit": "die", "Klavier": "das", "Kleid": "das",
    "Kopf": "der", "Krankenhaus": "das", "Kreuz": "das", "Kuchen": "der",
    "Küche": "die", "Kühlschrank": "der", "Kugelschreiber": "der",
    "Künstler": "der", "Künstlerin": "die", "Kurs": "der",
    # L
    "Lampe": "die", "Land": "das", "Laptop": "der", "Lehrer": "der",
    "Lehrerin": "die", "Link": "der", "Lösung": "die", "Lust": "die",
    # M
    "Mädchen": "das", "Mail": "die", "Mailbox": "die", "Mal": "das",
    "Mann": "der", "Mantel": "der", "Markt": "der", "Marktplatz": "der",
    "Marmelade": "die", "Milch": "die", "Mineralwasser": "das", "Minute": "die",
    "Mittag": "der", "Musik": "die", "Mutter": "die",
    # N
    "Nachmittag": "der", "Nachricht": "die", "Nacht": "die", "Name": "der",
    "Norden": "der", "Note": "die", "Nummer": "die",
    # O
    "Obst": "das", "Ohrring": "der", "Onkel": "der", "Ordnung": "die",
    "Osten": "der",
    # P
    "Paket": "das", "Park": "der", "Partner": "der", "Partnerin": "die",
    "Pause": "die", "Pferd": "das", "Pizza": "die", "Platz": "der",
    "Post": "die", "Poster": "das", "Postkarte": "die", "Problem": "das",
    "Prüfungsteil": "der", "Pullover": "der",
    # Q
    "Quatsch": "der", "Quiz": "das",
    # R
    "Rad": "das", "Radiergummi": "der", "Radio": "das", "Rätsel": "das",
    "Regen": "der", "Reise": "die", "Restaurant": "das", "Ring": "der",
    "Rucksack": "der",
    # S
    "Sache": "die", "Saft": "der", "Salat": "der", "Schauspieler": "der",
    "Schauspielerin": "die", "Schiff": "das", "Schmerz": "der",
    "Schokolade": "die", "Schule": "die", "Schwester": "die",
    "Schwimmbad": "das", "See": "der", "Sekretär": "der", "Sekretärin": "die",
    "Smartphone": "das", "Spaß": "der", "Spiel": "das", "Spielplatz": "der",
    "Sport": "der", "Sprache": "die", "Sprachenschule": "die", "Stadt": "die",
    "Strand": "der", "Straße": "die", "Stück": "das", "Stunde": "die",
    "Supermarkt": "der", "Suppe": "die",
    # T
    "Tag": "der", "Tante": "die", "Tasche": "die", "Taschengeld": "das",
    "Tasse": "die", "Techniker": "der", "Technikerin": "die", "Tee": "der",
    "Teil": "der", "Test": "der", "Text": "der", "Theater": "das",
    "Thema": "das", "Tier": "das", "Tisch": "der", "Toilette": "die",
    "Tür": "die", "T-Shirt": "das",
    # U
    "U-Bahn": "die", "Uhr": "die", "Unterricht": "der",
    # V
    "Vater": "der", "Vormittag": "der", "Vorname": "der",
    # W
    "Wald": "der", "Wasser": "das", "Westen": "der", "Wiedersehen": "das",
    "Woche": "die", "Wochenende": "das", "Wohnung": "die", "Wohnzimmer": "das",
    "Wort": "das", "Wörterbuch": "das", "Wurst": "die",
    # Z
    "Zahn": "der", "Zeit": "die", "Zeitung": "die", "Zimmer": "das", "Zug": "der",
    # времена года / суток / прочее с явным родом
    "Morgen": "der", "Abend": "der", "Sommer": "der", "Winter": "der",
    "Süden": "der", "Angestellte": "der",
    # месяцы (все der)
    "Januar": "der", "Februar": "der", "März": "der", "April": "der",
    "Mai": "der", "Juni": "der", "Juli": "der", "August": "der",
    "September": "der", "Oktober": "der", "November": "der", "Dezember": "der",
    # дни недели (все der)
    "Sonntag": "der", "Montag": "der", "Dienstag": "der", "Mittwoch": "der",
    "Donnerstag": "der", "Freitag": "der", "Samstag": "der",
}

# --- Особые случаи документа ---

# гомографы и субстантивированные прил.: в документе указан такой род (набор).
# В словаре у них по несколько карточек (со значением), проверяем пересечение.
MULTI = {
    "See": {"der"},                 # r See
    "Band": {"die"},                # e Band (муз. группа)
    "Teil": {"der"},                # r Teil
    "Cola": {"die", "das"},         # e/s Cola
    "Comic": {"der", "das"},        # r/s Comic
    "Erwachsene": {"der", "die"},   # r/e Erwachsene
    "Jugendliche": {"der", "die"},  # r/e Jugendliche
    "Angestellte": {"der", "die"},  # r/e Angestellte
}

# перечислены в документе без явного артикля, но род есть — теперь добавлены
ARTICLED_SUBJECTS = {
    "Deutsch": "das", "Englisch": "das", "Mathematik": "die", "Geografie": "die",
    "Kunst": "die", "Sozialkunde": "die", "Physik": "die", "Chemie": "die",
    "Cent": "der", "Karneval": "der", "Ostern": "das", "Weihnachten": "das",
}

# только множественное число — правильный ответ «Plural»
PLURAL_EXPECTED = ["Eltern", "Geschwister", "Großeltern", "Ferien", "Jeans",
                   "Leute", "Süßigkeiten"]


def main():
    words = json.load(open(os.path.join(ROOT, "public", "words.json"), encoding="utf-8"))
    present = {}                      # слово -> множество родов (учёт всех значений)
    for w in words:
        present.setdefault(w["word"], set()).add(w["article"])

    # однозначные существительные из документа (один род)
    single = {w: a for w, a in FULL.items() if w not in MULTI}
    single.update(ARTICLED_SUBJECTS)

    missing, mismatch = [], []

    # 1) однозначные: нужный род должен присутствовать
    for w, a in single.items():
        arts = present.get(w)
        if not arts:
            missing.append(f"{a} {w}")
        elif a not in arts:
            mismatch.append((w, a, "/".join(sorted(arts))))

    # 2) гомографы/адъективные: хотя бы один из родов документа присутствует
    for w, allowed in MULTI.items():
        if not (present.get(w, set()) & allowed):
            missing.append(f"{'/'.join(sorted(allowed))} {w}")

    # 3) только множественное число: должен быть ответ «Plural»
    for w in PLURAL_EXPECTED:
        if "Plural" not in present.get(w, set()):
            missing.append(f"Plural {w}")

    total = len(single) + len(MULTI) + len(PLURAL_EXPECTED)

    print("=" * 64)
    print("АУДИТ ПРОТИВ Goethe A1 (Fit in Deutsch 1) Wortliste")
    print("=" * 64)
    print(f"Существительных с однозначным родом               : {len(single)}")
    print(f"Гомографы / адъективные (несколько родов)         : {len(MULTI)}")
    print(f"Только множественное число (ответ «Plural»)       : {len(PLURAL_EXPECTED)}")
    print(f"ИТОГО существительных из документа                : {total}")
    print(f"Всего записей в словаре (со значениями гомографов) : {len(words)}")
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
