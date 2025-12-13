def verify_message(original_message, decoded_message):
    """
    Porownuje oryginalna i odczytana wiadomosc.
    
    Args:
        original_message (str): Wiadomość do ukrycia
        decoded_message (str): Wiadomość odczytana z obrazu
    
    Returns:
        tuple: (bool, str) - (czy się zgadza, komunikat)
    """
    if original_message == decoded_message:
        return True, "Wiad sa IDENTYCZNE"
    else:
        return False, f"BŁĄD: Wiad się roznia\n" \
                     f"Oryginalna: '{original_message}'\n" \
                     f"Odczytana: '{decoded_message}'"

def calculate_similarity(original, decoded):
    """
    Oblicza % podobieństwa
    """
    if not original and not decoded:
        return 100.0
    
    from difflib import SequenceMatcher
    similarity = SequenceMatcher(None, original, decoded).ratio()
    return round(similarity * 100, 2)