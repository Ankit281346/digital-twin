from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.status import Status
from rich.theme import Theme

# Custom theme for Claude-like aesthetic
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "tool": "bold rapid_blink blue",
    "tool_output": "dim italic white",
    "thought": "dim green",
    "user": "bold yellow",
    "ai": "bold white",
})

console = Console(theme=custom_theme)

class RichCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out using Rich."""
    
    def __init__(self, console: Console):
        self.console = console
        self.status: Optional[Status] = None

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        # self.status = self.console.status("[bold green]Thinking...", spinner="dots")
        # self.status.start()
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        # if self.status:
        #     self.status.stop()
        pass

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        if self.status:
            self.status.stop()
            
        tool_name = serialized.get("name")
        self.console.print(f"[tool]🛠️  Action: {tool_name}[/tool]")
        self.console.print(f"[dim]   Input: {input_str}[/dim]")
        
        # self.status = self.console.status(f"[bold blue]Running {tool_name}...", spinner="dots")
        # self.status.start()

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        # if self.status:
        #     self.status.stop()
            
        clean_output = str(output)[:200] + "..." if len(str(output)) > 200 else str(output)
        self.console.print(f"[tool_output]   Output: {clean_output}[/tool_output]")
        
        # self.status = self.console.status("[bold green]Thinking...", spinner="dots")
        # self.status.start()

    def on_agent_action(self, action: Any, **kwargs: Any) -> Any:
        """Run on agent action."""
        # self.console.print(f"[thought]Thought: {action.log}[/thought]")
        pass

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> Any:
        """Run when chain errors."""
        self.console.print(f"[error]Error: {error}[/error]")

