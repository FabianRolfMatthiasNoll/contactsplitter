"""Logic for generating the brief salutation (briefanrede) based on language and gender."""

from domain.contact import Contact


def generate_briefanrede(contact: Contact) -> str:
    """
    Generate a brief salutation string based on the contact's language, gender, title, and last name.
    Uses predefined patterns for supported languages (de, en, it, fr, es).
    """
    lang = contact.sprache.lower() if contact.sprache else ""
    gender = contact.geschlecht.lower() if contact.geschlecht else "-"
    last_name = contact.nachname.strip()
    title = contact.titel.strip()
    # Default to generic output if no info
    if not lang or lang not in {"de", "en", "it", "fr", "es"}:
        # If unknown language, default to German generic as fallback.
        lang = "de"
    # Determine salutation based on language and gender
    if lang == "de":
        if gender == "w":
            # "Sehr geehrte Frau <Titel?> <Nachname>"
            if title:
                return f"Sehr geehrte Frau {title} {last_name}".strip()
            else:
                return f"Sehr geehrte Frau {last_name}".strip()
        elif gender == "m":
            if title:
                return f"Sehr geehrter Herr {title} {last_name}".strip()
            else:
                return f"Sehr geehrter Herr {last_name}".strip()
        else:
            return "Sehr geehrte Damen und Herren"
    elif lang == "en":
        # Determine courtesy based on gender and provided anrede
        if gender == "w":
            courtesy = "Ms"
            if contact.anrede:
                ar = contact.anrede.lower()
                if ar in {"mrs", "miss", "ms"}:
                    courtesy = contact.anrede  # preserve original casing
        elif gender == "m":
            courtesy = "Mr"
            if contact.anrede:
                ar = contact.anrede.lower()
                if ar == "mr":
                    courtesy = contact.anrede
        else:
            return "Dear Sirs"
        # If title indicates Dr or Prof, use it in salutation instead of courtesy
        if title:
            first_title_token = title.split()[0]
            ft_lower = first_title_token.lower().rstrip(".")
            if ft_lower == "dr":
                return f"Dear {first_title_token} {last_name}"
            if ft_lower.startswith("prof"):
                return f"Dear {first_title_token} {last_name}"
        return f"Dear {courtesy} {last_name}"
    elif lang == "it":
        if gender == "w":
            return f"Gentile Signora {last_name}"
        elif gender == "m":
            return f"Egregio Signor {last_name}"
        else:
            return "Egregi Signori"
    elif lang == "fr":
        if gender == "w":
            return f"Madame {last_name}"
        elif gender == "m":
            return f"Monsieur {last_name}"
        else:
            return "Messieursdames"
    elif lang == "es":
        if gender == "w":
            return f"Estimada Señora {last_name}"
        elif gender == "m":
            return f"Estimado Señor {last_name}"
        else:
            return "Estimados Señores y Señoras"
    # Fallback (should not happen due to earlier default)
    return f"Dear {last_name}"
