"""
AI-Powered PR Reviewer — powered by Google Gemini (FREE)
---------------------------------------------------------
חינמי לחלוטין, בלי כרטיס אשראי.
"""

import os
import subprocess
import urllib.request
import urllib.error
import json

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]
PR_NUMBER      = os.environ["PR_NUMBER"]
REPO           = os.environ["REPO"]
BASE_SHA       = os.environ["BASE_SHA"]
HEAD_SHA       = os.environ["HEAD_SHA"]

GITHUB_API = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"


def get_diff() -> str:
    result = subprocess.run(
        ["git", "diff", BASE_SHA, HEAD_SHA, "--unified=5"],
        capture_output=True, text=True
    )
    diff = result.stdout.strip()
    return diff[:8000] if len(diff) > 8000 else diff


def review_with_gemini(diff: str) -> str:
    prompt = f"""You are a senior DevOps engineer reviewing a Pull Request.
Review the following git diff and provide a concise, helpful code review.

Focus on: security issues, Docker best practices, Kubernetes best practices,
Terraform best practices, GitHub Actions best practices, code quality.

Format your response as:
## 🤖 AI Code Review

**Summary:** (1-2 sentences)

**✅ Good:**
- (what's done well)

**⚠️ Suggestions:**
- (improvements)

**🔒 Security:**
- (security concerns or "No issues found")

---
Git diff:
```diff
{diff}
```"""

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]


def post_github_comment(body: str):
    payload = json.dumps({"body": body}).encode("utf-8")
    req = urllib.request.Request(
        GITHUB_API,
        data=payload,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST"
    )
    urllib.request.urlopen(req)
    print(f"✅ Review posted on PR #{PR_NUMBER}")


def main():
    print("🔍 Getting PR diff...")
    diff = get_diff()
    if not diff:
        print("No diff — skipping.")
        return

    print("🤖 Sending to Gemini...")
    review = review_with_gemini(diff)
    review += "\n\n---\n*🤖 Reviewed automatically by Gemini AI*"

    print("💬 Posting to GitHub...")
    post_github_comment(review)


if __name__ == "__main__":
    main()
