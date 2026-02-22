"""
Text Simplifier — o3-mini version.

Usage:
    uv run python main_o3_mini.py
"""

import sys

from dotenv import load_dotenv

from simplifier import TextSimplifier

load_dotenv()


def main():
    """Interactive text simplification loop using o3-mini."""
    print("=" * 60)
    print("  Text Simplifier  (o3-mini)")
    print("=" * 60)

    try:
        simplifier = TextSimplifier(
            deployment="o3-mini",
            api_version="2024-12-01-preview",
        )
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
            print("\nOutput:")
            print(result)
            print()
        except Exception as exc:
            print(f"\nError during simplification: {exc}\n")


if __name__ == "__main__":
    main()
