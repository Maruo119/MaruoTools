import argostranslate.translate

def translate_ja_to_en(text):
    try:
        return argostranslate.translate.translate(text, "ja", "en")
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

def translate_eng_to_jpn(text):
    try:
        return argostranslate.translate.translate(text, "en", "ja")
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

def translate(text, src_lang, dest_lang):
    try:
        return argostranslate.translate.translate(text, src_lang, dest_lang)
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

if __name__ == "__main__":
    print(translate_ja_to_en("もし「どうしても言い換えまで自動化したい、でもセキュリティが心配」という場合は、やはり「Javaでの機械的チェック」と「ローカルLLM（Ollama）でのリライト」の二段構えが最強です。"))