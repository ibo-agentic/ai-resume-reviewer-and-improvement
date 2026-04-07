# AI Resume Reviewer & Improver

An AI-powered resume reviewer built with Groq AI and Gradio. Upload your resume, enter the job role you're applying for, and get instant feedback and rewritten content.

---

## What it does

- Analyzes your resume for missing keywords, weak sections, formatting issues, and gives a score out of 10
- Rewrites your summary, bullet points, and suggests keywords to add
- Supports PDF upload or plain text paste
- Follow-up chat — ask things like "make the summary more aggressive" and it remembers context
- Conversation memory across the session

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Groq API (Llama 3.3 70B) | LLM backend |
| Gradio | Web UI |
| PyPDF2 | PDF text extraction |
| Python | Core logic |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/ibo-agentic/ai-resume-reviewer-and-improvement.git
cd ai-resume-reviewer-and-improvement
```

**2. Install dependencies**
```bash
pip install groq gradio python-dotenv PyPDF2
```

**3. Add your Groq API key**

Create a `.env` file in the root folder: