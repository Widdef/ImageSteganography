from tests.verification import verify_message, calculate_similarity
import unittest
import sys

class TestVerification(unittest.TestCase):
    """Testy jednostkowe dla funkcji verify_message"""
    
    def test_identical_strings(self):
        """Test gdy wiadomości są identyczne"""
        result, msg = verify_message("Hello", "Hello")
        self.assertTrue(result)  
        self.assertIn("IDENTYCZNE", msg)  
    
    def test_different_strings(self):
        result, msg = verify_message("Hello", "World")
        self.assertFalse(result)  
        # Używamy 'roznia' zamiast 'różnią' bo funkcja zwraca 'roznia'
        self.assertIn("roznia", msg.lower())
    
    def test_case_sensitive(self):
        """Test czy funkcja rozróżnia wielkość liter"""
        result, msg = verify_message("Hello", "hello")
        self.assertFalse(result)  #powinno byc False
    
    def test_empty_strings(self):
        """Test pustych stringów"""
        result, msg = verify_message("", "")
        self.assertTrue(result)  
    
    def test_one_empty(self):
        """Test gdy jedna wiadomość jest pusta"""
        result, msg = verify_message("Hello", "")
        self.assertFalse(result)
    
    def test_polish_chars(self):
        """Test polskich znaków"""
        result, msg = verify_message("Zażółć gęślą jaźń", "Zażółć gęślą jaźń")
        self.assertTrue(result)
    
    def test_whitespace_difference(self):
        """Test różnicy w białych znakach"""
        result, msg = verify_message("Hello World", "Hello  World")  #jedna vs dwie spacje
        self.assertFalse(result)
    
    def test_special_characters(self):
        """Test znaków specjalnych"""
        test_str = "!@#$%^&*()_+{}|:\"<>?"
        result, msg = verify_message(test_str, test_str)
        self.assertTrue(result)
    
    def test_long_strings(self):
        """Test długich wiadomości"""
        long_text = "A" * 1000
        result, msg = verify_message(long_text, long_text)
        self.assertTrue(result)
    
    def test_newlines(self):
        """Test tekstu z enterami"""
        text = "Linia 1\nLinia 2\nLinia 3"
        result, msg = verify_message(text, text)
        self.assertTrue(result)

class TestSimilarity(unittest.TestCase):
    """Testy dla funkcji calculate_similarity"""
    
    def test_identical(self):
        """Test 100% podobieństwa"""
        self.assertEqual(calculate_similarity("ABC", "ABC"), 100.0)
    
    def test_partial(self):
        """Test częściowego podobieństwa"""
        # "ABC" vs "ABD"  2 z 3 = 66.67%
        self.assertEqual(calculate_similarity("ABC", "ABD"), 66.67)
    
    def test_empty_both(self):
        """Test dwóch pustych stringów"""
        self.assertEqual(calculate_similarity("", ""), 100.0)
    
    def test_completely_different(self):
        """Test zupełnie różnych stringów"""
        self.assertEqual(calculate_similarity("ABC", "XYZ"), 0.0)

def run_debug_tests():
    print()
    print("TESTY WERYFIKACJI - PODGLĄD (dla debugowania)")
    print()
    
    test_cases = [
        ("Identyczne", "test", "test", True),
        ("Różne", "test", "inny", False),
        ("Wielkość liter", "Test", "test", False),
        ("Polskie znaki", "łąka", "łąka", True),
        ("Puste", "", "", True),
        ("Jedno puste", "test", "", False),
        ("Białe znaki", "test test", "test  test", False),
        ("Długi tekst", "A"*50, "A"*50, True),
        ("Znaki specjalne", "!@#$", "!@#$", True),
        ("Z emoji", "Hello 😀", "Hello 😀", True),
    ]
    
    all_passed = True
    passed_count = 0
    
    for name, orig, dec, expected in test_cases:
        result, msg = verify_message(orig, dec)
        similarity = calculate_similarity(orig, dec)
        
        if result == expected:
            status = "Przeszlo"
            passed_count += 1
        else:
            status = "Blad"
            all_passed = False
        
        #Skracanie dlugich wiad
        display_orig = orig if len(orig) <= 20 else orig[:17] + "..."
        display_dec = dec if len(dec) <= 20 else dec[:17] + "..."
        
        print(f"{name:20} '{display_orig}' vs '{display_dec}': {status}")
        print(f"   Podobieństwo: {similarity}% | Oczekiwano: {expected}, Dostałem: {result}")
        
        if result != expected:
            #Wyswietla tylko pierwsza linie błędu
            error_line = msg.split('\n')[0]
            print(f"   Błąd: {error_line}")
        print()
    
    print(f"PODSUMOWANIE: {passed_count}/{len(test_cases)} testow zaliczonych")
    
    if all_passed:
        print("WSZYSTKIE TESTY OK!")
    else:
        print("CZESCIOWE BLEDY!")   
    print()
    
    return all_passed


def run_comprehensive_test_suite():
    """Uruchamia kompleksowe testy - jednostkowe i debugowe."""

    print("URUCHAMIANIE KOMPLETNYCH TESTÓW WERYFIKACJI")   
    print("\n[1/2] TESTY DEBUGOWE:")
    debug_success = run_debug_tests()
    
    print("\n[2/2] TESTY JEDNOSTKOWE (unittest):")
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestVerification))
    
    suite.addTests(loader.loadTestsFromTestCase(TestSimilarity))
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    unit_test_result = runner.run(suite)
    
    print()
    print("KOŃCOWE PODSUMOWANIE")
    print()
    
    unit_tests_passed = unit_test_result.testsRun - len(unit_test_result.failures) - len(unit_test_result.errors)
    
    print(f"TESTY DEBUGOWE:   {'WSZYSTKO OK' if debug_success else 'PROBLEMY'}")
    print(f"TESTY JEDNOSTKOWE: {unit_tests_passed}/{unit_test_result.testsRun} zaliczone")
    
    if debug_success and unit_test_result.wasSuccessful():
        print("\n WSZYSTKIE TESTY ZALICZONE!")
        return True
    else:
        print("\n WYKRYTO BLEDY")
        return False

if __name__ == "__main__":
    """
    Jak uruchomić:
    1. Normalnie: python test_verification_final.py
    2. Tylko unittest: python -m unittest test_verification_final.py
    3. Tylko unittest (inaczej): python test_verification_final.py --unit-only
    """
    
    if len(sys.argv) > 1 and sys.argv[1] == "--unit-only":
        unittest.main(argv=[sys.argv[0]] + sys.argv[2:])
    else:
        success = run_comprehensive_test_suite()
        sys.exit(0 if success else 1)