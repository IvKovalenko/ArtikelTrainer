#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генератор словаря для тренажёра артиклей.
Слова сгруппированы по уровню (A1..C2) и роду (der/die/das).
Правь списки ниже и запускай:  python tools/gen_words.py
Результат: public/words.json  (плоский массив {word, article, level}).
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Переводы слов: {немецкое слово: перевод}. Отдельные модули, чтобы
# не раздувать этот файл. Слова без перевода останутся без поля "ru"/"en".
from translations import TRANSLATIONS
from translations_en import TRANSLATIONS_EN

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
        "der": ["Antrag","Reisepass","Lebenslauf",
                "Bewerber","Arbeitgeber","Arbeitnehmer","Betrieb","Gewinn","Verlust",
                "Umsatz","Haushalt","Verbrauch","Anschluss","Empfang","Zuschlag",
                "Zuschuss","Betrag","Überblick","Eindruck","Ausdruck","Zusammenhang",
                "Zweck","Ablauf","Vorschlag","Hinweis","Ratschlag",
                "Streit","Konflikt","Stau","Wald","Fluss","Gipfel","Boden",
                "Zweig","Ast"],
        "die": ["Bewerbung","Kündigung","Versicherung","Steuer","Gebühr",
                "Genehmigung","Verwaltung","Behörde","Regierung",
                "Gesellschaft","Bevölkerung","Wirtschaft","Industrie","Umwelt",
                "Verantwortung","Beziehung","Ehe","Scheidung","Erziehung",
                "Ausbildung","Prüfung","Note","Leistung","Fähigkeit","Voraussetzung",
                "Bedingung","Möglichkeit","Gelegenheit","Wirkung","Ursache","Folge",
                "Entwicklung","Veränderung","Verbesserung","Herausforderung",
                "Sicherheit","Freiheit","Wahrheit","Wahl","Nachricht","Werbung",
                "Anzeige"],
        "das": ["Gesetz","Recht","Urteil","Gefängnis","Verbrechen","Opfer",
                "Gebäude","Grundstück","Eigentum","Vermögen","Einkommen","Unternehmen",
                "Ereignis","Verhalten","Verhältnis","Bedürfnis","Vorurteil",
                "Missverständnis","Abkommen","Netzwerk","Verfahren","Merkmal",
                "Vorbild","Bewusstsein","Wachstum","Publikum","Gelände","Ufer","Tal",
                "Gebirge","Klima","Jahrhundert","Jahrzehnt"],
    },
    "B2": {
        "der": ["Anspruch","Aufwand","Beitrag","Verzicht","Ansatz","Aspekt","Begriff",
                "Standpunkt","Widerspruch","Vorwurf","Verdacht","Beweis","Nachweis",
                "Rückgang","Anstieg","Aufschwung","Wohlstand",
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
                "Demut","Anmut","Muße","Bürde","Fülle","Leere","Ferne","Tugend",
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
            "Herr","Hunger","Junge","Kakao","Kiosk","Kuchen","Kugelschreiber (Kuli)",
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
    "die": ["Achtung","Ahnung","Angst","Ärztin","Bluse","Diskothek (Disco)","Eins",
            "Entschuldigung","Fahrkarte","Geschichte","Hausaufgabe","Information",
            "Insel","Jacke","Kamera","Klasse","Klassenarbeit","Lust","Marmelade",
            "Ordnung","Pause","Pizza","Postkarte","Sache","Schokolade","Tante",
            "Toilette","U-Bahn","Wurst","CD","DVD","Homepage","Mail","Mailbox",
            "Aufgabe","Lösung","Partnerin","Grundschule","Hauptschule",
            "Sprachenschule","Architektin","Technikerin","Künstlerin","Ingenieurin",
            "Kauffrau","Hausfrau","Schauspielerin","Sekretärin","Großmutter",
            # школьные предметы (в документе без артикля, но род есть):
            "Mathematik","Physik","Chemie","Geografie","Kunst","Sozialkunde","Cola",
            # перенесено из PLURAL_WORDS (есть ед. число):
            "Süßigkeit","Jeans"],
    "das": ["Alter","Bad","Brötchen","Ende","Essen","Fach","Fernsehen","Eis",
            "Geschäft","Glück","Kleid","Mal","Mineralwasser","Quiz","Rad","Rätsel",
            "Schwimmbad","Stück","Taschengeld","Theater","T-Shirt","Wiedersehen",
            "Wohnzimmer","Internet","Poster","Smartphone","Fax","Kreuz","Gespräch",
            "Wörterbuch","Gymnasium","Wochenende",
            # языки как предметы (в документе без артикля, но род есть):
            "Deutsch","Englisch","Ostern","Weihnachten"],
}

# --- Существительные из официального словаря Goethe A2 (Goethe-Zertifikat A2, 2016),
#     которых не было в основных списках DATA выше. Добавляются на уровень A2.
#     Структура аналогична GOETHE_A1_ADD. Слова из A1 не дублируются.
GOETHE_A2_ADD = {
    "der": [
        "Bäcker", "Doktor", "Fahrer", "Friseur", "Handwerker", "Koch",
        "Krankenpfleger", "Mechaniker", "Musiker", "Polizist", "Rentner",
        "Sänger", "Cousin", "Enkel", "Direktor", "Stundenplan",
        "Apparat", "Arbeitstag", "Ausgang", "Ausweis",
        "Bescheid", "Buchstabe",
        "Chef", "Eingang", "Eintritt", "Empfänger",
        "Fan", "Feiertag", "Flohmarkt", "Flug", "Führerschein",
        "Gast", "Hamburger", "Kalender", "Kriminalroman (Krimi)",
        "Laden","Magen", "Motor", "Motorroller", "Müll", "Ort",
        "Pass", "Plan", "Raum", "Reifen", "Reiseführer", "Rock", "Rundgang",
        "Satz", "Schalter", "Schirm", "Schüler", "Service", "Ski",
        "Spaziergang", "Stadtplan", "Star", "Stiefel", "Stift", "Stock",
        "Stress", "Student", "Tipp", "Titel", "Tourist",
        "Umzug", "Unterschied", "Verein", "Verkehr", "Vertrag",
        "Volleyball", "Wettbewerb", "Witz", "Workshop",
        "Zahnarzt", "Zettel", "Zirkus", "Zoo",
        "Anzug", "Besuch", "Drucker", "Ehemann", "Fernseher",
        "Job", "Koffer", "Kontakt", "Kredit",
        "Mensch", "Moment", "Prospekt", "Schuh", "Topf", "Wagen",
    ],
    "die": [
        "Bäckerin", "Doktorin", "Fahrerin", "Friseurin", "Handwerkerin",
        "Köchin", "Krankenschwester", "Mechanikerin", "Musikerin",
        "Polizistin", "Rentnerin", "Sängerin", "Verkäuferin",
        "Cousine", "Enkelin", "Verwandte",
        "Biologie", "Klassenfahrt", "Religion",
        "Mitternacht",
        "Ankunft", "Auskunft", "Ausstellung", "Autobahn",
        "Baustelle", "Bitte", "Bohne", "Brücke",
        "Cafeteria", "Creme",
        "Dame", "Datei",
        "Ehefrau", "Erlaubnis", "Ermäßigung",
        "Feier", "Firma", "Freizeit", "Führung",
        "Garage", "Geldbörse", "Gitarre", "Gruppe",
        "Halle", "Heimat", "Hilfe", "Hose",
        "Jugendherberge", "Kette", "Kleidung", "Krankenkasse", "Kreditkarte",
        "Kultur", "Lüge", "Mannschaft", "Messe", "Mode",
        "Nähe", "Natur", "Notiz", "Nudel",
        "Party", "Person", "Pflanze", "Polizei", "Portion", "Postleitzahl",
        "Praxis", "Qualität", "Reinigung", "Reihe", "Reparatur", "Rose", "Ruhe",
        "Schere", "Schweiz", "Sehenswürdigkeit", "Seife", "Seite",
        "Sendung", "Situation", "Speisekarte", "Sprechstunde",
        "Stelle", "Straßenbahn", "Tafel", "Tour", "Unterschrift", "Unterkunft", "Universität",
        "Veranstaltung", "Verspätung",
        "Webseite", "Welt", "Werkstatt", "Wolke",
        "Zeitschrift", "Anmeldung", "Birne", "Briefmarke", "Ecke",
        "Kollegin", "Kundin", "Maschine", "Menge", "Mütze",
        "Nachbarin", "Rezeption", "Sekunde", "Studentin",
        "Torte", "Touristin", "Zitrone", "Kenntnis",
    ],
    "das": [
        "Abitur", "Französisch", "Latein", "Sekretariat",
        "Blatt", "Café", "Ding", "Doppelzimmer", "Dorf",
        "E-Book", "Einkaufszentrum", "Einzelzimmer", "Erdgeschoss",
        "Festival (Fest)", "Fieber",
        "Gerät", "Gericht", "Geschirr", "Gewitter",
        "Hähnchen", "Hemd", "Interview",
        "Leben", "Licht", "Lied",
        "Mittel", "Mobiltelefon", "Museum",
        "Öl", "Paar", "Parfüm", "Passwort", "Plakat",
        "Produkt", "Programm", "Projekt",
        "Rind", "Schlafzimmer", "Schloss",
        "Stipendium", "Stockwerk",
        "Tablet", "Taxi", "Team", "Tennis", "Training",
        "Zelt", "Zentrum", "Lebensmittel", "Möbel",
        "Datum", "Gegenteil", "Kaufhaus", "Rathaus",
        "Reisebüro", "Schild", "Verkehrsmittel",
    ],
}

# --- Существительные из официального словаря Goethe B1 (Zertifikat B1, 2016),
#     которых не было в основных списках DATA и в добавках A1/A2 выше.
#     Добавляются на уровень B1. Структура аналогична GOETHE_A1_ADD / A2_ADD.
#     Слова из A1/A2 не дублируются. Артикль — стандартный немецкий.
GOETHE_B1_ADD = {
    "der": [
        "Abfalleimer", "Abschied", "Abschnitt", "Absender", "Affe", "Akkumulator (Akku)",
        "Alarm", "Alkohol", "Alltag", "Anbieter", "Anwalt", "Arbeiter",
        "Arbeitsplatz", "Atem", "Aufenthalt", "Ausländer", "Auszubildende",
        "Babysitter", "Bancomat", "Bart", "Bau", "Bauer", "Bauernhof", "Beamte",
        "Beleg", "Betreuer", "Bikini", "Bogen", "Braten", "Briefkasten",
        "Briefträger", "Briefumschlag", "Bundeskanzler", "Bundespräsident",
        "Bundesrat", "Bundestag", "Bär", "Bürger", "Bürgermeister", "Chip",
        "Club", "Coiffeur", "Dialekt", "Dialog", "Dieb", "Dienst", "Donner",
        "Einbrecher", "Einbruch", "Einfall", "Elefant", "Ersatz", "Europäer",
        "Experte", "Fachmann", "Faktor", "Familienstand", "Fasching", "Fauteuil",
        "Feierabend", "Fleck", "Fleischhauer", "Flur", "Fotograf", "Franken",
        "Führerausweis", "Gegensatz", "Gegenstand", "Gegner",
        "Gehsteig", "Gott", "Grad", "Grieche", "Grill", "Hafen", "Halt",
        "Hammer", "Handel", "Hase", "Held", "Hersteller", "Hit", "Honig",
        "Humor", "Husten", "Hut", "Händler", "Hörer", "Hügel", "ICE",
        "Intensivkurs", "Jazz", "Journalist", "Kampf", "Kanal", "Kandidat",
        "Kanton", "Kasten", "Katalog", "Ketchup", "Killer", "Kilometer", "Klick",
        "Kloß", "Knochen", "Knopf", "Knödel", "Kommentar", "Kopierer", "Kranke",
        "Krankenwagen", "Kreis", "Kunststoff", "Kursleiter", "Kuss",
        "Käufer", "König", "Laster", "Lautsprecher", "Lehrling", "Leiter",
        "Lerner", "Leser", "Lift", "Liter", "Lastkraftwagen (Lkw)", "Lohn", "Löwe", "Maler",
        "Manager", "Meister", "Meter", "Metzger", "Migrant", "Minister",
        "Moderator", "Monitor", "Muskel", "Mut", "Nachwuchs", "Nagel",
        "Nationalrat", "Nebel", "Neffe", "Nichtraucher", "Notausgang", "Notfall",
        "Notruf", "Ober", "Opa", "Ordner", "Ozean", "PC", "Paradeiser",
        "Passagier", "Patient", "Personenstand", "Pfeffer", "Pfleger", "Pilz",
        "Pinguin", "Personenkraftwagen (Pkw)", "Praktikant", "Professor", "Profi", "Profisportler",
        "Protest", "Prozess", "Quadratmeter", "Radfahrer", "Rahm", "Rappen",
        "Rasen", "Rat", "Rechner", "Rekord", "Reporter", "Respekt", "Rest",
        "Richter", "Roman", "Saal", "Sack", "Salon", "Schein", "Schinken",
        "Schlaf", "Schmuck", "Schmutz", "Schnupfen", "Schreck", "Schriftsteller",
        "Schritt", "Schutz", "Schweizer", "Sender", "Sieg", "Sieger", "Sinn",
        "Sitz", "Snack", "Song", "Sozialarbeiter", "Speisewagen", "Spezialist",
        "Spiegel", "Sportler", "Spot", "Staat", "Start", "Staub", "Stein",
        "Stempel", "Steward", "Stil", "Stoff", "Strafzettel", "Streik", "Strom",
        "Strumpf", "Studierende", "Sturm", "Ständerat", "Swimmingpool",
        "Tagesablauf", "Tanz", "Teilnehmer", "Terminal", "Terminkalender",
        "Textaufbau", "Tierpark", "Tod", "Tote", "Tourismus", "Trainer",
        "Transport", "Treffpunkt", "Trend", "Turm", "Typ", "Täter", "Türke",
        "Ukrainer", "Unternehmer", "User", "Verbrecher", "Verlierer", "Vermieter",
        "Vertreter", "Virus", "Vortrag", "Wert", "Wetterbericht", "Wirt",
        "Wissenschaftler", "Wochentag", "Wohnsitz", "Zeitpunkt", "Zentimeter",
        "Zeuge", "Zivilstand", "Zoll", "Zugang", "Zuschauer", "Zünder",
        "Österreicher", "Übersetzer", "Senior", "Zins",
    ],
    "die": [
        "Abbildung", "Abfahrt", "Absenderin", "Akademie", "Aktion", "Aktivität",
        "Alternative", "Anlage", "Anleitung", "Annonce", "Anrede", "Ansage",
        "Anwältin", "Anzahl", "Arbeiterin", "Arbeitserlaubnis",
        "Arbeitslosigkeit", "Arbeitsstelle", "Art", "Aufforderung", "Aufnahme",
        "Ausfahrt", "Aushilfe", "Ausländerin", "Aussage", "Aussprache",
        "Auswahl", "Babysitterin", "Badewanne", "Bahn", "Bankleitzahl",
        "Batterie", "Beamtin", "Bedienungsanleitung", "Berufsmittelschule",
        "Berufsschule", "Besserung", "Betreuerin", "Betreuung", "Bezirksschule",
        "Biene", "Breite", "Brieftasche", "Briefträgerin", "Broschüre",
        "Bundeskanzlerin", "Bundespräsidentin", "Bundesrätin", "Burg", "Büchse",
        "Bühne", "Bürgerin", "Bürgermeisterin", "Bürste", "Castingshow",
        "Chance", "Chipkarte", "Couch", "Darstellung", "Dauer", "Decke",
        "Demokratie", "Diplommittelschule", "Distanz", "Diät",
        "Dose", "Droge", "Drogerie", "Durchsage", "Einbahnstraße",
        "Einbrecherin", "Einführung", "Einleitung", "Einnahme", "Einrichtung",
        "Einzahlung", "Einzelheit", "Empfehlung", "Ente", "Entfernung",
        "Entlassung", "Etage", "Europäerin", "Fachfrau", "Fahrbahn", "Fasnacht",
        "Fernbedienung", "Festplatte", "Feuerwehr", "Figur", "Fitness",
        "Fleischhauerin", "Flucht", "Fläche", "Flöte", "Folie", "Fortbildung",
        "Fortsetzung", "Fremdsprache", "Freundschaft", "Frist", "Frisur",
        "Frucht", "Fähre", "Galerie", "Gaststätte", "Gebrauchsanweisung",
        "Geburt", "Gemeinde", "Gemeinschaft", "Generation", "Gesamtschule",
        "Geschwindigkeit", "Beschränkung", "Gewalt", "Gewerkschaft", "Gewohnheit",
        "Giraffe", "Grafik", "Gratulation", "Griechin", "Gymnastik",
        "Halbpension", "Haut", "Heldin", "Hitze", "Hochschule", "Hoffnung",
        "Hälfte", "Händlerin", "Höhe", "Hörerin", "Hütte", "Infektion",
        "Integration", "Intelligenz", "Jause", "Journalistin", "Kabine", "Kanne",
        "Kantine", "Karotte", "Karriere", "Kassette", "Katastrophe", "Killerin",
        "Kindertagesstätte", "Klimaanlage", "Klingel", "Klinik", "Kneipe",
        "Kommunikation", "Konferenz", "Konfitüre", "Konkurrenz", "Kontrolle",
        "Kopie", "Kraft", "Kriminalpolizei", "Krippe", "Krise", "Kuh", "Kälte",
        "Käuferin", "Küste", "Lage", "Landung", "Landwirtschaft", "Langeweile",
        "Laune", "Lehre", "Lehrstelle", "Leiterin", "Leitung", "Lernerin",
        "Leserin", "Liebe", "Lieferung", "Limonade", "Linie", "Lippe",
        "Literatur", "Mahlzeit", "Mahnung", "Malerin", "Managerin", "Mappe",
        "Margarine", "Marille", "Matura", "Mauer", "Maus", "Mehrwertsteuer",
        "Meldung", "Mensa", "Methode", "Metropole", "Migrantin", "Migration",
        "Milliarde", "Million", "Ministerin", "Mittelschule", "Mobilbox",
        "Mobilität", "Moderatorin", "Muttersprache", "Mücke", "Mühe",
        "Müllabfuhr", "Mülltonne", "Münze", "Nachfrage", "Nachhilfe",
        "Nachspeise", "Nadel", "Neuigkeit", "Nichte", "Nichtraucherin",
        "Notaufnahme", "Oma", "Oper", "Operation", "Ordination",
        "Orientierungsstufe", "Panne", "Partei", "Passagierin", "Patientin",
        "Pension", "Pfanne", "Pflaume", "Pflegerin", "Pflicht", "Philosophie",
        "Pille", "Planung", "Plattform", "Praktikantin", "Presse",
        "Primarschule", "Produktion", "Professorin", "Profisportlerin", "Puppe",
        "Qualifikation", "Radfahrerin", "Realschule", "Recherche", "Rede",
        "Reform", "Reihenfolge", "Reklame", "Reportage", "Reporterin",
        "Reservierung", "Richterin", "Richtung", "Rolle", "Rufnummer", "Runde",
        "Rundfahrt", "Rückfahrt", "Rückkehr", "Rückmeldung", "SMS", "Saison",
        "Salbe", "Schachtel", "Scheibe", "Schildkröte", "Schrift",
        "Schriftstellerin", "Schularbeit", "Schuld", "Schulter",
        "Schwangerschaft", "Schweizerin", "Schüssel", "Sekundarschule", "Semmel",
        "Serie", "Show", "Siegerin", "Socke", "Software", "Sonderschule",
        "Sorge", "Sozialarbeiterin", "Spezialistin", "Spielgruppe", "Sportart",
        "Sportlerin", "Spritze", "Spur", "Station", "Statistik", "Stewardess",
        "Stiege", "Stimme", "Stimmung", "Strafe", "Strecke", "Struktur",
        "Studie", "Stufe", "Sucht", "Summe", "Tabelle", "Tankstelle", "Tastatur",
        "Taste", "Tat", "Tatsache", "Technik", "Technologie", "Teilnahme",
        "Teilnehmerin", "Teilzeit", "Terrasse", "Theorie", "Therapie",
        "Trainerin", "Trennung", "Träne", "Täterin", "Tätigkeit", "Türkin",
        "Tüte", "Ukrainerin", "Umfrage", "Umleitung", "Umweltverschmutzung",
        "Uniform", "Unterhaltung", "Unternehmerin", "Unterstützung",
        "Untersuchung", "Urkunde", "Userin", "Vase", "Verabredung",
        "Verbrecherin", "Verliererin", "Vermieterin", "Vermietung", "Vermittlung",
        "Versammlung", "Versichertenkarte", "Vertreterin", "Vertretung",
        "Visitenkarte", "Volkshochschule", "Volksschule", "Vorbereitung",
        "Vorfahrt", "Vorschrift", "Vorsicht", "Vorwahl", "Wohngemeinschaft (WG)", "Wanderung",
        "Ware", "Weiterbildung", "Wettervorhersage", "Wirklichkeit", "Wirtin",
        "Wissenschaft", "Wissenschaftlerin", "Wolle", "Wunde", "Wärme",
        "Zahlung", "Zahnbürste", "Zahncreme", "Zange", "Zeichnung", "Zeile",
        "Zeugin", "Zigarette", "Zone", "Zusammenarbeit", "Zuschauerin",
        "Zweitsprache", "Öffentlichkeit", "Österreicherin", "Übernachtung",
        "Überraschung", "Überschrift", "Übersetzerin", "Übersetzung",
        "Überstunde", "Überweisung", "Fundsache", "Zutat"
    ],
    "das": [
        "Abenteuer", "Abonnement (Abo)", "Alphabet", "Altenheim", "Altersheim",
        "Amt", "Apartment", "Ballett", "Boot", "Buffet", "Bundesland", "Camp",
        "Couvert", "Detail", "Diplom", "E-Bike", "Einschreiben", "Faschierte",
        "Feuerzeug", "Forum", "Frühjahr", "Fundbüro", "Gasthaus", "Gebäck",
        "Gedicht", "Geheimnis", "Gift", "Girokonto", "Gramm", "Gras",
        "Hackfleisch", "Hallenbad", "Haustier", "Heim", "Heimweh", "Hilfsmittel",
        "Holz", "Insekt", "Inserat", "Institut", "Jahrtausend", "Kabel",
        "Kaffeehaus", "Kapitel", "Kennzeichen", "Kraftfahrzeug (Kfz)", "Kilogramm (Kilo)", "Knie",
        "Konsulat", "Kostüm", "Kraftfahrzeug", "Kraftwerk", "Krokodil", "Lager",
        "Laufwerk", "Leder", "Lexikon", "Loch", "Lokal", "Magazin", "Material",
        "Meer", "Mehl", "Menü", "Metall", "Modell", "Modul", "Mountainbike",
        "Märchen", "Müsli", "Nahrungsmittel", "Netz", "Obergeschoss", "Orchester",
        "Original", "Parlament", "Pech", "Personal", "Pflaster", "Picknick",
        "Portemonnaie", "Poulet", "Prozent", "Puzzle", "Referat",
        "Risiko", "Rohr", "Rüebli", "Sandwich", "Schaf", "Schaufenster",
        "Schmerzmittel", "Schnitzel", "Schwammerl", "Schwein", "Semester",
        "Souvenir", "Stadion", "Steak", "Stiegenhaus", "Streichholz", "Studio",
        "Suchtmittel", "Symbol", "TV", "Talent", "Taschentuch", "Tempo", "Tram",
        "Treppenhaus", "Trinkgeld", "Trottoir", "Untergeschoss", "Vergnügen",
        "Verkehrszeichen", "Verständnis", "Video", "Visum", "Vitamin",
        "Vorstellungsgespräch", "WC", "Werk", "Wissen", "Wunder", "Zeichen",
        "Zertifikat", "Zeug", "Zündholz", "Abgas", "Medium",
    ],
}

# --- Существительные из пользовательского списка B2_Vocabs_All.csv,
#     которых не было в основных списках DATA и в добавках A1/A2/B1 выше.
#     Добавляются на уровень B2. Отобраны только реальные существительные
#     (глаголы, прилагательные, фразы, опечатки, имена собственные и формы
#     мн. числа из исходного файла исключены; ясные формы мн. приведены к ед.).
#     Артикль — стандартный немецкий (по правилам суффиксов / последнего корня).
B2_VOCAB_ADD = {
    "der": [
        "Abgang", "Abschluss", "Abschwung", "Absturz", "Aktienkurs", "Alleingang",
        "Angriffspunkt", "Anhänger", "Anlauf", "Anpfiff", "Appell", "Aufschlag",
        "Auftakt", "Auftritt", "Aufwind", "Auslöser", "Ausschnitt", "Ballungsraum",
        "Baukasten", "Befürworter", "Beitritt", "Beweggrund", "Bezug", "Blickwinkel",
        "Bodenschatz", "Brennpunkt", "Brennstoff", "Bruch", "Buchhalter", "Chirurg",
        "Dauerauftrag", "Dauerbrenner", "Domplatz", "Durchbruch", "Einnahmeausfall",
        "Einsatz", "Einschnitt", "Erdkreis", "Erkenntnisgewinn", "Fachbegriff",
        "Fernverkehr", "Föderalismus", "Friedensschluss", "Friedensvertrag",
        "Frontverlauf", "Galopp", "Gedankengang", "Gehweg", "Gesichtspunkt",
        "Gottesdienst", "Graben", "Haftbefehl", "Hergang", "Hinterhof",
        "Inhaltsstoff", "Irrglaube", "Jahresabschluss", "Karfreitag", "Katzensprung",
        "Knochenjob", "Knotenpunkt", "Kohlenstoff", "Leitzins", "Losentscheid",
        "Machthaber", "Maiseintopf", "Maschinenbau", "Militärputsch", "Milliardenwert",
        "Mittelweg", "Mobilfunk", "Morgenmuffel", "Moscheeverband", "Nachahmungstäter",
        "Nachholbedarf", "Nahverkehr", "Notfallsanitäter", "Parkverstoß",
        "Rechtsschutz", "Rechtsstaat", "Ruderverein", "Rückstand", "Sachverstand",
        "Saldo", "Samt", "Sanierungsfall", "Sanierungsstau", "Sattelschlepper",
        "Scheibenwischer", "Scheinwerfer", "Schnabel", "Schöpfer", "Schrott",
        "Schwachkopf", "Seelsorger", "Sonnenstrom", "Spielraum", "Spitzenvertreter",
        "Sprengstoff", "Stausee", "Stützpunkt", "Sündenfall", "Teamgeist",
        "Trauschein", "Unterhaltsvorschuss", "Unterschlupf", "Verbraucher", "Verfall",
        "Verfassungsrang", "Vergleich", "Verhaltenskodex", "Verlag",
        "Versorgungsengpass", "Vorgänger", "Waffenstillstand", "Wahlkreis",
        "Wassermangel", "Weisheitszahn", "Werdegang", "Wirtschaftsberater",
        "Wühltisch", "Zeitgeist", "Zeitraum", "Zuzug", "Zwilling", "Zwischenfall",
        "Zwischenruf",
    ],
    "die": [
        "Aberkennung", "Abkehr", "Abrüstung", "Abschiebung", "Abschreibung",
        "Abtreibung", "Abwehr", "Abweichung", "Abwertung", "Akteneinsicht",
        "Aktiengesellschaft", "Albernheit", "Altersvorsorge", "Andeutung",
        "Anfeindung", "Anforderung", "Anlaufstelle", "Anordnung", "Anreizwirkung",
        "Anspannung", "Antike", "Arbeitsausbeutung", "Aufhebung", "Aufmunterung",
        "Aufrüstung", "Aufweichung", "Augenbraue", "Ausdauer", "Aushilfstätigkeit",
        "Ausschreibung", "Ausweitung", "Bagatellgrenze", "Bedrohung",
        "Beeinträchtigung", "Beerdigung", "Befugnis", "Begabung", "Begegnung",
        "Belastbarkeit", "Belastung", "Belohnung", "Belüftung", "Benennung",
        "Bereicherung", "Berufung", "Beschaffungsmethode", "Bescheidenheit",
        "Beschäftigung", "Bestandsaufnahme", "Bestechung", "Bestätigung",
        "Beteiligung", "Bettdecke", "Beute", "Bevormundung", "Bezugsperson",
        "Blessur", "Bohrplattform", "Bonität", "Borreliose", "Brotzeit",
        "Bundeswehr", "Bürgschaft", "Dachfirma", "Datenauswertung", "Drohkulisse",
        "Dunkelflaute", "Dunkelziffer", "Durchlässigkeit", "Dürre", "Einbettung",
        "Einbeziehung", "Einhaltung", "Einmischung", "Einstiegsfrage", "Einweihung",
        "Einzelfallgerechtigkeit", "Eisenbahn", "Energiewende", "Enthaltung",
        "Erforschung", "Ernennung", "Erpressung", "Ersparnis", "Erstattung",
        "Erwerbsminderung", "Essenausgabe", "Fachrichtung", "Fahne",
        "Fahrradkolonne", "Fehlbildung", "Fehlinformation", "Finanzierung",
        "Fledermaus", "Forschung", "Gebietsabtretung",
        "Gebrauchstauglichkeit", "Gebrechlichkeit", "Gehbehinderung", "Geheimhaltung",
        "Gemengelage", "Gerechtigkeit", "Geschwulst", "Gesprächsrunde",
        "Glasfaserleitung", "Gleichstellung", "Gliederung", "Grenzabgabe",
        "Haftstrafe", "Haftung", "Halbleitertechnik", "Handelsbeziehung",
        "Hauptausrichtung", "Haushaltsführung", "Hebamme", "Heißhungerattacke",
        "Hemmung", "Herrschaft", "Hinrichtung", "Hochspannung", "Inhaftierung",
        "Insolvenz", "Kaserne", "Katerstimmung", "Kinderlähmung",
        "Kindersterblichkeit", "Kostenstelle", "Kumpelwirtschaft", "Kundgebung",
        "Kurtaxe", "Kutsche", "Körperschaftsteuer", "Kürzung", "Laborthese",
        "Ladentheke", "Ladesäule", "Lebenseinstellung", "Lücke", "Mangelerscheinung",
        "Mariendarstellung", "Maßnahme", "Meerenge", "Menschenmenge",
        "Menschenrechtsfrage", "Menschenrechtslage", "Menschenwürde", "Miene",
        "Mitschrift", "Motorhaube", "Narbe", "Niederlassungserlaubnis", "Obergrenze",
        "Ohnmacht", "Persönlichkeit", "Pferdezucht", "Profitgier", "Prominenz",
        "Protestwelle", "Rankhilfe", "Raststätte", "Rautetaste", "Razzia",
        "Rechnungsprüfung", "Rechtsstaatlichkeit", "Regelung", "Reisestrapaze",
        "Rendite", "Rückendeckung", "Rückforderung", "Rückgabe", "Rückgewinnung",
        "Schadstoffbelästigung", "Scheinsicherheit", "Schienenmaut", "Schieflage",
        "Schlagzeile", "Schlammschlacht", "Schwachstelle", "Schwelle",
        "Selbstbestimmung", "Siegermacht", "Sondersitzung", "Spannung", "Sperrung",
        "Spüle", "Stoßstange", "Stornierung", "Strafanzeige", "Strafbemessung",
        "Straffreiheit", "Strahlung", "Subvention", "Suchmaschine", "Szene",
        "Tauglichkeit", "Tierhaltung", "Tröpfcheninfektion", "Übelkeit",
        "Übereinkunft", "Übereinstimmung", "Überholspur", "Überlastung",
        "Überlegenheit", "Überschwemmung", "Überwachung", "Umrüstung", "Umschulung",
        "Umstellung", "Unterführung", "Untersuchungshaft", "Unwissenheit",
        "Verbraucherreklamation", "Vergabe", "Vereitelung", "Verhandlung",
        "Verlegung", "Verliebtheit", "Vermögensverteilung", "Vernehmung",
        "Vernichtung", "Verschlechterung", "Verschwendung", "Verschwörungstheorie",
        "Verunsicherung", "Vielseitigkeit", "Vorreiterfunktion", "Vorschau",
        "Waffenniederlegung", "Wasserstraße", "Wattwanderung", "Weigerung",
        "Welterbeliste", "Werbetafel", "Wettbewerbsfähigkeit", "Wiese",
        "Wissenschaftsleugnung", "Worthülse", "Wunschvorstellung", "Zelle",
        "Zulassung", "Zumutung", "Zwischenüberschrift", "Äußerung",
    ],
    "das": [
        "Achselzucken", "Armutszeugnis", "Attentat", "Attest", "Auffanglager",
        "Ausfallrisiko", "Bauchgefühl", "Binnenschiff", "Bundesmittel", "Düngemittel",
        "Ehrenamt", "Endlager", "Felsbild", "Flugblatt", "Gefieder", "Gemeindegebet",
        "Gerichtsverfahren", "Gerücht", "Geschick", "Gestrüpp", "Gesundheitswesen",
        "Gewinnspiel", "Gremium", "Gutachten", "Haushaltsmittel", "Herzstück",
        "Konjunkturprogramm", "Kopfgeld", "Kopfschütteln", "Kompliment",
        "Machtvakuum", "Mindestmaß", "Missgeschick", "Problemfeld", "Pulverfass",
        "Randphänomen", "Rückgrat", "Sachbuch", "Schachfeld", "Schließfach",
        "Schlupfloch", "Schlusslicht", "Schmiergeld", "Untier",
        "Urheberrecht", "Verbrennerverbot", "Verhängnis", "Vorfeld", "Vorzeichen",
        "Wahrzeichen", "Wirtschaftswachstum", "Zahlenwerk",
    ],
}

# --- Существительные из пользовательского списка (Deutschblog), которых ещё не
#     было в словаре. Структура: {уровень: {род: [слова]}} — уровень оценён
#     примерно по частотности/сложности. Гомограф Plastik (die/das) вынесен в
#     HOMOGRAPHS. Артикль — по исходному списку (Diesel взят как der — стандарт).
DEUTSCHBLOG_VOCAB_ADD = {
    "A2": {
        "der": ["Becher", "Eimer", "Engel", "Esel", "Gedanke", "Gürtel",
                "Kontinent", "Schmetterling"],
        "die": ["Diskussion", "Freude", "Grammatik", "Nationalität"],
        "das": ["Aussehen", "Deodorant", "Medikament", "Päckchen", "Silber",
                "Tablett", "Viertel", "Zuhause"],
    },
    "B1": {
        "der": ["Akzent", "Atlantik", "Besen", "Beutel", "Bewohner",
                "Bibliothekar", "Deckel", "Diesel", "Felsen", "Flügel",
                "Frieden", "Glaube", "Haufen", "Käfig", "Knöchel", "Kommissar",
                "Kontrast", "Liebling", "Palast", "Pinsel", "Speicher", "Spion",
                "Sprung", "Strich", "Wechsel", "Wille", "Würfel", "Zweifel",
                "Ärmel"],
        "die": ["Botschaft", "Definition", "Feder", "Flüssigkeit", "Formel",
                "Funktion", "Kompetenz", "Kugel", "Last", "Muschel", "Orgel",
                "Schaufel", "Schaukel"],
        "das": ["Becken", "Drittel", "Gedächtnis", "Gemälde", "Getreide",
                "Häuschen", "Labor", "Lachen", "Militär", "Monster", "Nomen",
                "Omelett", "Pronomen", "Pulver", "Recycling", "Seminar",
                "Sprechen", "Tauchen", "Unentschieden"],
    },
    "B2": {
        "der": ["Blinker", "Busen", "Flieger", "Gatte", "Gletscher", "Hagel",
                "Kittel", "Konsum", "Krümel", "Lappen", "Notar", "Optimismus",
                "Samen", "Schädel", "Schenkel", "Schimmel", "Schwung", "Sprudel",
                "Zement"],
        "die": ["Ader", "Arroganz", "Ewigkeit", "Geisel", "Kammer",
                "Solidarität", "Toleranz", "Wildnis", "Wimper", "Zauberei"],
        "das": ["Bündnis", "Ferkel", "Futter", "Glossar", "Honorar", "Inventar",
                "Laken", "Phänomen", "Segel", "Verzeichnis"],
    },
    "C1": {
        "der": ["Antiquar", "Rachen", "Rochen"],
        "die": ["Besorgnis", "Finsternis", "Kordel"],
        "das": ["Häuslein"],
    },
}

# Анатомия человека — общеупотребительные слова, которых не хватало (2026-07).
# Базовые части тела (Kopf, Auge, Bauch, Magen, Herz …) уже есть в списках выше;
# здесь — дополнение. Уровни: чем употребительнее, тем ниже. Глубокая анатомия
# (Milz, Zwerchfell, Speiseröhre …) сознательно не включена.
ANATOMY_VOCAB_ADD = {
    "A2": {
        "der": [],
        "die": ["Zunge", "Brust"],
        "das": ["Blut"],
    },
    "B1": {
        "der": ["Nacken", "Ellenbogen", "Zeh", "Oberschenkel", "Po", "Bauchnabel"],
        "die": ["Wange", "Stirn", "Faust", "Handfläche", "Ferse", "Hüfte", "Wade",
                "Lunge", "Leber", "Rippe"],
        "das": ["Kinn", "Handgelenk", "Gehirn", "Gelenk"],
    },
    "B2": {
        "der": ["Darm", "Nerv"],
        "die": ["Niere", "Sehne", "Wirbelsäule", "Pupille", "Schläfe", "Achsel",
                "Kehle", "Taille"],
        "das": ["Skelett", "Augenlid", "Organ"],
    },
}

# Животные — общеупотребительные виды, которых не хватало (2026-07).
# Базовые (Hund, Katze, Vogel, Fisch, Pferd, Kuh, Schwein, Bär, Löwe, Elefant,
# Affe, Giraffe, Krokodil, Biene, Mücke …) уже есть в списках выше; здесь —
# дополнение. Уровни в духе существующей раскладки: ферма и известные дикие —
# B1 (как Kuh, Bär), более редкие — B2 (как Fledermaus).
ANIMALS_VOCAB_ADD = {
    "B1": {
        "der": ["Hahn", "Hamster", "Fuchs", "Wolf", "Igel", "Hirsch", "Tiger",
                "Frosch", "Adler", "Papagei", "Schwan", "Hai", "Wal", "Delfin",
                "Wurm", "Käfer"],
        "die": ["Ziege", "Gans", "Ratte", "Schlange", "Taube", "Eule", "Spinne",
                "Fliege", "Wespe", "Ameise", "Schnecke"],
        "das": ["Huhn", "Kaninchen", "Eichhörnchen", "Reh", "Wildschwein",
                "Zebra", "Kamel"],
    },
    "B2": {
        "der": ["Stier", "Truthahn", "Dachs", "Biber", "Maulwurf", "Rabe",
                "Storch", "Spatz", "Falke", "Pfau", "Krebs", "Marienkäfer"],
        "die": ["Eidechse", "Kröte", "Krähe", "Möwe", "Robbe", "Qualle",
                "Hummel", "Libelle", "Raupe", "Zecke"],
        "das": ["Meerschweinchen", "Kalb", "Lamm", "Känguru", "Nashorn",
                "Nilpferd"],
    },
}

# Гомографы: одно написание — разный род по значению, каждое значение — отдельная
# карточка. gloss — русское значение (и часть ключа прогресса, НЕ менять!),
# en — то же значение по-английски (для интерфейса en/de). (Уровень A1.)
HOMOGRAPHS = [
    {"word": "See", "article": "der", "gloss": "озеро", "en": "lake"},
    {"word": "See", "article": "die", "gloss": "море", "en": "sea"},
    {"word": "Band", "article": "der", "gloss": "том", "en": "volume"},
    {"word": "Band", "article": "die", "gloss": "группа", "en": "band"},
    {"word": "Band", "article": "das", "gloss": "лента", "en": "ribbon"},
    {"word": "Teil", "article": "der", "gloss": "часть", "en": "part"},
    {"word": "Teil", "article": "das", "gloss": "деталь", "en": "component"},
    # субстантивированные прилагательные: род зависит от пола человека
    {"word": "Erwachsene", "article": "der", "gloss": "муж.", "en": "male"},
    {"word": "Erwachsene", "article": "die", "gloss": "жен.", "en": "female"},
    {"word": "Jugendliche", "article": "der", "gloss": "муж.", "en": "male"},
    {"word": "Jugendliche", "article": "die", "gloss": "жен.", "en": "female"},
    {"word": "Angestellte", "article": "der", "gloss": "муж.", "en": "male"},
    {"word": "Angestellte", "article": "die", "gloss": "жен.", "en": "female"},
    {"word": "Bekannte", "article": "der", "gloss": "муж.", "en": "male", "level": "A2"},
    {"word": "Bekannte", "article": "die", "gloss": "жен.", "en": "female", "level": "A2"},
    # B2 (из B2_Vocabs_All.csv)
    {"word": "Kiefer", "article": "der", "gloss": "челюсть", "en": "jaw", "level": "B2"},
    {"word": "Kiefer", "article": "die", "gloss": "сосна", "en": "pine", "level": "B2"},
    # Plastik: die Plastik (скульптура) / das Plastik (пластик как материал)
    {"word": "Plastik", "article": "die", "gloss": "скульптура", "en": "sculpture", "level": "B2"},
    {"word": "Plastik", "article": "das", "gloss": "пластик", "en": "plastic", "level": "B1"},
]

# Существительные только во множественном числе — правильный ответ «Plural».
# Только настоящие pluralia tantum — слова без формы единственного числа.
# Слова, у которых ед. число есть (Süßigkeit, Kenntnis, Möbel, Abgas, Medium,
# Senior, Zins, Zutat, Jeans, Fundsache, Lebensmittel), перенесены в der/die/das
# на свой уровень. "Papiere" убрано — ед. "Papier" уже есть на A1.
# Пары (слово, уровень): ответ «Plural», уровень — свой для каждого слова.
PLURAL_WORDS = [
    ("Eltern", "A1"), ("Geschwister", "A1"), ("Großeltern", "A1"),
    ("Ferien", "A1"), ("Leute", "A1"),
    ("Pommes frites", "A2"),
    ("Personalien", "B1"),
    # pluralia tantum, добавлены 2026-07 (проверены по Duden: Pluralwort)
    ("Kosten", "B1"), ("Daten", "B1"), ("Schulden", "B1"), ("Nebenkosten", "B1"),
    ("Finanzen", "B2"), ("Trümmer", "B2"), ("Masern", "B2"), ("Windpocken", "B2"),
    ("Klamotten", "B2"), ("Gliedmaßen", "B2"),
    ("Flitterwochen", "B2"),   # перенесено из die Flitterwoche — ед. числа нет
    ("Einkünfte", "C1"), ("Spesen", "C1"), ("Tropen", "C1"), ("Gezeiten", "C1"),
    ("Memoiren", "C1"), ("Textilien", "C1"), ("Wehen", "C1"), ("Devisen", "C1"),
    ("Habseligkeiten", "C2"), ("Machenschaften", "C2"), ("Annalen", "C2"),
]

LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


def build():
    # добавляем слова из словарей Goethe A1/A2 к соответствующим уровням
    for article, words in GOETHE_A1_ADD.items():
        DATA["A1"][article].extend(words)
    for article, words in GOETHE_A2_ADD.items():
        DATA["A2"][article].extend(words)
    for article, words in GOETHE_B1_ADD.items():
        DATA["B1"][article].extend(words)
    for article, words in B2_VOCAB_ADD.items():
        DATA["B2"][article].extend(words)
    for level, arts in DEUTSCHBLOG_VOCAB_ADD.items():
        for article, words in arts.items():
            DATA[level][article].extend(words)
    for level, arts in ANATOMY_VOCAB_ADD.items():
        for article, words in arts.items():
            DATA[level][article].extend(words)
    for level, arts in ANIMALS_VOCAB_ADD.items():
        for article, words in arts.items():
            DATA[level][article].extend(words)

    out = []
    seen = set()          # ключ = (слово, значение) — гомографы не конфликтуют
    dupes = []
    missing = []          # слова без русского перевода
    missing_en = []       # слова без английского перевода

    def add(word, article, level, gloss=None, en_gloss=None):
        key = (word, gloss or "")
        if key in seen:
            dupes.append(word if not gloss else f"{word} ({gloss})")
            return
        seen.add(key)
        entry = {"word": word, "article": article, "level": level}
        if gloss:
            entry["gloss"] = gloss
        # перевод: у гомографов — их значение (gloss / en), у остальных — из словарей
        ru = gloss if gloss else TRANSLATIONS.get(word)
        if ru:
            entry["ru"] = ru
        else:
            missing.append(word)
        en = en_gloss if gloss else TRANSLATIONS_EN.get(word)
        if en:
            entry["en"] = en
        else:
            missing_en.append(word)
        out.append(entry)

    for level in LEVEL_ORDER:
        for article in ("der", "die", "das"):
            for word in DATA[level][article]:
                add(word, article, level)
    for h in HOMOGRAPHS:
        add(h["word"], h["article"], h.get("level", "A1"), h["gloss"], h.get("en"))
    for word, level in PLURAL_WORDS:
        add(word, "Plural", level)

    return out, dupes, missing, missing_en


def main():
    words, dupes, missing, missing_en = build()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "public", "words.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=0, separators=(",", ":"))
        f.write("\n")

    per_level = {lvl: 0 for lvl in LEVEL_ORDER}
    for w in words:
        per_level[w["level"]] += 1
    translated = sum(1 for w in words if w.get("ru"))
    translated_en = sum(1 for w in words if w.get("en"))
    print(f"Записано {len(words)} слов в {dest}")
    for lvl in LEVEL_ORDER:
        print(f"  {lvl}: {per_level[lvl]}")
    print(f"С переводом (ru): {translated} / {len(words)}")
    print(f"С переводом (en): {translated_en} / {len(words)}")
    if dupes:
        print(f"Пропущены дубликаты: {sorted(set(dupes))}")
    if missing:
        print(f"Без перевода ru ({len(missing)}): {sorted(set(missing))}")
    if missing_en:
        print(f"Без перевода en ({len(missing_en)}): {sorted(set(missing_en))}")


if __name__ == "__main__":
    main()
