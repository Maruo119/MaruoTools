from sklearn.feature_extraction.text import TfidfVectorizer

# サンプルデータ
documents = ["私は猫が好きです", "猫と犬は友達です", "私は犬も好きです"]

# TF-IDFベクトル化
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

# 単語とTF-IDF値を表示
print(vectorizer.get_feature_names_out())
print(X.toarray())

# 実行結果
'''
['猫と犬は友達です' '私は犬も好きです' '私は猫が好きです']
[[0. 0. 1.]
 [1. 0. 0.]
 [0. 1. 0.]]
'''
