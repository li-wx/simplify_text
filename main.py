"""
Text Simplifier - AI-based text simplification using Azure OpenAI.

Transforms complex text into easy-to-understand content with:
- Ultra Short Summary (max 3 sentences)
- Key Points Extraction
- Additional Details
"""

import os
import sys
from datetime import datetime
from pathlib import Path
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
# Step 2 – Organise logical flow
# ---------------------------------------------------------------------------
STEP2_SYSTEM = """\
You are an expert editor focused on logical structure and flow. You will \
receive a numbered list of points extracted from a text. Your ONLY job is \
to reorganise them for clarity while keeping every point accurate and complete.
"""

STEP2_USER = """\
Reorganise the extracted points below. Follow these rules strictly:

1. **Accuracy first**: Keep EVERY point. Do NOT drop, merge, or invent \
information.
2. **Importance ordering**: Put the most important points first.
3. **Logical dependencies**: If point A is needed to understand point B, \
put A before B — even if B is more important.
4. **Grouping**: Group closely related points together as sub-points.
5. **Smooth transitions**: Add brief connecting words or phrases between \
points and groups so a reader can follow the flow easily.

Output a numbered list of the reorganised points. Keep the original wording \
for now — do NOT simplify the language yet.

Extracted points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 3 – Enhance detail quality
# ---------------------------------------------------------------------------
STEP3_SYSTEM = """\
You are a plain-language editor. You will receive an ordered list of points. \
Your job is to polish the language and separate key points from additional \
details.
"""

STEP3_USER = """\
Rewrite the ordered points below. Follow these rules strictly:

1. **Sentence Length**: Every sentence must contain no more than 12 words. \
Break longer sentences into shorter ones.
2. **Common Language**: Use only simple, everyday words. If a technical term \
is essential, briefly explain it in parentheses.
3. **No Redundancy**: Remove duplicated ideas, but do NOT remove unique \
details.
4. **No Ambiguity**: Use clear, precise language.
5. **Separate sections**:
   - "Key Points": a numbered list of the main, critical points.
   - "Additional Details": move non-critical points, minor context, \
extra explanations of any unresolved ambiguities here. \
Write "None." if empty.

Output exactly those two sections.

Ordered points:
{points}
"""

# ---------------------------------------------------------------------------
# Step 4 – Generate the Ultra Short Summary
# ---------------------------------------------------------------------------
STEP4_SYSTEM = """\
You are a summarizer. You will receive simplified key points and additional \
details. Write an ultra-short summary.
"""

STEP4_USER = """\
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
# Step 5 – Final validation
# ---------------------------------------------------------------------------
STEP5_SYSTEM = """\
You are a strict quality-assurance editor. You will receive:
  (A) The ORIGINAL text.
  (B) A simplified version with three sections.

Your job is to verify and fix the simplified version.
"""

STEP5_USER = """\
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
        debug_dir: Optional[str] = None,
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

        self.debug_dir = Path(debug_dir) if debug_dir else Path("debug_output")

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
            kwargs["max_completion_tokens"] = 8192
        else:
            kwargs["max_tokens"] = 8192
            kwargs["temperature"] = 0.1

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    def _save_debug(self, run_dir: Path, filename: str, content: str) -> None:
        """Save intermediate output to a debug file."""
        run_dir.mkdir(parents=True, exist_ok=True)
        filepath = run_dir / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"  [debug] Saved {filepath}")

    def simplify(self, text: str) -> str:
        """Simplify the given text through a multi-step pipeline.

        Step 1: Extract all points from the original text accurately.
        Step 2: Organise logical flow (ordering, grouping, transitions).
        Step 3: Enhance detail quality (simplify language, split sentences,
                 separate key points from additional details).
        Step 4: Generate an ultra-short summary from the polished content.
        Step 5: Validate accuracy, completeness, and all writing rules.

        Intermediate results from every step are saved to the debug
        output directory for inspection.

        Args:
            text: The complex text to simplify.

        Returns:
            The simplified text with three sections.
        """
        if not text.strip():
            return ""

        # Create a timestamped directory for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.debug_dir / timestamp

        # Save the original input
        self._save_debug(run_dir, "step0_input.txt", text)

        # Step 1 – Extract every point from the original text
        extracted = self._call_llm(
            STEP1_SYSTEM,
            STEP1_USER.format(text=text),
        )
        self._save_debug(run_dir, "step1_extracted_points.txt", extracted)

        # Step 2 – Organise logical flow
        organised = self._call_llm(
            STEP2_SYSTEM,
            STEP2_USER.format(points=extracted),
        )
        self._save_debug(run_dir, "step2_organised_flow.txt", organised)

        # Step 3 – Enhance detail quality
        polished = self._call_llm(
            STEP3_SYSTEM,
            STEP3_USER.format(points=organised),
        )
        self._save_debug(run_dir, "step3_polished.txt", polished)

        # Step 4 – Generate the ultra-short summary
        summary = self._call_llm(
            STEP4_SYSTEM,
            STEP4_USER.format(content=polished),
        )
        self._save_debug(run_dir, "step4_summary.txt", summary)

        # Combine into final draft
        draft = f"{summary.strip()}\n\n{polished.strip()}"
        self._save_debug(run_dir, "step4_draft_combined.txt", draft)

        # Step 5 – Final validation against the original
        validated = self._call_llm(
            STEP5_SYSTEM,
            STEP5_USER.format(original=text, simplified=draft),
        )
        self._save_debug(run_dir, "step5_final_output.txt", validated.strip())

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
