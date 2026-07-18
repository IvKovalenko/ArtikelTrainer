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
                "Bruder","Vater","Papa","Sohn","Name","Morgen","Abend","Monat","Sommer",
                "Winter","Frühling","Herbst","Kaffee","Tee","Zug","Bus","Film",
                "Brief","Garten","Kopf","Fuß","Arm","Mund","Schlüssel","Löffel",
                "Teller","Fisch","Vogel","Wein","Saft","Käse","Zucker","Regen",
                "Schnee","Wind","Himmel","Stern","Mond","Preis","Euro","Freund",
                "Lehrer","Arzt","Zahn"],
        "die": ["Frau","Stadt","Tür","Blume","Katze","Mutter","Mama","Tochter","Schwester",
                "Nacht","Woche","Stunde","Minute","Zeit","Sonne","Straße","Schule",
                "Kirche","Bank","Uhr","Lampe","Tasche","Flasche","Tasse","Gabel",
                "Milch","Butter","Suppe","Banane","Orange","Tomate","Kartoffel",
                "Zwiebel","Familie","Sprache","Musik","Farbe","Zahl","Frage",
                "Antwort","Reise","Arbeit","Zeitung","Adresse","Nummer","Karte",
                "Hand","Nase","Brille","Küche","Wand","Freundin","Lehrerin"],
        "das": ["Haus","Kind","Land","Wasser","Brot","Fenster","Auto","Buch","Bett",
                "Zimmer","Bild","Papier","Heft","Wort","Jahr","Ei","Fleisch","Obst",
                "Gemüse","Bier","Glas","Messer","Handy","Telefon","Mobiltelefon","Radio","Fahrrad",
                "Flugzeug","Schiff","Tier","Pferd","Geld","Herz","Auge","Ohr","Bein",
                "Haar","Gesicht","Kino","Hotel","Restaurant","Büro","Krankenhaus",
                "Wetter","Feuer","Spiel","Foto","Baby","Mädchen","Getränk"],
    },
    "A2": {
        "der": ["Beruf","Urlaub","Termin","Ausflug","Flughafen","Bahnhof","Markt",
                "Supermarkt","Platz","Weg","Unfall","Fehler","Wunsch","Traum",
                "Anfang","Schluss","Erfolg","Nachteil","Vorteil","Grund","Rabatt",
                "Verkäufer","Kellner","Kollege","Partner","Körper","Rücken",
                "Bauch","Finger","Daumen","Schrank","Sessel","Teppich","Vorhang",
                "Wecker","Kühlschrank","Herd","Ofen","Balkon","Keller","Aufzug","Lift",
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
                "Frühstück","Mittagessen","Abendessen","Besteck","Werkzeug",
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
        "die": ["Bewerbung","Kündigung","Versicherung","Gebühr",
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
#       * омонимы (разный род по значению) — в HOMONYMS (со значением по-русски);
#       * только множественное число — в PLURAL_WORDS (ответ «Plural»).
#     Cola/Comic взяты в стандартном роде (die Cola, der Comic); региональные
#     варианты das Cola / das Comic существуют, но здесь не проверяются.
GOETHE_A1_ADD = {
    "der": ["Anruf","Anrufbeantworter","Appetit","Artikel","Automat","Bahnsteig",
            "Basketball","Bleistift","Dank","Durst","Fahrplan","Familienname",
            "Fotoapparat","Fußball","Geburtstag","Glückwunsch","Gruß","Hals",
            "Herr","Hunger","Kakao","Kiosk","Kuchen","Kugelschreiber (Kuli)",
            "Kurs","Mantel","Marktplatz","Ohrring","Park","Pullover","Quatsch",
            "Radiergummi","Ring","Rucksack","Salat","Schmerz","Spaß","Spielplatz",
            "Sport","Strand","Unterricht","Vorname","Computer","Blog","CD-Player",
            "Laptop","Link","Chat","Antwortbogen","Prüfungsteil","Test","Text",
            "Architekt","Techniker","Ingenieur","Künstler","Kaufmann","Hausmann",
            "Schauspieler","Sekretär","Onkel","Großvater","Opa","Norden","Süden","Westen",
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
            "Aufgabe","Lösung","Partnerin","Grundschule",
            "Architektin","Technikerin","Künstlerin","Ingenieurin",
            "Kauffrau","Hausfrau","Schauspielerin","Sekretärin","Großmutter","Oma",
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
        "Bescheid", "Buchstabe", "Chef", "Eingang", "Eintritt", "Empfänger",
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
        "Mensch", "Prospekt", "Schuh", "Topf", "Wagen",
    ],
    "die": [
        "Bäckerin", "Doktorin", "Fahrerin", "Friseurin", "Handwerkerin",
        "Köchin", "Krankenschwester", "Mechanikerin", "Musikerin",
        "Polizistin", "Rentnerin", "Sängerin", "Verkäuferin",
        "Cousine", "Enkelin", "Verwandte",
        "Biologie", "Klassenfahrt", "Religion",
        "Mitternacht", "Ankunft", "Auskunft", "Ausstellung", "Autobahn",
        "Baustelle", "Bitte", "Bohne", "Brücke",
        "Cafeteria", "Creme", "Dame", "Datei", "Ehefrau", "Erlaubnis", "Ermäßigung",
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
        "Stelle", "Straßenbahn", "Tafel", "Tour", "Unterschrift", "Unterkunft", "Universität (Uni)",
        "Veranstaltung", "Verspätung", "Webseite", "Welt", "Werkstatt", "Wolke",
        "Zeitschrift", "Anmeldung", "Birne", "Briefmarke", "Ecke",
        "Kollegin", "Kundin", "Maschine", "Menge", "Mütze",
        "Nachbarin", "Rezeption", "Sekunde", "Studentin",
        "Torte", "Touristin", "Zitrone", "Kenntnis",
    ],
    "das": [
        "Abitur", "Französisch", "Latein", "Sekretariat",
        "Blatt", "Café", "Ding", "Doppelzimmer", "Dorf",
        "E-Book", "Einkaufszentrum", "Erdgeschoss",
        "Festival (Fest)", "Fieber", "Gerät", "Gericht", "Geschirr", "Gewitter",
        "Hähnchen", "Hemd", "Interview", "Leben", "Licht", "Lied", "Mittel", "Museum",
        "Öl", "Paar", "Parfüm", "Passwort", "Plakat",
        "Produkt", "Programm", "Projekt", "Rind", "Schlafzimmer", "Schloss",
        "Stipendium", "Stockwerk", "Tablet", "Taxi", "Team", "Tennis", "Training",
        "Zelt", "Zentrum", "Lebensmittel", "Möbel",
        "Datum", "Gegenteil", "Kaufhaus", "Rathaus", "Reisebüro", "Verkehrsmittel",
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
        "Babysitter", "Bart", "Bau", "Bauernhof", "Beamte",
        "Beleg", "Betreuer", "Bikini", "Bogen", "Braten", "Briefkasten",
        "Briefträger", "Briefumschlag", "Bundeskanzler", "Bundespräsident",
        "Bundesrat", "Bundestag", "Bär", "Bürger", "Bürgermeister", "Chip",
        "Club", "Dialekt", "Dialog", "Dieb", "Dienst", "Donner",
        "Einbrecher", "Einbruch", "Einfall", "Elefant", "Ersatz", "Europäer",
        "Experte", "Fachmann", "Faktor", "Familienstand", "Fasching",
        "Feierabend", "Fleck", "Flur", "Fotograf", "Franken",
        "Gegensatz", "Gegenstand", "Gegner", "Geldautomat",
        "Gehsteig", "Gott", "Grad", "Grieche", "Grill", "Hafen", "Halt",
        "Hammer", "Handel", "Hase", "Held", "Hersteller", "Hit", "Honig",
        "Humor", "Husten", "Hut", "Händler", "Hörer", "Hügel", "ICE",
        "Intensivkurs", "Jazz", "Journalist", "Kampf", "Kanal", "Kandidat",
        "Kanton", "Kasten", "Katalog", "Ketchup", "Killer", "Kilometer", "Klick",
        "Kloß", "Knochen", "Knopf", "Knödel", "Kommentar", "Kopierer", "Kranke",
        "Krankenwagen", "Rettungswagen", "Kreis", "Kunststoff", "Kursleiter", "Kuss",
        "Käufer", "König", "Lautsprecher", "Lehrling",
        "Lerner", "Leser", "Liter", "Lastkraftwagen (Lkw)", "Lohn", "Löwe", "Maler",
        "Manager", "Meister", "Meter", "Metzger (Fleischhauer)", "Migrant", "Minister",
        "Moderator", "Monitor", "Muskel", "Mut", "Nachwuchs", "Nagel",
        "Nationalrat", "Nebel", "Neffe", "Nichtraucher", "Notausgang", "Notfall",
        "Notruf", "Ober", "Ordner", "Ozean", "PC",
        "Passagier", "Patient", "Personenstand", "Pfeffer", "Pfleger", "Pilz",
        "Pinguin", "Personenkraftwagen (Pkw)", "Praktikant", "Professor", "Profi", "Profisportler",
        "Protest", "Prozess", "Quadratmeter", "Radfahrer", "Rahm", "Rappen",
        "Rasen", "Rat", "Rechner", "Rekord", "Reporter", "Respekt", "Rest",
        "Richter", "Roman", "Saal", "Sack", "Salon", "Schein", "Schinken",
        "Schlaf", "Schmuck", "Schmutz", "Schnupfen", "Schreck", "Schriftsteller",
        "Schritt", "Schutz", "Schweizer", "Sender", "Sieg", "Sieger", "Sinn",
        "Sitz", "Snack", "Song", "Sozialarbeiter", "Spezialist",
        "Spiegel", "Sportler", "Spot", "Staat", "Start", "Staub", "Stein",
        "Stempel", "Steward", "Stil", "Stoff", "Strafzettel", "Streik", "Strom",
        "Strumpf", "Studierende", "Sturm", "Ständerat",
        "Tagesablauf", "Tanz", "Teilnehmer", "Terminal", "Terminkalender",
        "Textaufbau", "Tierpark", "Tod", "Tote", "Tourismus", "Trainer",
        "Transport", "Treffpunkt", "Trend", "Turm", "Typ", "Täter", "Türke",
        "Ukrainer", "Unternehmer", "User", "Verbrecher", "Verlierer", "Vermieter",
        "Vertreter", "Virus", "Vortrag", "Wert", "Wetterbericht", "Wirt",
        "Wissenschaftler", "Wochentag", "Wohnsitz", "Zeitpunkt", "Zentimeter",
        "Zeuge", "Zoll", "Zugang", "Zuschauer", "Zünder",
        "Österreicher", "Übersetzer", "Senior", "Zins",
    ],
    "die": [
        "Abbildung", "Abfahrt", "Absenderin", "Akademie", "Aktion", "Aktivität",
        "Alternative", "Anlage", "Anleitung", "Annonce", "Anrede", "Ansage",
        "Anwältin", "Anzahl", "Arbeiterin", "Arbeitserlaubnis",
        "Arbeitslosigkeit", "Art", "Aufforderung", "Aufnahme",
        "Ausfahrt", "Aushilfe", "Ausländerin", "Aussage", "Aussprache",
        "Auswahl", "Babysitterin", "Badewanne", "Bahn", "Bankleitzahl",
        "Batterie", "Beamtin", "Bedienungsanleitung", "Berufsmittelschule",
        "Berufsschule", "Besserung", "Betreuerin", "Betreuung", 
        "Biene", "Breite", "Brieftasche", "Briefträgerin", "Broschüre",
        "Bundeskanzlerin", "Bundespräsidentin", "Bundesrätin", "Burg", "Büchse",
        "Bühne", "Bürgerin", "Bürgermeisterin", "Bürste", "Castingshow",
        "Chance", "Chipkarte", "Couch", "Darstellung", "Dauer", "Decke",
        "Demokratie", "Distanz", "Diät",
        "Dose", "Droge", "Drogerie", "Durchsage", "Einbahnstraße",
        "Einbrecherin", "Einführung", "Einleitung", "Einnahme", "Einrichtung",
        "Einzahlung", "Einzelheit", "Empfehlung", "Ente", "Entfernung",
        "Entlassung", "Etage", "Europäerin", "Fachfrau", "Fahrbahn",
        "Fernbedienung", "Festplatte", "Feuerwehr", "Figur", "Fitness",
        "Flucht", "Fläche", "Flöte", "Folie", "Fortbildung",
        "Fortsetzung", "Fremdsprache", "Freundschaft", "Frist", "Frisur",
        "Frucht", "Fähre", "Galerie", "Gaststätte", "Gebrauchsanweisung",
        "Geburt", "Gemeinde", "Gemeinschaft", "Generation", 
        "Geschwindigkeit", "Beschränkung", "Gewalt", "Gewerkschaft", "Gewohnheit",
        "Giraffe", "Grafik", "Gratulation", "Griechin", "Gymnastik",
        "Halbpension", "Haut", "Heldin", "Hitze", "Hochschule", "Hoffnung",
        "Hälfte", "Händlerin", "Höhe", "Hörerin", "Hütte", "Infektion",
        "Integration", "Intelligenz", "Journalistin", "Kabine", "Kanne",
        "Kantine", "Karotte", "Aprikose", "Karriere", "Kassette", "Katastrophe", "Killerin",
        "Kindertagesstätte (Kita)", "Klimaanlage", "Klingel", "Klinik", "Kneipe",
        "Kommunikation", "Konferenz", "Konfitüre", "Konkurrenz", "Kontrolle",
        "Kopie", "Kraft", "Kriminalpolizei", "Kripo", "Krippe", "Krise", "Kuh", "Kälte",
        "Käuferin", "Küste", "Lage", "Landung", "Landwirtschaft", "Langeweile",
        "Laune", "Lehre", "Leiterin", "Leitung", "Lernerin",
        "Leserin", "Liebe", "Lieferung", "Limonade", "Linie", "Lippe",
        "Literatur", "Mahlzeit", "Mahnung", "Malerin", "Managerin", "Mappe",
        "Margarine", "Mauer", "Maus", "Mehrwertsteuer",
        "Meldung", "Mensa", "Methode", "Metropole", "Migrantin", "Migration",
        "Milliarde", "Million", "Ministerin", "Mobilbox",
        "Mobilität", "Moderatorin", "Muttersprache", "Mücke", "Mühe",
        "Müllabfuhr", "Mülltonne", "Münze", "Nachfrage", "Nachhilfe",
        "Nachspeise", "Nadel", "Neuigkeit", "Nichte", "Nichtraucherin",
        "Notaufnahme", "Oper", "Operation",
        "Orientierungsstufe", "Panne", "Partei", "Passagierin", "Patientin",
        "Pension", "Pfanne", "Pflaume", "Pflegerin", "Pflicht", "Philosophie",
        "Pille", "Planung", "Plattform", "Praktikantin", "Presse",
        "Produktion", "Professorin", "Profisportlerin", "Puppe",
        "Qualifikation", "Radfahrerin", "Recherche", "Rede",
        "Reform", "Reihenfolge", "Reklame", "Reportage", "Reporterin",
        "Reservierung", "Richterin", "Richtung", "Rolle", "Rufnummer", "Runde",
        "Rundfahrt", "Rückfahrt", "Rückkehr", "Rückmeldung", "SMS", "Saison",
        "Salbe", "Schachtel", "Scheibe", "Schildkröte", "Schrift",
        "Schriftstellerin", "Schuld", "Schulter",
        "Schwangerschaft", "Schweizerin", "Schüssel", "Semmel",
        "Serie", "Show", "Siegerin", "Socke", "Software", 
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
        "Visitenkarte", "Volkshochschule", "Vorbereitung",
        "Vorfahrt", "Vorschrift", "Vorsicht", "Vorwahl", "Wohngemeinschaft (WG)", "Wanderung",
        "Ware", "Weiterbildung", "Wettervorhersage", "Wirklichkeit", "Wirtin",
        "Wissenschaft", "Wissenschaftlerin", "Wolle", "Wunde", "Wärme",
        "Zahlung", "Zahnbürste", "Zahncreme", "Zange", "Zeichnung", "Zeile",
        "Zeugin", "Zigarette", "Zone", "Zusammenarbeit", "Zuschauerin",
        "Öffentlichkeit", "Österreicherin", "Übernachtung",
        "Überraschung", "Überschrift", "Übersetzerin", "Übersetzung",
        "Überstunde", "Überweisung", "Fundsache", "Zutat"
    ],
    "das": [
        "Abenteuer", "Abonnement (Abo)", "Alphabet", "Altenheim", 
        "Amt", "Apartment", "Ballett", "Boot", "Buffet", "Bundesland", "Camp",
        "Detail", "Diplom", "E-Bike", "Einschreiben",
        "Feuerzeug", "Forum", "Frühjahr", "Fundbüro", "Gebäck", "Geschlecht", 
        "Gedicht", "Geheimnis", "Gift", "Girokonto", "Gramm", "Gras",
        "Hackfleisch", "Hallenbad", "Haustier", "Heim", "Heimweh", 
        "Holz", "Insekt", "Inserat", "Institut", "Jahrtausend", "Kabel",
        "Kapitel", "Kennzeichen", "Kraftfahrzeug (Kfz)", "Kilogramm (Kilo)", "Knie",
        "Konsulat", "Kostüm", "Kraftfahrzeug", "Kraftwerk", "Krokodil", "Lager",
        "Leder", "Lexikon", "Loch", "Lokal", "Magazin", "Material",
        "Meer", "Mehl", "Menü", "Metall", "Modell", "Modul", "Mountainbike",
        "Märchen", "Müsli", "Netz", "Obergeschoss", "Orchester",
        "Original", "Parlament", "Pech", "Personal", "Pflaster", "Picknick",
        "Portemonnaie", "Prozent", "Puzzle", "Referat",
        "Risiko", "Rohr", "Sandwich", "Schaf", "Schaufenster",
        "Schmerzmittel", "Schnitzel", "Schwein", "Semester",
        "Souvenir", "Stadion", "Steak", "Streichholz", "Studio",
        "Symbol", "TV", "Talent", "Taschentuch", "Tempo",
        "Treppenhaus", "Trinkgeld", "Untergeschoss", "Vergnügen",
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
        "Anhänger", "Anlauf", "Anpfiff", "Appell", "Aufschlag",
        "Auftakt", "Auftritt", "Aufwind", "Auslöser", "Ausschnitt", 
        "Baukasten", "Befürworter", "Beitritt", "Beweggrund", "Bezug", "Blickwinkel",
        "Bodenschatz", "Bruch", "Buchhalter", "Chirurg",
        "Dauerauftrag", "Dauerbrenner", "Durchbruch", "Einnahmeausfall",
        "Einsatz", "Einschnitt", "Erkenntnisgewinn", "Fachbegriff",
        "Föderalismus", "Friedensschluss", "Friedensvertrag",
        "Frontverlauf", "Galopp", "Gedankengang", "Gehweg", 
        "Gottesdienst", "Graben", "Haftbefehl", "Hergang", "Hinterhof",
        "Irrglaube", "Jahresabschluss", "Karfreitag", "Katzensprung",
        "Knochenjob", "Kohlenstoff", "Leitzins", "Losentscheid",
        "Machthaber", "Maiseintopf", "Maschinenbau", "Militärputsch", "Milliardenwert",
        "Mittelweg", "Mobilfunk", "Morgenmuffel", "Moscheeverband", "Nachahmungstäter",
        "Nachholbedarf", "Nahverkehr", "Notfallsanitäter", "Parkverstoß",
        "Rechtsstaat", "Ruderverein", "Rückstand", "Sachverstand",
        "Saldo", "Samt", "Sanierungsstau", "Sattelschlepper",
        "Scheibenwischer", "Scheinwerfer", "Schnabel", "Schöpfer", "Schrott",
        "Schwachkopf", "Seelsorger", "Sonnenstrom", "Spielraum", "Spitzenvertreter",
        "Sprengstoff", "Stausee", "Sündenfall", "Teamgeist",
        "Trauschein", "Unterhaltsvorschuss", "Unterschlupf", "Verbraucher", "Verfall",
        "Verfassungsrang", "Vergleich", "Verhaltenskodex", "Verlag",
        "Versorgungsengpass", "Vorgänger", "Waffenstillstand", 
        "Wassermangel", "Weisheitszahn", "Werdegang", "Wirtschaftsberater",
        "Wühltisch", "Zeitgeist", "Zeitraum", "Zuzug", "Zwilling", "Zwischenfall",
        "Zwischenruf",
    ],
    "die": [
        "Aberkennung", "Abkehr", "Abrüstung", "Abschiebung", "Abschreibung",
        "Abtreibung", "Abwehr", "Abweichung", "Abwertung", "Akteneinsicht",
        "Aktiengesellschaft", "Albernheit", "Altersvorsorge", "Andeutung",
        "Anfeindung", "Anforderung", "Anordnung", "Anreizwirkung",
        "Anspannung", "Antike", "Arbeitsausbeutung", "Aufhebung", "Aufmunterung",
        "Aufrüstung", "Aufweichung", "Augenbraue", "Ausdauer", "Aushilfstätigkeit",
        "Ausschreibung", "Ausweitung", "Bedrohung",
        "Beeinträchtigung", "Beerdigung", "Befugnis", "Begabung", "Begegnung",
        "Belastbarkeit", "Belastung", "Belohnung", "Belüftung", "Benennung",
        "Bereicherung", "Berufung", "Beschaffungsmethode", "Bescheidenheit",
        "Beschäftigung", "Bestandsaufnahme", "Bestechung", "Bestätigung",
        "Beteiligung", "Bettdecke", "Beute", "Bevormundung", "Bezugsperson",
        "Blessur", "Bohrplattform", "Bonität", "Borreliose", 
        "Bundeswehr", "Bürgschaft", "Dachfirma", "Datenauswertung", "Drohkulisse",
        "Dunkelflaute", "Dunkelziffer", "Durchlässigkeit", "Dürre", "Einbettung",
        "Einbeziehung", "Einhaltung", "Einmischung", "Einstiegsfrage", "Einweihung",
        "Einzelfallgerechtigkeit", "Eisenbahn", "Energiewende", "Enthaltung",
        "Erforschung", "Ernennung", "Erpressung", "Ersparnis", "Erstattung",
        "Erwerbsminderung", "Essenausgabe", "Fahne",
        "Fahrradkolonne", "Fehlbildung", "Fehlinformation", "Finanzierung",
        "Fledermaus", "Forschung", "Gebietsabtretung",
        "Gebrauchstauglichkeit", "Gebrechlichkeit", "Gehbehinderung", 
        "Gerechtigkeit", "Geschwulst", "Gesprächsrunde",
        "Glasfaserleitung", "Gleichstellung", "Gliederung", "Grenzabgabe",
        "Haftstrafe", "Haftung", "Halbleitertechnik", 
        "Hauptausrichtung", "Hebamme", "Heißhungerattacke",
        "Hemmung", "Herrschaft", "Hinrichtung", "Hochspannung", "Inhaftierung",
        "Insolvenz", "Kaserne", "Katerstimmung", "Kinderlähmung",
        "Kindersterblichkeit", "Kumpelwirtschaft", "Kundgebung",
        "Kurtaxe", "Kutsche", "Körperschaftsteuer", "Kürzung", "Laborthese",
        "Ladentheke", "Lebenseinstellung", "Lücke", "Mangelerscheinung",
        "Mariendarstellung", "Maut", "Maßnahme", "Meerenge", "Menschenmenge",
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
        "Waffenniederlegung", "Wattwanderung", "Weigerung",
        "Welterbeliste", "Werbetafel", "Wettbewerbsfähigkeit", "Wiese",
        "Wissenschaftsleugnung", "Worthülse", "Wunschvorstellung", "Zelle",
        "Zulassung", "Zumutung", "Zwischenüberschrift", "Äußerung",
    ],
    "das": [
        "Achselzucken", "Armutszeugnis", "Attentat", "Attest", "Auffanglager",
        "Ausfallrisiko", "Bauchgefühl", "Binnenschiff", "Düngemittel",
        "Ehrenamt", "Endlager", "Felsbild", "Flugblatt", "Gefieder", "Gemeindegebet",
        "Gerichtsverfahren", "Gerücht", "Geschick", "Gestrüpp", "Gesundheitswesen",
        "Gremium", "Gutachten", "Herzstück",
        "Konjunkturprogramm", "Kopfschütteln", "Kompliment",
        "Machtvakuum", "Missgeschick", "Pulverfass",
        "Randphänomen", "Rückgrat", "Sachbuch", "Schachfeld", "Schließfach",
        "Schlupfloch", "Schlusslicht", "Schmiergeld", "Untier",
        "Urheberrecht", "Verbrennerverbot", "Verhängnis", "Vorfeld", "Vorzeichen",
        "Wahrzeichen", "Wirtschaftswachstum", "Zahlenwerk",
    ],
}

# --- Существительные из пользовательского списка (Deutschblog), которых ещё не
#     было в словаре. Структура: {уровень: {род: [слова]}} — уровень оценён
#     примерно по частотности/сложности. Омоним Plastik (die/das) вынесен в
#     HOMONYMS. Артикль — по исходному списку (Diesel взят как der — стандарт).
DEUTSCHBLOG_VOCAB_ADD = {
    "A2": {
        "der": ["Becher", "Eimer", "Engel", "Esel", "Gedanke", "Gürtel",
                "Kontinent", "Schmetterling"],
        "die": ["Diskussion", "Freude", "Grammatik", "Nationalität"],
        "das": ["Aussehen", "Deodorant (Deo)", "Medikament", "Päckchen", "Silber",
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

# --- Существительные из немецкого Викисловаря (список gambolputty/german-nouns),
#     отобранные по частотности в Лейпцигском корпусе (deu_news_2023_1M):
#     дополнение уровней B2/C1/C2 до ~1000 слов каждый. Частые → B2, реже → C1,
#     редкие → C2. Имена собственные, региональные варианты, словоформы уже
#     имеющихся слов и производные на -in отсеяны. Данные: CC BY-SA (Wiktionary).
WIKI_NEWS_ADD = {
    "B2": {
        "der": [
            "Abstand", "Abstieg", "Angreifer", "Angriff", "Anleger", "Anteil",
            "Antisemitismus", "Anwohner", "Applaus", "Arbeitsmarkt", "Aufbau", "Aufsteiger",
            "Aufstieg", "Auftrag", "Ausbau", "Ausgleich", "Ausschuss", "Austausch",
            "Autofahrer", "Autor", "Außenminister", "Bedarf", "Beginn", "Bericht", "Beschluss",
            "Besitzer", "Bestandteil", "Besucher", "Betreiber", "Bezirk", "Blick",
            "Botschafter", "Bund", "Bundestrainer", "Charakter", "Coach", "Deal", "Dollar",
            "Durchgang", "Durchschnitt", "Effekt", "Eigentümer", "Einwohner",
            "Einzug", "Entwickler", "Entwurf", "Erhalt", "Ermittler", "Fachkräftemangel",
            "Fall", "Fokus", "Fonds", "Forscher", "Fußgänger",
            "Gang", "Gastgeber", "Gegenzug", "Gemeinderat", "Geschmack", "Geschäftsführer",
            "Gewinner", "Gier", "Gründer", "Helfer", "Hinblick", "Hintergrund",
            "Hubschrauber", "Höhepunkt", "Inhalt", "Kader", "Kanzler",
            "Kapitän", "Kauf", "Kindergarten", "Klassenerhalt", "Klassiker", "Klimaschutz",
            "Klimawandel", "Klub", "Konzern", "Krieg", "Kritiker", "Landkreis",
            "Landrat", "Landtag", "Lauf", "Lenker", "Mieter", "Ministerpräsident",
            "Mitarbeiter", "Mittelpunkt", "Mord", "Nachfolger",
            "Nationalspieler", "Neuzugang", "Nutzer", "Oberbürgermeister", 
            "Palästinenser", "Panzer", "Papst", "Parkplatz", "Pfarrer", "Podcast", "Politiker",
            "Polizeisprecher", "Premier", "Prinz", "Präsident", "Punkt",
            "Rand", "Rang", "Rauch", "Regierungschef", "Regisseur", "Republikaner",
            "Rettungsdienst", "Ruhestand", "Rücktritt", "Sachschaden",
            "Schaden", "Schiedsrichter", "Schlag", "Schnitt", "Schock", "Schuss", "Senat",
            "Sex", "Spieler", "Spieltag", "Spitzenreiter", "Sprecher", "Stadtrat", "Stadtteil",
            "Standort", "Status", "Sturz", "Stürmer", "Tabellenführer", "Tatort",
            "Ton", "Torhüter", "Torwart", "Treffer", "Umbau", "Umfang", "Veranstalter",
            "Verband", "Verkauf", "Verkehrsunfall", "Versuch", "Verteidiger",
            "Vordergrund", "Vorfall", "Vorsitzender", "Vorsprung",
            "Vorstand", "Vortag", "Wahlkampf", "Wasserstoff", "Weihnachtsmarkt", "Weltkrieg",
            "Weltmeister", "Widerstand", "Wohnraum", "Wähler", "Zugriff",
            "Zusammenstoß", "Zähler", "Ärger"
        ],
        "die": [
            "Absage", "Abstimmung", "Abteilung", "Agentur", "Aktie", "Allianz", 
            "Analyse", "Anerkennung", "Anfrage", "Anklage", "Ankündigung", "Ansicht",
            "Anwendung", "App", "Arena", "Armee", "Armut", "Atmosphäre", "Attacke",
            "Aufklärung", "Auflage", "Auflösung", "Aufmerksamkeit", "Aufregung", "Ausgabe",
            "Ausrüstung", "Ausstattung", "Auswertung", "Auszeichnung", "Basis", "Bedeutung",
            "Begründung", "Beratung", "Bereitschaft", "Bewertung", "Bilanz", "Bildung",
            "Branche", "Bundesliga", "Bundespolizei", "Bundesregierung", "Bundesstraße",
            "Börse", "Community", "Debatte", "Defensive", "Demonstration", "Digitalisierung",
            "Ebene", "Einheit", "Einigung", "Einschätzung", "Energie", "Entlastung", "Erde",
            "Erhöhung", "Erinnerung", "Erklärung", "Erkrankung", "Erweiterung", "Eröffnung",
            "Explosion", "Fahrtrichtung", "Festnahme", "Form", "Fraktion", "Förderung",
            "Gastronomie", "Gefahr", "Größe", "Gründung", "Haft", 
            "Herkunft", "Herstellung", "Hinsicht", "Identität", "Inflation", "Infrastruktur",
            "Initiative", "Innenstadt", "Invasion", "Jahreszeit", "Jury", "Justiz", "Kampagne",
            "Kategorie", "Kita", "Klage", "Klimakrise", "Koalition", "Kombination",
            "Kommission", "Kooperation", "Krone", "Kurve", "Körperverletzung",
            "Landeshauptstadt", "Landtagswahl", "Leiche", "Leidenschaft",
            "Liga", "Liste", "Länge", "Macht", "Marke", "Meisterschaft", "Mischung", "Mission",
            "Mitteilung", "Munition", "Nachrichtenagentur", "Nationalmannschaft", "Niederlage",
            "Not", "Notwendigkeit", "Nutzung", "Offensive", "Opposition", "Option",
            "Organisation", "Pandemie", "Partie", "Partnerschaft", "Performance", "Perspektive",
            "Pflege", "Phase", "Politik", "Position", "Premiere", "Pressekonferenz",
            "Pressemitteilung", "Prognose", "Präsentation", "Reaktion", "Realität", "Redaktion",
            "Rente", "Republik", "Rettung", "Sanierung", "Schließung", "Sicht", "Sitzung",
            "Spitze", "Staatsanwaltschaft", "Stabilität", "Stadtverwaltung",
            "Staffel", "Stellung", "Stellungnahme", "Stiftung", "Story", "Strategie", "Stärke",
            "Suche", "Temperatur", "Teuerung", "Tradition", "Transformation", "Transparenz",
            "Truppe", "Umsetzung", "Unfallstelle", "Union", "Variante", "Verbindung",
            "Vereinigung", "Verfassung", "Verlängerung", "Verpflichtung", "Version",
            "Versorgung", "Verteidigung", "Verwendung", "Veröffentlichung", "Vielzahl", "Villa",
            "Vision", "Vorlage", "Waffe", "Wahrscheinlichkeit", "Warnung", "Website", "Weise",
            "Wende", "Zentralbank", "Zerstörung", "Änderung", "Übernahme"
        ],
        "das": [
            "Album", "Amtsgericht", "Areal", "Budget", "Bundesamt", "Chaos", "Comeback",
            "Derby", "Design", "Duell", "Duo", "Dutzend", "Engagement", "Erdbeben", "Event",
            "Fahrzeug", "Fazit", "Feld", "Finale", "Gas", "Gebiet", "Gewicht",
            "Gold", "Halbfinale", "Halbjahr", "Heimspiel", "Highlight", "Jahresende",
            "Jubiläum", "Konzept", "Management", "Match",
            "Ministerium", "Mitglied", "Mittelfeld", "Model", "Motto", "Niveau", "Potenzial",
            "Prinzip", "Promille", "Quartal", "Rennen", "Schicksal", "Signal", "Stadtgebiet",
            "Statement", "System", "Tierheim", "Turnier", "Umfeld", "Unglück",
            "Unwetter", "Update", "Verbot", "Verteidigungsministerium", 
            "Visier", "Volk", "Vorjahr", "Wohnhaus"
        ],
    },
    "C1": {
        "der": [
            "Abbau", "Abbruch", "Abfall", "Abpfiff", "Abriss", "Absatz", "Abschuss",
            "Advent", "Airport", "Akt", "Aktienmarkt",
            "Amerikaner", "Amtsantritt", "Analyst", "Anbau", "Anblick", "Anführer", "Anschlag",
            "Ansprechpartner", "Anstoß", "Antrieb", "Anwender", "Asphalt", "Asylbewerber",
            "Aufprall", "Aufruf", "Aufsichtsrat", "Aufstand", "Ausblick", "Ausbruch", "Ausfall",
            "Ausschluss", "Aussteller", "Ausstieg", "Autobauer", "Außenseiter", "Bagger",
            "Ballbesitz", "Begleiter", "Beifahrer", "Beifall",
            "Beobachter", "Berater", "Beschuss", "Beton", "Betrüger", "Bildschirm", "Bischof",
            "Boss", "Brite", "Brunnen", "Bundesstaat", "Bundesverband", "Campus", "Charme",
            "Chatbot", "Cheftrainer", "Chor", "Clip", "Code", "Container", "Coup", "Crash",
            "Cup", "Damm", "Darsteller", "Datenschutz", "Designer", "Diebstahl",
            "Dienstleister", "Discounter", "Doppelpack", "Dynamo", "Einbau", "Einblick",
            "Eingriff", "Einkauf", "Einklang", "Einlass", "Einstieg", "Einzelfall",
            "Einzelhandel", "Elfmeter", "Erlös", "Ernstfall", "Erwerb", 
            "Fahrstreifen", "Fahrzeugführer", "Fake", "Favorit", "Feind", "Fernsehsender",
            "Festakt", "Follower", "Franzose", "Freistoß", "Friedhof", "Frost", "Frust", "Fund",
            "Fußballer", "Gebrauch", 
            "Geheimdienst", "Geist", "General", "Genuss", "Gerichtshof",
            "Gerichtssaal", "Geruch", "Gesang", "Gesetzentwurf", "Gesetzgeber",
            "Gesundheitsminister", "Glanz", "Glühwein", "Gouverneur", "Grenzübergang",
            "Gutachter", "Hacker", "Haken", "Halter", "Handball",
            "Handballer", "Handlungsbedarf", "Hang", "Hass", "Hauptsitz",
            "Heiligabend", "Heimsieg", "Helm", "Historiker", "Horizont", "Hype", "Index",
            "Influencer", "Inhaber", "Innenhof", "Insider", "Investor",
            "Islam", "Italiener", "Jahresbeginn", "Jahrestag", "Jahreswechsel", "Jahrgang",
            "Joker", "Journalismus", "Jubel", "Jude", "Kampfpanzer", "Kater", "Keeper",
            "Kicker", "Kläger", "Knall", "Koalitionsvertrag", "Komfort",
            "Kommandant", "Kongress", "Konkurrent", "Konter", "Kontext", "Kreistag",
            "Kreisverkehr", "Kämpfer", "Landwirt", "Lastwagen", "Lebensraum",
            "Leib", "Leitindex", "Leopard", "Livestream", "Look", "Luxus", "Lärm", "Läufer",
            "Macher", "Marktanteil", "Mediziner", "Mehrwert", "Meilenstein",
            "Meistertitel", "Migrationshintergrund", "Mindestlohn", "Missbrauch", "Mitspieler",
            "Modus", "Musikverein", "Mörder", "Nationalpark",
            "Nationalsozialismus", "Neustart", "Niederländer", "Niederschlag",
            "Nordosten", "Nordwesten", "Norweger", "Notarzt", 
            "Parteitag", "Pegel", "Pendler", "Personalmangel", "Pfosten", "Pilot", "Pokal",
            "Pole", "Polizeibericht", "Polizeieinsatz", "Pop", "Pressesprecher", "Priester",
            "Radweg", "Rapper", "Rassismus", "Rechtsanwalt", "Regierungsrat", "Reis", "Report",
            "Retter", "Rettungshubschrauber", "Rhythmus", "Roboter", "Roller", "Rollstuhl",
            "Routinier", "Rundfunk", "Räuber", "Rückblick", "Rückschlag", "Rückzug",
            "Sand", "Sauerstoff", "Schauer", "Schlager",
            "Schreibtisch", "Schriftzug", "Schulleiter", "Segen", 
            "Sektor", "Server", "Skandal", "Soldat", "Sonnenschein", "Sound", "Spanier",
            "Sportplatz", "Sportvorstand", "Sprint", "Spruch", "Staatsanwalt", "Staatsbürger",
            "Staatschef", "Staatssekretär", "Standard", "Starkregen", "Startschuss",
            "Stellenwert", "Stellvertreter", "Steuerzahler", "Stich", "Stichtag", "Stillstand",
            "Stopp", "Straßenverkehr", "Streich", "Streifen",
            "Superstar", "Support", "Syrer", 
            "Teamkollege", "Teenager", "Teig", "Terror", "Teufel",
            "Titelverteidiger", "Torjäger", "Torschütze", "Trailer", "Traktor", "Transfer",
            "Transporter", "Treibstoff", "Trick", "Triumph", "Träger", "Tunnel", "Turner",
            "Umstand", "Umstieg", "Unfallort", "Unfallverursacher", "Unmut",
            "Untergrund", "Unterstützer", "Urlauber", "Verbleib", 
            "Verfolger", "Verkehrsteilnehmer", "Verstoß", "Vertrieb",
            "Verursacher", "Verweis", "Vierbeiner", "Vizekanzler", "Vizepräsident",
            "Vorjahreszeitraum", "Vorsitz", "Vorverkauf", 
            "Wahnsinn", "Wanderer", "Warnstreik", "Weihnachtsbaum", "Wettkampf", "Wiederaufbau",
            "Winzer", "Wirbel", "Wohnort", "Wohnungsbau", "Zaun", "Zeitplan", "Zuhörer",
            "Zusammenschluss", "Zuspruch", "Zutritt", "Zuwachs", "Überfall",
            "Übergang"
        ],
        "die": [
            "Abgabe", "Abhilfe", "Abhängigkeit", "Ablöse", "Abschaffung", "Absicherung",
            "Absprache", "Abwechslung", "Abwesenheit", "Action", "Affäre", "Agenda",
            "Aggression", "Airline", "Akzeptanz", "Allee", "Anfangsphase", "Angelegenheit",
            "Anhebung", "Anhörung", "Anpassung", "Anreise", "Anschaffung", "Ansprache",
            "Arbeitswelt", "Arbeitszeit", "Architektur", "Aufarbeitung",
            "Aufführung", "Aufschrift", "Aufstellung", "Augenhöhe", "Ausbreitung",
            "Ausrichtung", "Ausstrahlung", "Außenpolitik", "Bahnstrecke", "Balance",
            "Bandbreite", "Bearbeitung", "Beendigung", "Befragung", "Befreiung", "Begleitung",
            "Behinderung", "Bekanntgabe", "Bekämpfung", "Belegschaft", "Beleidigung",
            "Beleuchtung", "Beliebtheit", "Beobachtung", "Berechnung", "Bereitstellung",
            "Bergung", "Berichterstattung", "Berufsfeuerwehr", "Berücksichtigung", "Besatzung",
            "Beschleunigung", "Beschreibung", "Besetzung", "Besonderheit", "Bestellung",
            "Bewährung", "Bewältigung", "Bezahlung", "Bezeichnung", "Biografie",
            "Blockade", "Bombe", "Box", "Brandstiftung", "Brandursache", "Brauerei", "Bremse",
            "Bronze", "Bundesebene", "Bundesrepublik", "Bundestagswahl",
            "Bushaltestelle", "Bürgerinitiative", "Bürgerschaft", "Bürokratie", "Challenge",
            "Cloud", "Coronapandemie", "Crew", "Delegation", "Demenz", "Diagnose", "Dimension",
            "Diskriminierung", "Disziplin", "Dividende", "Dokumentation (Doku)", "Drohne",
            "Drohung", "Dunkelheit", "Durchführung", "Durchsuchung", "Dynamik", 
            "Edition", "Effizienz", "Ehre", "Einreise", "Einschränkung", "Elektromobilität",
            "Empörung", "Entdeckung", "Entschädigung", "Entspannung",
            "Entstehung", "Entwarnung", "Episode", "Erderwärmung", "Erfüllung", "Ergänzung",
            "Erhebung", "Erholung", "Erleichterung", "Erneuerung", "Ernte", "Errichtung",
            "Erscheinung", "Erstellung", "Eskalation", "Etappe", "Euphorie",
            "Evakuierung", "Exekutive", "Existenz", "Expertise",
            "Fabrik", "Fahndung", "Fahrerlaubnis", "Fantasie", "Fassade", "Fassung",
            "Fernwärme", "Fertigstellung", "Filiale", "Flagge", "Flanke",
            "Flexibilität", "Flotte", "Fluggesellschaft", "Flut", "Fotografie", "Freigabe",
            "Freilassung", "Fusion", "Fußgängerzone", "Gefährdung",
            "Gegenfahrbahn", "Gegenoffensive", "Gegenwart", "Geldstrafe",
            "Generalstaatsanwaltschaft", "Geschäftsführung", "Gestaltung",
            "Grafikkarte", "Großstadt", "Grundsteuer", 
            "Halbinsel", "Handlung", "Hardware", "Hauptrolle", "Hauptversammlung",
            "Haustür", "Holding", "Höhle", "Hölle", "Hündin",
            "Hürde", "Immobilie", "Impfung", "Inbetriebnahme", "Inflationsrate", "Inklusion",
            "Innovation", "Inspiration", "Installation", "Instanz", "Institution",
            "Inszenierung", "Intensität", "Internetseite", "Investition", "Jagd", "Kandidatur",
            "Kapazität", "Kinderbetreuung", "Kirchengemeinde", "Klarheit", "Kleinstadt",
            "Klärung", "Kohle", "Kollision", "Kommune", "Komödie", "Konjunktur",
            "Konsequenz", "Konsole", "Konstellation", "Konzentration", "Korruption",
            "Kreativität", "Kreisliga", "Kriminalität", "Krönung", "Kulisse", "Kundschaft",
            "Königsklasse", "Kürze", "Ladung", "Laufbahn", 
            "Lebensgefahr", "Lebensqualität", "Legende", "Leinwand", "Leitplanke", "Lesung",
            "Logistik", "Luftwaffe", "Lupe", "Marine", "Maske", "Maskenpflicht", "Masse",
            "Medaille", "Menschheit", "Mitgliedschaft",
            "Modernisierung", "Moral", "Motivation", "Musikschule", "Nachbarschaft",
            "Nachfolge", "Nachspielzeit", "Nahrung", "Neuauflage", "Neutralität", "Normalität",
            "Notenbank", "Novelle", "Oberfläche", "Orientierung", "Ortschaft",
            "Panik", "Parade", "Petition", "Piste", "Platte", "Pleite", "Prinzessin",
            "Priorität", "Probe", "Propaganda", "Provinz", "Präsenz", "Prävention",
            "Psychiatrie", "Pyrotechnik", "Quelle", "Quote", "Rakete", 
            "Reduktion", "Reduzierung", "Regie", "Regionalliga", "Regulierung", "Relevanz",
            "Rentenversicherung", "Reserve", "Resolution", "Resonanz", "Revision", "Revolution",
            "Rezession", "Route", "Räumung", "Rückseite", "Sachbeschädigung",
            "Sammlung", "Schaffung", "Schale", "Schau", "Schiene", 
            "Schwäche", "Schätzung", "Schönheit", "Seele", "Senkung", "Sensation", "Session",
            "Sicherung", "Siedlung", "Silvesternacht", "Skepsis", "Sommerpause", "Souveränität",
            "Sparkasse", "Spende", "Sperre", "Sporthalle", "Staatsanwältin",
            "Staatsbürgerschaft", "Startelf", "Steuerung", 
            "Straftat", "Streife", "Stromversorgung", "Stärkung", "Störung", "Substanz",
            "Synagoge", "Tagesordnung", "Tagestemperatur", "Tageszeitung", "Taktik", "Teilhabe",
            "Telefonnummer", "Terrororganisation", "These", "Tiefgarage", "Todesursache",
            "Tonne", "Tragödie", "Tribüne", "Trockenheit", "Tötung", "Umgestaltung",
            "Unabhängigkeit", "Unruhe", "Unsicherheit", "Unterbringung", "Unterzahl",
            "Verabschiedung", "Verarbeitung", "Verbraucherzentrale", "Verbreitung",
            "Verfolgung", "Verfügbarkeit", "Vergewaltigung", "Verkehrskontrolle",
            "Verkehrssicherheit", "Verleihung", "Verordnung", "Verschiebung", "Verschärfung",
            "Verstärkung", "Verteilung", "Verurteilung", "Verzweiflung", "Verzögerung",
            "Volkspartei", "Volkswirtschaft", "Vorfreude", "Vorrunde",
            "Vorsaison", "Vorwoche", "Waffenruhe", "Wartezeit", 
            "Weile", "Weiterentwicklung", "Weltmeisterschaft",
            "Wertschätzung", "Wiederwahl", "Windkraft", "Wucht", "Wut", "Wüste",
            "Zeitenwende", "Zeremonie", "Zielgruppe", "Zivilbevölkerung", "Zufahrt", "Zunahme",
            "Zusage", "Zusammensetzung", "Zuwanderung", "Ära", "Ärztekammer",
            "Öffnung", "Übergabe", "Überprüfung", "Übersicht", "Übertragung", "Übung"
        ],
        "das": [
            "Abgeordnetenhaus", "Achtelfinale", "Ambiente", "Anwesen", "Anzeichen", "Argument",
            "Arsenal", "Asyl", "Beben",
            "Bekenntnis", "Benzin", "Betriebssystem", "Business", "Bußgeld", "Coronavirus",
            "Debüt", "Defizit", "Denkmal", "Dilemma", "Display", "Drama", "Drehbuch", "Ehepaar",
            "Einfamilienhaus", "Element", "Endspiel", "Ensemble", "Entertainment", "Erdgas",
            "Exil", "Experiment", "Familienunternehmen", "Fass", "Feedback", "Festzelt", "Fett",
            "Feuerwerk", "Finanzamt", "Format", "Foul", "Foyer",
            "Fragezeichen", "Freibad", "Fundament", "Gegentor", "Gehäuse", "Geschäftsmodell", "Geständnis", 
            "Gewerbe", "Gewerbegebiet", "Gewässer", "Grab", "Großaufgebot", "Grundgesetz",
            "Handwerk", "Heck", "Heimatland", "Hochwasser", "Homeoffice", "Image",
            "Immunsystem", "Innenministerium", "Journal", "Kabinett", "Kanzleramt", "Kapital",
            "Klinikum", "Kloster", "Kriegsverbrechen", "Kunstwerk", "Königreich", "Landesamt",
            "Landeskriminalamt", "Landratsamt", "Level", "Limit",
            "Lob", "Lächeln", "Mandat", "Manöver", "Marketing", "Massaker", "Maß",
            "Mehrfamilienhaus", "Mikrofon", "Mittelalter", "Motiv", "Mindestmaß", "Motorrad", "Musical",
            "Muster", "Oberlandesgericht", "Objekt", "Oktoberfest",
            "Olympiastadion", "Ordnungsamt", "Outfit", "Parkhaus", "Pfund", "Pilotprojekt",
            "Pixel", "Podium", "Polizeipräsidium", "Portal", "Portfolio", "Privatleben",
            "Profil", "Protokoll", "Quartier", "Radfahren", "Ranking", "Regime", "Remis",
            "Resultat", "Saisonende", "Salz", "Schnäppchen", "Schuljahr",
            "Segment", "Selbstbewusstsein", "Selbstvertrauen", "Sortiment", "Spektrum",
            "Spielfeld", "Stichwort", "Szenario", "Telefonat", "Territorium",
            "Todesopfer", "Tool", "Trainingslager", "Trikot", "Trinkwasser",
            "Trio", "Universum", "Unrecht", "Verwaltungsgericht", "Volumen", "Votum",
            "Waldstück", "Wertpapier"
        ],
    },
    "C2": {
        "der": [
            "Abflug", "Abgeordneter", "Abgrund", "Ableger", "Abnehmer", "Absteiger",
            "Acker", "Adventskalender",
            "Akteur", "Aktivist", "Albtraum", "Altar", "Amtsinhaber", "Anfänger", "Anker",
            "Anklang", "Anrainer", "Anreiz", "Anrufer", "Anschein", "Ansturm", "Apotheker",
            "Arbeitsalltag", "Argentinier", "Assistent", 
            "Aufenthaltsort", "Auffahrunfall", "Aufpreis", "Aufruhr", "Aufschluss",
            "Aufwärtstrend", "Augenblick", "Ausgangspunkt", "Ausnahmezustand", "Australier",
            "Austritt", "Ausweg", "Auszug", "Autohersteller", "Autounfall",
            "Außenverteidiger", "Avatar", "Bachelor", "Ballon",
            "Bann", "Basketballer", "Bass", "Bauabschnitt", "Bauarbeiter", 
            "Bauhof", "Behälter", "Belgier", "Benutzer", "Bernstein",
            "Berufsverkehr", "Bestseller", "Betriebsrat", "Biergarten", "Blitz", "Blues",
            "Bonus", "Brasilianer", "Browser", "Bruchteil", "Bundesgerichtshof", "Bundesligist",
            "Bundesminister", "Bunker", "Busfahrer", "Böller", "Bürgerkrieg",
            "Campingplatz", "Champion", "Chefredakteur", "Controller", "Dachstuhl",
            "Dauerregen", "Diabetes", "Diktator", "Dirigent", "Dorn", "Draht",
            "Dreck", "Dreh", "Duft", "Durchmesser", "Dämpfer", "Einmarsch",
            "Einsatzort", "Einspruch", "Eintrag", "Energiekonzern",
            "Energieversorger", "Engländer", "Entertainer",
            "Entschluss", "Erfinder", "Erreger", "Ertrag", "Erzbischof", "Erzieher", "Etat",
            "Europameister", "Fachbereich", "Faden", "Fahrgast", "Familienvater",
            "Feuerwehrmann", "Filmemacher", "Flugverkehr", "Flyer", "Foulelfmeter", "Frachter",
            "Freispruch", "Freundeskreis", "Frühschoppen",
            "Fürst", "Gastronom", "Gegenwind", "Geiger", "Geldbeutel",
            "Gesamtschaden", "Gesamtwert", "Gesellschafter", "Gesetzesentwurf",
            "Gläubiger", "Großbrand", "Gärtner",
            "Haftrichter", "Hauch", "Hauptdarsteller", "Hauptgrund", "Hausarzt", "Hausbesitzer",
            "Hausmeister", "Heimweg", "Helikopter", "Herausforderer", "Herzinfarkt",
            "Hingucker", "Hochdruck", "Horror", "Höchststand", "Idealfall", "Imbiss",
            "Impfstoff", "Impuls", "Intendant",
            "Jahresvergleich", "Japaner", "Joint", "Junior", "Jurist", 
            "Kanadier", "Kapitalismus", "Kardinal", "Kinderwagen", "Kinofilm",
            "Klartext", "Knoblauch", "Knoten", "Kofferraum", "Kollaps", "Komiker",
            "Kommandeur", "Komponist", "Konzernchef", "Kopfhörer", "Korb", "Kragen", "Kran",
            "Kreuzbandriss", "Kumpel", "Kämmerer", "Lebensstil",
            "Leerstand", "Leichnam", "Linienbus", "Lokführer", "Luftraum",
            "Machtkampf", "Magistrat", "Major", "Mandant", "Marathon", "Marktführer",
            "Marschflugkörper", "Master", "Meteorologe", "Mietvertrag", "Milliardär",
            "Millionär", "Mitschüler", "Mitstreiter", "Mittelstand", "Mittelstürmer",
            "Motorsport", "Mythos", "Nachdruck", "Nachschub", "Nationaltrainer", "Neuanfang",
            "Neuschnee", "Newsletter", "Oberkörper", "Olympiasieger",
            "Oppositionsführer", "Organisator", "Ortskern", "Ortsvorsteher", "Panther",
            "Paragraf", "Parlamentarier", "Passant", "Pater", "Pavillon", "Pianist", "Planet",
            "Platzverweis", "Polizeihubschrauber", "Populismus", "Preisanstieg", "Preisträger",
            "Produzent", "Profifußball", "Projektleiter", "Prototyp", 
            "Prozessor", "Puma", "Putsch", "Pächter", "Ratgeber", "Raub", "Rausch", "Rauswurf",
            "Rechnungshof", "Rechtsextremismus", "Rechtsstreit", "Redner", "Regierungssprecher",
            "Rektor", "Renner", "Rennstall", "Saisonbeginn", "Sammler",
            "Sanitäter", "Sattelzug", "Schadenersatz", "Scherz", "Schienenersatzverkehr",
            "Schlaganfall", "Schlamm", "Schlusspfiff", "Schub", "Schulhof",
            "Schwimmer", "Schützenpanzer", "Shop", "Siedler", "Siegtreffer", 
            "Slalom", "Slogan", "Sparer", "Spargel", "Spatenstich", "Spaziergänger", "Spender",
            "Spielbetrieb", "Spielplan", "Spitzenkandidat", "Spott", "Spätsommer",
            "Staatspräsident", "Stadtpark", "Stamm", "Stammspieler", "Strafstoß",
            "Straftäter", "Strang", "Straßenrand", "Streamer", "Stromausfall", "Strompreis",
            "Stromverbrauch", "Takt", "Tank", "Tarif", "Taucher",
            "Teich", "Tenor", "Terrorismus", 
            "Tierschutz", "Tierschützer", "Todesfall", "Totalschaden", "Treiber", "Tänzer",
            "Umkreis", "Umlauf", "Umweg", "Unfallhergang", "Unsinn", "Untergang",
            "Untersuchungsausschuss", "Valentinstag", "Vandalismus", "Verbrenner", "Verbund",
            "Vermittler", "Verzehr", "Vize", "Vollbrand", "Vollzug", "Vorabend",
            "Vorgeschmack", "Vormarsch", "Vorort", "Vorrang", "Vorreiter", "Vorwand",
            "Völkermord", "Wahlsieg", "Waldbrand", "Wasserstand", "Wegfall", "Weihnachtsmann",
            "Weltraum", "Weltverband", "Western", "Wohnbau",
            "Wohnungsmarkt", "Wurf", "Zauber", "Zoff", "Zulauf", "Zweitligist",
            "Ökonom", "Überschuss"
        ],
        "die": [
            "Abendkasse", "Abkühlung", "Abrechnung", "Abreise", "Abwicklung", "Achse",
            "Altersgruppe", "Altersklasse", "Anbindung", "Anfahrt", "Angabe", "Anklageschrift",
            "Annäherung", "Ansiedlung", "Anspielung", "Anweisung", "Anwesenheit",
            "Arbeitsgemeinschaft", "Arbeitslosenquote", "Argumentation", "Artenvielfalt",
            "Artillerie", "Asche", "Atomkraft", "Attraktion", "Attraktivität", "Aufholjagd",
            "Aufsicht", "Aufstockung", "Aufwertung", "Auktion", "Aula", "Ausbeutung",
            "Ausführung", "Auslieferung", "Auslosung", "Auszahlung", "Auszählung",
            "Autoindustrie", "Automatisierung", "Automobilindustrie", "Barrierefreiheit",
            "Bauzeit", "Beachtung", "Bebauung", "Bedienung", "Befürchtung", "Begrenzung",
            "Begrüßung", "Begutachtung", "Bekanntheit", "Belästigung", 
            "Berufserfahrung", "Berührung", "Beschaffung", "Beseitigung", "Besichtigung",
            "Bestimmung", "Betrachtung", "Beurteilung", "Bibel", "Bindung",
            "Biodiversität", "Blasmusik", "Blutentnahme", "Blutprobe", "Blüte",
            "Bodenoffensive", "Braut", "Buchhandlung", "Buchmesse", "Bundesagentur",
            "Bundesanwaltschaft", "Bundeshauptstadt", "Böschung", "Dankbarkeit", "Datenbank",
            "Deckung", "Dekarbonisierung", "Depression", "Desinformation", "Devise", "Diakonie",
            "Differenz", "Diktatur", "Diplomatie", "Diversität", "Dominanz",
            "Drehleiter", "Dringlichkeit", "Ehrung", "Einfahrt", "Einigkeit", "Einsamkeit",
            "Einwanderung", "Elektronik", "Elite", "Empathie", "Energieeffizienz", "Entführung",
            "Entschlossenheit", "Entsorgung", "Erfindung", "Erfolgsgeschichte", "Erhaltung",
            "Ermittlung", "Ermordung", "Erschließung", "Erwärmung", "Erzählung", 
            "Eurozone", "Evolution", "Expansion", "Fachzeitschrift", "Fahrspur", "Faszination",
            "Fertigung", "Festung", "Feuchtigkeit", "Finanzkrise", "Flamme", "Flutkatastrophe",
            "Flüchtlingsunterkunft", "Formation", "Formulierung", "Foundation", "Frontlinie",
            "Föderation", "Garantie", "Gedenkstätte", "Gegenseite", "Geldwäsche",
            "Genesung", "Genossenschaft", 
            "Gesetzgebung", "Gestalt", "Geste", "Glasfaser", "Glaubwürdigkeit",
            "Gleichberechtigung", "Glätte", "Goldmedaille", "Grundversorgung",
            "Gruppierung", "Größenordnung", "Handelskammer", "Handvoll", "Harmonie",
            "Hauptfigur", "Hauptsache", "Hausnummer", "Hauswand", "Helligkeit",
            "Herangehensweise", "Hetze", "Hilfsorganisation", "Historie", "Hitzewelle",
            "Homosexualität", "Härte", "Höchstgeschwindigkeit", "Hüpfburg",
            "Ideologie", "Informatik", "Integrität", "Intensivstation", "Interpretation",
            "Ironie", "Isolation", "Jahreshauptversammlung", "Jahreshälfte", 
            "Jugendfeuerwehr", "Kante", "Kanzlei", "Kaufkraft", "Kaution", 
            "Kinderarmut", "Kippe", "Kirmes", "Klassik", "Kollektion", "Kolumne",
            "Komplexität", "Komponente", "Konfrontation",
            "Konstruktion", "Kontinuität", "Koordination", "Korrektur", "Krankenversicherung",
            "Kreisstadt", "Kühlung", "Lady", 
            "Landesebene", "Lautstärke", "Lebensdauer", "Lebenserwartung", "Lebensfreude",
            "Legalisierung", "Legislaturperiode", "Leichtigkeit", "Leihe", "Leistungsfähigkeit",
            "Liegenschaft", "Linde", "Liquidität", "Lizenz", "Logik", "Lok",
            "Luftfahrt", "Luftfeuchtigkeit", "Luke", "Magie", "Malerei", "Mangelware",
            "Manipulation", "Masche", "Materie", "Mediathek", "Meinungsfreiheit",
            "Menschlichkeit", "Mentalität", "Messerattacke", "Moderation", "Monarchie",
            "Mordkommission", "Moschee", "Nervosität", "Neuerung",
            "Neugestaltung", "Niederschlagsmenge", "Nominierung", "Norm", "Notlage", "Nötigung",
            "Obduktion", "Offenheit", "Optik", "Optimierung", "Packung",
            "Palette", "Parteispitze", "Passage", "Periode", "Personalie",
            "Pfarrkirche", "Philharmonie", "Photovoltaik", "Pipeline", "Pistole",
            "Podiumsdiskussion", "Polizeidirektion", "Polizeistreife", "Polizeiwache",
            "Preiserhöhung", "Preisverleihung", "Pressestelle", "Privatsphäre", "Problematik",
            "Produktivität", "Provokation", "Prämie", "Präsidentenwahl",
            "Präsidentschaftswahl", "Präzision", "Psychologie", "Rache", "Rangliste",
            "Realisierung", "Rebellion", "Regierungspartei", "Registrierung",
            "Relegation", "Rettungsaktion", "Revue", "Rhetorik", "Richtlinie", "Routine",
            "Rücksprache", "Satzung", "Sauna", "Schande", "Scheune", "Schicht", "Schlacht",
            "Schlägerei", "Schulleitung", "Schusswaffe", "Seitenlinie",
            "Selbstständigkeit", "Seltenheit", "Sexualität", "Sichtbarkeit", "Siegerehrung",
            "Skulptur", "Sonde", "Sorte", "Spaltung", "Sparte", "Sprengung",
            "Spurensicherung", "Staatsangehörigkeit", "Staatskanzlei", "Staatsoper",
            "Staatsregierung", "Stabilisierung", "Stadtbibliothek", "Stadträtin",
            "Steuererklärung", "Stromerzeugung", "Suchaktion", "Säule",
            "Tagung", "Taufe", "Thematik", "Tournee",
            "Transaktion", "Trauerfeier", "Trendwende", "Trophäe", "Turnhalle", 
            "Unfallursache", "Uniklinik", "Unterbrechung", "Unterdrückung", "Unzufriedenheit",
            "Uraufführung", "Verbundenheit", "Vergütung", "Verhaftung", "Vermarktung",
            "Vernissage", "Vernunft", "Verpackung", "Verpflegung", "Versorgungssicherheit",
            "Verständigung", "Versöhnung", "Vertragsverlängerung", "Verwirrung",
            "Videobotschaft", "Viertelstunde", "Vorarbeit",
            "Voraussicht", "Vorgabe", "Vorgehensweise", "Vorhersage", "Vorsorge",
            "Vorstandsvorsitzende", "Wache", "Wahlbeteiligung", "Wartung", "Waschmaschine",
            "Weide", "Weiterfahrt", "Weltrangliste", "Weltwirtschaft", "Wendung", "Wertung",
            "Wette", "Wichtigkeit", "Wiederaufnahme", "Wiedereröffnung",
            "Wiederherstellung", "Wiederholung", "Wiedervereinigung", "Windenergie",
            "Wirksamkeit", "Wirtschaftspolitik", "Witterung", "Währung", "Zubereitung",
            "Zugabe", "Zurückhaltung", "Zuverlässigkeit", "Überarbeitung",
            "Überlegung", "Überzahl"
        ],
        "das": [
            "Abwasser", "Archiv", "Arzneimittel", "Asylverfahren", "Atelier", "Aufgebot",
            "Augenmerk", "Aushängeschild", "Bauprojekt", "Bauvorhaben", 
            "Berufsleben", "Bezirksamt", "Bistum", "Blaulicht", "Brett",
            "Bruttoinlandsprodukt", "Bundeskabinett", "Bundesministerium", 
            "Cockpit", "College", "Cover", "Darlehen", "Date", "Deck", "Depot", "Desaster",
            "Diebesgut", "Dinner", "Doppel", "Dreieck", "Echo", "Eigenkapital",
            "Eigentor", "Einvernehmen", "Einzel", "Eisen", "Eishockey", "Elektroauto",
            "Elfmeterschießen", "Elterngeld", "Entsetzen", "Erscheinungsbild", "Erzbistum",
            "Europaparlament", "Exemplar", "Fachwissen", "Fehlverhalten", "Fell", "Festland",
            "Fitnessstudio", "Förderprogramm", "Gebot", "Gefährt", "Gehör",
            "Genre", "Gespür", "Gipfeltreffen",
            "Glyphosat", "Grenzgebiet", "Grundwasser", "Heizöl", "Herzblut",
            "Hochhaus", "Inland", "Jobcenter", 
            "Karriereende", "Klassenzimmer", "Kohlendioxid", "Komitee", "Kommando", "Label",
            "Laub", "Lebewesen", "Lenkrad", "Lithium", "Lotto", "Marihuana",
            "Minimum", "Mitgefühl", "Mobbing", "Nachsehen", "Nationalteam",
            "Nest", "Neujahr", "Paradies", "Parkett", "Pflegeheim",
            "Polizeirevier", "Präsidium", "Pärchen", "Quartett",
            "Rampenlicht", "Referendum", "Register", "Remake", "Repertoire", "Ressort",
            "Revier", "Rollenspiel", "Ruder", "Schauspiel", "Schlachtfeld", "Schützenfest",
            "Selfie", "Siegel", "Skifahren", "Sommerfest", 
            "Sondervermögen", "Spielzeug", "Staatsoberhaupt", "Stadium", "Stadtzentrum",
            "Streaming", "Stromnetz", "Tageslicht", "Tempolimit", "Theaterstück", 
            "Trauma", "Umland", "Universitätsklinikum", "Unverständnis", "Upgrade", "Versagen",
            "Veto", "Volksfest", "Vorstandsmitglied", "Völkerrecht", "Wahlergebnis",
            "Weihnachtsfest", "Weingut", "Wohngebiet", "Wohngebäude", "Wohnmobil", "Zeitalter",
            "Zitat", "Zusammenleben", "Ökosystem", "Übergewicht"
        ],
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

# Диалектизмы — гельветизмы (швейц.) и австрицизмы (австр.): региональные слова,
# которые сами немцы порой не знают. У каждого есть стандартный аналог в основных
# списках (Paradeiser → Tomate, Trottoir → Gehsteig, Glace → Eis …).
# Все — уровень C2; в переводах стоит пометка региона. (2026-07)
DIALECT_VOCAB_ADD = {
    "C2": {
        "der": ["Bancomat", "Coiffeur", "Fauteuil", "Führerausweis",
                "Paradeiser", "Zivilstand",
                "Erdapfel", "Topfen", "Kren", "Jänner"],
        "die": ["Fasnacht", "Glace", "Jause", "Marille", "Matura",
                "Ordination", "Primarschule",
                "Palatschinke"],
        "das": ["Couvert", "Faschierte", "Poulet", "Rüebli", "Schwammerl",
                "Stiegenhaus", "Tram", "Trottoir",
                "Velo", "Billett", "Schlagobers", "Sackerl", "Spital"],
    },
}

# Резерв композитов (в words.json НЕ попадает — build() этот блок не читает).
# Прореживание 2026-07: для каждой базы оставлен ~1 композит на уровень,
# остальные прозрачные композиты (род наследуется от базы и новой информации
# для тренировки артиклей не несёт) лежат здесь. Переводы в translations*.py
# сохранены — чтобы вернуть слово, достаточно перенести его в активный список.
RESERVE_COMPOUNDS = {
    "A1": {
        "die": [
            "Hauptschule", "Sprachenschule",
        ],
    },
    "A2": {
        "das": [
            "Einzelzimmer",
        ],
    },
    "B1": {
        "der": [
            "Speisewagen",
        ],
        "die": [
            "Arbeitsstelle", "Bezirksschule", "Gesamtschule", "Lehrstelle", "Mittelschule",
            "Realschule", "Schularbeit", "Sekundarschule", "Sonderschule", "Volksschule",
            "Zweitsprache",
        ],
        "das": [
            "Altersheim", "Gasthaus", "Hilfsmittel", "Kaffeehaus", "Laufwerk",
            "Nahrungsmittel", "Suchtmittel",
        ],
    },
    "B2": {
        "der": [
            "Angriffskrieg", "Angriffspunkt", "Ballungsraum", "Brennpunkt", "Brennstoff",
            "Domplatz", "Dortmunder", "Erdkreis", "Fernverkehr", "Finanzminister", "Freistaat",
            "Gesichtspunkt", "Großteil", "Inhaltsstoff", "Innenminister", "Knotenpunkt",
            "Motorradfahrer", "Ortsteil", "Premierminister", "Rechtsschutz", "Sanierungsfall",
            "Strafraum", "Stützpunkt", "Verteidigungsminister", "Wahlkreis",
            "Wirtschaftsminister",
        ],
        "die": [
            "Amtszeit", "Anlaufstelle", "Bagatellgrenze", "Brotzeit", "Fachrichtung",
            "Geheimhaltung", "Gemengelage", "Halbzeit", "Handelsbeziehung", "Haushaltsführung",
            "Kostenstelle", "Ladesäule", "Landesregierung", "Spielzeit", "Wasserstraße",
        ],
        "das": [
            "Bundesmittel", "Geschäftsjahr", "Gewinnspiel", "Haushaltsmittel", "Kopfgeld",
            "Landgericht", "Problemfeld", "Viertelfinale",
        ],
    },
    "C1": {
        "der": [
            "Abstiegskampf", "Abwehrspieler", "Bahnverkehr", "Baustein", "Fahrradfahrer",
            "Förderverein", "Gegenspieler", "Gegenverkehr", "Generalsekretär", "Großeinsatz",
            "Grundstein", "Hauptplatz", "Innenverteidiger", "Koalitionspartner", "Kopfball",
            "Kriegsbeginn", "Medienbericht", "Mittelfeldspieler", "Naturschutz", "Parteichef",
            "Saisonstart", "Schauplatz", "Schneefall", "Seitenwechsel", "Streamingdienst",
            "Streifenwagen", "Südosten", "Südwesten", "Tabellenplatz", "Umweltschutz",
            "Verfassungsschutz", "Verkehrsminister", "Vorstandschef", "Wahlgang", "Zweikampf",
        ],
        "die": [
            "Arbeitsgruppe", "Auszeit", "Bezirksliga", "Echtzeit", "Energieversorgung",
            "Erstversorgung", "Europameisterschaft", "Feuerpause", "Freiheitsstrafe",
            "Geldpolitik", "Generalversammlung", "Gruppenphase", "Hafenstadt", "Hansestadt",
            "Heimatstadt", "Hinrunde", "Klimapolitik", "Landesliga", "Laufzeit",
            "Mitgliederversammlung", "Oberliga", "Rauchentwicklung", "Rückrunde",
            "Schlussphase", "Stadthalle", "Stichwahl", "Volksrepublik", "Wasserversorgung",
            "Weihnachtszeit", "Winterpause", "Zwischenzeit",
        ],
        "das": [
            "Auswärtsspiel", "Außenministerium", "Bauwerk", "Finanzministerium", "Gastspiel",
            "Gesundheitsministerium", "Hinspiel", "Landesgericht", "Lebensjahr", "Nachbarland",
            "Rückspiel", "Sternzeichen", "Testspiel", "Wirtschaftsministerium",
        ],
    },
    "C2": {
        "der": [
            "Abteilungsleiter", "Abwehrchef", "Abwärtstrend", "Arbeitsminister", "Atemschutz",
            "Auswärtssieg", "Autoverkehr", "Außenbereich", "Baubeginn", "Bebauungsplan",
            "Börsengang", "Denkmalschutz", "Eingangsbereich", "Einsatzleiter", "Energieträger",
            "Energieverbrauch", "Euroraum", "Fraktionschef", "Frauenfußball", "Gegentreffer",
            "Geschäftsmann", "Gesundheitszustand", "Goldpreis", "Großraum", "Immobilienmarkt",
            "Innenraum", "Justizminister", "Kaufpreis", "Kleinwagen", "Landesverband",
            "Landsmann", "Leistungsträger", "Neuwagen", "Prozentpunkt", "Rückenwind",
            "Schlosspark", "Skifahrer", "Sportwagen", "Startplatz", "Tarifstreit",
            "Tarifvertrag", "Taxifahrer", "Tiefpunkt", "Tierarzt", "Vizemeister",
            "Wochenbeginn", "Wochenmarkt", "Zugverkehr",
        ],
        "die": [
            "Beratungsstelle", "Bestzeit", "Dienststelle", "Europawahl", "Generalprobe",
            "Geschäftsleitung", "Geschäftsstelle", "Großbank", "Jugendarbeit", "Kehrtwende",
            "Kommunalpolitik", "Kommunalwahl", "Küstenwache", "Lagerhalle", "Leitstelle",
            "Nationalbank", "Oppositionspartei", "Parlamentswahl", "Protestaktion",
            "Raumstation", "Schulzeit", "Spielweise", "Tabellenführung", "Tabellenspitze",
            "Uhrzeit", "Volksbank", "Vollzeit", "Wetterlage",
        ],
        "das": [
            "Bergland", "Beweismittel", "Bürgerhaus", "Eigenheim", "Genehmigungsverfahren",
            "Gesundheitssystem", "Gruppenspiel", "Industriegebiet", "Justizministerium",
            "Länderspiel", "Menschenleben", "Naturschutzgebiet", "Pflichtspiel", "Preisgeld",
            "Skigebiet", "Sommerhaus", "Trainerteam",
        ],
    },
}

# Омонимы (Homonyme, разг. Teekesselchen): пишутся и звучат одинаково, но
# артикль меняет значение. Каждое значение — отдельная карточка.
# gloss — русское значение (и часть ключа прогресса, НЕ менять!),
# en — то же значение по-английски (для интерфейса en/de). (Без level — A1.)
HOMONYMS = [
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
    # классические Teekesselchen — раньше лежали одной карточкой с одним
    # артиклем и смешанным переводом («die Steuer — налог/руль»), это неверно
    {"word": "Steuer", "article": "die", "gloss": "налог", "en": "tax", "level": "B1"},
    {"word": "Steuer", "article": "das", "gloss": "руль", "en": "steering wheel", "level": "B1"},
    {"word": "Leiter", "article": "der", "gloss": "руководитель", "en": "manager", "level": "B1"},
    {"word": "Leiter", "article": "die", "gloss": "приставная лестница", "en": "ladder", "level": "B1"},
    {"word": "Schild", "article": "das", "gloss": "табличка", "en": "sign", "level": "A2"},
    {"word": "Schild", "article": "der", "gloss": "щит", "en": "shield", "level": "B2"},
    {"word": "Verdienst", "article": "der", "gloss": "заработок", "en": "earnings", "level": "B2"},
    {"word": "Verdienst", "article": "das", "gloss": "заслуга", "en": "merit", "level": "C1"},
    # пары из списка Википедии «Substantive mit unterschiedlichem Genus» (2026-07);
    # der Laster раньше лежал одной картой «грузовик/порок» — порок на деле das
    {"word": "Laster", "article": "der", "gloss": "грузовик", "en": "truck", "level": "B1"},
    {"word": "Laster", "article": "das", "gloss": "порок", "en": "vice", "level": "C1"},
    {"word": "Tor", "article": "das", "gloss": "ворота", "en": "gate/goal", "level": "B2"},
    {"word": "Tor", "article": "der", "gloss": "глупец", "en": "fool", "level": "C2"},
    {"word": "Bauer", "article": "der", "gloss": "крестьянин", "en": "farmer", "level": "B1"},
    {"word": "Bauer", "article": "das", "gloss": "птичья клетка", "en": "birdcage", "level": "C2"},
    {"word": "Otter", "article": "der", "gloss": "выдра", "en": "otter", "level": "C1"},
    {"word": "Otter", "article": "die", "gloss": "гадюка", "en": "viper", "level": "C1"},
    {"word": "Tau", "article": "der", "gloss": "роса", "en": "dew", "level": "B2"},
    {"word": "Tau", "article": "das", "gloss": "канат", "en": "rope", "level": "C1"},
    {"word": "Heide", "article": "die", "gloss": "пустошь", "en": "heath", "level": "C1"},
    {"word": "Heide", "article": "der", "gloss": "язычник", "en": "heathen", "level": "C2"},
    # классические пары род-меняет-значение, добавлены 2026-07:
    # der Moment (миг) / das Moment (фактор, физ.: das Drehmoment!)
    {"word": "Moment", "article": "der", "gloss": "момент", "en": "moment", "level": "A2"},
    {"word": "Moment", "article": "das", "gloss": "фактор", "en": "factor (physics)", "level": "C1"},
    {"word": "Kunde", "article": "der", "gloss": "клиент", "en": "customer", "level": "A2"},
    {"word": "Kunde", "article": "die", "gloss": "весть", "en": "tidings", "level": "C2"},
    {"word": "Gehalt", "article": "das", "gloss": "зарплата", "en": "salary", "level": "A2"},
    {"word": "Gehalt", "article": "der", "gloss": "содержание", "en": "content", "level": "C1"},
    {"word": "Junge", "article": "der", "gloss": "мальчик", "en": "boy", "level": "A1"},
    {"word": "Junge", "article": "das", "gloss": "детёныш", "en": "young animal", "level": "B2"},
    {"word": "Erbe", "article": "das", "gloss": "наследство", "en": "heritage", "level": "B2"},
    {"word": "Erbe", "article": "der", "gloss": "наследник", "en": "heir", "level": "C1"},
    {"word": "Golf", "article": "das", "gloss": "гольф", "en": "golf", "level": "B2"},
    {"word": "Golf", "article": "der", "gloss": "залив", "en": "gulf", "level": "C1"},
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
    ("Fachleute", "C1"),
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
    for level, arts in DIALECT_VOCAB_ADD.items():
        for article, words in arts.items():
            DATA[level][article].extend(words)
    for level, arts in WIKI_NEWS_ADD.items():
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
    for h in HOMONYMS:
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
