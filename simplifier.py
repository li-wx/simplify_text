"""
TextSimplifier — core class for the multi-step text simplification pipeline.

Supports both reasoning models (o3-mini, o4-mini) and standard models
(GPT-4o, GPT-4.1, GPT-4.1 mini, etc.) with automatic parameter adjustment.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from openai import AzureOpenAI

from prompts import (
    STEP1_SYSTEM, STEP1_USER,
    STEP2_SYSTEM, STEP2_USER,
    STEP3_SYSTEM, STEP3_USER,
    STEP4_SYSTEM, STEP4_USER,
    STEP5_SYSTEM, STEP5_USER,
)


class TextSimplifier:
    """Simplifies complex text using Azure OpenAI.

    Args:
        endpoint:    Azure OpenAI endpoint URL (or env AZURE_OPENAI_ENDPOINT).
        api_key:     Azure OpenAI API key (or env AZURE_OPENAI_KEY).
        deployment:  Model deployment name (or env AZURE_OPENAI_DEPLOYMENT_NAME).
        api_version: API version string (or env AZURE_OPENAI_API_VERSION).
        debug_dir:   Directory for intermediate debug output files.
    """

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
        self.deployment = deployment or ""
        self.api_version = api_version or ""

        if not self.deployment or not self.api_version:
            raise ValueError(
                "deployment and api_version are required. "
                "Pass them explicitly when creating TextSimplifier."
            )

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
    def _is_reasoning_model(self) -> bool:
        """Check if the deployment is a reasoning-series model (o3/o4)."""
        name = self.deployment.lower()
        return name.startswith("o3") or name.startswith("o4")

    def _call_llm(self, system: str, user: str) -> str:
        """Make a single LLM call with appropriate parameters for the model."""
        if self._is_reasoning_model:
            messages = [
                {"role": "developer", "content": system},
                {"role": "user", "content": user},
            ]
        else:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]

        kwargs: dict = {
            "model": self.deployment,
            "messages": messages,
        }

        if self._is_reasoning_model:
            kwargs["max_completion_tokens"] = 16384
        else:
            kwargs["max_tokens"] = 16384
            kwargs["temperature"] = 0.05

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def _save_debug(self, run_dir: Path, filename: str, content: str) -> None:
        """Save intermediate output to a debug file."""
        run_dir.mkdir(parents=True, exist_ok=True)
        filepath = run_dir / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"  [debug] Saved {filepath}")

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

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
        print("Step 1: Extracting points...")
        extracted = self._call_llm(
            STEP1_SYSTEM,
            STEP1_USER.format(text=text),
        )
        self._save_debug(run_dir, "step1_extracted_points.txt", extracted)

        # Step 2 – Organise logical flow
        print("Step 2: Organising logical flow...")
        organised = self._call_llm(
            STEP2_SYSTEM,
            STEP2_USER.format(points=extracted),
        )
        self._save_debug(run_dir, "step2_organised_flow.txt", organised)

        # Step 3 – Enhance detail quality
        print("Step 3: Polishing language and separating details...")
        polished = self._call_llm(
            STEP3_SYSTEM,
            STEP3_USER.format(points=organised),
        )
        self._save_debug(run_dir, "step3_polished.txt", polished)

        # Step 4 – Generate the ultra-short summary
        print("Step 4: Generating summary...")
        summary = self._call_llm(
            STEP4_SYSTEM,
            STEP4_USER.format(content=polished),
        )
        self._save_debug(run_dir, "step4_summary.txt", summary)

        # Combine into final draft
        draft = f"{summary.strip()}\n\n{polished.strip()}"
        self._save_debug(run_dir, "step4_draft_combined.txt", draft)

        # Step 5 – Final validation against the original
        print("Step 5: Validating accuracy and completeness...")
        validated = self._call_llm(
            STEP5_SYSTEM,
            STEP5_USER.format(original=text, simplified=draft),
        )
        self._save_debug(run_dir, "step5_final_output.txt", validated.strip())

        print("Done.")
        return validated.strip()
