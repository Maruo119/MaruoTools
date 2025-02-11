import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from janome.tokenizer import Tokenizer

# Janomeの形態素解析器のインスタンスを作成
tokenizer = Tokenizer()

# 日本語テキストのトークン化関数
def tokenize(text):
    # Janomeで形態素解析を行い、単語をリストで返す
    return [token.base_form for token in tokenizer.tokenize(text)]

# データの読み込み (FAQデータ)
faq_data = pd.read_csv("faq_data.csv")

# 質問と回答の列を取得
questions = faq_data['質問']
answers = faq_data['回答']

# TF-IDFのベクトライザーを作成（tokenizerにJanomeを使用）
vectorizer = TfidfVectorizer(stop_words='english', tokenizer=tokenize)

# 質問をベクトル化
question_vectors = vectorizer.fit_transform(questions)

def get_answer(user_question):
    # ユーザーの質問をベクトル化
    user_question_vector = vectorizer.transform([user_question])
    
    # コサイン類似度を計算
    similarity = cosine_similarity(user_question_vector, question_vectors)
    
    # 類似度が最も高い質問を検索
    best_match_index = similarity.argmax()
    
    # 最も類似した回答を返す
    return answers[best_match_index]

# ユーザーからの入力を受け取る
user_input = "割引などの制度はある？"
response = get_answer(user_input)
print(response)
