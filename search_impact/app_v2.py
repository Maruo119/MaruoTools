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
    keyword = request.form['keyword']
    repo_path = request.form['repo_path']

    try:
        cmd = ['grep', '-rn', keyword, repo_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

        output = result.stdout.splitlines()
        grep_results = {}
        for idx, line in enumerate(output):
            parts = line.split(":", 2)
            if len(parts) == 3:
                file_name, line_number, content = parts
                grep_results[idx] = {
                    "file_name": file_name,
                    "line_number": line_number,
                    "content": content
                }

        return render_template('results_v2.html', results=grep_results)

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
