from pathlib import Path
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in .env")


client = Groq(api_key=api_key)


def generate_ai_analysis(project_dir: Path):

    code_files = []

    for file in project_dir.rglob("*"):

        if not file.is_file():
            continue

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            code_files.append(
                f"\n--- {file.name} ---\n"
                f"{content[:12000]}"
            )

        except Exception:
            continue

    if not code_files:
        return {
            "status": "error",
            "message": "No readable code files found."
        }

    code = "\n".join(code_files)

    prompt = f"""
You are LegacyMind AI, an expert software modernization assistant.

Analyze the following legacy codebase.

Provide the following sections:

1. Codebase Overview
2. Architecture Analysis
3. Security Issues
4. Code Quality Issues
5. Dependency / Technology Concerns
6. Modernization Recommendations
7. Priority Actions

Keep the analysis practical and easy to understand.

LEGACY CODE:

{code}
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert software modernization "
                    "and security engineer."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        max_tokens=3000
    )

    return {
        "status": "success",
        "model": "llama-3.3-70b-versatile",
        "analysis": response.choices[0].message.content
    }