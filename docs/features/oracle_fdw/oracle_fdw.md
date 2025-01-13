# oracle_fdw

## 当ページの目的
業務でPostgreSQLとOracleを連動させたようなシステムを開発することになったので個人的な技術検証として以下の記録を残す。

### 簡単な背景
従来はOracleで管理していたDBについて特定のテーブル（従業員勤務実績テーブルととその子テーブルとする）をPostgreSQLに移行することになった。しかし、アプリケーション側では複雑なSQLを多数使用しておりSQLロジック自体は可能な限り修正を回避したい。

そこで当対応ではDBリンクの仕組みを利用することとし、PostgreSQLからOracleを参照する仕組みを利用するになった。
（更新についても検討しないといけないが、それはまた今後・・・）

上記を踏まえ、業務時間に可能な限り円滑にOracle FDWの実装や検証ができるようにするため、事前に接続検証などを実行したく、以下の通り記録を残す。

## 事前準備

### 1. OracleDB, PostgreSQL-DBを作成する。

　技術検証用でありDBに登録する内容は仮に盗まれても問題ないという前提で以下の設定を行った。
　以下、自分にとって重要な点のみを記載。

* VPC セキュリティグループ：default (sg-xx)
    * インバウンドルール「0.0.0.0/0」を追加しておく（接続に関する問題を回避するため）
    * インバウンドルールはOracle, PostgreSQLの両方上記が必要
* DB接続情報
    * AWSフルマネージド？を選択したため、Secrets Managerを参照する必要あり。
        * 「シークレットの値を取得する」から確認可能 

### 2. Amazon WorkspacesでWindows環境を作成する

筆者はMakBook Air(M1)を利用しており、Oracle Cliantのインストールに失敗した。
Oracle CliantがインストールされたDockerを使おうと思い挑戦したが、Docker内でsql plusを実行することに失敗して断念。
色々と調べた結果、Windows環境で実行することが好ましいと判断し、Windows PCを買うよりも手軽なAmazon Workspacesを利用することにした。

Amazon Workspacesの利用において特に詰まった点はなかったが、サーバーに接続できるまで30分掛かったため今後は当作業を初期段階で実施すると良い。


### 3. Amazon Workspaces内でOracle Cliantがインストールする

Oracleのページからダウンロードしてzipを解凍してパスを通した。
私の場合はtnsnames.oraが作成されていなかったため準備して配置するなどした。


###  4. DBクライアントツールでOracle, PostgreSQLに接続する

その後、sqlplusなどでDBに接続できることを確認した。
なかなか接続できず、以下のコマンドを利用して原因の切り分けなどを実施したため、メモとして残す。

* DNSの問題を確認
    * nslookup oracle-database-1.XXXXX.ap-southeast-2.rds.amazonaws.com

* ポート解放の確認
    * telnet oracle-database-1.XXXXX.ap-southeast-2.rds.amazonaws.com 1521

* 実際に遭遇したエラー
    * amazon workplaceのpcでa5m2のツールをインストールしてDBに接続し他とき
        * 「no pg_hba.conf entry for host "52.XX.XXX.83", user "postgres", database "mypostgre", no encryption」
        * 原因：DB側のVPC セキュリティグループに接続元サーバーのアドレスを設定していかなったため。
        * 対処：今回はめんどくさかったのでインバウンドルールに「0.0.0.0/0」を追加した

### 5. Oracle FDWを作成する

以下に記載したが、私は「admin」を小文字で記載しており接続がうまくいかず詰まってしまったため、今後は注意すること。

```sql
-- 1. EXTENSIONの作成
CREATE EXTENSION oracle_fdw;

-- 2. サーバーの作成
CREATE SERVER ora_server FOREIGN DATA WRAPPER oracle_fdw OPTIONS (dbserver '//oracle-database-1.XXXXX.ap-southeast-2.rds.amazonaws.com:1521/ORCL');

-- 3. ユーザーマッピングの作成
CREATE USER MAPPING FOR postgres SERVER ora_server OPTIONS (user 'ADMIN', password 'ORACLE-PASSWORD');

-- もしユーザーマッピングを削除したい場合はこちら
-- というのは、'ADMIN'を最初は小文字で作成してしまい、接続できない問題が発生していたため。
DROP USER MAPPING IF EXISTS FOR postgres SERVER ora_server;
-- これも残しておく
DROP FOREIGN TABLE IF EXISTS f_students CASCADE;

-- 4. 外部テーブルの作成
-- ポイントはスキーマ名は（私のようなデフォルト設定を利用する場合は）大文字を利用すること。ここに詰まり数時間費やしてしまった・・・。
CREATE FOREIGN TABLE f_STUDENTS(
   student_id integer OPTIONS (key 'true'),
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL,
    class VARCHAR(50) NOT NULL)     
    SERVER ora_server OPTIONS (schema 'ADMIN',table 'STUDENTS');

-- 5. 外部テーブルへの接続確認とデータ取得のテスト
select * from f_STUDENTS
```




