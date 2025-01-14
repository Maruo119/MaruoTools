from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import re
import json
import subprocess

app = Flask(__name__)

# Grep結果を一時的に保存する辞書
grep_results = {}

def load_notes(search_keyword):
    notes_file = f"user_notes_{search_keyword}.json"
    if os.path.exists(notes_file):
        with open(notes_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_notes_to_file(notes, search_keyword):
    notes_file = f"user_notes_{search_keyword}.json"
    with open(notes_file, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)

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

def search_keyword_in_repository(repo_path, keyword):
    notes = {f"{note['file_path']}:{note['line_number']}": note["user_notes"] for note in load_notes(keyword)}
    results = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
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

@app.route('/')
def input_page():
    """キー入力画面"""
    return render_template('input.html')

@app.route('/grep', methods=['POST'])
def grep():
    keyword = request.form['keyword']
    repo_path = request.form['repo_path']

    results_data = search_keyword_in_repository(repo_path, keyword)

    print("Results Data:", results_data)

    return render_template('results_v3.html', results=results_data)

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
