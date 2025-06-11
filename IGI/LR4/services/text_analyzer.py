import re

class TextAnalyzer:
    def __init__(self, text):
        self.text = text

    def find_capital_letters(self):
        return re.findall(r'[A-Z]', self.text)

    def replace_sequence(self):
        return re.sub(r'(a+)(b{2,})(c+)', 'qqq', self.text, flags=re.IGNORECASE)

    def max_length_words_count(self):
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0
        max_len = max(len(word) for word in words)
        return sum(1 for word in words if len(word) == max_len)

    def words_followed_by_punctuation(self):
        return re.findall(r'\b(\w+)[.,]', self.text)

    def longest_word_ending_with_e(self):
        words = re.findall(r'\b\w+e\b', self.text, flags=re.IGNORECASE)
        return max(words, key=len, default="") if words else ""

    def count_sentences_by_type(self):
        narrative = len(re.findall(r'(\w+\.(\s|$))', self.text))
        interrogative = len(re.findall(r'(\w+\?(\s|$))', self.text))
        imperative = len(re.findall(r'(\w+!(\s|$))', self.text))

        return {
            "narrative": narrative,
            "interrogative": interrogative,
            "Incentives": imperative
        }

    def average_sentence_length(self):
        sentences = [s.strip() for s in re.split(r'[.!?]', self.text) if s.strip()]
        if not sentences:
            return 0
        return sum(len(re.findall(r'\b\w+\b', s)) for s in sentences) / len(sentences)

    def average_word_length(self):
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0
        total_chars = sum(len(word) for word in words)
        return total_chars / len(words)

    def count_smileys(self):
        return len(re.findall(r'[:;][-]*([(){}\[\]])\1*', self.text))