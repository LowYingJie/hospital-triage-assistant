from googletrans import Translator

def translate_text(text, target_lang="English"):
    lang_map = {
        "English": "en",
        "Malay": "ms",
        "Mandarin": "zh-CN",
        "Tamil": "ta"
    }
    translator = Translator()
    return translator.translate(text, dest=lang_map[target_lang]).text
