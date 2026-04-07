# ============================================================
# AI RESUME REVIEWER & IMPROVER
# Built with Groq AI + Gradio
# ============================================================

import os
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

load_dotenv()
client = Groq()

# ============================================================
# CONVERSATION MEMORY
# ============================================================
conversation_history = []

def add_to_memory(role, content):
    conversation_history.append({"role": role, "content": content})

def get_conversation_history():
    return conversation_history[-10:]

# ============================================================
# PDF READER
# ============================================================
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# ============================================================
# TOOL 1: ANALYZE RESUME
# ============================================================
def analyze_resume(resume_text, job_role):
    prompt = f"""
    You are a strict but helpful HR manager with 15 years experience.
    Analyze this resume for a {job_role} position.
    Resume: {resume_text}
    
    Find and report:
    1. MISSING KEYWORDS - important keywords for {job_role} that are missing
    2. WEAK SECTIONS - sections that are too vague or weak
    3. FORMATTING ISSUES - any formatting problems
    4. MISSING SECTIONS - important sections not included
    5. OVERALL SCORE - score out of 10 with reason
    
    Be specific and honest. Write like a human reviewer.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an experienced HR professional and career coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content

# ============================================================
# TOOL 2: SUGGEST IMPROVEMENTS
# ============================================================
def suggest_improvements(resume_text, job_role, analysis):
    prompt = f"""
    You are a professional CV writer who helped 500+ people land dream jobs.
    Original Resume: {resume_text}
    Job Role: {job_role}
    Previous Analysis: {analysis}
    
    Provide:
    1. REWRITE THE SUMMARY - powerful 3-line professional summary
    2. IMPROVE BULLET POINTS - rewrite 3 weak bullet points with numbers and action verbs
    3. ADD MISSING KEYWORDS - 10 keywords to add and where
    4. SUGGESTED SKILLS SECTION - improved skills section
    5. FINAL TIPS - 3 specific tips to get noticed
    
    Write naturally. Be encouraging but honest.
    """
    messages = [{"role": "system", "content": "You are a professional CV writer and career coach."}]
    messages.extend(get_conversation_history())
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=2000
    )
    result = response.choices[0].message.content
    add_to_memory("user", f"Reviewed resume for {job_role}")
    add_to_memory("assistant", result[:500])
    return result

# ============================================================
# MAIN AGENT
# ============================================================
def run_resume_agent(pdf_file, resume_text, job_role, progress=gr.Progress()):
    final_resume_text = ""
    
    if pdf_file is not None:
        progress(0.1, desc="📖 Reading your PDF...")
        final_resume_text = extract_text_from_pdf(pdf_file)
        if final_resume_text.startswith("Error"):
            return format_error(final_resume_text), ""
    elif resume_text and len(resume_text) > 50:
        final_resume_text = resume_text
    else:
        return format_error("Please upload a PDF or paste your resume text!"), ""
    
    if not job_role:
        return format_error("Please enter the job role you are applying for!"), ""
    
    try:
        progress(0.3, desc="🔍 Analyzing your resume...")
        analysis = analyze_resume(final_resume_text, job_role)
        
        progress(0.6, desc="✨ Writing improvements...")
        improvements = suggest_improvements(final_resume_text, job_role, analysis)
        
        progress(0.9, desc="🎨 Preparing report...")
        analysis = analysis.replace("**", "")
        improvements = improvements.replace("**", "")
        html_result = format_results(analysis, improvements, job_role)
        
        progress(1.0, desc="✅ Done!")
        return html_result, f"ANALYSIS:\n{analysis}\n\nIMPROVEMENTS:\n{improvements}"
    
    except Exception as e:
        return format_error(str(e)), ""

# ============================================================
# FOLLOW UP
# ============================================================
def followup_agent(followup_question, progress=gr.Progress()):
    if not followup_question:
        return format_error("Please type a follow-up question!")
    if not conversation_history:
        return format_error("Please analyze a resume first!")
    
    progress(0.3, desc="🧠 Thinking...")
    messages = [{"role": "system", "content": "You are a professional CV writer with memory of previous reviews."}]
    messages.extend(get_conversation_history())
    messages.append({"role": "user", "content": followup_question})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )
    result = response.choices[0].message.content.replace("**", "")
    add_to_memory("user", followup_question)
    add_to_memory("assistant", result[:500])
    progress(1.0, desc="Done!")
    return format_followup(result)

# ============================================================
# HTML FORMATTERS
# ============================================================
def format_error(msg):
    return f"""
    <div style="
        background: #1c0a0a;
        border: 1px solid #7f1d1d;
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 20px 24px;
        color: #fca5a5;
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        margin: 10px 0;
    ">⚠️ {msg}</div>
    """

def format_results(analysis, improvements, job_role):
    return f"""
    <style>
        .rc {{ font-family: 'Segoe UI', sans-serif; padding: 4px; }}
        .hero {{
            background: linear-gradient(135deg, #0f172a, #1e3a5f, #1d4ed8);
            border-radius: 20px;
            padding: 32px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
        }}
        .hero-emoji {{ font-size: 56px; margin-bottom: 12px; }}
        .hero-title {{
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, #93c5fd, #c4b5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        .hero-sub {{ color: #94a3b8; font-size: 15px; margin-bottom: 16px; }}
        .badges {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
        .badge {{
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        .b1 {{ background: #1e3a5f; color: #60a5fa; }}
        .b2 {{ background: #14532d; color: #4ade80; }}
        .b3 {{ background: #2d1b69; color: #a78bfa; }}
        .card {{
            background: #0f172a;
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 20px;
            border: 1px solid #1e293b;
            position: relative;
            overflow: hidden;
        }}
        .card::after {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 5px; height: 100%;
            background: linear-gradient(180deg, #3b82f6, #8b5cf6);
        }}
        .card.green::after {{
            background: linear-gradient(180deg, #22c55e, #16a34a);
        }}
        .card-head {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #1e293b;
        }}
        .card-icon {{
            width: 44px; height: 44px;
            border-radius: 12px;
            display: flex; align-items: center;
            justify-content: center;
            font-size: 22px;
            background: #1e293b;
            flex-shrink: 0;
        }}
        .card-title {{
            font-size: 18px;
            font-weight: 700;
            color: #60a5fa;
        }}
        .card-title.green {{ color: #4ade80; }}
        .card-desc {{ color: #64748b; font-size: 13px; margin-top: 2px; }}
        .card-body {{
            color: #cbd5e1;
            font-size: 14px;
            line-height: 2;
            white-space: pre-wrap;
        }}
    </style>
    <div class="rc">
        <div class="hero">
            <div class="hero-emoji">🎯</div>
            <div class="hero-title">Your Resume Review is Ready!</div>
            <div class="hero-sub">Personalized feedback powered by AI — built just for you</div>
            <div class="badges">
                <span class="badge b1">🎯 Role: {job_role}</span>
                <span class="badge b2">✅ Analysis Complete</span>
                <span class="badge b3">✨ Improvements Ready</span>
            </div>
        </div>

        <div class="card">
            <div class="card-head">
                <div class="card-icon">🔍</div>
                <div>
                    <div class="card-title">What Needs Work</div>
                    <div class="card-desc">Honest analysis of your current resume</div>
                </div>
            </div>
            <div class="card-body">{analysis}</div>
        </div>

        <div class="card green">
            <div class="card-head">
                <div class="card-icon">✨</div>
                <div>
                    <div class="card-title green">Rewritten & Improved</div>
                    <div class="card-desc">AI-powered improvements ready to copy</div>
                </div>
            </div>
            <div class="card-body">{improvements}</div>
        </div>
    </div>
    """

def format_followup(result):
    return f"""
    <div style="
        font-family: 'Segoe UI', sans-serif;
        background: #0f172a;
        border-radius: 20px;
        padding: 28px;
        border: 1px solid #2d1b69;
        position: relative;
        overflow: hidden;
        margin-top: 8px;
    ">
        <div style="
            position: absolute;
            top: 0; left: 0;
            width: 5px; height: 100%;
            background: linear-gradient(180deg, #7c3aed, #a78bfa);
        "></div>
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 14px;
            border-bottom: 1px solid #1e293b;
        ">
            <div style="
                width: 44px; height: 44px;
                background: #2d1b69;
                border-radius: 12px;
                display: flex; align-items: center;
                justify-content: center;
                font-size: 22px;
            ">🧠</div>
            <div>
                <div style="color: #a78bfa; font-size: 18px; font-weight: 700;">Follow-up Response</div>
                <div style="color: #64748b; font-size: 13px;">Based on your previous resume analysis</div>
            </div>
        </div>
        <div style="color: #cbd5e1; font-size: 14px; line-height: 2; white-space: pre-wrap;">{result}</div>
    </div>
    """

# ============================================================
# GRADIO UI
# ============================================================
custom_css = """
    .gradio-container { max-width: 1300px !important; margin: 0 auto !important; }
    footer { display: none !important; }
    button.primary { 
        background: linear-gradient(135deg, #1d4ed8, #7c3aed) !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
"""

with gr.Blocks(title="AI Resume Reviewer", css=custom_css) as demo:

    # HERO HEADER
    gr.HTML("""
    <div style="
        text-align: center;
        padding: 50px 20px 30px;
        background: linear-gradient(135deg, #0f172a 0%, #1a1a3e 50%, #0f172a 100%);
        border-radius: 24px;
        margin-bottom: 28px;
        border: 1px solid #1e293b;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: -50px; left: 50%;
            transform: translateX(-50%);
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
            pointer-events: none;
        "></div>
        
        <div style="font-size: 60px; margin-bottom: 16px;">📄</div>
        
        <h1 style="
            color: white;
            font-size: 36px;
            font-weight: 800;
            margin: 0 0 10px 0;
            background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">AI Resume Reviewer & Improver</h1>
        
        <p style="color: #94a3b8; font-size: 17px; margin: 0 0 24px 0; max-width: 500px; margin-left: auto; margin-right: auto;">
            Upload your CV and get instant AI feedback to land your dream job
        </p>
        
        <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <div style="background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.3); color: #60a5fa; padding: 8px 20px; border-radius: 24px; font-size: 14px; font-weight: 600;">🔍 Deep Analysis</div>
            <div style="background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; padding: 8px 20px; border-radius: 24px; font-size: 14px; font-weight: 600;">✨ AI Rewriting</div>
            <div style="background: rgba(167,139,250,0.15); border: 1px solid rgba(167,139,250,0.3); color: #a78bfa; padding: 8px 20px; border-radius: 24px; font-size: 14px; font-weight: 600;">🧠 Memory Active</div>
            <div style="background: rgba(251,146,60,0.15); border: 1px solid rgba(251,146,60,0.3); color: #fb923c; padding: 8px 20px; border-radius: 24px; font-size: 14px; font-weight: 600;">📎 PDF Upload</div>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):

        # LEFT COLUMN — inputs
        with gr.Column(scale=4):

            gr.HTML("""<div style="
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border-radius: 16px; padding: 20px 24px;
                border: 1px solid #1e3a5f; margin-bottom: 12px;">
                <div style="color: #60a5fa; font-size: 16px; font-weight: 700;">📎 Step 1 — Upload Resume PDF</div>
                <div style="color: #475569; font-size: 13px; margin-top: 4px;">Drag and drop or click to browse</div>
            </div>""")

            pdf_upload = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath"
            )

            gr.HTML("""<div style="
                text-align: center; color: #334155;
                font-size: 14px; padding: 10px 0;
                display: flex; align-items: center; gap: 10px;">
                <div style="flex:1; height:1px; background:#1e293b;"></div>
                <span>OR paste text</span>
                <div style="flex:1; height:1px; background:#1e293b;"></div>
            </div>""")

            resume_input = gr.Textbox(
                label="📝 Resume Text",
                placeholder="Paste your resume here...",
                lines=6
            )

            gr.HTML("""<div style="
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border-radius: 16px; padding: 20px 24px;
                border: 1px solid #1e3a5f; margin: 12px 0;">
                <div style="color: #60a5fa; font-size: 16px; font-weight: 700;">🎯 Step 2 — Target Job Role</div>
                <div style="color: #475569; font-size: 13px; margin-top: 4px;">What position are you applying for?</div>
            </div>""")

            job_role_input = gr.Textbox(
                label="Job Role",
                placeholder="e.g. Python Developer, Data Scientist...",
                lines=1
            )

            gr.Examples(
                examples=[["Python Developer"], ["Data Scientist"],
                          ["Machine Learning Engineer"], ["Frontend Developer"], ["Product Manager"]],
                inputs=job_role_input,
                label="Quick select"
            )

            analyze_btn = gr.Button(
                "🚀  Analyze & Improve My Resume",
                variant="primary", size="lg"
            )

            gr.HTML("""<div style="
                background: linear-gradient(135deg, #0f0a1e, #1a1240);
                border-radius: 16px; padding: 20px 24px;
                border: 1px solid #2d1b69; margin-top: 20px;">
                <div style="color: #a78bfa; font-size: 16px; font-weight: 700; margin-bottom: 10px;">🧠 Follow-up Questions</div>
                <div style="color: #475569; font-size: 13px; line-height: 1.8;">
                    After analysis, try asking:<br>
                    • "Make the summary more aggressive"<br>
                    • "Add more Python keywords"<br>
                    • "Rewrite for a senior role"
                </div>
            </div>""")

            followup_input = gr.Textbox(
                label="💬 Ask a Follow-up",
                placeholder="Ask anything about your resume...",
                lines=2
            )

            followup_btn = gr.Button("💬 Ask Follow-up", variant="secondary", size="lg")

        # RIGHT COLUMN — outputs
        with gr.Column(scale=6):
            gr.HTML("""<div style="
                color: #475569; font-size: 13px;
                text-align: center; padding: 8px 0 16px;
            ">Results will appear here after analysis</div>""")
            
            html_output = gr.HTML()
            followup_output = gr.HTML()

            gr.HTML("<br>")
            
            with gr.Accordion("📋 Copy Raw Text Output", open=False):
                raw_output = gr.Textbox(
                    label="Raw Text",
                    lines=12,
                    placeholder="Raw output will appear here for easy copying..."
                )

    # Footer
    gr.HTML("""
    <div style="
        text-align: center; padding: 20px;
        color: #334155; font-size: 13px;
        border-top: 1px solid #1e293b;
        margin-top: 16px;
    ">
        🤖 Built with <strong style="color:#60a5fa">Groq AI</strong> + 
        <strong style="color:#a78bfa">Gradio</strong> &nbsp;|&nbsp;
        Tools: <code style="color:#4ade80">analyze_resume</code> → 
        <code style="color:#4ade80">suggest_improvements</code> &nbsp;|&nbsp;
        Model: <strong style="color:#fb923c">Llama 3.3 70B</strong>
    </div>
    """)

    analyze_btn.click(
        fn=run_resume_agent,
        inputs=[pdf_upload, resume_input, job_role_input],
        outputs=[html_output, raw_output],
        show_progress=True
    )

    followup_btn.click(
        fn=followup_agent,
        inputs=followup_input,
        outputs=followup_output,
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch(share=False)