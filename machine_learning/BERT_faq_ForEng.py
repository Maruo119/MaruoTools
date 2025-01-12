from transformers import BertTokenizer, BertForQuestionAnswering
import torch

# モデルとトークナイザを一度だけロード
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


def clear_gpu_memory():
    """GPUメモリを解放する関数"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def answer_question(question, context):
    """質問応答の推論を実行"""
    inputs = tokenizer(question, context, return_tensors="pt")

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
with open("BERT_context.txt", "r", encoding="utf-8") as file:
    context = file.read()

# 質問を定義
question_1_1 = "What is the maximum subsidy amount the Tokyo metropolitan government will provide to residents choosing painless deliveries?"
question_1_2 = "Is this the first program at the prefecture level in Japan to subsidize the cost of painless childbirths? Please answer yes or no."
question_1_3 = "For which fiscal year has the Tokyo metropolitan government allocated 1.1 billion yen in the initial budget for this program?"

question_2_1 = "What will Japan provide to Indonesia as part of their agreement?"
question_2_2 = "What type of meeting did the two leaders agree to hold between their countries' foreign and defense ministers?."
question_2_3 = "What did Prime Minister Ishiba promise to cooperate on with Indonesia?"


# 1回目
print("1-1問目:", answer_question(question_1_1, context))
print("1-2問目:", answer_question(question_1_2, context))
print("1-3問目:", answer_question(question_1_3, context))

print("2-1問目:", answer_question(question_2_1, context))
print("2-2問目:", answer_question(question_2_2, context))
print("2-3問目:", answer_question(question_2_3, context))

# GPUメモリ解放
clear_gpu_memory()

# 2回目
#print("2回目の推論:", answer_question(question, context))
