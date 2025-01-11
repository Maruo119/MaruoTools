# MaruoTools

setosa は Iris データセットに格納されている花の種類（ターゲットラベル）の名前で、iris.target_names に格納されています。

Iris データセットの構造
load_iris() を使用して取得した Iris データセットには、以下のような情報が含まれています：

特徴量（iris.data）:

各データポイント（花）の測定値（数値データ）。
列：
がく片の長さ（sepal length, cm）
がく片の幅（sepal width, cm）
花弁の長さ（petal length, cm）
花弁の幅（petal width, cm）
ターゲットラベル（iris.target）:

数値データとして花の種類を表現します。
値：
0: setosa
1: versicolor
2: virginica
ターゲット名（iris.target_names）:

花の種類を文字列で表現した配列。
値：
python
コードをコピーする
['setosa', 'versicolor', 'virginica']
setosa の参照
setosa のデータは、以下のようにコード内で参照されています：

python
コードをコピーする
# ラベル（数値データ）
y = iris.target  # 数値ラベルが入っている（例: 0, 1, 2）

# ラベル名（文字列）
target_names = iris.target_names  # ['setosa', 'versicolor', 'virginica']
モデルの予測結果が数値として返される場合、それを名前に変換する際に使用します：

python
コードをコピーする
# 数値ラベルを名前に変換
predicted_class = iris.target_names[prediction[0]]
print(f"予測結果: {predicted_class}")
ここで prediction[0] が 0 の場合、iris.target_names[0] に格納されている "setosa" が取得されます。

補足: Iris データセットの確認方法
データを直接確認したい場合、以下のコードを使用してください：

python
コードをコピーする
from sklearn.datasets import load_iris
iris = load_iris()

# ターゲット名
print("ターゲット名:", iris.target_names)

# データの例
print("特徴量の例:", iris.data[:5])  # 最初の5件
print("ターゲットラベルの例:", iris.target[:5])  # 最初の5件（数値ラベル）
