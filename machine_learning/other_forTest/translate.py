# pip install googletrans==4.0.0-rc1
from googletrans import Translator

def translate_to_english(japanese_text):
    """
    Translate Japanese text to English using googletrans library.
    :param japanese_text: str, Japanese text to translate
    :return: str, Translated English text
    """
    translator = Translator()
    try:
        # Translate Japanese to English
        result = translator.translate(japanese_text, src='ja', dest='en')
        return result.text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Input Japanese text
    japanese_text = input("日本語を入力してください: ")

    # Translate to English
    english_translation = translate_to_english(japanese_text)

    # Output the result
    print("英語の翻訳:", english_translation)
