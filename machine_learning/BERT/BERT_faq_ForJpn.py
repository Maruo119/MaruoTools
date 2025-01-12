from transformers import BertJapaneseTokenizer, BertForQuestionAnswering
import torch

# モデルとトークナイザをロード
tokenizer = BertJapaneseTokenizer.from_pretrained('tohoku-nlp/bert-base-japanese')
model = BertForQuestionAnswering.from_pretrained('tohoku-nlp/bert-base-japanese')

def clear_gpu_memory():
    """GPUメモリを解放する関数"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def answer_question(question, context):
    """質問応答の推論を実行"""
    inputs = tokenizer(question, context, return_tensors="pt", max_length=512, truncation=True)

    # モデルで予測
    outputs = model(**inputs)
    start_idx = torch.argmax(outputs.start_logits)
    end_idx = torch.argmax(outputs.end_logits)

    # インデックス確認
    if start_idx < len(inputs.input_ids[0]) and end_idx < len(inputs.input_ids[0]):
        return tokenizer.decode(inputs.input_ids[0][start_idx:end_idx+1])
    else:
        return "答えが見つかりませんでした。"

# コンテキストをテキストファイルから読み込む
with open("BERT_context_Jpn.txt", "r", encoding="utf-8") as file:
    context = file.read()

# 質問を定義
question_1_1 = "東京都は無痛分娩を選択した住民に最大いくら補助しますか？"
question_1_2 = "無痛分娩の費用を補助するのは、日本の都道府県レベルでは初めてですか？"
question_1_3 = "東京都がこのプログラムの初期予算に11億円を計上した年度はいつですか？"

question_2_1 = "日本は合意の一環としてインドネシアに何を提供しますか？"
question_2_2 = "両国の外務・防衛大臣会議の開催について、両国首脳はどのような合意をしましたか？"
question_2_3 = "インドネシアとの協力について、石破首相が約束した内容は何ですか？"

# 1回目
print("1-1問目:", answer_question(question_1_1, context))
#print("1-2問目:", answer_question(question_1_2, context))
#print("1-3問目:", answer_question(question_1_3, context))

#print("2-1問目:", answer_question(question_2_1, context))
#print("2-2問目:", answer_question(question_2_2, context))
#print("2-3問目:", answer_question(question_2_3, context))

# GPUメモリ解放
clear_gpu_memory()
