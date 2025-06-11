from services.text_analyzer import TextAnalyzer
import zipfile


def run():
    try:
        with open("input.txt", "r") as f:
            text = f.read()

        analyzer = TextAnalyzer(text)

        with open("output.txt", "w") as f:
            f.write(f"Capital letters: {analyzer.find_capital_letters()}\n")
            f.write(f"Modified text: {analyzer.replace_sequence()}\n")
            f.write(f"Max length words count: {analyzer.max_length_words_count()}\n")
            f.write(f"Words followed by punctuation: {analyzer.words_followed_by_punctuation()}\n")
            f.write(f"Longest word ending with 'e': {analyzer.longest_word_ending_with_e()}\n")

            sentence_types = analyzer.count_sentences_by_type()
            f.write(f"narrative: {sentence_types['narrative']}\n")
            f.write(f"interrogative: {sentence_types['interrogative']}\n")
            f.write(f"Incentives: {sentence_types['Incentives']}\n")

            f.write(f"Average sentence length (words): {analyzer.average_sentence_length():.2f}\n")
            f.write(f"Average word length (characters): {analyzer.average_word_length():.2f}\n")
            f.write(f"Smileys count: {analyzer.count_smileys()}\n")

        with zipfile.ZipFile('result.zip', 'w') as zipf:
            zipf.write('output.txt')

            print("completed!!!!!")


    except Exception as e:
        print(f"Ошибка: {e}")