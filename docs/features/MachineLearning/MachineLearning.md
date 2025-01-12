# TF-IDF、Word2Vec、BERT

## 1. TF-IDF (Term Frequency-Inverse Document Frequency)
### 概要
TF-IDFは、文書内の単語の重要性を数値で表現する手法です。
単語の頻度（TF: Term Frequency）と、その単語がどれだけ他の文書に登場しているかの逆数（IDF: Inverse Document Frequency）を掛け合わせて計算します。

### 特徴
* メリット
    * 単純で計算が速い。
    * 各単語の相対的な重要性を考慮。

* デメリット:
    * 単語の順序や文脈を無視。
    * 同義語や多義語を区別できない。

### 実装例（Python）
``` python
from sklearn.feature_extraction.text import TfidfVectorizer

# サンプルデータ
documents = ["私は猫が好きです", "猫と犬は友達です", "私は犬も好きです"]

# TF-IDFベクトル化
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

# 単語とTF-IDF値を表示
print(vectorizer.get_feature_names_out())
print(X.toarray())
```

## 2. Word2Vec
### 概要
Word2Vecは、単語を高次元の数値ベクトルに変換するための方法で、Googleが提案しました。
単語間の意味的な類似性を捉えることができます。
ニューラルネットワークを使って単語を学習し、ベクトル化します。

### 手法
* CBOW (Continuous Bag of Words):
    * 周辺単語から中心単語を予測するモデル。

* Skip-gram:
    * 中心単語から周辺単語を予測するモデル。

### 特徴
* メリット:
    * 単語間の意味的な関係を捉える（例: king - man + woman ≈ queen）。
    * 次元が低く、計算効率が高い。

* デメリット:
    * 文脈を考慮しないため、多義語に弱い。

### 実装例（Python）
``` python
from gensim.models import Word2Vec

# サンプルデータ
sentences = [["私は", "猫", "が", "好き", "です"], ["猫", "と", "犬", "は", "友達", "です"], ["私は", "犬", "も", "好き", "です"]]

# Word2Vecモデルの学習
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# 単語ベクトルを取得
print(model.wv["猫"])
```

## 3. BERT (Bidirectional Encoder Representations from Transformers)
### 概要
BERTは、Googleが提案した自然言語処理（NLP）モデルで、文脈を考慮した特徴量を生成します。
Transformerアーキテクチャを使用し、単語だけでなく文全体や段落の意味も理解できます。

### 特徴
* 双方向の文脈理解:
    * 前後の単語を考慮して単語の意味を学習。
    * 例: "bank"（銀行/川岸）のような多義語も文脈によって解釈。

* 事前学習とファインチューニング:
    * 事前学習（Pre-training）: 大規模データで一般的な単語の関係を学習。
    * ファインチューニング（Fine-tuning）: 特定のタスク用に微調整。

* メリット
    * 高精度で多様なタスクに対応（分類、翻訳、質問応答など）。
    * 文脈を正確に捉える。
* デメリット
    * 計算コストが非常に高い。
    * モデルサイズが大きい（数百MB〜GB）。

### 実装例（Python）
```python
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
```

## 比較表

| 特徴 | TF-IDF | Word2Vec | BERT |
| ---- | ---- | ---- | ---- |
| 文脈の考慮  |	無視  | 無視  |考慮 |
| 次元 | 高い |低い |高い |
| 計算コスト | 低い | 中程度 | 非常に高い |
| 多義語の対応 | 弱い | 弱い | 強い |
| 文単位の対応 | 不可 | 不可 | 可能 |
| 用途 | シンプルなモデルや特徴量抽出 | 単語間の類似性解析 | 高度な自然言語処理 |

## どれを選ぶべきか？
* 簡単なタスク（例: 単純な分類やクラスタリング）→ TF-IDF。
* 単語間の意味的な関係を分析（例: 類似性やアナロジー解析）→ Word2Vec。
* 文脈を考慮した高度なタスク（例: 質問応答、要約生成）→ BERT。

# その他
https://huggingface.co/docs/huggingface_hub/package_reference/overview
