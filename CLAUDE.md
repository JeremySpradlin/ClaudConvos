# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Self-Conversation Experiment Tool - A PyQt6 application that allows two AI sessions to have conversations with each other using the Anthropic API. This is a research tool for observing AI conversational dynamics and emergent behaviors.

## Project Structure

- `main.py` - Main application with PyQt6 GUI and conversation management
- `requirements.txt` - Python dependencies (PyQt6, anthropic, etc.)
- `install.py` - Installation script for setting up dependencies
- `config.json` - Configuration file (created automatically)
- `.venv/` - Python virtual environment (Python 3.13)
- `.claude/` - Claude Code configuration

## Development Environment

### Setup
1. Activate virtual environment: `source .venv/bin/activate`
2. Install dependencies: `python install.py` or `pip install -r requirements.txt`
3. Run application: `python main.py`

### Common Commands
- Run the application: `python main.py`
- Install dependencies: `python install.py`
- Manual dependency install: `pip install -r requirements.txt`

## Architecture

### Core Components
- `AIConversationApp` - Main PyQt6 window with split-screen interface
- `ConversationManager` - QThread that manages AI-to-AI conversations via Anthropic API
- Configuration panel for API keys, personas, and conversation parameters
- Real-time conversation display with separate panels for each AI
- Export functionality for conversation logs

### Key Features
- Split-screen interface showing both AI conversation sides
- Configurable AI personas and conversation parameters
- Start/stop/pause controls for conversation management
- JSON export of conversation logs with metadata
- Error handling and progress tracking
- Settings persistence

### Threading Model
- Main UI runs on primary thread
- `ConversationManager` runs conversations on separate QThread
- Uses Qt signals/slots for thread-safe communication between AI responses and UI updates

## Usage Notes
- Requires Anthropic API key for Claude AI integration
- Conversations are rate-limited with configurable delays
- All conversations are logged and can be exported as JSON
- Designed as a research tool for studying AI interaction patterns