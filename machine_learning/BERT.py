
# pip install transformers torch が必要

from transformers import BertTokenizer, BertModel
import torch

# BERTトークナイザとモデルをロード
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

# テキストをトークン化
text = "I love cats and dogs."
tokens = tokenizer(text, return_tensors="pt")

# ベクトルを生成
output = model(**tokens)
print(output.last_hidden_state)  # 文のベクトル
