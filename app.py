# Add debug logging to trace request and error

from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Basic analysis function
def analyze_url(url):
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title tag'
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc['content'] if meta_desc else 'No meta description'

        issues = []
        suggestions = []
        score = 100

        if not soup.title:
            score -= 20
            issues.append("Missing <title> tag")
            suggestions.append("Add a relevant <title> tag to your homepage")

        if not meta_desc or len(meta_desc) < 50:
            score -= 15
            issues.append("Meta description too short or missing")
            suggestions.append("Write a compelling meta description of 150–160 characters")

        if not soup.find_all('h1'):
            score -= 10
            issues.append("Missing H1 tag")
            suggestions.append("Ensure there's at least one H1 tag on the page")

        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "title": title,
            "meta_description": meta_desc
        }

    except Exception as e:
        print(f"Error in analyze_url: {e}")
        return {
            "score": 0,
            "issues": [f"Error accessing site: {str(e)}"],
            "suggestions": ["Check if the website is publicly accessible."],
            "title": "N/A",
            "meta_description": "N/A"
        }

# Email sending function
def send_email(to_email, subject, body):
    try:
        print(f"Sending email to {to_email}...")
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('EMAIL_FROM')
        msg['To'] = to_email

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            smtp.send_message(msg)
        print("Email sent.")
    except Exception as e:
        print(f"Email send failed: {e}")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        name = data.get('name')
        email = data.get('email')
        print(f"Received form data: URL={url}, Name={name}, Email={email}")

        result = analyze_url(url)

        body = f"LLM Readiness Report for {url}\n\n" \
               f"Submitted by: {name} <{email}>\n\n" \
               f"Score: {result['score']}\n" \
               f"Title: {result['title']}\n" \
               f"Meta Description: {result['meta_description']}\n\n" \
               f"Issues:\n - " + "\n - ".join(result['issues']) + "\n\n" \
               f"Suggestions:\n - " + "\n - ".join(result['suggestions'])

        send_email("michael@mccabemedia.com", f"LLM Readiness Report: {url}", body)

        return jsonify(result)
    except Exception as e:
        print(f"Error in /analyze route: {e}")
        return jsonify({"error": "Failed to process request."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

