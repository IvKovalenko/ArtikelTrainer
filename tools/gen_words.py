#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генератор словаря для тренажёра артиклей.
Слова сгруппированы по уровню (A1..C2) и роду (der/die/das).
Правь списки ниже и запускай:  python tools/gen_words.py
Результат: public/words.json  (плоский массив {word, article, level}).
"""
import json
import os

# der = мужской, die = женский, das = средний
DATA = {
    "A1": {
        "der": ["Tag","Mann","Tisch","Stuhl","Baum","Hund","Apfel","Ball","Berg",
                "Bruder","Vater","Sohn","Name","Morgen","Abend","Monat","Sommer",
                "Winter","Frühling","Herbst","Kaffee","Tee","Zug","Bus","Film",
                "Brief","Garten","Kopf","Fuß","Arm","Mund","Schlüssel","Löffel",
                "Teller","Fisch","Vogel","Wein","Saft","Käse","Zucker","Regen",
                "Schnee","Wind","Himmel","Stern","Mond","Preis","Euro","Freund",
                "Lehrer","Arzt","Zahn"],
        "die": ["Frau","Stadt","Tür","Blume","Katze","Mutter","Tochter","Schwester",
                "Nacht","Woche","Stunde","Minute","Zeit","Sonne","Straße","Schule",
                "Kirche","Bank","Uhr","Lampe","Tasche","Flasche","Tasse","Gabel",
                "Milch","Butter","Suppe","Banane","Orange","Tomate","Kartoffel",
                "Zwiebel","Familie","Sprache","Musik","Farbe","Zahl","Frage",
                "Antwort","Reise","Arbeit","Zeitung","Adresse","Nummer","Karte",
                "Hand","Nase","Brille","Küche","Wand","Freundin","Lehrerin"],
        "das": ["Haus","Kind","Land","Wasser","Brot","Fenster","Auto","Buch","Bett",
                "Zimmer","Bild","Papier","Heft","Wort","Jahr","Ei","Fleisch","Obst",
                "Gemüse","Bier","Glas","Messer","Handy","Telefon","Radio","Fahrrad",
                "Flugzeug","Schiff","Tier","Pferd","Geld","Herz","Auge","Ohr","Bein",
                "Haar","Gesicht","Kino","Hotel","Restaurant","Büro","Krankenhaus",
                "Wetter","Feuer","Spiel","Foto","Baby","Mädchen","Getränk"],
    },
    "A2": {
        "der": ["Beruf","Urlaub","Termin","Ausflug","Flughafen","Bahnhof","Markt",
                "Supermarkt","Platz","Weg","Unfall","Fehler","Wunsch","Traum",
                "Anfang","Schluss","Erfolg","Nachteil","Vorteil","Grund","Rabatt",
                "Kunde","Verkäufer","Kellner","Kollege","Partner","Körper","Rücken",
                "Bauch","Finger","Daumen","Schrank","Sessel","Teppich","Vorhang",
                "Wecker","Kühlschrank","Herd","Ofen","Balkon","Keller","Aufzug",
                "Schatten","Nachbar"],
        "die": ["Fahrt","Wohnung","Miete","Rechnung","Quittung","Kasse","Bäckerei",
                "Apotheke","Bibliothek","Post","Haltestelle","Ampel","Kreuzung",
                "Umgebung","Gegend","Landschaft","Grenze","Hauptstadt","Region",
                "Meinung","Idee","Erfahrung","Gesundheit","Krankheit","Erkältung",
                "Grippe","Verletzung","Behandlung","Medizin","Tablette","Ernährung",
                "Bewegung","Entscheidung","Einladung","Hochzeit","Kindheit","Jugend",
                "Zukunft","Vergangenheit","Wäsche","Dusche","Heizung","Treppe",
                "Aussicht"],
        "das": ["Gepäck","Ticket","Gleis","Ziel","Ergebnis","Beispiel","Problem",
                "Thema","Interesse","Hobby","Konzert","Instrument","Klavier","Rezept",
                "Frühstück","Mittagessen","Abendessen","Besteck","Werkzeug","Gehalt",
                "Konto","Bargeld","Angebot","Geschenk","Paket","Formular","Dokument",
                "Zeugnis","Studium","Praktikum","Ausland","Erlebnis","Gefühl","Sofa",
                "Regal","Kissen","Handtuch","Waschbecken"],
    },
    "B1": {
        "der": ["Vertrag","Antrag","Ausweis","Reisepass","Führerschein","Lebenslauf",
                "Bewerber","Arbeitgeber","Arbeitnehmer","Betrieb","Gewinn","Verlust",
                "Umsatz","Haushalt","Verbrauch","Anschluss","Empfang","Zuschlag",
                "Zuschuss","Betrag","Überblick","Eindruck","Ausdruck","Zusammenhang",
                "Unterschied","Zweck","Ablauf","Vorschlag","Hinweis","Ratschlag",
                "Streit","Konflikt","Verkehr","Stau","Wald","Fluss","Gipfel","Boden",
                "Zweig","Ast"],
        "die": ["Bewerbung","Kündigung","Versicherung","Steuer","Gebühr",
                "Unterschrift","Genehmigung","Verwaltung","Behörde","Regierung",
                "Gesellschaft","Bevölkerung","Wirtschaft","Industrie","Umwelt",
                "Verantwortung","Beziehung","Ehe","Scheidung","Erziehung",
                "Ausbildung","Prüfung","Note","Leistung","Fähigkeit","Voraussetzung",
                "Bedingung","Möglichkeit","Gelegenheit","Wirkung","Ursache","Folge",
                "Entwicklung","Veränderung","Verbesserung","Lösung","Herausforderung",
                "Sicherheit","Freiheit","Wahrheit","Wahl","Nachricht","Werbung",
                "Anzeige"],
        "das": ["Gesetz","Recht","Urteil","Gericht","Gefängnis","Verbrechen","Opfer",
                "Gebäude","Grundstück","Eigentum","Vermögen","Einkommen","Unternehmen",
                "Ereignis","Verhalten","Verhältnis","Bedürfnis","Vorurteil",
                "Missverständnis","Abkommen","Netzwerk","Verfahren","Merkmal",
                "Vorbild","Bewusstsein","Wachstum","Publikum","Gelände","Ufer","Tal",
                "Gebirge","Klima","Jahrhundert","Jahrzehnt"],
    },
    "B2": {
        "der": ["Anspruch","Aufwand","Beitrag","Verzicht","Ansatz","Aspekt","Begriff",
                "Standpunkt","Widerspruch","Vorwurf","Verdacht","Beweis","Nachweis",
                "Rückgang","Anstieg","Aufschwung","Wettbewerb","Wohlstand",
                "Fortschritt","Ruf","Einfluss","Druck","Zwang","Mangel","Überfluss",
                "Verlauf","Umgang","Bereich","Rahmen","Maßstab","Schwerpunkt",
                "Grundsatz","Zusammenhalt","Zufall","Anlass","Vorgang","Ursprung",
                "Wandel"],
        "die": ["Grundlage","Annahme","Vermutung","Behauptung","Feststellung",
                "Erkenntnis","Einsicht","Absicht","Haltung","Einstellung",
                "Überzeugung","Wahrnehmung","Vorstellung","Auffassung",
                "Auseinandersetzung","Vereinbarung","Zustimmung","Ablehnung","Kritik",
                "Beschwerde","Forderung","Erwartung","Enttäuschung","Begeisterung",
                "Zufriedenheit","Rücksicht","Nachhaltigkeit","Verfügung",
                "Zuständigkeit","Vielfalt","Mehrheit","Minderheit","Ausnahme","Regel",
                "Tendenz","Steigerung"],
        "das": ["Vorhaben","Anliegen","Bestreben","Zugeständnis","Zusammenspiel",
                "Gleichgewicht","Ausmaß","Missverhältnis","Hindernis","Versäumnis",
                "Gewissen","Vertrauen","Misstrauen","Verlangen","Vorgehen",
                "Eingreifen","Streben","Wesen","Ansehen"],
    },
    "C1": {
        "der": ["Diskurs","Konsens","Kompromiss","Sachverhalt","Tatbestand",
                "Missstand","Zustand","Aufschub","Vorbehalt","Einwand","Vorstoß",
                "Rückhalt","Verzug","Verschleiß","Niedergang","Umbruch","Aufbruch",
                "Zerfall","Zusammenbruch","Andrang"],
        "die": ["Erörterung","Abhandlung","Auslegung","Deutung","Willkür","Nachsicht",
                "Umsicht","Weitsicht","Zuversicht","Gewissheit","Ungewissheit",
                "Beharrlichkeit","Beständigkeit","Tragweite","Reichweite",
                "Gepflogenheit","Gegebenheit","Selbstverständlichkeit"],
        "das": ["Ermessen","Vermächtnis","Gefüge","Gemisch","Unterfangen","Sinnbild",
                "Gleichnis","Aufsehen","Aufkommen","Wohlbefinden","Unbehagen"],
    },
    "C2": {
        "der": ["Dissens","Überdruss","Verdruss","Scharfsinn","Eifer","Ehrgeiz","Neid",
                "Zorn","Groll","Trost","Reiz","Reichtum","Irrtum","Brauch","Ruhm",
                "Beistand"],
        "die": ["Voreingenommenheit","Befangenheit","Gesinnung","Vergänglichkeit",
                "Endlichkeit","Wehmut","Sehnsucht","Zuneigung","Abneigung","Ehrfurcht",
                "Demut","Anmut","Muße","Bürde","Fülle","Leere","Ferne","Nähe","Tugend",
                "Sitte","Beliebigkeit"],
        "das": ["Gepräge","Gemenge","Trugbild","Zerrbild","Gedeihen","Verderben",
                "Wohlwollen","Missfallen","Dasein","Sein","Werden","Ansinnen"],
    },
}

# --- Существительные из официального словаря Goethe A1 (Fit in Deutsch 1, 2024),
#     которых не было в основном списке выше. Добавляются на уровень A1.
#     Однозначные слова (один род) — здесь. Особые случаи — ниже:
#       * гомографы (разный род по значению) — в HOMOGRAPHS (со значением по-русски);
#       * только множественное число — в PLURAL_WORDS (ответ «Plural»).
#     Cola/Comic взяты в стандартном роде (die Cola, der Comic); региональные
#     варианты das Cola / das Comic существуют, но здесь не проверяются.
GOETHE_A1_ADD = {
    "der": ["Anruf","Anrufbeantworter","Appetit","Artikel","Automat","Bahnsteig",
            "Basketball","Bleistift","Dank","Durst","Fahrplan","Familienname",
            "Fotoapparat","Fußball","Geburtstag","Glückwunsch","Gruß","Hals",
            "Herr","Hunger","Junge","Kakao","Kiosk","Kuchen","Kugelschreiber",
            "Kurs","Mantel","Marktplatz","Ohrring","Park","Pullover","Quatsch",
            "Radiergummi","Ring","Rucksack","Salat","Schmerz","Spaß","Spielplatz",
            "Sport","Strand","Unterricht","Vorname","Computer","Blog","CD-Player",
            "Laptop","Link","Chat","Antwortbogen","Prüfungsteil","Test","Text",
            "Architekt","Techniker","Ingenieur","Künstler","Kaufmann","Hausmann",
            "Schauspieler","Sekretär","Onkel","Großvater","Norden","Süden","Westen",
            "Osten","Vormittag","Mittag","Nachmittag","Januar","Februar","März",
            "April","Mai","Juni","Juli","August","September","Oktober","November",
            "Dezember","Sonntag","Montag","Dienstag","Mittwoch","Donnerstag",
            "Freitag","Samstag",
            # в документе перечислены без артикля, но род есть:
            "Cent","Karneval","Comic"],
    "die": ["Achtung","Ahnung","Angst","Ärztin","Bluse","Disco","Eins",
            "Entschuldigung","Fahrkarte","Geschichte","Hausaufgabe","Information",
            "Insel","Jacke","Kamera","Klasse","Klassenarbeit","Lust","Marmelade",
            "Ordnung","Pause","Pizza","Postkarte","Sache","Schokolade","Tante",
            "Toilette","U-Bahn","Wurst","CD","DVD","Homepage","Mail","Mailbox",
            "Aufgabe","Lösung","Partnerin","Grundschule","Hauptschule",
            "Sprachenschule","Architektin","Technikerin","Künstlerin","Ingenieurin",
            "Kauffrau","Hausfrau","Schauspielerin","Sekretärin","Großmutter",
            # школьные предметы (в документе без артикля, но род есть):
            "Mathematik","Physik","Chemie","Geografie","Kunst","Sozialkunde","Cola"],
    "das": ["Alter","Bad","Brötchen","Ende","Essen","Fach","Fernsehen","Eis",
            "Geschäft","Glück","Kleid","Mal","Mineralwasser","Quiz","Rad","Rätsel",
            "Schwimmbad","Stück","Taschengeld","Theater","T-Shirt","Wiedersehen",
            "Wohnzimmer","Internet","Poster","Smartphone","Fax","Kreuz","Gespräch",
            "Wörterbuch","Gymnasium","Wochenende",
            # языки как предметы (в документе без артикля, но род есть):
            "Deutsch","Englisch","Ostern","Weihnachten"],
}

# Гомографы: одно написание — разный род по значению. Показываются со значением
# по-русски, каждое значение — отдельная карточка. (Уровень A1.)
HOMOGRAPHS = [
    {"word": "See", "article": "der", "gloss": "озеро"},
    {"word": "See", "article": "die", "gloss": "море"},
    {"word": "Band", "article": "der", "gloss": "том"},
    {"word": "Band", "article": "die", "gloss": "группа"},
    {"word": "Band", "article": "das", "gloss": "лента"},
    {"word": "Teil", "article": "der", "gloss": "часть"},
    {"word": "Teil", "article": "das", "gloss": "деталь"},
    # субстантивированные прилагательные: род зависит от пола человека
    {"word": "Erwachsene", "article": "der", "gloss": "муж."},
    {"word": "Erwachsene", "article": "die", "gloss": "жен."},
    {"word": "Jugendliche", "article": "der", "gloss": "муж."},
    {"word": "Jugendliche", "article": "die", "gloss": "жен."},
    {"word": "Angestellte", "article": "der", "gloss": "муж."},
    {"word": "Angestellte", "article": "die", "gloss": "жен."},
]

# Существительные только во множественном числе — правильный ответ «Plural».
PLURAL_WORDS = ["Eltern", "Geschwister", "Großeltern", "Ferien", "Jeans",
                "Leute", "Süßigkeiten"]

LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def build():
    # добавляем слова из словаря Goethe A1 к уровню A1
    for article, words in GOETHE_A1_ADD.items():
        DATA["A1"][article].extend(words)

    out = []
    seen = set()          # ключ = (слово, значение) — гомографы не конфликтуют
    dupes = []

    def add(word, article, level, gloss=None):
        key = (word, gloss or "")
        if key in seen:
            dupes.append(word if not gloss else f"{word} ({gloss})")
            return
        seen.add(key)
        entry = {"word": word, "article": article, "level": level}
        if gloss:
            entry["gloss"] = gloss
        out.append(entry)

    for level in LEVEL_ORDER:
        for article in ("der", "die", "das"):
            for word in DATA[level][article]:
                add(word, article, level)
    for h in HOMOGRAPHS:
        add(h["word"], h["article"], h.get("level", "A1"), h["gloss"])
    for word in PLURAL_WORDS:
        add(word, "Plural", "A1")

    return out, dupes


def main():
    words, dupes = build()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "public", "words.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=0, separators=(",", ":"))
        f.write("\n")

    per_level = {lvl: 0 for lvl in LEVEL_ORDER}
    for w in words:
        per_level[w["level"]] += 1
    print(f"Записано {len(words)} слов в {dest}")
    for lvl in LEVEL_ORDER:
        print(f"  {lvl}: {per_level[lvl]}")
    if dupes:
        print(f"Пропущены дубликаты: {sorted(set(dupes))}")


if __name__ == "__main__":
    main()
