from gensim.models import Word2Vec

# pip install gensim が必要
# サンプルデータ
sentences = [["私は", "猫", "が", "好き", "です"], ["猫", "と", "犬", "は", "友達", "です"], ["私は", "犬", "も", "好き", "です"]]

# Word2Vecモデルの学習
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# 単語ベクトルを取得
print(model.wv["猫"])
print(model.wv["好き"])