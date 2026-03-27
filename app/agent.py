import os
import requests
from typing import Dict, Any
from .utils import setup_logger
from .parser import extract_and_parse_json
from .mcp.tool_registry import tool_registry

logger = setup_logger("agent")

# --- Groq Free Cloud API ---
GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

SYSTEM_PROMPT_HEADER: str = """You are a CAD assistant converting natural language to predefined JSON function calls.
Convert user commands into JSON function calls ONLY. 

Available functions:
"""

SYSTEM_PROMPT_FOOTER: str = """
IMPORTANT: Return ONLY a JSON object in this exact format, no extra text:
{"function": "<function_name>", "arguments": {...}}
"""

def _build_system_prompt() -> str:
    """Dynamically builds system prompt from registered tools."""
    tools_desc: str = tool_registry.generate_prompt_description()
    return SYSTEM_PROMPT_HEADER + tools_desc + SYSTEM_PROMPT_FOOTER

def generate_cad_command(prompt: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Get a free key at https://console.groq.com/keys and run: "
            "export GROQ_API_KEY='your-key-here'"
        )

    system_prompt: str = _build_system_prompt()

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 256
    }
    
    logger.info(f"Sending prompt to Groq ({model})")
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Groq: {e}")
        raise RuntimeError(f"Failed to connect to Groq API: {e}")

    data: Dict[str, Any] = response.json()
    response_text: str = data["choices"][0]["message"]["content"]
    
    parsed: Dict[str, Any] = extract_and_parse_json(response_text)
    
    if "function" not in parsed or "arguments" not in parsed:
        raise ValueError("LLM returned JSON, but missing 'function' or 'arguments' keys.")
        
    return parsed