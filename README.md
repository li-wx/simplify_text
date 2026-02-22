# Text Simplifier

An AI-based text simplifier that helps users quickly grasp the content of complex text.

## Features

Given a text input, returns an easier version explaining what it says with the following 3 sections:

1. **Ultra Short Summary**: First gives an ultra short summary of the text that contains at most three sentences.

2. **Key Points Extraction**: After the ultra short summary, lists key points that the text contains.

3. **Additional Details**: If there are additional details not included in key points, list them here.

When generating text, make sure the following requirements are met:

1. **Logical Ordering**: Orders the sentences and key points by importance, but ensures the logic is clear (e.g., if you need point A to explain point B, don't put A behind B).

2. **Smooth Transitions**: Provides smooth transitions between key points and sentences. If needed, add intermediate context or additional explanations to help the reader with transitions.

3. **Sentence Breaking**: Breaks long sentences into short ones. Every sentence in all sections should contain no more than 12 words.

4. **Common Language**: Uses common words and phrases only. Does not use those rarely seen in plain language.

5. **Ambiguity Removal**: Check and eliminate ambiguity. If the original text contains ambiguity that cannot be resolved, choose the most likely meaning and add explanations to the section of "Additional Details".

6. **Redundancy Removal**: Check and remove redundancy from the text.

## Setup

### Prerequisites

- Python 3.9 or higher
- Azure OpenAI resource with API access

### Installation

1. **Clone or download this repository**

2. **Install dependencies** (using uv):
   ```bash
   uv sync
   ```
   
   > **Note**: If you have a `requirements.txt` file from a previous setup, you can remove it as `uv` uses `pyproject.toml` for dependency management.

3. **Set up Azure OpenAI credentials**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=o3-mini
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

### Getting Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or access your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy your endpoint URL and API key
5. Note your deployment name (e.g., "o3-mini", "gpt-4", "gpt-35-turbo")
6. For o3-mini model, use API version `2024-12-01-preview`

> **Note**: The o3-mini model is optimized for reasoning tasks and works excellent for text simplification. The application automatically adjusts parameters for optimal performance when using o3-mini.

## Usage

### Interactive Mode

Run the main script for interactive text simplification:

```bash
uv run python main.py
```

Enter your text and press Enter twice (empty line) to process. Type 'quit' to exit.

### Test Script

Run the test script to see a demonstration:

```bash
uv run python test_simplifier.py
```

### Example

**Input:**
```
The implementation of artificial intelligence in contemporary healthcare systems represents 
a paradigmatic shift towards precision medicine, wherein algorithmic frameworks leverage 
vast repositories of heterogeneous biomedical data to facilitate enhanced diagnostic 
accuracy and therapeutic optimization.
```

**Output:**
```
AI is changing healthcare. It helps doctors make better diagnoses. It also improves treatments.

Key points:
1. AI uses large amounts of medical data
2. This helps doctors be more accurate
3. Treatments become more personalized
4. Healthcare systems work better
```

## Implementation Details

The text simplifier uses a multi-step approach with Azure OpenAI LLM:

1. **Multi-Pass Processing**: Uses multiple LLM calls to ensure all requirements are met
2. **Structured Pipeline**: Each requirement is handled by a dedicated processing step
3. **Quality Assurance**: Multiple validation passes ensure output quality
4. **Error Handling**: Robust error handling for API calls and processing

## Project Structure

```
.
├── main.py              # Main application with TextSimplifier class
├── test_simplifier.py   # Test script with example
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file (protects .env)
├── pyproject.toml      # Project configuration and dependencies (uv)
├── uv.lock             # Lock file for reproducible builds (auto-generated)
└── README.md           # This file
```

## Dependencies

Managed via `uv` and defined in `pyproject.toml`:
- `openai>=2.21.0` - Azure OpenAI Python client
- `python-dotenv>=1.0.0` - Environment variable loading

**Supported Models**: 
- o3-mini (recommended for reasoning tasks like text simplification)
- GPT-4, GPT-4 Turbo
- GPT-3.5 Turbo

To add new dependencies:
```bash
uv add package-name
```

## Security Notes

- Never commit `.env` file to version control
- Keep your Azure OpenAI API keys secure
- The `.gitignore` file is configured to protect sensitive information

## UV Command Reference

Useful `uv` commands for this project:

```bash
# Install all dependencies
uv sync

# Run the application
uv run python main.py

# Run tests
uv run python test_simplifier.py

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Remove dependencies
uv remove package-name

# Update dependencies
uv sync --upgrade

# Create a virtual environment
uv venv

# Show dependency tree
uv tree
```

## Troubleshooting

**Common Issues:**

1. **Missing Environment Variables**: Make sure `.env` file is created and contains valid Azure OpenAI credentials
2. **API Errors**: Verify your Azure OpenAI endpoint URL and API key
3. **Deployment Not Found**: Check that your deployment name matches the actual deployment in Azure
4. **Rate Limiting**: Azure OpenAI has rate limits; the tool handles this gracefully but processing may take longer
5. **UV Not Found**: Install uv with `pip install uv` or follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## Contributing

Feel free to submit issues and enhancement requests!

