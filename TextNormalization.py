# Text Normalization for Cardinal Numbers (0-1000) and Currency
# -----------------------------------------------------------------------
# Fix: SystemExit: 5 occurred because unittest.main() found **zero tests**.
# Solution: explicitly build a test suite and run it using TextTestRunner.

import re
import unittest
from typing import Match

# -------------------------
#  NUMBER → WORDS MAPPING
# -------------------------
ONES = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"
}
TEENS = {
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen"
}
TENS = {
    20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
    60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"
}

# -------------------------
#  NUMBER → WORDS FUNCTION
# -------------------------
def number_to_words(n: int) -> str:
    """Convert an integer n (0 <= n <= 1000) to written-out English."""
    if not (0 <= n <= 1000):
        raise ValueError("number out of range (expected 0..1000)")

    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n]
    if n < 100:
        tens_part = (n // 10) * 10
        ones_part = n % 10
        if ones_part == 0:
            return TENS[tens_part]
        return f"{TENS[tens_part]}-{ONES[ones_part]}"

    if n < 1000:
        hundreds = n // 100
        rest = n % 100
        if rest == 0:
            return f"{ONES[hundreds]} hundred"
        return f"{ONES[hundreds]} hundred {number_to_words(rest)}"

    return "one thousand"

# -------------------------
#  CURRENCY MAPPING
# -------------------------
CURRENCY_SYMBOLS = {
    "$": "dollar",
    "€": "euro",
    "£": "pound"
}
# Currency regex: $12, €12.50, £1000
CURRENCY_RE = re.compile(r"\b([$€£])(\d{1,4}(?:\.\d{1,2})?)\b")

def number_to_words_currency(amount: str) -> str:
    """Convert a currency amount string to words."""
    if '.' in amount:
        whole, fraction = amount.split('.')
        whole_val = int(whole)
        fraction_val = int(fraction)
        words = []
        if whole_val > 0:
            words.append(number_to_words(whole_val))
        if fraction_val > 0:
            words.append(f"{number_to_words(fraction_val)} cents")
        return ' '.join(words)
    else:
        val = int(amount)
        return number_to_words(val)

def normalize_currency(text: str) -> str:
    """Replace currency amounts with words."""
    def _repl(match: Match[str]) -> str:
        symbol, amount = match.groups()
        try:
            words = number_to_words_currency(amount)
        except ValueError:
            return match.group(0)
        currency_word = CURRENCY_SYMBOLS.get(symbol, "")
        # pluralize if amount is not exactly 1
        if float(amount) != 1:
            currency_word += "s"
        if words:
            return f"{words} {currency_word}".strip()
        return currency_word
    return CURRENCY_RE.sub(_repl, text)

# -------------------------
#  SENTENCE NORMALIZER
# -------------------------
NUMBER_RE = re.compile(r"\b(\d{1,4})\b")

def normalize(text: str) -> str:
    """Replace integers 0..1000 and currency with words."""
    # 1️⃣ Normalize currency first
    text = normalize_currency(text)

    # 2️⃣ Normalize plain numbers 0..1000
    def _repl(match: Match[str]) -> str:
        s = match.group(1)
        try:
            val = int(s)
        except ValueError:
            return s
        if 0 <= val <= 1000:
            return number_to_words(val)
        return s

    return NUMBER_RE.sub(_repl, text)

# -------------------------
#  UNIT TESTS
# -------------------------
class TestNumberToWords(unittest.TestCase):
    def test_basic_ones(self):
        self.assertEqual(number_to_words(0), "zero")
        self.assertEqual(number_to_words(5), "five")
        self.assertEqual(number_to_words(9), "nine")

    def test_teens(self):
        self.assertEqual(number_to_words(10), "ten")
        self.assertEqual(number_to_words(13), "thirteen")
        self.assertEqual(number_to_words(19), "nineteen")

    def test_tens(self):
        self.assertEqual(number_to_words(20), "twenty")
        self.assertEqual(number_to_words(21), "twenty-one")
        self.assertEqual(number_to_words(99), "ninety-nine")

    def test_hundreds(self):
        self.assertEqual(number_to_words(100), "one hundred")
        self.assertEqual(number_to_words(101), "one hundred one")
        self.assertEqual(number_to_words(215), "two hundred fifteen")
        self.assertEqual(number_to_words(999), "nine hundred ninety-nine")

    def test_thousand(self):
        self.assertEqual(number_to_words(1000), "one thousand")

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            number_to_words(-1)
        with self.assertRaises(ValueError):
            number_to_words(1001)

class TestNormalize(unittest.TestCase):
    def test_simple_sentences(self):
        self.assertEqual(normalize("I have 21 cats and 5 dogs"),
                         "I have twenty-one cats and five dogs")
        self.assertEqual(normalize("Zero 0 10 1000"),
                         "Zero zero ten one thousand")

    def test_punctuation_and_boundaries(self):
        self.assertEqual(normalize("In 2024, we did 3 tasks."),
                         "In 2024, we did three tasks.")
        self.assertEqual(normalize("Room 101 is next to 1001."),
                         "Room one hundred one is next to 1001.")

    def test_leading_zeros(self):
        self.assertEqual(normalize("IDs: 007, 000"), "IDs: seven, zero")

    def test_embedded_numbers(self):
        self.assertEqual(normalize("var1 and a2b"), "var1 and a2b")

    def test_edge_values(self):
        self.assertEqual(normalize("0 1 999 1000"), "zero one nine hundred ninety-nine one thousand")

    def test_multiple_spaces(self):
        self.assertEqual(normalize("I saw 5   dogs"), "I saw five   dogs")

    def test_no_numbers(self):
        self.assertEqual(normalize("Hello world"), "Hello world")

    # ✅ Currency test cases
    def test_currency(self):
        self.assertEqual(normalize("I have $5 and €12.50"),
                         "I have five dollars and twelve euros fifty cents")
        self.assertEqual(normalize("He owes £1"), "He owes one pound")
        self.assertEqual(normalize("Price: $1.01"), "Price: one dollar one cents")
        self.assertEqual(normalize("Cost: €0.99"), "Cost: ninety-nine cents")

# -------------------------
#  INTERACTIVE MODE ONLY
# -------------------------
if __name__ == "__main__":
    print("Smart Text Normalizer — Enter a sentence (or leave blank to exit):")
    while True:
        user_text = input("→ ").strip()
        if not user_text:
            print("Goodbye!")
            break
        print("Normalized form:", normalize(user_text))
        print()
