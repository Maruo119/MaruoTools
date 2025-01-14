from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import subprocess

app = Flask(__name__)

# Grep結果を一時的に保存する辞書
grep_results = {}

@app.route('/')
def input_page():
    """キー入力画面"""
    return render_template('input.html')

@app.route('/grep', methods=['POST'])
def grep():
    """Grep検索を実行し、結果確認画面を表示"""
    keyword = request.form['keyword']
    repo_path = request.form['repo_path']

    if not os.path.exists(repo_path):
        return "リポジトリパスが存在しません", 400

    try:
        # Grepコマンド実行
        cmd = ['grep', '-rn', keyword, repo_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        # 結果を保存
        global grep_results
        grep_results = {idx: line for idx, line in enumerate(output)}

        return render_template('results.html', results=grep_results)
    except Exception as e:
        return f"エラー: {e}", 500

@app.route('/save', methods=['POST'])
def save_results():
    """影響調査コメントをJSONファイルに保存"""
    comments = request.form.to_dict()
    comments.pop('csrf_token', None)  # CSRFトークンが含まれている場合は削除

    # JSONファイルに保存
    with open('comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

    return redirect(url_for('input_page'))

if __name__ == '__main__':
    app.run(debug=True)
