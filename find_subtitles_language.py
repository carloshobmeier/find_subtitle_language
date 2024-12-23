import os
from flask import Flask, render_template
import chardet

app = Flask(__name__)


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


def calculate_stats(subtitles):
    """Calculate statistics from subtitles."""
    total = len(subtitles)
    total_english = sum(1 for s in subtitles if s[0])  # First element indicates English
    total_portuguese = sum(1 for s in subtitles if s[1])  # Second element indicates Portuguese
    total_undefined = sum(1 for s in subtitles if s[2])  # Third element indicates Undefined
    total_errors = sum(1 for s in subtitles if s[3])  # Fourth element indicates Errors
    return {
        "total": total,
        "total_english": total_english,
        "total_portuguese": total_portuguese,
        "total_undefined": total_undefined,
        "total_errors": total_errors,
    }


@app.route('/')
def index():
    stats = calculate_stats(subtitles)
    return render_template('index.html', subtitles=subtitles, stats=stats, enumerate=enumerate)


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
