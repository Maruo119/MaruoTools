import os
import re
from flask import Flask, render_template_string, request

def find_function_declaration(file_path, line_number):
    """
    Searches upwards in a file from a specific line number to find the enclosing function declaration.
    For Java files, it looks for function definitions such as those containing 'public', 'private', 'protected', or 'static'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(line_number - 2, -1, -1):  # Search backwards from the line above the hit
                if re.search(r'\b(public|private|protected|static|abstract)\b.*\b(class|interface|void|[a-zA-Z_][a-zA-Z0-9_]*)\b', lines[i]):
                    return lines[i].strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return "Unknown Function Declaration"

def search_keyword_in_repository(repo_path, keyword):
    results = []

    # Walk through the repository
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".java"):  # Process only Java files
                file_path = os.path.join(root, file)

                # Only process text files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_number, line in enumerate(f, start=1):
                            if re.search(keyword, line):
                                function_declaration = find_function_declaration(file_path, line_number)
                                results.append({
                                    "file_path": file_path,
                                    "line_number": line_number,
                                    "function_declaration": function_declaration,
                                    "line_content": line.strip()
                                })
                except (UnicodeDecodeError, PermissionError):
                    # Skip non-text files or files without read permissions
                    continue
    return results

def read_file_content_with_line_numbers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(f"{i + 1:4}: {line}" for i, line in enumerate(lines))
    except Exception as e:
        return f"Error reading file {file_path}: {e}"

app = Flask(__name__)

@app.route("/report")
def report():
    repository_path = "/Users/yuta/Documents/examples-main".strip()
    search_keyword = "draw".strip()


    results = search_keyword_in_repository(repository_path, search_keyword)

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results</title>
        <style>
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
            }
            a {
                color: blue;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Search Results</h1>
        <table>
            <thead>
                <tr>
                    <th>File Path</th>
                    <th>Line Number</th>
                    <th>Function Declaration</th>
                    <th>Line Content</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                <tr>
                    <td><a href="/file?path={{ result.file_path }}" target="_blank">{{ result.file_path }}</a></td>
                    <td>{{ result.line_number }}</td>
                    <td>{{ result.function_declaration }}</td>
                    <td>{{ result.line_content }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results)

@app.route("/file")
def file_content():
    file_path = request.args.get("path")
    if not file_path:
        return "File path not provided."
    content = read_file_content_with_line_numbers(file_path)
    return f"<pre>{content}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
