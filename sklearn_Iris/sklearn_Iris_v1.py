# 必要なライブラリをインポート
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Irisデータセットをロード
iris = load_iris()
X = iris.data  # 特徴量（花のサイズなど）
y = iris.target  # ラベル（花の種類）

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ランダムフォレストを使用したモデルの作成
model = RandomForestClassifier()

# 訓練データでモデルを学習
model.fit(X_train, y_train)

# テストデータで予測
y_pred = model.predict(X_test)

# 精度を計算
accuracy = accuracy_score(y_test, y_pred)
print(f"モデルの精度: {accuracy * 100:.2f}%")

# 新しいデータの予測（花の特徴量を入力）
#new_data = [[5.1, 3.5, .4, 0.2]]  # 新しい花の特徴量（例） -> 「setosa」になる
new_data = [[10.1, 1.2, .2, 0.9]]  # 新しい花の特徴量（例） -> 「versicolor」になる
prediction = model.predict(new_data)
predicted_class = iris.target_names[prediction[0]]
print(iris.target_names) # -> 「['setosa' 'versicolor' 'virginica']」が表示される
print(f"予測結果: {predicted_class}")
