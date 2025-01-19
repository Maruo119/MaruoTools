from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import re
import json
from urllib.parse import quote, unquote

app = Flask(__name__)

# 保存先ディレクトリ（適宜設定してください）
SAVE_DIRECTORY = "notes"

# Grep結果を一時的に保存する辞書
grep_results = {}

def load_notes(search_keyword):
    notes_file = f"notes_{search_keyword}.json"
    file_path = os.path.join(SAVE_DIRECTORY, notes_file)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def find_function_declaration(file_path, line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(line_number - 2, -1, -1):
                if re.search(r'\b(public|private|protected|static|abstract)\b.*\b(class|interface|void|[a-zA-Z_][a-zA-Z0-9_]*)\b', lines[i]):
                    return lines[i].strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return "Unknown Function Declaration"

import os
import re

def search_keyword_in_repository(repo_path, keyword, file_type_include=None, file_type_exclude=None):

    # 対象拡張子と対象外拡張子をリストに変換
    include_exts = set(ext.strip().lower() for ext in (file_type_include or "").split(",") if ext.strip())
    exclude_exts = set(ext.strip().lower() for ext in (file_type_exclude or "").split(",") if ext.strip())
    
    # ノートの読み込み（既存の関数）
    notes = {f"{note['file_path']}:{note['line_number']}": note["user_notes"] for note in load_notes(keyword)}
    results = []

    # ファイルの再帰的検索
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()  # 拡張子を取得
            
            # include と exclude の条件をチェック
            if include_exts and file_ext not in include_exts:
                continue
            if file_ext in exclude_exts:
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_number, line in enumerate(f, start=1):
                        if re.search(keyword, line):
                            key = f"{file_path}:{line_number}"
                            results.append({
                                "file_path": file_path,
                                "line_number": line_number,
                                "function_declaration": find_function_declaration(file_path, line_number),
                                "line_content": line.strip(),
                                "user_notes": notes.get(key, "")
                            })
            except (UnicodeDecodeError, PermissionError):
                continue

    return results


def read_file_content_with_line_numbers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "\n".join(f"{i + 1}: {line}" for i, line in enumerate(lines))
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except PermissionError:
        return f"Permission denied: {file_path}"
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

@app.route('/')
def input_page():
    return render_template('input_v9.html')

@app.route('/grep', methods=['GET', 'POST'])
def grep():
    if request.method == 'POST':
        # POSTリクエストから results を取得
        if 'results' in request.form:
            results_encoded = request.form['results']
            results_data = json.loads(results_encoded) if results_encoded else []
        else:
            keyword = request.form['keyword']
            repo_path = request.form['repo_path']
            file_type_include = request.form['file_type_include']
            file_type_exclude = request.form['file_type_exclude']

            results_data = search_keyword_in_repository(repo_path, keyword, file_type_include, file_type_exclude)

            # テンプレートに渡す
            return render_template('results_v9.html', keyword=keyword, repo_path=repo_path, results=results_data, file_type_include=file_type_include, file_type_exclude=file_type_exclude)

    else:
        # GETリクエストで results を処理
        results_encoded = request.args.get("results", "")
        results_data = json.loads(results_encoded) if results_encoded else []

    return render_template('results_v9.html', results=results_data)

@app.route("/file")
def file_content():
    file_path = request.args.get("path")
    if not file_path:
        return "File path not provided."

    keyword = request.args.get("keyword")
    repo_path = request.args.get("repo_path")
    file_type_include = request.args.get("file_type_include")
    file_type_exclude = request.args.get("file_type_exclude")

    content = read_file_content_with_line_numbers(file_path)
    
    return render_template("result_file_content_v9.html", file_path=file_path, content=content, keyword=keyword, repo_path=repo_path, file_type_include=file_type_include, file_type_exclude=file_type_exclude)

@app.route('/save', methods=['POST'])
def save_notes():
    try:
        # フォームデータの取得
        keyword = request.form.get('keyword')
        repo_path = request.form.get('repo_path')
        results = json.loads(request.form.get('results'))  # JSON文字列を辞書形式に変換

        if not keyword or not repo_path or not results:
            return jsonify({"error": "Missing required data"}), 400

        # ファイル名を生成
        file_name = f"notes_{keyword}.json"
        file_path = os.path.join(SAVE_DIRECTORY, file_name)

        # 保存先ディレクトリが存在しない場合は作成
        os.makedirs(SAVE_DIRECTORY, exist_ok=True)

        # JSONファイルに書き込み（上書きまたは新規作成）
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        return jsonify({"message": "Notes saved successfully", "file_path": file_path}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
