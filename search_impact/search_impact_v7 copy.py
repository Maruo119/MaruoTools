import os
import re
import json
from flask import Flask, render_template_string, request, jsonify

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
            if file.endswith(".java"):
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

app = Flask(__name__)

results_data = []
search_keyword = ""

@app.route("/report", methods=["GET", "POST"])
def report():
    global results_data, search_keyword
    if request.method == "POST":
        updates = request.json
        for update in updates:
            for result in results_data:
                if (result["file_path"] == update["file_path"] and
                        result["line_number"] == update["line_number"]):
                    result["user_notes"] = update["user_notes"]
        save_notes_to_file(results_data, search_keyword)
        return jsonify({"status": "success"})

    #repository_path = input("Enter the path to the repository: ").strip()
    search_keyword = input("Enter the keyword to search for: ").strip()
 
    repository_path = "/Users/yuta/Documents/examples-main".strip()
    #search_keyword = "map".strip()


    results_data = search_keyword_in_repository(repository_path, search_keyword)

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #f4f4f4;
                text-align: left;
                position: sticky;
                top: 60px;
                z-index: 2;
            }
            a {
                color: blue;
                text-decoration: underline;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                position: sticky;
                top: 0;
                width: 100%;
                background-color: #fff;
                border-bottom: 1px solid #ddd;
                padding: 10px;
                z-index: 3;
            }
            .content {
                margin-top: 60px;
            }
        </style>
        <script>
            async function saveNotes() {
                const notes = [];
                document.querySelectorAll('tr[data-file-path]').forEach(row => {
                    const filePath = row.getAttribute('data-file-path');
                    const lineNumber = row.getAttribute('data-line-number');
                    const userNotes = row.querySelector('textarea').value;
                    notes.push({ file_path: filePath, line_number: parseInt(lineNumber), user_notes: userNotes });
                });

                const response = await fetch("/report", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(notes)
                });

                const result = await response.json();
                alert(result.status);
            }
        </script>
    </head>
    <body>
        <div class="header">
            <h1>Search Results</h1>
            <button onclick="saveNotes()">Save Notes</button>
        </div>
        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>File Path</th>
                        <th>Line Number</th>
                        <th>Function Declaration</th>
                        <th>Line Content</th>
                        <th>User Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in results %}
                    <tr data-file-path="{{ result.file_path }}" data-line-number="{{ result.line_number }}">
                        <td>{{ loop.index }}</td>
                        <td><a href="/file?path={{ result.file_path }}" target="_blank">{{ result.file_path }}</a></td>
                        <td>{{ result.line_number }}</td>
                        <td>{{ result.function_declaration }}</td>
                        <td>{{ result.line_content }}</td>
                        <td><textarea>{{ result.user_notes }}</textarea></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results_data)

@app.route("/file")
def file_content():
    file_path = request.args.get("path")
    if not file_path:
        return "File path not provided."
    content = read_file_content_with_line_numbers(file_path)
    return f"<pre>{content}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
