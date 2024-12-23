import os
from flask import Flask, render_template_string
import chardet

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Subtitle Language Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
    </style>
</head>
<body>
    <h1>Subtitle Files and Detected Languages</h1>
    <table>
        <tr>
            <th>#</th>
            <th>Inglês</th>
            <th>Português</th>
            <th>Indeterminado</th>
            <th>Erro</th>
        </tr>
        {% for idx, (english, portuguese, undefined, error) in enumerate(subtitles, start=1) %}
        <tr>
            <td>{{ idx }}</td>
            <td>{{ english }}</td>
            <td>{{ portuguese }}</td>
            <td>{{ undefined }}</td>
            <td>{{ error }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'  # Fallback to utf-8 if detection fails

def detect_language_logic(file_path):
    """Detect language based on the presence of specific words."""
    try:
        # Detect encoding and open the file accordingly
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read().lower()
        
        # Get the filename without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # First check for Portuguese
        if "você" in content:
            return "", file_name, "", ""
        
        # If not Portuguese, check for English
        if "you" in content:
            return file_name, "", "", ""
        
        # If neither Portuguese nor English
        return "", "", file_name, ""
    
    except Exception as e:
        return "", "", "", f"{os.path.basename(file_path)}: {str(e)}"

def get_subtitles_languages(directory_path):
    """Gets the list of subtitles and their detected languages."""
    subtitles = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.srt'):
            file_path = os.path.join(directory_path, file_name)
            english, portuguese, undefined, error = detect_language_logic(file_path)
            subtitles.append((english, portuguese, undefined, error))
    return subtitles

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, subtitles=subtitles, enumerate=enumerate)


if __name__ == '__main__':
    # Prompt user for directory path before starting the server
    directory = input("Enter the directory path containing .srt files: ").strip()
    if not os.path.isdir(directory):
        print("Invalid directory. Please restart and provide a valid path.")
        exit(1)
    
    subtitles = get_subtitles_languages(directory)
    print("Starting the server...")
    print("Visit http://127.0.0.1:5000 in your browser.")
    app.run(debug=False)
