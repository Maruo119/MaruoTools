import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from janome.tokenizer import Tokenizer
from gensim.models import KeyedVectors
import numpy as np

# Janomeの形態素解析器のインスタンスを作成
tokenizer = Tokenizer()

# 日本語テキストのトークン化関数
def tokenize(text):
    return [token.base_form for token in tokenizer.tokenize(text)]


'''
解決方法：
モデルファイルの場所を確認する:

path_to_your_word2vec_model.bin は、実際にあなたが使いたいWord2Vecモデルのファイルパスに置き換える必要があります。
もしGoogleの事前学習済み日本語Word2Vecモデル（word2vec）を使う場合は、まずそのモデルファイルをダウンロードする必要があります。
Word2Vecモデルのダウンロード:

Googleの日本語の事前学習済みWord2Vecモデルをダウンロードする場合、以下の手順で進めます。

日本語のWord2Vecモデル（例えば、cc.ja.300.vec）をダウンロードするには、このリンクからGoogleのWord2Vec日本語モデルを取得することができます。
ダウンロード後、cc.ja.300.vecファイルをバイナリ形式に変換する必要があります。次のコマンドで変換を行います。
bash
コピーする
編集する
python -m gensim.scripts.glove2word2vec --input cc.ja.300.vec --output cc.ja.300.bin

'''

# Word2Vecモデルのロード（事前に学習されたモデルを使用）
# ここでは、GoogleのWord2Vecの日本語モデルなどを使用できます
word2vec_model = KeyedVectors.load_word2vec_format('path_to_your_word2vec_model.bin', binary=True)

# 質問データと回答データの読み込み
faq_data = pd.read_csv("faq_data.csv")
questions = faq_data['質問']
answers = faq_data['回答']

# Word2Vecで文章をベクトル化する関数
def get_word2vec_vector(text):
    tokens = tokenize(text)
    vector = np.zeros(300)  # Word2Vecのベクトルサイズは通常300次元
    valid_tokens = 0
    for token in tokens:
        try:
            vector += word2vec_model[token]  # 各トークンのベクトルを加算
            valid_tokens += 1
        except KeyError:
            continue  # モデルにない単語は無視
    return vector / valid_tokens if valid_tokens > 0 else vector

# FAQデータの質問をベクトル化
question_vectors = np.array([get_word2vec_vector(q) for q in questions])

def get_answer(user_question):
    # ユーザーの質問をベクトル化
    user_question_vector = get_word2vec_vector(user_question)
    
    # コサイン類似度を計算
    similarity = cosine_similarity([user_question_vector], question_vectors)
    
    # 最も類似した質問のインデックスを取得
    best_match_index = similarity.argmax()
    
    # 最も類似した回答を返す
    return answers[best_match_index]

# ユーザーからの入力を受け取る
user_input = "割引などの制度はある？"
response = get_answer(user_input)
print(response)
