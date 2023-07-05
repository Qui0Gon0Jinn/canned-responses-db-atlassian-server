# TODO: analyze canned responses content
# search and correct newlines which weren't interpreted correctly - if a text is surrounded by "" but has a linebreak, write /n
# search for specific dates
# search for Usernames/Signatures/Passwords/...

import re

def canned_responses_content_analyzer(cr_item):
    time_sensitive_items = {
        # Weitere zeitlich begrenzte Textbausteine hinzugefügt
        "Mai 2023": "Mai",
        "Q1 2021": "erstes Quartal",
        "Q4 2022": "viertes Quartal",
        "August 2021": "August",
        "Dezember 2020": "Dezember",
        "April 2023": "April",
        "Winterschlussverkauf 2022": "Winterschlussverkauf",
        "Frühjahrskollektion 2021": "Frühjahrskollektion",
        "Herbst/Winter 2023": "Herbst/Winter-Kollektion",
        "2021-2022 Schuljahr": "aktuelles Schuljahr",
        "2022-2023 Akademisches Jahr": "aktuelles akademisches Jahr",
        "Sommersemester 2022": "Sommersemester",
        "Wintersemester 2023": "Wintersemester",
        "Oktoberfest 2021": "Oktoberfest",
        "Karneval 2022": "Karneval",
        "Fußball-WM 2018": "Fußball-WM",
        "Olympische Spiele 2020": "Olympische Spiele",
        "Maria Mustermann": "Maria",
        "Max Mustermann": "Max",
        "+49 123 456789": "Telefonnummer",
        "0170 1234567": "Mobilnummer",
        "555-1234": "Telefonnummer",
        "ID: 123456": "ID",
        "Bestellnummer: 987654": "Bestellnummer",
        "Rechnungsnummer: 246810": "Rechnungsnummer",
        "Kundennummer: 13579": "Kundennummer",
        "Fallnummer: 86420": "Fallnummer",
        "Kursbeginn: 3. September 2022": "Kursbeginn",
        "Anmeldeschluss: 1. August 2023": "Anmeldeschluss",
        "Veranstaltung: 21. Juni 2022": "Veranstaltung",
        "Ablaufdatum: 31. Dezember 2021": "Ablaufdatum",
        "Mit freundlichen Grüßen, Maria": "Mit freundlichen Grüßen",
        "Viele Grüße, Max": "Viele Grüße",
        "Ihr Team von [Firmenname] 2022": "Ihr Team von [Firmenname]",
        "Mit freundlichen Grüßen, Maria": "Mit freundlichen Grüßen",
        "Viele Grüße, Max": "Viele Grüße",
        "Ihr Team von [Firmenname] 2022": "Ihr Team von [Firmenname]",
        "vorname.nachname@wu.ac.at": "E-Mail-Adresse"
    }

    time_sensitive_patterns = {
        # Regex-Muster für die zusätzlichen Beispiele hinzugefügt
        "Mai 2023": r'\bMai \d{4}\b',
        "Q1 2021": r'\bQ[1-4] \d{4}\b',
        "Q4 2022": r'\bQ[1-4] \d{4}\b',
        "August 2021": r'\bAugust \d{4}\b',
        "Dezember 2020": r'\bDezember \d{4}\b',
        "April 2023": r'\bApril \d{4}\b',
        "Winterschlussverkauf 2022": r'\bWinterschlussverkauf \d{4}\b',
        "Frühjahrskollektion 2021": r'\bFrühjahrskollektion \d{4}\b',
        "Herbst/Winter 2023": r'\bHerbst/Winter \d{4}\b',
        "2021-2022 Schuljahr": r'\d{4}-\d{4} Schuljahr\b',
        "2022-2023 Akademisches Jahr": r'\d{4}-\d{4} Akademisches Jahr\b',
        "Sommersemester 2022": r'\bSommersemester \d{4}\b',
        "Wintersemester 2023": r'\bWintersemester \d{4}\b',
        "Oktoberfest 2021": r'\bOktoberfest \d{4}\b',
        "Karneval 2022": r'\bKarneval \d{4}\b',
        "Fußball-WM 2018": r'\bFußball-WM \d{4}\b',
        "Olympische Spiele 2020": r'\bOlympische Spiele \d{4}\b',
        "Maria Mustermann": r'\bMaria Mustermann\b',
        "Max Mustermann": r'\bMax Mustermann\b',
        "+49 123 456789": r'\+\d{2} \d{3} \d{6}',
        "0170 1234567": r'\d{4} \d{7}',
        "555-1234": r'\d{3}-\d{4}',
        "ID: 123456": r'ID: \d{6}',
        "Bestellnummer: 987654": r'Bestellnummer: \d{6}',
        "Rechnungsnummer: 246810": r'Rechnungsnummer: \d{6}',
        "Kundennummer: 13579": r'Kundennummer: \d{5}',
        "Fallnummer: 86420": r'Fallnummer: \d{5}',
        "Kursbeginn: 3. September 2022": r'Kursbeginn: \d{1,2}\. [A-Za-z]+ \d{4}',
        "Anmeldeschluss: 1. August 2023": r'Anmeldeschluss: \d{1,2}\. [A-Za-z]+ \d{4}',
        "Veranstaltung: 21. Juni 2022": r'Veranstaltung: \d{1,2}\. [A-Za-z]+ \d{4}',
        "Mit freundlichen Grüßen, Maria": r'(Mit freundlichen Grüßen,|Viele Grüße,)\s+\b[A-Z][a-z]+',
        "Viele Grüße, Max": r'(Mit freundlichen Grüßen,|Viele Grüße,)\s+\b[A-Z][a-z]+',
        "vorname.nachname@wu.ac.at": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    }

