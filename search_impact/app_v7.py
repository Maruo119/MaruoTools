from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import re
import json
from urllib.parse import quote, unquote

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
    return render_template('input.html')

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
            results_data = search_keyword_in_repository(repo_path, keyword)

            return render_template('results_v7.html', results=results_data, keyword=keyword, repo_path=repo_path)
    else:
        # GETリクエストで results を処理
        results_encoded = request.args.get("results", "")
        results_data = json.loads(results_encoded) if results_encoded else []

    return render_template('results_v7.html', results=results_data)


@app.route("/file")
def file_content():
    file_path = request.args.get("path")
    if not file_path:
        return "File path not provided."

    content = read_file_content_with_line_numbers(file_path)
    results_encoded = request.args.get("results", "")
    results = json.loads(unquote(results_encoded)) if results_encoded else []

    return render_template("result_file_content_v7.html", file_path=file_path, content=content, results=results)

if __name__ == '__main__':
    app.run(debug=True)
