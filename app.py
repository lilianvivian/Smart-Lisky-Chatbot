import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
app = Flask(__name__)
CORS(app)

# 2. Configure API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Use the Flash model
model = genai.GenerativeModel('models/gemini-2.5-flash-lite-preview-09-2025')
# 3. TARGET URL (Layer 1)
TARGET_URL = "https://liskybot.co.ke"

# 4. INTERNAL MANUAL (Layer 2)
# Add things here that are NOT on the website, but you want the bot to know.
INTERNAL_KNOWLEDGE = """
PRICING GUIDELINES:
- Basic Websites start at KES 15,000.
- Mobile Apps start at KES 40,000.
- AI Agents require a custom quote.
- Consultation is FREE for the first 30 minutes.

CONTACTS:
- Urgent Support: +254 768 951 560 (Do not give this unless asked for urgent help).
- Office Hours: Mon-Fri, 8am - 5pm.
"""

def scrape_website(url):
    print(f"--- 📡 READING {url} ---")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Website unreachable."
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        return text[:15000] 
    except Exception as e:
        return "Website unreachable."

# Load Website Data ONCE
website_data = scrape_website(TARGET_URL)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    # 5. THE HYBRID PROMPT (Layer 3)
    prompt = f"""
    You are the AI assistant for Liskybot Company.
    
    Your Knowledge Sources:
    1. **Website Data:** {website_data}
    2. **Internal Manual:** {INTERNAL_KNOWLEDGE}
    3. **General AI Knowledge:** Tech, Coding, and Business.
    
    USER QUESTION: {user_message}
    
    STRICT INSTRUCTIONS:
    1. **NO REPETITION:** NEVER start your response with "I am Lisky" or "As Lisky" or "Lisky here". Just answer the question directly.
    2. **IDENTITY:** If explicitly asked "Who are you?", THEN you can say "I am Lisky, your Global Tech Assistant."
    3. **LOCATION:** If asked location, say "We are HQ'd in Juja, Kenya, but serve clients globally."
    4. **TONE:** Professional, concise, and human-like.
    5. **BOUNDARIES:** Decline questions about cooking/politics.
    """
   

    
    
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "My brain is rebooting. Please try again."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)