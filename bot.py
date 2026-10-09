import os
import time
import json
import requests
from github import Github

GH_TOKEN = os.getenv("GH_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

g = Github(GH_TOKEN)

def get_ai_response(prompt):
    """Fallback System: Groq -> Gemini -> OpenAI"""
    
    # ১. Groq API
    if GROQ_KEY:
        try:
            print("Trying Groq API...")
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            res = requests.post(url, json=data, headers=headers).json()
            return res['choices'][0]['message']['content']
        except Exception as e:
            print(f"Groq failed: {e}")

    # ২. Gemini API
    if GEMINI_KEY:
        try:
            print("Trying Gemini API...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=data, headers=headers).json()
            return res['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini failed: {e}")

    # ৩. OpenAI API
    if OPENAI_KEY:
        try:
            print("Trying OpenAI API...")
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
            res = requests.post(url, json=data, headers=headers).json()
            return res['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenAI failed: {e}")

    return None

def run_automation():
    print("Analyzing software trends with Multi-AI...")
    prompt = """Generate a JSON object for a useful Python open-source script.
    Return ONLY JSON in this format:
    {
      "repo_name": "auto-tool",
      "description": "An automated AI generated utility",
      "filename": "main.py",
      "code": "print('Automated Bot Execution Successful!')"
    }
    """
    
    content = get_ai_response(prompt)
    if not content:
        print("All AI APIs failed!")
        return

    try:
        idea = json.loads(content[content.find('{'):content.rfind('}')+1])
        user = g.get_user()
        repo_name = f"{idea['repo_name']}-{int(time.time())}"
        print(f"Creating Repo: {repo_name}")
        
        repo = user.create_repo(name=repo_name, description=idea['description'])
        repo.create_file("README.md", "Init", f"# {repo_name}\n\n{idea['description']}")
        repo.create_file(idea['filename'], "Add code", idea['code'])
        
        print(f"Live on GitHub: {repo.html_url}")
    except Exception as e:
        print(f"Error creating GitHub Repo: {e}")

if __name__ == "__main__":
    run_automation()
