# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Self-Conversation Experiment Tool - A PyQt6 application that allows two AI sessions to have conversations with each other using the Anthropic API or OpenAI API. This is a research tool for observing AI conversational dynamics and emergent behaviors.

## Project Structure

- `main.py` - Main application with PyQt6 GUI and conversation management
- `conversation_cli.py` - Terminal-based tool for generating AI conversations
- `analyze_cli.py` - Command-line NLP analysis tool for conversation logs
- `analysis/` - NLP analysis modules (sentiment, topics, flow metrics)
- `requirements.txt` - Python dependencies (PyQt6, anthropic, openai, nltk, etc.)
- `install.py` - Installation script for setting up dependencies
- `config.json` - Configuration file (created automatically)
- `.venv/` - Python virtual environment

## Development Environment

### Setup
1. Activate virtual environment: `source .venv/bin/activate`
2. Install dependencies: `python install.py` or `pip install -r requirements.txt`
3. Run application: `python main.py`

### Common Commands
- Run GUI application: `python main.py`
- Generate conversations (CLI): `python conversation_cli.py`
- Analyze conversations: `python analyze_cli.py conversation_file.json`
- List saved conversations: `python analyze_cli.py --list`
- Install dependencies: `python install.py`

### Environment Variables
- `ANTHROPIC_API_KEY` - Required for Claude AI
- `OPENAI_API_KEY` - Required for GPT models

## Architecture

### Core Components
- `AIConversationApp` - Main PyQt6 window with split-screen interface
- `ConversationManager` - QThread that manages AI-to-AI conversations via APIs
- Configuration panel for API keys, personas, and conversation parameters
- Real-time conversation display with separate panels for each AI
- Export functionality for conversation logs

### Key Features
- Split-screen interface showing both AI conversation sides
- Support for both Anthropic Claude and OpenAI GPT models
- Configurable AI personas and conversation parameters
- Start/stop/pause controls for conversation management
- JSON export of conversation logs with metadata
- NLP analysis tools for sentiment, topics, and conversation flow
- Error handling and progress tracking
- Settings persistence

### Threading Model
- Main UI runs on primary thread
- `ConversationManager` runs conversations on separate QThread
- Uses Qt signals/slots for thread-safe communication between AI responses and UI updates

### API Integration
- Supports multiple providers: Anthropic and OpenAI
- Each AI participant can use different providers/models
- Conversation history maintained for context
- Configurable token limits and response delays

## Analysis Capabilities

The `analysis/` directory contains modules for:
- Sentiment analysis (positive/negative/neutral tracking)
- Topic modeling using Latent Dirichlet Allocation
- Word frequency and linguistic analysis
- Conversation flow and engagement metrics
- Turn-taking pattern analysis

## Usage Notes
- Requires API keys for chosen AI providers
- Conversations are rate-limited with configurable delays
- All conversations are logged and can be exported as JSON
- PyQt6 has compatibility issues with Python 3.13 - use Python 3.11 or terminal tools
- Designed as a research tool for studying AI interaction patterns