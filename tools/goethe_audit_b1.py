#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Аудит словаря против официального Goethe B1 (Goethe-/ÖSD-Zertifikat B1) Wortliste.
Проверяет: (1) артикли имеющихся слов совпадают с документом,
(2) все подходящие существительные из документа попали в словарь,
и печатает статистику. Запуск:  python tools/goethe_audit_b1.py

Слова, уже проверяемые в goethe_audit.py (A1) и goethe_audit_a2.py (A2),
здесь не дублируются.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Существительные из Goethe B1 Wortliste (2016), НЕ входящие в аудиты A1/A2 ---
# Источник: Wortgruppen (стр. 8–15) + алфавитный список (стр. 16–102).
FULL = {
    # der
    "Abfalleimer": "der", "Abschied": "der", "Abschnitt": "der",
    "Absender": "der", "Affe": "der", "Akku": "der", "Alarm": "der",
    "Alkohol": "der", "Alltag": "der", "Anbieter": "der", "Anwalt": "der",
    "Arbeiter": "der", "Arbeitsplatz": "der", "Atem": "der",
    "Aufenthalt": "der", "Ausländer": "der", "Auszubildende": "der",
    "Babysitter": "der", "Bancomat": "der", "Bart": "der", "Bau": "der",
    "Bauer": "der", "Bauernhof": "der", "Beamte": "der", "Beleg": "der",
    "Betreuer": "der", "Bikini": "der", "Bogen": "der", "Braten": "der",
    "Briefkasten": "der", "Briefträger": "der", "Briefumschlag": "der",
    "Bundeskanzler": "der", "Bundespräsident": "der", "Bundesrat": "der",
    "Bundestag": "der", "Bär": "der", "Bürger": "der",
    "Bürgermeister": "der", "Chip": "der", "Club": "der",
    "Coiffeur": "der", "Dialekt": "der", "Dialog": "der", "Dieb": "der",
    "Dienst": "der", "Donner": "der", "Einbrecher": "der",
    "Einbruch": "der", "Einfall": "der", "Elefant": "der", "Ersatz": "der",
    "Europäer": "der", "Experte": "der", "Fachmann": "der",
    "Faktor": "der", "Familienstand": "der", "Fasching": "der",
    "Fauteuil": "der", "Feierabend": "der", "Fleck": "der",
    "Fleischhauer": "der", "Flur": "der", "Fotograf": "der",
    "Franken": "der", "Friede": "der", "Führerausweis": "der",
    "Gegensatz": "der", "Gegenstand": "der", "Gegner": "der",
    "Gehsteig": "der", "Gott": "der", "Grad": "der", "Grieche": "der",
    "Grill": "der", "Hafen": "der", "Halt": "der", "Hammer": "der",
    "Handel": "der", "Hase": "der", "Held": "der", "Hersteller": "der",
    "Hit": "der", "Honig": "der", "Humor": "der", "Husten": "der",
    "Hut": "der", "Händler": "der", "Hörer": "der", "Hügel": "der",
    "ICE": "der", "Intensivkurs": "der", "Jazz": "der",
    "Journalist": "der", "Kampf": "der", "Kanal": "der", "Kandidat": "der",
    "Kanton": "der", "Kasten": "der", "Katalog": "der", "Ketchup": "der",
    "Killer": "der", "Kilometer": "der", "Klick": "der", "Kloß": "der",
    "Knochen": "der", "Knopf": "der", "Knödel": "der", "Kommentar": "der",
    "Kopierer": "der", "Kranke": "der", "Krankenwagen": "der",
    "Kreis": "der", "Kuli": "der", "Kunststoff": "der",
    "Kursleiter": "der", "Kuss": "der", "Käufer": "der", "König": "der",
    "Laster": "der", "Lautsprecher": "der", "Lehrling": "der",
    "Leiter": "der", "Lerner": "der", "Leser": "der", "Lift": "der",
    "Liter": "der", "Lkw": "der", "Lohn": "der", "Löwe": "der",
    "Maler": "der", "Manager": "der", "Meister": "der", "Meter": "der",
    "Metzger": "der", "Migrant": "der", "Minister": "der",
    "Moderator": "der", "Monitor": "der", "Muskel": "der", "Mut": "der",
    "Nachwuchs": "der", "Nagel": "der", "Nationalrat": "der",
    "Nebel": "der", "Neffe": "der", "Nichtraucher": "der",
    "Notausgang": "der", "Notfall": "der", "Notruf": "der", "Ober": "der",
    "Opa": "der", "Ordner": "der", "Ozean": "der", "PC": "der",
    "Paradeiser": "der", "Passagier": "der", "Patient": "der",
    "Personenstand": "der", "Pfeffer": "der", "Pfleger": "der",
    "Pilz": "der", "Pinguin": "der", "Pkw": "der", "Praktikant": "der",
    "Professor": "der", "Profi": "der", "Profisportler": "der",
    "Protest": "der", "Prozess": "der", "Quadratmeter": "der",
    "Radfahrer": "der", "Rahm": "der", "Rappen": "der", "Rasen": "der",
    "Rat": "der", "Rechner": "der", "Rekord": "der", "Reporter": "der",
    "Respekt": "der", "Rest": "der", "Richter": "der", "Roman": "der",
    "Saal": "der", "Sack": "der", "Salon": "der", "Schein": "der",
    "Schinken": "der", "Schlaf": "der", "Schmuck": "der", "Schmutz": "der",
    "Schnupfen": "der", "Schreck": "der", "Schriftsteller": "der",
    "Schritt": "der", "Schutz": "der", "Schweizer": "der", "Sender": "der",
    "Sieg": "der", "Sieger": "der", "Sinn": "der", "Sitz": "der",
    "Snack": "der", "Song": "der", "Sozialarbeiter": "der",
    "Speisewagen": "der", "Spezialist": "der", "Spiegel": "der",
    "Sportler": "der", "Spot": "der", "Staat": "der", "Start": "der",
    "Staub": "der", "Stein": "der", "Stempel": "der", "Steward": "der",
    "Stil": "der", "Stoff": "der", "Strafzettel": "der", "Streik": "der",
    "Strom": "der", "Strumpf": "der", "Studierende": "der", "Sturm": "der",
    "Ständerat": "der", "Swimmingpool": "der", "Tagesablauf": "der",
    "Tanz": "der", "Teilnehmer": "der", "Terminal": "der",
    "Terminkalender": "der", "Textaufbau": "der", "Tierpark": "der",
    "Tod": "der", "Tote": "der", "Tourismus": "der", "Trainer": "der",
    "Transport": "der", "Treffpunkt": "der", "Trend": "der", "Turm": "der",
    "Typ": "der", "Täter": "der", "Türke": "der", "Ukrainer": "der",
    "Unternehmer": "der", "User": "der", "Verbrecher": "der",
    "Verlierer": "der", "Vermieter": "der", "Vertreter": "der",
    "Virus": "der", "Vortrag": "der", "Wert": "der",
    "Wetterbericht": "der", "Wirt": "der", "Wissenschaftler": "der",
    "Wochentag": "der", "Wohnsitz": "der", "Zeitpunkt": "der",
    "Zentimeter": "der", "Zeuge": "der", "Zivilstand": "der",
    "Zoll": "der", "Zugang": "der", "Zuschauer": "der", "Zünder": "der",
    "Österreicher": "der", "Übersetzer": "der",
    # die
    "Abbildung": "die", "Abfahrt": "die", "Absenderin": "die",
    "Akademie": "die", "Aktion": "die", "Aktivität": "die",
    "Alternative": "die", "Anlage": "die", "Anleitung": "die",
    "Annonce": "die", "Anrede": "die", "Ansage": "die", "Anwältin": "die",
    "Anzahl": "die", "Arbeiterin": "die", "Arbeitserlaubnis": "die",
    "Arbeitslosigkeit": "die", "Arbeitsstelle": "die", "Art": "die",
    "Aufforderung": "die", "Aufnahme": "die", "Ausfahrt": "die",
    "Aushilfe": "die", "Ausländerin": "die", "Aussage": "die",
    "Aussprache": "die", "Auswahl": "die", "Babysitterin": "die",
    "Badewanne": "die", "Bahn": "die", "Bankleitzahl": "die",
    "Batterie": "die", "Beamtin": "die", "Bedienungsanleitung": "die",
    "Berufsmittelschule": "die", "Berufsschule": "die", "Besserung": "die",
    "Betreuerin": "die", "Betreuung": "die", "Bezirksschule": "die",
    "Biene": "die", "Breite": "die", "Brieftasche": "die",
    "Briefträgerin": "die", "Broschüre": "die", "Bundeskanzlerin": "die",
    "Bundespräsidentin": "die", "Bundesrätin": "die", "Burg": "die",
    "Büchse": "die", "Bühne": "die", "Bürgerin": "die",
    "Bürgermeisterin": "die", "Bürste": "die", "Castingshow": "die",
    "Chance": "die", "Chipkarte": "die", "City": "die", "Couch": "die",
    "Darstellung": "die", "Dauer": "die", "Decke": "die",
    "Demokratie": "die", "Diplommittelschule": "die", "Diskothek": "die",
    "Distanz": "die", "Diät": "die", "Dose": "die", "Droge": "die",
    "Drogerie": "die", "Durchsage": "die", "Einbahnstraße": "die",
    "Einbrecherin": "die", "Einführung": "die", "Einleitung": "die",
    "Einnahme": "die", "Einrichtung": "die", "Einzahlung": "die",
    "Einzelheit": "die", "Empfehlung": "die", "Ente": "die",
    "Entfernung": "die", "Entlassung": "die", "Etage": "die",
    "Europäerin": "die", "Fachfrau": "die", "Fahrbahn": "die",
    "Fasnacht": "die", "Fernbedienung": "die", "Festplatte": "die",
    "Feuerwehr": "die", "Figur": "die", "Fitness": "die",
    "Fleischhauerin": "die", "Flucht": "die", "Fläche": "die",
    "Flöte": "die", "Folie": "die", "Fortbildung": "die",
    "Fortsetzung": "die", "Fremdsprache": "die", "Freundschaft": "die",
    "Frist": "die", "Frisur": "die", "Frucht": "die", "Fähre": "die",
    "Galerie": "die", "Gaststätte": "die", "Gebrauchsanweisung": "die",
    "Geburt": "die", "Gemeinde": "die", "Gemeinschaft": "die",
    "Generation": "die", "Gesamtschule": "die",
    "Geschwindigkeitsbeschränkung": "die", "Gewalt": "die",
    "Gewerkschaft": "die", "Gewohnheit": "die", "Giraffe": "die",
    "Glace": "die", "Grafik": "die", "Gratulation": "die",
    "Griechin": "die", "Gymnastik": "die", "Halbpension": "die",
    "Haut": "die", "Heldin": "die", "Hitze": "die", "Hochschule": "die",
    "Hoffnung": "die", "Hälfte": "die", "Händlerin": "die", "Höhe": "die",
    "Hörerin": "die", "Hütte": "die", "Infektion": "die",
    "Integration": "die", "Intelligenz": "die", "Jause": "die",
    "Journalistin": "die", "Kabine": "die", "Kanne": "die",
    "Kantine": "die", "Karotte": "die", "Karriere": "die",
    "Kassette": "die", "Katastrophe": "die", "Killerin": "die",
    "Kindertagesstätte": "die", "Klimaanlage": "die", "Klingel": "die",
    "Klinik": "die", "Kneipe": "die", "Kommunikation": "die",
    "Konferenz": "die", "Konfitüre": "die", "Konkurrenz": "die",
    "Kontrolle": "die", "Kopie": "die", "Kraft": "die",
    "Kriminalpolizei": "die", "Krippe": "die", "Krise": "die",
    "Kuh": "die", "Kälte": "die", "Käuferin": "die", "Küste": "die",
    "Lage": "die", "Landung": "die", "Landwirtschaft": "die",
    "Langeweile": "die", "Laune": "die", "Lehre": "die",
    "Lehrstelle": "die", "Leiterin": "die", "Leitung": "die",
    "Lernerin": "die", "Leserin": "die", "Liebe": "die",
    "Lieferung": "die", "Limonade": "die", "Linie": "die", "Lippe": "die",
    "Literatur": "die", "Mahlzeit": "die", "Mahnung": "die",
    "Malerin": "die", "Managerin": "die", "Mappe": "die",
    "Margarine": "die", "Marille": "die", "Matura": "die", "Mauer": "die",
    "Maus": "die", "Mehrwertsteuer": "die", "Meldung": "die",
    "Mensa": "die", "Methode": "die", "Metropole": "die",
    "Migrantin": "die", "Migration": "die", "Milliarde": "die",
    "Million": "die", "Ministerin": "die", "Mittelschule": "die",
    "Mobilbox": "die", "Mobilität": "die", "Moderatorin": "die",
    "Muttersprache": "die", "Mücke": "die", "Mühe": "die",
    "Müllabfuhr": "die", "Mülltonne": "die", "Münze": "die",
    "Nachfrage": "die", "Nachhilfe": "die", "Nachspeise": "die",
    "Nadel": "die", "Neuigkeit": "die", "Nichte": "die",
    "Nichtraucherin": "die", "Notaufnahme": "die", "Oma": "die",
    "Oper": "die", "Operation": "die", "Ordination": "die",
    "Orientierungsstufe": "die", "Panne": "die", "Partei": "die",
    "Passagierin": "die", "Patientin": "die", "Pension": "die",
    "Pfanne": "die", "Pflaume": "die", "Pflegerin": "die",
    "Pflicht": "die", "Philosophie": "die", "Pille": "die",
    "Planung": "die", "Plattform": "die", "Praktikantin": "die",
    "Presse": "die", "Primarschule": "die", "Produktion": "die",
    "Professorin": "die", "Profisportlerin": "die", "Puppe": "die",
    "Qualifikation": "die", "Radfahrerin": "die", "Realschule": "die",
    "Recherche": "die", "Rede": "die", "Reform": "die",
    "Reihenfolge": "die", "Reklame": "die", "Reportage": "die",
    "Reporterin": "die", "Reservierung": "die", "Richterin": "die",
    "Richtung": "die", "Rolle": "die", "Rufnummer": "die", "Runde": "die",
    "Rundfahrt": "die", "Rückfahrt": "die", "Rückkehr": "die",
    "Rückmeldung": "die", "SMS": "die", "Saison": "die", "Salbe": "die",
    "Schachtel": "die", "Scheibe": "die", "Schildkröte": "die",
    "Schrift": "die", "Schriftstellerin": "die", "Schularbeit": "die",
    "Schuld": "die", "Schulter": "die", "Schwangerschaft": "die",
    "Schweizerin": "die", "Schüssel": "die", "Sekundarschule": "die",
    "Semmel": "die", "Serie": "die", "Show": "die", "Siegerin": "die",
    "Socke": "die", "Software": "die", "Sonderschule": "die",
    "Sorge": "die", "Sozialarbeiterin": "die", "Spezialistin": "die",
    "Spielgruppe": "die", "Sportart": "die", "Sportlerin": "die",
    "Spritze": "die", "Spur": "die", "Station": "die", "Statistik": "die",
    "Stewardess": "die", "Stiege": "die", "Stimme": "die",
    "Stimmung": "die", "Strafe": "die", "Strecke": "die",
    "Struktur": "die", "Studie": "die", "Stufe": "die", "Sucht": "die",
    "Summe": "die", "Tabelle": "die", "Tankstelle": "die",
    "Tastatur": "die", "Taste": "die", "Tat": "die", "Tatsache": "die",
    "Technik": "die", "Technologie": "die", "Teilnahme": "die",
    "Teilnehmerin": "die", "Teilzeit": "die", "Terrasse": "die",
    "Theorie": "die", "Therapie": "die", "Trainerin": "die",
    "Trennung": "die", "Träne": "die", "Täterin": "die",
    "Tätigkeit": "die", "Türkin": "die", "Tüte": "die",
    "Ukrainerin": "die", "Umfrage": "die", "Umleitung": "die",
    "Umweltverschmutzung": "die", "Uniform": "die", "Unterhaltung": "die",
    "Unternehmerin": "die", "Unterstützung": "die", "Untersuchung": "die",
    "Urkunde": "die", "Userin": "die", "Vase": "die", "Verabredung": "die",
    "Verbrecherin": "die", "Verliererin": "die", "Vermieterin": "die",
    "Vermietung": "die", "Vermittlung": "die", "Versammlung": "die",
    "Versichertenkarte": "die", "Vertreterin": "die", "Vertretung": "die",
    "Visitenkarte": "die", "Volkshochschule": "die", "Volksschule": "die",
    "Vorbereitung": "die", "Vorfahrt": "die", "Vorschrift": "die",
    "Vorsicht": "die", "Vorwahl": "die", "WG": "die", "Wanderung": "die",
    "Ware": "die", "Weiterbildung": "die", "Wettervorhersage": "die",
    "Wirklichkeit": "die", "Wirtin": "die", "Wissenschaft": "die",
    "Wissenschaftlerin": "die", "Wolle": "die", "Wunde": "die",
    "Wärme": "die", "Zahlung": "die", "Zahnbürste": "die",
    "Zahncreme": "die", "Zange": "die", "Zeichnung": "die", "Zeile": "die",
    "Zeugin": "die", "Zigarette": "die", "Zone": "die",
    "Zusammenarbeit": "die", "Zuschauerin": "die", "Zweitsprache": "die",
    "Öffentlichkeit": "die", "Österreicherin": "die",
    "Übernachtung": "die", "Überraschung": "die", "Überschrift": "die",
    "Übersetzerin": "die", "Übersetzung": "die", "Überstunde": "die",
    "Überweisung": "die",
    # das
    "Abenteuer": "das", "Abo": "das", "Abonnement": "das",
    "Alphabet": "das", "Altenheim": "das", "Altersheim": "das",
    "Amt": "das", "Apartment": "das", "Ballett": "das", "Boot": "das",
    "Buffet": "das", "Bundesland": "das", "Camp": "das", "Couvert": "das",
    "Detail": "das", "Diplom": "das", "E-Bike": "das",
    "Einschreiben": "das", "Faschierte": "das", "Feuerzeug": "das",
    "Forum": "das", "Frühjahr": "das", "Fundbüro": "das",
    "Gasthaus": "das", "Gebäck": "das", "Gedicht": "das",
    "Geheimnis": "das", "Gift": "das", "Girokonto": "das", "Gramm": "das",
    "Gras": "das", "Hackfleisch": "das", "Hallenbad": "das",
    "Haustier": "das", "Heim": "das", "Heimweh": "das",
    "Hilfsmittel": "das", "Holz": "das", "Insekt": "das", "Inserat": "das",
    "Institut": "das", "Jahrtausend": "das", "Kabel": "das",
    "Kaffeehaus": "das", "Kapitel": "das", "Kennzeichen": "das",
    "Kfz": "das", "Kilo": "das", "Knie": "das", "Konsulat": "das",
    "Kostüm": "das", "Kraftfahrzeug": "das", "Kraftwerk": "das",
    "Krokodil": "das", "Lager": "das", "Laufwerk": "das", "Leder": "das",
    "Lexikon": "das", "Loch": "das", "Lokal": "das", "Magazin": "das",
    "Material": "das", "Meer": "das", "Mehl": "das", "Menü": "das",
    "Metall": "das", "Modell": "das", "Modul": "das",
    "Mountainbike": "das", "Märchen": "das", "Müsli": "das",
    "Nahrungsmittel": "das", "Netz": "das", "Obergeschoss": "das",
    "Orchester": "das", "Original": "das", "Parlament": "das",
    "Pech": "das", "Personal": "das", "Pflaster": "das", "Picknick": "das",
    "Plastik": "das", "Portemonnaie": "das", "Poulet": "das",
    "Prozent": "das", "Puzzle": "das", "Referat": "das", "Risiko": "das",
    "Rohr": "das", "Rüebli": "das", "Sandwich": "das", "Schaf": "das",
    "Schaufenster": "das", "Schmerzmittel": "das", "Schnitzel": "das",
    "Schwammerl": "das", "Schwein": "das", "Semester": "das",
    "Souvenir": "das", "Stadion": "das", "Steak": "das",
    "Stiegenhaus": "das", "Streichholz": "das", "Studio": "das",
    "Suchtmittel": "das", "Symbol": "das", "TV": "das", "Talent": "das",
    "Taschentuch": "das", "Tempo": "das", "Tram": "das",
    "Treppenhaus": "das", "Trinkgeld": "das", "Trottoir": "das",
    "Untergeschoss": "das", "Vergnügen": "das", "Verkehrszeichen": "das",
    "Verständnis": "das", "Video": "das", "Visum": "das", "Vitamin": "das",
    "Vorstellungsgespräch": "das", "WC": "das", "Werk": "das",
    "Wissen": "das", "Wunder": "das", "Zeichen": "das",
    "Zertifikat": "das", "Zeug": "das", "Zündholz": "das",
}

# Гомографы, новые для B1: нет (See/Band/Teil/Cola/Comic/Erwachsene/
# Jugendliche/Angestellte — уже в A1-аудите, Bekannte — в A2).
MULTI = {}

# Только множественное число — новые относительно A1/A2
PLURAL_EXPECTED_B1 = ["Abgase", "Medien", "Personalien", "Senioren",
                      "Zinsen", "Zutaten"]


def main():
    words = json.load(open(os.path.join(ROOT, "public", "words.json"), encoding="utf-8"))
    present = {}
    for w in words:
        present.setdefault(w["word"], set()).add(w["article"])

    single = {w: a for w, a in FULL.items() if w not in MULTI}

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

    for w in PLURAL_EXPECTED_B1:
        if "Plural" not in present.get(w, set()):
            missing.append(f"Plural {w}")

    total_single = len(single)
    total_multi = len(MULTI)
    total_plural = len(PLURAL_EXPECTED_B1)
    total = total_single + total_multi + total_plural

    print("=" * 64)
    print("АУДИТ ПРОТИВ Goethe B1 (Zertifikat B1) Wortliste")
    print("(только слова, не входящие в аудиты A1/A2)")
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
