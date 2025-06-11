#Lr3, Var1, Task4
#Abdulov Alexandr 353503
#Date: 07.04.25
#Description: This module analyzes a given text string.

def analyze_text(text):

    words = text.split()
    longest_word = max(words, key=len)
    longest_word_index = words.index(longest_word) + 1
    even_words = [word for i, word in enumerate(words, start=1) if i % 2 == 0]

    return {
        "word_count": len(words),
        "longest_word": longest_word,
        "longest_word_number": longest_word_index,
        "even_words": even_words
    }


def main():

    text = ("So she was considering in her own mind, as well as she could, "
            "for the hot day made her feel very sleepy and stupid, whether the pleasure "
            "of making a daisy-chain would be worth the trouble of getting up and picking "
            "the daisies, when suddenly a White Rabbit with pink eyes ran close by her.")

    results = analyze_text(text)
    print("\nAnalysis Results:")
    print(f"a) Number of words: {results['word_count']}")
    print(f"b) Longest word: '{results['longest_word']}' (number: {results['longest_word_index']})")
    print(f"c) Even words: {results['even_words']}")

if __name__ == "__main__":
    main()
