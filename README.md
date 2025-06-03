# AI Conversation Analysis System

A powerful system for generating and analyzing AI-to-AI conversations, with advanced NLP capabilities for understanding conversation dynamics, sentiment, and topics.

## Features

- 🤖 AI-to-AI conversation generation using Anthropic/OpenAI APIs
- 📊 Advanced NLP analysis including:
  - Sentiment analysis
  - Topic modeling
  - Word frequency analysis
  - Conversation flow metrics
  - Turn-taking pattern analysis
- 💻 Multiple interfaces:
  - Terminal-based conversation tool
  - CLI analysis tool
  - (GUI components available for Python 3.11)

## Prerequisites

- Python 3.11+ (3.13 recommended for CLI tools)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
python install.py
```

## Usage

### Generating Conversations

```bash
python conversation_cli.py
```

This will start an interactive session where you can:
- Configure AI personas
- Set message limits
- Generate AI-to-AI conversations
- Export conversations to JSON

### Analyzing Conversations

```bash
# List available conversations
python analyze_cli.py --list

# Analyze a specific conversation
python analyze_cli.py conversation_file.json

# Export detailed analysis
python analyze_cli.py conversation_file.json --format json
```

## Project Structure

- `conversation_cli.py` - Terminal-based conversation generator
- `analyze_cli.py` - NLP analysis tool
- `analysis/` - Core NLP analysis modules
- `config.json` - Configuration settings
- `requirements.txt` - Project dependencies

## Configuration

Edit `config.json` to customize:
- API keys
- Model settings
- Analysis parameters
- Output preferences

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Acknowledgments

- Anthropic for Claude API
- OpenAI for GPT API
- NLTK and TextBlob for NLP capabilities 