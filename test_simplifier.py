"""
Test script for Text Simplifier.

Demonstrates the simplifier with a sample complex text.
"""

from main import TextSimplifier


SAMPLE_TEXT = (
    "The implementation of artificial intelligence in contemporary healthcare systems "
    "represents a paradigmatic shift towards precision medicine, wherein algorithmic "
    "frameworks leverage vast repositories of heterogeneous biomedical data to facilitate "
    "enhanced diagnostic accuracy and therapeutic optimization."
)


def main():
    print("=" * 60)
    print("  Text Simplifier – Test Script")
    print("=" * 60)

    simplifier = TextSimplifier()
    print(f"\nDeployment: {simplifier.deployment}")
    print(f"Endpoint:   {simplifier.endpoint}\n")

    print("Input:")
    print("-" * 40)
    print(SAMPLE_TEXT)
    print("-" * 40)
    print("\nSimplifying…\n")

    result = simplifier.simplify(SAMPLE_TEXT)

    print("Output:")
    print("-" * 40)
    print(result)
    print("-" * 40)
    print("\nDone.")


if __name__ == "__main__":
    main()
