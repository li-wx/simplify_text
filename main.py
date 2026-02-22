"""
Text Simplifier - AI-based text simplification using Azure OpenAI.

Transforms complex text into easy-to-understand content with:
- Ultra Short Summary (max 3 sentences)
- Key Points Extraction
- Additional Details
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


# ---------------------------------------------------------------------------
# Step 1 – Extract every point from the original text
# ---------------------------------------------------------------------------
STEP1_SYSTEM = """\
You are a precise information extractor. Your ONLY job is to capture every \
single claim, fact, detail, and nuance from the original text. Do NOT \
simplify, rephrase, or omit anything.
"""

STEP1_USER = """\
Read the text below carefully. Extract ALL points it makes — main ideas, \
supporting details, qualifications, and any implied meanings.

Rules:
- Output a numbered list. Each item = one distinct point.
- Preserve the meaning exactly. Do not add information that is not in the text.
- If the text contains ambiguity, note it explicitly (e.g., "Ambiguity: …").
- Do NOT simplify the language yet.

Text:
{text}
"""

# ---------------------------------------------------------------------------
# Step 2 – Rewrite extracted points in plain language
# ---------------------------------------------------------------------------
STEP2_SYSTEM = """\
You are a plain-language rewriter. You will receive a numbered list of \
points extracted from a text. Rewrite them so they are easy to read while \
keeping every point accurate and complete.
"""

STEP2_USER = """\
Rewrite the extracted points below following these strict rules:

1. **Accuracy**: Keep EVERY point. Do NOT drop, merge, or invent information.
2. **Sentence Length**: Every sentence must contain no more than 12 words. \
Break longer sentences into shorter ones.
3. **Common Language**: Use only simple, everyday words. If a technical term \
is essential, briefly explain it in parentheses.
4. **Logical Ordering**: Order items by importance, but if point A is needed \
to understand point B, put A before B.
5. **Smooth Transitions**: Add brief connecting words between points so the \
reader can follow easily.
6. **No Redundancy**: Remove duplicated ideas, but do NOT remove unique details.
7. **No Ambiguity**: Use clear, precise language. If the original had \
ambiguity, keep your note about it.

Output format:
- Section "Key Points": a numbered list of the rewritten points.
- Section "Additional Details": any extra context, ambiguity notes, or \
minor details that do not fit as key points. Write "None." if empty.

Extracted points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 3 – Generate the Ultra Short Summary
# ---------------------------------------------------------------------------
STEP3_SYSTEM = """\
You are a summarizer. You will receive simplified key points and additional \
details. Write an ultra-short summary.
"""

STEP3_USER = """\
Based ONLY on the content below, write an "Ultra Short Summary" section.

Rules:
- At most 3 sentences, written as a single paragraph (no bullet points 
or line breaks between sentences).
- Every sentence must contain no more than 12 words.
- Use only simple, everyday words.
- Do NOT add any information not present below.

Content:
{content}
"""

# ---------------------------------------------------------------------------
# Step 4 – Final validation
# ---------------------------------------------------------------------------
STEP4_SYSTEM = """\
You are a strict quality-assurance editor. You will receive:
  (A) The ORIGINAL text.
  (B) A simplified version with three sections.

Your job is to verify and fix the simplified version.
"""

STEP4_USER = """\
Compare the simplified version against the original text and fix any issues.

Checks to perform:
1. **Accuracy**: Every claim in the output must be supported by the original. \
Remove or correct anything the original does not say. Flag nothing as missing \
only if the original actually states it.
2. **Completeness**: Every distinct point from the original must appear in \
Key Points or Additional Details. If something is missing, add it.
3. **Sentence Length**: Every sentence must have no more than 12 words. Split \
any that are longer.
4. **Common Language**: Replace any uncommon words with everyday equivalents.
5. **Logical Order**: Rearrange if needed so prerequisite ideas come first.
6. **Smooth Transitions**: Add brief connectors between points if needed.
7. **No Redundancy**: Remove duplicated ideas.
8. **No Ambiguity**: Clarify vague references. If inherent ambiguity exists, \
note it in Additional Details.

Output exactly these three sections and nothing else:

### Ultra Short Summary
(at most 3 sentences, written as a single paragraph)

### Key Points
(numbered list)

### Additional Details
(list, or "None.")

--- ORIGINAL TEXT ---
{original}

--- SIMPLIFIED VERSION ---
{simplified}
"""


class TextSimplifier:
    """Simplifies complex text using Azure OpenAI."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY", "")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o3-mini")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure OpenAI credentials are required. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in your .env file."
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    @property
    def _is_o3(self) -> bool:
        """Check if the deployment is an o3-series model."""
        return "o3" in self.deployment.lower()

    def _call_llm(self, system: str, user: str) -> str:
        """Make a single LLM call with appropriate parameters for the model."""
        messages = []

        if self._is_o3:
            # o3-mini doesn't support the system role; use developer role instead
            messages.append({"role": "developer", "content": system})
        else:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": user})

        kwargs: dict = {
            "model": self.deployment,
            "messages": messages,
        }

        if self._is_o3:
            # o3-mini uses max_completion_tokens instead of max_tokens
            kwargs["max_completion_tokens"] = 4096
        else:
            kwargs["max_tokens"] = 4096
            kwargs["temperature"] = 0.3

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    def simplify(self, text: str) -> str:
        """Simplify the given text through a multi-step pipeline.

        Step 1: Extract all points from the original text accurately.
        Step 2: Rewrite the points in plain, simple language.
        Step 3: Generate an ultra-short summary from the rewritten points.
        Step 4: Validate accuracy, completeness, and all writing rules.

        Args:
            text: The complex text to simplify.

        Returns:
            The simplified text with three sections.
        """
        if not text.strip():
            return ""

        # Step 1 – Extract every point from the original text
        extracted = self._call_llm(
            STEP1_SYSTEM,
            STEP1_USER.format(text=text),
        )

        # Step 2 – Rewrite extracted points in plain language
        rewritten = self._call_llm(
            STEP2_SYSTEM,
            STEP2_USER.format(points=extracted),
        )

        # Step 3 – Generate the ultra-short summary
        summary = self._call_llm(
            STEP3_SYSTEM,
            STEP3_USER.format(content=rewritten),
        )

        # Combine into final draft
        draft = f"{summary.strip()}\n\n{rewritten.strip()}"

        # Step 4 – Final validation against the original
        validated = self._call_llm(
            STEP4_SYSTEM,
            STEP4_USER.format(original=text, simplified=draft),
        )

        return validated.strip()


def main():
    """Interactive text simplification loop."""
    print("=" * 60)
    print("  Text Simplifier  (Azure OpenAI)")
    print("=" * 60)

    try:
        simplifier = TextSimplifier()
    except ValueError as exc:
        print(f"\nError: {exc}")
        print("Please set up your .env file. See .env.example for details.")
        sys.exit(1)

    print(f"\nUsing deployment: {simplifier.deployment}")
    print("Enter text to simplify. Press Enter twice (empty line) to process.")
    print("Type 'quit' to exit.\n")

    while True:
        print("-" * 60)
        lines: list[str] = []
        print("Input:")
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip().lower() == "quit":
                print("\nGoodbye!")
                sys.exit(0)
            if line == "" and lines:
                break
            lines.append(line)

        text = "\n".join(lines).strip()
        if not text:
            continue

        print("\nProcessing…\n")

        try:
            result = simplifier.simplify(text)
            print("Output:")
            print(result)
            print()
        except Exception as exc:
            print(f"\nError during simplification: {exc}\n")


if __name__ == "__main__":
    main()
