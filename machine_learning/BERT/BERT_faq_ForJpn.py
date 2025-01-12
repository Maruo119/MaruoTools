from transformers import BertTokenizer, BertForQuestionAnswering
import torch
from googletrans import Translator

# モデルとトークナイザを一度だけロード
# 日本語モデルを使うと回答が安定しないので英語モデルを使い毎回翻訳するように実装した。
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

def clear_gpu_memory():
    """GPUメモリを解放する関数"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def answer_question(question_jpn, context):

    question_eng = translate_to_english(question_jpn)

    """質問応答の推論を実行"""
    inputs = tokenizer(question_eng, context, return_tensors="pt", max_length=512, truncation=True)

    # モデルで予測
    outputs = model(**inputs)
    start_idx = torch.argmax(outputs.start_logits)
    end_idx = torch.argmax(outputs.end_logits)

    # インデックス確認
    if start_idx < len(inputs.input_ids[0]) and end_idx < len(inputs.input_ids[0]):
        return tokenizer.decode(inputs.input_ids[0][start_idx:end_idx+1])
    else:
        return "答えが見つかりませんでした。"

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

def translate_to_japanese(english_text):
    """
    Translate English text to Japanese using googletrans library.
    :param english_text: str, English text to translate
    :return: str, Translated Japanese text
    """
    translator = Translator()
    try:
        # Translate English to Japanese
        result = translator.translate(english_text, src='en', dest='ja')
        return english_text + ' -> ' + result.text
    except Exception as e:
        return f"An error occurred: {e}"

# コンテキストをテキストファイルから読み込む
#with open("BERT_context_Jpn.txt", "r", encoding="utf-8") as file:
with open("BERT_context_Eng.txt", "r", encoding="utf-8") as file:
    #jpn_context = file.read()
    #context = translate_to_english(jpn_context)
    context = file.read()

# 翻訳した内容を新しいファイルに保存
with open("BERT_context_Eng.txt", "w", encoding="utf-8") as file:
    file.write(context)
    

# 質問を定義
question_1_1 = "東京都の留学支援制度において、短期留学の場合、助成される費用の最大額はいくらですか？"
question_1_2 = "東京都の留学支援制度の対象となる留学生は、どのような条件を満たす必要がありますか？"
question_1_3 = "東京都がこの留学支援制度を通じて年間に支援を予定している中・長期留学者数は何人ですか？"

question_2_1 = "第300条において、保険の勧誘や契約締結に関して禁止されている行為は何ですか？"
question_2_2 = "第300条によると、契約の重要事項を告知しないことが許容されるのはどのような場合ですか？"
question_2_3 = "第300条の2で定義される「特定保険契約」とは何を指しますか？"
question_2_4 = "第300条において、保険商品間の比較に関して禁止されている行為は何ですか？"
question_2_5 = "将来の配当や剰余金分配など、不確実な将来の利益に関する断定的判断について適用される制限は何ですか？"


# 1回目
'''
print("1-1問目:", translate_to_japanese(answer_question(question_1_1, context)))
print("1-2問目:", translate_to_japanese(answer_question(question_1_2, context)))
print("1-3問目:", translate_to_japanese(answer_question(question_1_3, context)))
'''

# 1回目
print("2-1問目:", translate_to_japanese(answer_question(question_2_1, context)))
print("2-2問目:", translate_to_japanese(answer_question(question_2_2, context)))
print("2-3問目:", translate_to_japanese(answer_question(question_2_3, context)))
print("2-4問目:", translate_to_japanese(answer_question(question_2_4, context)))
print("2-5問目:", translate_to_japanese(answer_question(question_2_5, context)))

# GPUメモリ解放
clear_gpu_memory()
