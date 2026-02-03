# Python 3.9
# All logic is built-in and uses no imports.
# Written By Aniq Abbasi

class ContentAnalyzer:
    # Average words per minute for reading and speaking
    _WPM_READING = 225
    _WPM_SPEAKING = 180

    def __init__(self, text: str):
        self.text = text
        self.metrics = {}
        if not text or not self._has_content(text):
            print("Warning: Input text is empty or contains only whitespace.")
            self._reset_metrics()
        else:
            self._process_text()

    def _has_content(self, text_to_check: str) -> bool:
        # Checks if the text contains any non-whitespace characters.
        for char in text_to_check:
            if char not in ' \t\n\r':
                return True
        return False

    def _reset_metrics(self):
        # Sets all analysis metrics to zero or empty values.
        self.metrics = {
            "Character Count": 0,
            "Word Count": 0,
            "Sentence Count": 0,
            "Paragraph Count": 0,
            "Reading Time": "0 minutes 0 seconds",
            "Speaking Time": "0 minutes 0 seconds",
            "Reading Level": "N/A",
            "Key Phrases (1-word)": [],
            "Key Phrases (2-word)": [],
            "Key Phrases (3-word)": [],
        }

    def _process_text(self):
        # Executes all analysis functions in order.
        char_count, word_count, clean_words = self._tokenize_and_count()
        self.metrics["Character Count"] = char_count
        self.metrics["Word Count"] = word_count

        sentence_count = self._find_sentence_boundaries()
        self.metrics["Sentence Count"] = sentence_count

        self.metrics["Paragraph Count"] = self._count_text_blocks()

        # Time estimations
        self.metrics["Reading Time"] = self._estimate_duration(word_count, self._WPM_READING)
        self.metrics["Speaking Time"] = self._estimate_duration(word_count, self._WPM_SPEAKING)

        # Complex metrics
        self.metrics["Reading Level"] = self._compute_grade_level(clean_words, sentence_count)
        
        # Keyword analysis
        (d1, d2, d3) = self._find_key_phrases(clean_words)
        self.metrics["Key Phrases (1-word)"] = d1
        self.metrics["Key Phrases (2-word)"] = d2
        self.metrics["Key Phrases (3-word)"] = d3

    def _tokenize_and_count(self) -> tuple[int, int, list]:
        # Manually iterates to count characters, words, and create a clean word list.
        char_count = len(self.text)
        words = []
        current_word = ""
        alpha_numeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        for char in self.text:
            if char in alpha_numeric:
                current_word += char
            else:
                if current_word:
                    words.append(current_word.lower())
                    current_word = ""
        
        # Add the last word if the text doesn't end with a delimiter
        if current_word:
            words.append(current_word.lower())

        return char_count, len(words), words

    def _find_sentence_boundaries(self) -> int:
        # Counts sentences by looking for terminators followed by whitespace.
        count = 0
        text_len = len(self.text)
        if not self._has_content(self.text):
            return 0
        
        has_unterminated_sentence = False
        terminators = ".!?"
        
        for i, char in enumerate(self.text):
            if char not in ' \t\n\r':
                has_unterminated_sentence = True # We have content
            
            if char in terminators:
                # Check if it's the end of text or followed by whitespace.
                if (i + 1 >= text_len) or (self.text[i+1] in ' \t\n\r'):
                    count += 1
                    has_unterminated_sentence = False

        # If content exists but no terminator was found, it's one sentence.
        if has_unterminated_sentence and count == 0:
            return 1
        elif has_unterminated_sentence:
            # Case where last sentence lacks punctuation.
            return count + 1

        return count

    def _count_text_blocks(self) -> int:
        # Counts paragraphs by finding double newline separators.
        stripped_text = self.text.strip(' \t\n\r')
        if not stripped_text:
            return 0

        # At least one paragraph if there's any text.
        count = 1
        search_from_index = 0
        
        while True:
            # string.find() is a built-in method, not an import.
            found_index = stripped_text.find('\n\n', search_from_index)
            if found_index != -1:
                count += 1
                search_from_index = found_index + 2 # Move past the found separator.
            else:
                break
        
        return count

    def _estimate_duration(self, word_count: int, wpm: int) -> str:
        # Calculates time in minutes and seconds.
        if wpm == 0 or word_count == 0:
            return "0 minutes 0 seconds"
        
        time_decimal = word_count / wpm
        minutes = int(time_decimal)
        seconds = int((time_decimal - minutes) * 60)
        
        # Handle pluralization manually.
        min_str = "minute" if minutes == 1 else "minutes"
        sec_str = "second" if seconds == 1 else "seconds"

        return f"{minutes} {min_str} {seconds} {sec_str}"

    def _guess_syllables(self, word: str) -> int:
        # A heuristic-based syllable counter. It's an estimation.
        word = word.lower()
        if len(word) == 0:
            return 0
        
        vowels = "aeiouy"
        syllable_count = 0
        is_prev_char_vowel = False

        # 1. Count vowel groups.
        for char in word:
            is_char_vowel = char in vowels
            if is_char_vowel and not is_prev_char_vowel:
                syllable_count += 1
            is_prev_char_vowel = is_char_vowel
        
        # 2. Handle silent 'e' at the end.
        if len(word) > 2 and word.endswith('e') and not word.endswith('le') and syllable_count > 1:
            if word[-2] not in vowels:
                syllable_count -= 1
        
        # 3. Ensure every word has at least one syllable.
        if syllable_count == 0:
            return 1
            
        return syllable_count

    def _compute_grade_level(self, words: list, sentence_count: int) -> str:
        # Calculates the Flesch-Kincaid Grade Level.
        word_count = len(words)
        if word_count == 0 or sentence_count == 0:
            return "N/A"

        total_syllables = 0
        for word in words:
            total_syllables += self._guess_syllables(word)
        
        try:
            grade_level = (0.39 * (word_count / sentence_count)) + \
                          (11.8 * (total_syllables / word_count)) - 15.59
        except ZeroDivisionError:
            return "N/A"

        # Round to nearest integer manually.
        rounded_grade = int(grade_level + 0.5) if grade_level > 0 else int(grade_level - 0.5)

        if rounded_grade < 1:
            return "Grade < 1 (Early reader)"
        elif rounded_grade >= 13:
            return f"Grade {rounded_grade} (College level)"
        else:
            return f"Grade {rounded_grade}"

    def _find_key_phrases(self, words: list, top_n=5) -> tuple[list, list, list]:
        # A small, manually defined list of common English stop words.
        stop_words = [
            'a', 'an', 'the', 'is', 'in', 'it', 'of', 'for', 'on', 'are', 'was',
            'with', 'as', 'by', 'at', 'to', 'and', 'or', 'but', 'that', 'this'
        ]

        # --- 1-word phrases (unigrams) ---
        unigrams = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                unigrams[word] = unigrams.get(word, 0) + 1
        
        # --- 2-word phrases (bigrams) ---
        bigrams = {}
        if len(words) > 1:
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                bigrams[phrase] = bigrams.get(phrase, 0) + 1
        
        # --- 3-word phrases (trigrams) ---
        trigrams = {}
        if len(words) > 2:
            for i in range(len(words) - 2):
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                trigrams[phrase] = trigrams.get(phrase, 0) + 1

        # Sort dictionaries by value (count) in descending order.
        # sorted() is a built-in function, not an import.
        sorted_unigrams = sorted(unigrams.items(), key=lambda item: item[1], reverse=True)
        sorted_bigrams = sorted(bigrams.items(), key=lambda item: item[1], reverse=True)
        sorted_trigrams = sorted(trigrams.items(), key=lambda item: item[1], reverse=True)
        
        return (
            [f'"{k}" ({v} times)' for k, v in sorted_unigrams[:top_n]],
            [f'"{k}" ({v} times)' for k, v in sorted_bigrams[:top_n]],
            [f'"{k}" ({v} times)' for k, v in sorted_trigrams[:top_n]],
        )

    def show_report(self):
        # Prints the analysis results in a readable format.
        print("\n--- Content Analysis Report ---")
        for key, value in self.metrics.items():
            if isinstance(value, list):
                print(f"{key}:")
                if not value:
                    print("  - (None found)")
                else:
                    for item in value:
                        print(f"  - {item}")
            else:
                print(f"{key}: {value}")
        print("-------------------------------\n")


if __name__ == "__main__":
    print("Please paste your text below. To finish, type 'ENDOFTEXT' on a new line and press Enter.")
    
    user_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'ENDOFTEXT':
                break
            user_lines.append(line)
        except EOFError:
            # Handles case where user signals end of input with Ctrl+D (Unix) or Ctrl+Z (Windows)
            break
            
    input_text = "\n".join(user_lines)

    analyzer = ContentAnalyzer(input_text)
    analyzer.show_report()