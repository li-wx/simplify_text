"""
Test script for Text Simplifier.

Demonstrates both the o3-mini and GPT-4.1 mini versions with a sample text.
"""

import sys

from dotenv import load_dotenv

from simplifier import TextSimplifier

load_dotenv()


SAMPLE_TEXT = (
    "The implementation of artificial intelligence in contemporary healthcare systems "
    "represents a paradigmatic shift towards precision medicine, wherein algorithmic "
    "frameworks leverage vast repositories of heterogeneous biomedical data to facilitate "
    "enhanced diagnostic accuracy and therapeutic optimization."
)


def run_test(simplifier: TextSimplifier) -> None:
    """Run the simplification test with a given simplifier instance."""
    print(f"\nDeployment: {simplifier.deployment}")
    print(f"Endpoint:   {simplifier.endpoint}")
    print(f"Debug dir:  {simplifier.debug_dir}\n")

    print("Input:")
    print("-" * 40)
    print(SAMPLE_TEXT)
    print("-" * 40)
    print("\nSimplifying…\n")

    result = simplifier.simplify(SAMPLE_TEXT)

    print("\nOutput:")
    print("-" * 40)
    print(result)
    print("-" * 40)


def main():
    model = "o3-mini"
    if len(sys.argv) > 1:
        model = sys.argv[1]

    print("=" * 60)
    print(f"  Text Simplifier – Test Script  ({model})")
    print("=" * 60)

    if model == "gpt-4.1-mini":
        simplifier = TextSimplifier(
            deployment="gpt-4.1-mini",
            api_version="2025-04-01-preview",
            debug_dir="debug_output_4_1_mini",
        )
    else:
        simplifier = TextSimplifier(
            deployment="o3-mini",
            api_version="2024-12-01-preview",
        )

    run_test(simplifier)
    print("\nDone.")


if __name__ == "__main__":
    main()
