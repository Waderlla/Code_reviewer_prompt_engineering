"""Jednorazowy skrypt: wgrywa treść promptów z prompts.py do LangFuse Prompt Management.

Uruchom raz: python push_prompts_to_langfuse.py
Potem prompts.py pobiera te prompty z LangFuse (z lokalnym fallbackiem).
"""
from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client

from prompts import SYSTEM_PROMPT_FALLBACK, USER_PROMPT_TEMPLATE_FALLBACK

langfuse = get_client()

langfuse.create_prompt(
    name="code-review-system",
    prompt=SYSTEM_PROMPT_FALLBACK,
    type="text",
    labels=["production"],
)

langfuse.create_prompt(
    name="code-review-user",
    prompt=USER_PROMPT_TEMPLATE_FALLBACK,
    type="text",
    labels=["production"],
)

langfuse.flush()
print("Prompty wgrane do LangFuse: code-review-system, code-review-user")
