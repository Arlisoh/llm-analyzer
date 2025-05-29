from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

def analyze_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else 'No title tag'
        meta = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta['content'].strip() if meta and 'content' in meta.attrs else 'No meta description'

        issues = []
        suggestions = []
        score = 100

        if not soup.title:
            score -= 20
            issues.append("Missing <title> tag")
            suggestions.append("Add a relevant <title> tag to your homepage")

        if not meta or len(meta_desc) < 50:
            score -= 15
            issues.append("Meta description too short or missing")
            suggestions.append("Write a compelling meta description of 150–160 characters")

        if not soup.find_all('h1'):
            score -= 10
            issues.append("Missing H1 tag")
            suggestions.append("Ensure there's at least one H1 tag on the page")

        return {
            "score": score,
            "title": title,
            "meta_description": meta_desc,
            "issues": issues,
            "suggestions": suggestions
        }

    except Exception as e:
        return {
            "score": 0,
            "issues": [f"Error accessing site: {str(e)}"],
            "suggestions": ["Check if the website is publicly accessible."],
            "title": "N/A",
            "meta_description": "N/A"
        }

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        name = data.get('name')
        email = data.get('email')

        result = analyze_url(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
