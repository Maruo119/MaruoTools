# 必要なライブラリをインポート
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# CSVデータの読み込み
# データ例:
# 問い合わせ概要,対応方法
# パスワードを忘れました,パスワード再設定リンクを送る
# アカウントがロックされた,サポートチームに転送
data = pd.read_csv("inquiries.csv")  # ファイル名を適宜変更

# 特徴量（問い合わせ概要）とターゲット（対応方法）を分ける
X = data['問い合わせ概要']  # 入力データ
y = data['対応方法']        # 出力データ（ラベル）

# テキストを数値に変換（Bag of Wordsを使用）
vectorizer = CountVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# ランダムフォレストを使用したモデルの作成
model = RandomForestClassifier()
model.fit(X_train, y_train)

# モデルの評価
y_pred = model.predict(X_test)
print("モデルの評価:")
print(classification_report(y_test, y_pred))

print(data['対応方法'].value_counts())

# 新しい問い合わせ概要の予測
print("\n新しい問い合わせ内容の対応方法を提案します。")
while True:
    new_inquiry = input("問い合わせ概要を入力してください（終了するには 'exit' と入力）: ")
    if new_inquiry.lower() == 'exit':
        print("終了します。")
        break
    # 入力をベクトル化して予測
    new_inquiry_vectorized = vectorizer.transform([new_inquiry])
    predicted_response = model.predict(new_inquiry_vectorized)
    print(f"提案される対応方法: {predicted_response[0]}\n")
