import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone

def main():
    repo = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    
    name = os.getenv("APPLICATION_NAME")
    email = os.getenv("APPLICATION_EMAIL")
    resume_link = os.getenv("APPLICATION_RESUME_LINK")
    signing_secret = os.getenv("B12_SIGNING_SECRET")

    if not all([name, email, resume_link, signing_secret, repo, run_id]):
        print("Error: Missing required environment variables.")
        return


    repository_link = f"{server_url}/{repo}"
    action_run_link = f"{server_url}/{repo}/actions/runs/{run_id}"
    
    timestamp = datetime.now().isoformat()
    
    payload = {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "resume_link": resume_link,
        "repository_link": repository_link,
        "action_run_link": action_run_link
    }

    json_body = json.dumps(
        payload, 
        sort_keys=True, 
        separators=(',', ':'), 
        ensure_ascii=False
    )
    body_bytes = json_body.encode('utf-8')

    secret_bytes = signing_secret.encode('utf-8')
    signature_hash = hmac.new(
        secret_bytes, 
        body_bytes, 
        hashlib.sha256
    ).hexdigest()
    
    signature_header = f"sha256={signature_hash}"

   
    url = "https://b12.io/apply/submission"
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": signature_header
    }

    print(f"Submitting")
    try:
        response = requests.post(url, data=body_bytes, headers=headers)
        response.raise_for_status()
        print(f"Success! Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        exit(1)

if __name__ == "__main__":
    main()
