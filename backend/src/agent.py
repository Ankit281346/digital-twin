import os
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

from src.config import config

try:
    from src.rag import initialize_rag
except ImportError:
    try:
        from .rag import initialize_rag
    except ImportError:
        pass # Will be handled in get_agent

load_dotenv()

@tool
def calculator(expression: str) -> str:
    """Calculates a mathematical expression. Input should be a valid python expression string."""
    try:
        allowed_names = {"abs": abs, "round": round, "min": min, "max": max, "pow": pow}
        return str(eval(expression, {"__builtins__": None}, allowed_names))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Useful for when you need to answer current events or general questions about the world."""
    if DDGS is None:
        return "Search functionality is currently unavailable (library missing)."
    
    try:
        with DDGS() as ddgs:
            try:
                results = [r for r in ddgs.text(query, max_results=3, backend="html")]
            except Exception:
                results = []
            
            if not results:
                try:
                    results = [r for r in ddgs.text(query, max_results=3, backend="api")]
                except Exception:
                    pass

            if results:
                # Truncate each snippet to avoid blowing Groq's token/minute rate limit
                formatted = "\n\n".join([
                    f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body'][:300]}"
                    for r in results
                ])
                # Hard cap on total search output to stay within token budget
                return formatted[:1500]
            return "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_agent():
    api_key = config.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    llm = ChatGroq(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        groq_api_key=api_key
    )
    
    try:
        from src.rag import initialize_rag
        resume_tool = initialize_rag()
        print("RAG Tool initialized")
    except Exception as e:
        print(f"Warning: RAG Tool failed to initialize: {e}")
        resume_tool = None

    # Use the wrapped tool
    tools = [web_search, calculator]
    if resume_tool:
        tools.append(resume_tool)

    # ReAct Prompt
    template = '''You are the Digital Twin of Ankit, a highly skilled AI Engineer.
Your goal is to represent him authentically to recruiters and include your personality.

CORE GUIDELINES:
1. **Be Professional yet Personable**: Use a tone that is confident and technically precise.
2. **Retrieve Information**: Your primary source of truth is the resume/knowledge base (use `get_resume_info`). Never hallucinates personal details.
3. **Showcase Projects**: Highlight technical skills and specific achievements from your knowledge base.
4. **Interview Mode**: If asked an interview question, use the STAR format (Situation, Task, Action, Result) based on resume data.

TOOLS AVAILABLE:
{tools}

To use a tool, please use the following format:

Question: the input question you must answer
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

If you do NOT need to use a tool, you MUST use the following format:

Question: the input question you must answer
Thought: Do I need to use a tool? No
Final Answer: [your response here]

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

    prompt = PromptTemplate.from_template(template)

    agent = create_react_agent(llm, tools, prompt)
    # Set verbose to based on config
    return AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=config.DEBUG_MODE, 
        handle_parsing_errors=True,
        max_iterations=5,
        max_execution_time=28,  # Stay under Render's 30s connection limit
    )
