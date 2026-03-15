from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import io
from typing import List, Optional
from fpdf import FPDF

# Add src to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent import get_agent
from src.config import config
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="Digital Twin API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    # Allow all origins for now to prevent any CORS issues during deployment
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    mode: str = "normal"  # "normal" or "recruiter"

class UpdateContentRequest(BaseModel):
    content: str
    type: str  # "bio" or "projects"

class GenerateRequest(BaseModel):
    company_name: str
    job_role: str

# Global Agent Instance (Lazy loaded)
agent_executor = None

def get_agent_instance():
    global agent_executor
    if agent_executor is None:
        agent_executor = get_agent()
    return agent_executor

@app.get("/health")
def health_check():
    return {"status": "ok", "model": config.LLM_MODEL}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        agent = get_agent_instance()
        
        # Convert history format if needed
        chat_history = []
        for msg in request.history:
            if msg.get("role") == "user":
                chat_history.append(HumanMessage(content=msg.get("content")))
            elif msg.get("role") == "assistant":
                chat_history.append(AIMessage(content=msg.get("content")))

        # Contextual Prompt Injection based on Mode
        context_prefix = ""
        if request.mode == "recruiter":
            context_prefix = (
                "SYSTEM INSTRUCTION: You are in 'Recruiter Mode'. "
                "ACT AS A THIRD-PARTY PORTFOLIO MANAGER representing Ankit. "
                "Refer to Ankit in the THIRD PERSON (e.g., 'Ankit is', 'He has'). "
                "Be strictly professional, concise, and persuasive. "
                "Use the available tools (resume/projects) to back up claims. "
                "User Query: "
            )
        else:
            context_prefix = (
                "SYSTEM INSTRUCTION: You are in 'Normal/Assistant Mode'. "
                "Act as the friendly Digital Twin of Ankit (First Person 'I'). "
                "Be helpful with daily tasks, math, or searching. "
                "User Query: "
            )

        full_input = context_prefix + request.message

        response = agent.invoke(
            {"input": full_input, "chat_history": chat_history}
        )
        return {"response": response.get("output", "No response generated.")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-memory/file")
async def update_file_memory(file: UploadFile = File(...)):
    """
    Update the RAG knowledge base by uploading a new PDF Resume.
    Deletes all previous PDFs to ensure single source of truth.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # 1. Clear existing PDFs
    for f in os.listdir(data_dir):
        if f.lower().endswith('.pdf'):
            try:
                os.remove(os.path.join(data_dir, f))
            except Exception as e:
                print(f"Warning: Failed to delete old PDF {f}: {e}")

    # 2. Save the new file
    file_path = os.path.join(data_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Trigger RAG re-initialization
    try:
        from src.rag import reindex_knowledge_base
        reindex_knowledge_base()
        # Reset agent so it picks up the new RAG tool (though ReAct agent tools are usually fixed references, existing RAG tool logic re-reads DB or is stateless retriever)
        # Actually in this architecture, the chroma DB is queried by the tool. Rebuilding DB is enough.
        return {"message": "Memory updated successfully with new resume. Old data removed."}
    except Exception as e:
         return {"message": f"File saved, but re-indexing failed: {str(e)}"}

@app.post("/update-memory/text")
def update_text_memory(request: UpdateContentRequest):
    """
    Update simple text files like bio.md or projects.json
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    if request.type == "bio":
        path = os.path.join(data_dir, 'bio.md')
    elif request.type == "projects":
        path = os.path.join(data_dir, 'projects.json')
    else:
        raise HTTPException(status_code=400, detail="Invalid content type")
        
    try:
        with open(path, "w") as f:
            f.write(request.content)
        return {"message": f"{request.type} updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_pdf_from_text(text: str, title: str = "Document") -> bytes:
    """Simple PDF generator using FPDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    try:
        title_latin = title.encode('latin-1', 'replace').decode('latin-1')
    except:
        title_latin = title
    pdf.cell(0, 10, title_latin, 0, 1, 'C')
    pdf.ln(10)
    
    # Body
    pdf.set_font("Arial", '', 11)
    # Simple sanitization for FPDF (latin-1 only)
    try:
        # Replacements for common smart quotes/chars
        sanitized = text.replace('“', '"').replace('”', '"').replace("’", "'").replace("–", "-")
        content_latin = sanitized.encode('latin-1', 'replace').decode('latin-1')
    except:
        content_latin = text
        
    pdf.multi_cell(0, 6, content_latin)
    
    # Return bytes
    return pdf.output(dest='S').encode('latin-1')

@app.post("/generate/cover-letter")
async def generate_cover_letter(request: GenerateRequest):
    """Generates a tailored cover letter PDF"""
    try:
        agent = get_agent_instance()
        prompt = (
            f"TASK: Write a complete, professional cover letter for a position as {request.job_role} at {request.company_name}.\n"
            "STEP 1: You MUST first use the 'get_resume_info' tool to search for 'my full work experience, projects, and skills'.\n"
            "STEP 2: Based on the retrieved resume details, write the letter. Highlight specific projects or skills from the resume that match the job.\n"
            "STEP 3: Return ONLY the final body of the letter. Do not include placeholders like '[Insert Name]'. "
            "Do not output conversational filler like 'Here is the letter'. Just the letter text."
        )
        
        response = agent.invoke({"input": prompt})
        content = response.get("output", "Could not generate letter.")
        
        # Generate PDF
        pdf_bytes = generate_pdf_from_text(content, title=f"Cover Letter - {request.company_name}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cover_letter_{request.company_name}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/resume")
async def generate_resume_tailor(request: GenerateRequest):
    """Generates a tailored resume summary PDF"""
    try:
        agent = get_agent_instance()
        prompt = (
            f"TASK: Act as a professional resume writer. Tailor my resume summary and key skills for the role of {request.job_role} at {request.company_name}.\n"
            "STEP 1: You MUST use the 'get_resume_info' tool to retrieve my actual bio and experience.\n"
            "STEP 2: Rewrite my 'Professional Summary' to target this specific job, and list 5-7 'Key Skills' I actually possess that are relevant.\n"
            "STEP 3: Return the content in a clean format with headers 'Professional Summary' and 'Key Skills'. Do not support skills I do not have."
        )
        
        response = agent.invoke({"input": prompt})
        content = response.get("output", "Could not generate resume tailoring.")
        
        # Generate PDF
        pdf_bytes = generate_pdf_from_text(content, title=f"Tailored Resume Summary - {request.job_role}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=resume_summary_{request.company_name}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
