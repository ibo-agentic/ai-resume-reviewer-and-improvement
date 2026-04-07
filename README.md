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

GROQ_API_KEY=your_key_here

Get a free API key at [console.groq.com](https://console.groq.com)

**4. Run the app**
```bash
python app.py
```

Open `http://127.0.0.1:7860` in your browser.

---

## How to use

1. Upload your resume as a PDF or paste the text
2. Enter the job role you are applying for (e.g. "Data Scientist")
3. Click **Analyze & Improve My Resume**
4. Read the feedback cards on the right
5. Use the follow-up box to ask further questions

---

## Features

- **Two AI tools** chained together — analysis output is passed as context to the improvement tool
- **Conversation memory** — remembers last 10 turns for follow-up questions
- **Clean UI** — results displayed as colored cards, raw text available for copying
- **PDF support** — extracts text automatically from uploaded PDFs

---

## Author

**Ibo** — [@ibo-agentic](https://github.com/ibo-agentic)