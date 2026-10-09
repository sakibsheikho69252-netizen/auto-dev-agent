import os
import random
import requests
import json

# ==========================================
# 1. API Keys & Configurations
# ==========================================
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ==========================================
# 2. AI Logic (Groq -> Gemini -> OpenAI Fallback)
# ==========================================
def generate_project_idea():
    prompt = "Generate a unique open-source Python or Web project idea. Return JSON with 'repo_name', 'description', 'filename', and 'code'."
    
    # Try Groq
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json=payload)
            if res.status_code == 200:
                data = json.loads(res.json()['choices'][0]['message']['content'])
                print("Generated idea using Groq AI")
                return data
        except Exception as e:
            print("Groq failed:", e)

    # Fallback Idea if API fails
    rand_id = random.randint(100, 999)
    return {
        "repo_name": f"auto-ai-tool-{rand_id}",
        "description": "An automated AI tool created by GitHub Action Agent.",
        "filename": "main.py",
        "code": "print('Hello, World! Created automatically by AI Bot.')\n"
    }

# ==========================================
# 3. GitHub Operations
# ==========================================
def get_username():
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code == 200:
        return res.json()["login"]
    else:
        print("Failed to fetch user profile:", res.text)
        return None

def create_repository(repo_name, description):
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": True
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 201:
        print(f"✅ Successfully created repository: {repo_name}")
        return True
    else:
        print(f"❌ Failed to create repository: {res.status_code} - {res.text}")
        return False

def add_file_to_repo(username, repo_name, filename, content):
    import base64
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{filename}"
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"Add {filename} via AI Bot",
        "content": encoded_content
    }
    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        print(f"✅ Created file {filename} in {repo_name}")
    else:
        print(f"❌ Failed to add file: {res.status_code} - {res.text}")

# ==========================================
# 4. Main Execution
# ==========================================
def main():
    username = get_username()
    if not username:
        print("Could not retrieve GitHub username. Stopping.")
        return

    idea = generate_project_idea()
    repo_name = idea.get("repo_name", f"auto-repo-{random.randint(100,999)}")
    description = idea.get("description", "Auto generated repo")
    filename = idea.get("filename", "main.py")
    code = idea.get("code", "print('Hello World')")

    if create_repository(repo_name, description):
        import time
        time.sleep(2)  # Wait for GitHub repo initialization
        add_file_to_repo(username, repo_name, filename, code)

if __name__ == "__main__":
    main()
