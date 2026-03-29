from flask import Flask, render_template_string, request, send_file
from bs4 import BeautifulSoup
import io
import re

app = Flask(__name__)

HTML_UI = """
<!doctype html>
<title>Clean Google Redirect Links</title>
<h2>Upload HTML file to clean Google redirect URLs</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file required>
  <input type=submit value="Upload & Clean">
</form>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return "No file uploaded", 400

        # Read HTML content
        content = uploaded_file.read()
        soup = BeautifulSoup(content, "html.parser")

        # Fix <a> tags
        for a in soup.find_all("a", href=True):
            href = a['href']

            # Only process Google redirect URLs
            if href.startswith("https://www.google.com/url?q="):
                # Remove prefix
                href = href.replace("https://www.google.com/url?q=", "", 1)
                # Remove everything after first & (tracking parameters)
                href = href.split("&")[0]
                a['href'] = href

        # Save cleaned HTML to in-memory file
        cleaned_html = io.BytesIO()
        cleaned_html.write(str(soup).encode('utf-8'))
        cleaned_html.seek(0)

        return send_file(
            cleaned_html,
            as_attachment=True,
            download_name=f"cleaned_{uploaded_file.filename}",
            mimetype="text/html"
        )

    return render_template_string(HTML_UI)

if __name__ == "__main__":
    app.run(debug=True)
