# Digital Twin: AI Portfolio & Assistant

An interactive AI application that serves as your 24/7 personal assistant and professional portfolio manager. It mimics your personality to chat with recruiters, showcases your projects dynamically, and automates job outreach with tailored cold emails.

A Next.js + FastAPI application that acts as your personalized "Digital Twin". It serves two main purposes:
1.  **Assistant Mode**: A helpful AI that can answer questions, use tools (Calculator, Web Search), and assist with daily tasks.
2.  **Recruiter Mode**: A professional portfolio manager that answers questions about your experience, generates cover letters, and acts as your agent for job opportunities.


## Features

-   **Dual Mode Engine**: Toggle between first-person "Assistant" and third-person "Recruiter" personas.
-   **RAG (Retrieval Augmented Generation)**: Upload your PDF resume to give the AI accurate knowledge about your history.
-   **Multimodal Voice**: Talk to your twin with microphone input and hear responses read aloud.
-   **Generator Tools**: Create tailored cold emails and resume summaries instantly.
-   **Modern UI**: Sleek, clean interface built with Next.js and Tailwind CSS.

## Tech Stack

-   **Frontend**: Next.js 14, Tailwind CSS, Lucide Icons.
-   **Backend**: Python, FastAPI, LangChain.
-   **AI**: Groq (Llama 3/Mixtral), ChromaDB (Vector Store).
-   **Tools**: DuckDuckGo Search, PDF Parsing, FPDF.

## Quick Start

### Prerequisites
-   Node.js & npm
-   Python 3.10+
-   A [Groq API Key](https://console.groq.com/)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run server
python server.py
```
Backend runs at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

### 3. Initialize Memory
1.  Place your resume PDF in `backend/data/` (e.g., `resume.pdf`).
2.  Restart the backend server to index it.
3.  The AI is now ready to answer questions about you!

## License
MIT
