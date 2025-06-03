#!/usr/bin/env python3
"""
AI Self-Conversation Experiment Tool - Fixed Version
Works around PyQt6 + Python 3.13 compatibility issues
"""

import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Try PySide6 first, then PyQt6
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTextEdit, QLineEdit, QPushButton, QLabel, QSpinBox, QGroupBox,
        QSplitter, QTabWidget, QFileDialog, QMessageBox, QProgressBar,
        QComboBox
    )
    from PySide6.QtCore import QThread, Signal as pyqtSignal, QTimer, Qt
    from PySide6.QtGui import QFont, QTextCursor
    GUI_FRAMEWORK = "PySide6"
except ImportError:
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTextEdit, QLineEdit, QPushButton, QLabel, QSpinBox, QGroupBox,
            QSplitter, QTabWidget, QFileDialog, QMessageBox, QProgressBar,
            QComboBox
        )
        from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
        from PyQt6.QtGui import QFont, QTextCursor
        GUI_FRAMEWORK = "PyQt6"
    except ImportError:
        print("Error: Neither PySide6 nor PyQt6 is available")
        print("Install with: pip install PySide6")
        sys.exit(1)

import anthropic
import openai


class ConversationManager(QThread):
    """Manages the conversation between two AI instances."""
    
    message_received = pyqtSignal(str, str)  # sender_id, message
    conversation_ended = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.conversation_history = []
        self.is_running = False
        self.is_paused = False
        
        # Initialize clients based on environment variables
        import os
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key) if anthropic_key else None
        self.openai_client = openai.OpenAI(api_key=openai_key) if openai_key else None
        
    def start_conversation(self):
        """Start the conversation between AI instances."""
        self.is_running = True
        self.is_paused = False
        self.start()
        
    def pause_conversation(self):
        """Pause the conversation."""
        self.is_paused = True
        
    def resume_conversation(self):
        """Resume the conversation."""
        self.is_paused = False
        
    def stop_conversation(self):
        """Stop the conversation."""
        self.is_running = False
        self.is_paused = False
        
    def run(self):
        """Main conversation loop."""
        try:
            # Initialize conversation with first AI
            if self.config.get('initial_prompt_ai1'):
                first_message = self.config['initial_prompt_ai1']
            else:
                first_message = "Hello! Let's have an interesting conversation."
                
            current_speaker = "ai1"
            message = first_message
            message_count = 0
            max_messages = self.config.get('message_limit', 50)
            
            while self.is_running and message_count < max_messages:
                if self.is_paused:
                    self.msleep(100)
                    continue
                    
                # Send message to current AI and get response
                try:
                    if current_speaker == "ai1":
                        persona = self.config.get('persona_ai1', '')
                        next_speaker = "ai2"
                    else:
                        persona = self.config.get('persona_ai2', '')
                        next_speaker = "ai1"
                        
                    response = self.get_ai_response(message, persona, current_speaker)
                    
                    # Emit the response
                    self.message_received.emit(current_speaker, response)
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        'speaker': current_speaker,
                        'message': response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Switch speakers
                    message = response
                    current_speaker = next_speaker
                    message_count += 1
                    
                    # Add delay between messages
                    delay = self.config.get('message_delay', 2000)
                    self.msleep(delay)
                    
                except Exception as e:
                    self.error_occurred.emit(f"API Error: {str(e)}")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"Conversation Error: {str(e)}")
            
        self.conversation_ended.emit()
        
    def get_ai_response(self, message: str, persona: str, speaker_id: str) -> str:
        """Get response from the configured AI provider."""
        system_prompt = f"""You are {speaker_id.upper()}. {persona}
        
You are having a conversation with another AI. Keep your responses conversational, 
thoughtful, and engaging. Aim for 1-3 sentences unless the topic requires more depth."""

        try:
            if speaker_id == "ai1":
                provider = self.config.get('provider_ai1', 'anthropic')
                model = self.config.get('model_ai1', 'claude-3-5-sonnet-20241022')
            else:
                provider = self.config.get('provider_ai2', 'anthropic')
                model = self.config.get('model_ai2', 'claude-3-5-sonnet-20241022')
                
            if provider == 'anthropic':
                return self._get_anthropic_response(message, system_prompt, model)
            elif provider == 'openai':
                return self._get_openai_response(message, system_prompt, model)
            else:
                raise Exception(f"Unknown provider: {provider}")
                
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")
            
    def _get_anthropic_response(self, message: str, system_prompt: str, model: str) -> str:
        """Get response from Anthropic API."""
        if not self.anthropic_client:
            raise Exception("Anthropic API key not found in environment")
            
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=self.config.get('max_tokens', 200),
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text
        except anthropic.AuthenticationError as e:
            raise Exception(f"Invalid Anthropic API key: {str(e)}")
        except anthropic.RateLimitError as e:
            raise Exception(f"Anthropic rate limit exceeded: {str(e)}")
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API error: {str(e)}")
            
    def _get_openai_response(self, message: str, system_prompt: str, model: str) -> str:
        """Get response from OpenAI API."""
        if not self.openai_client:
            raise Exception("OpenAI API key not found in environment")
            
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                max_tokens=self.config.get('max_tokens', 200),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except openai.AuthenticationError as e:
            raise Exception(f"Invalid OpenAI API key: {str(e)}")
        except openai.RateLimitError as e:
            raise Exception(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class AIConversationApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.conversation_manager = None
        self.conversation_history = []
        self.dark_mode = True  # Start with dark mode
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"AI Self-Conversation Experiment Tool ({GUI_FRAMEWORK})")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create main tab widget
        self.main_tabs = QTabWidget()
        
        # Main conversation tab
        conversation_tab = self.create_conversation_tab()
        self.main_tabs.addTab(conversation_tab, "Live Conversation")
        
        # Analysis placeholder tab
        analysis_tab = self.create_analysis_placeholder_tab()
        self.main_tabs.addTab(analysis_tab, "Analysis")
        
        main_layout.addWidget(self.main_tabs)
    
    def create_conversation_tab(self) -> QWidget:
        """Create the main conversation tab."""
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        
        # Create configuration panel
        config_panel = self.create_config_panel()
        tab_layout.addWidget(config_panel, 1)
        
        # Create conversation area
        conversation_area = self.create_conversation_area()
        tab_layout.addWidget(conversation_area, 4)
        
        return tab_widget
    
    def create_analysis_placeholder_tab(self) -> QWidget:
        """Create analysis placeholder tab."""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # Info about CLI analysis
        info_group = QGroupBox("Analysis Tools")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
Advanced NLP analysis is available via command line:

• python analyze_cli.py --list
  (List available conversation files)

• python analyze_cli.py conversation_file.json
  (Analyze a specific conversation)

Features include:
• Sentiment analysis timeline
• Topic modeling and evolution  
• Word frequency analysis
• Conversation flow metrics
• Engagement scoring

The CLI tool provides detailed insights into AI conversation patterns.
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-family: monospace; font-size: 12px; padding: 10px;")
        
        info_layout.addWidget(info_text)
        
        # Button to run analysis
        button_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Last Conversation")
        self.analyze_button.clicked.connect(self.run_cli_analysis)
        self.analyze_button.setEnabled(False)
        
        self.open_folder_button = QPushButton("Open Conversation Folder")
        self.open_folder_button.clicked.connect(self.open_conversation_folder)
        
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        
        info_layout.addLayout(button_layout)
        tab_layout.addWidget(info_group)
        tab_layout.addStretch()
        
        return tab_widget
    
    def run_cli_analysis(self):
        """Run CLI analysis on the last conversation."""
        # Find the most recent conversation file
        json_files = list(Path('.').glob('conversation_*.json'))
        if not json_files:
            QMessageBox.information(self, "Info", "No conversation files found")
            return
        
        # Get the most recent file
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        # Run analysis
        import subprocess
        try:
            result = subprocess.run([
                sys.executable, 'analyze_cli.py', str(latest_file)
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                # Show results in a dialog
                results_dialog = QMessageBox()
                results_dialog.setWindowTitle("Analysis Results")
                results_dialog.setText(f"Analysis of {latest_file.name} completed!")
                results_dialog.setDetailedText(result.stdout)
                results_dialog.exec()
            else:
                QMessageBox.critical(self, "Error", f"Analysis failed:\n{result.stderr}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run analysis: {str(e)}")
    
    def open_conversation_folder(self):
        """Open the conversation folder."""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "."])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", "."])
            else:  # Linux
                subprocess.run(["xdg-open", "."])
        except Exception as e:
            QMessageBox.information(self, "Info", f"Cannot open folder: {str(e)}")
        
    def create_config_panel(self) -> QWidget:
        """Create the configuration panel."""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_layout = QVBoxLayout(api_group)
        
        # Environment keys info
        keys_info = QLabel("API keys loaded from environment variables:\nANTHROPIC_API_KEY and OPENAI_API_KEY")
        keys_info.setStyleSheet("color: #6c757d; font-style: italic; font-size: 10px;")
        keys_info.setWordWrap(True)
        api_layout.addWidget(keys_info)
        
        layout.addWidget(api_group)
        
        # Conversation Settings
        conv_group = QGroupBox("Conversation Settings")
        conv_layout = QVBoxLayout(conv_group)
        
        conv_layout.addWidget(QLabel("Message Limit:"))
        self.message_limit_spin = QSpinBox()
        self.message_limit_spin.setRange(1, 1000)
        self.message_limit_spin.setValue(50)
        conv_layout.addWidget(self.message_limit_spin)
        
        conv_layout.addWidget(QLabel("Message Delay (ms):"))
        self.message_delay_spin = QSpinBox()
        self.message_delay_spin.setRange(100, 10000)
        self.message_delay_spin.setValue(2000)
        conv_layout.addWidget(self.message_delay_spin)
        
        conv_layout.addWidget(QLabel("Max Tokens per Response:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(50, 1000)
        self.max_tokens_spin.setValue(200)
        conv_layout.addWidget(self.max_tokens_spin)
        
        layout.addWidget(conv_group)
        
        # Model Configuration
        model_group = QGroupBox("Model Configuration")
        model_layout = QVBoxLayout(model_group)
        
        # AI 1 Configuration
        ai1_layout = QVBoxLayout()
        ai1_layout.addWidget(QLabel("AI 1 Settings:"))
        
        ai1_provider_layout = QHBoxLayout()
        ai1_provider_layout.addWidget(QLabel("Provider:"))
        self.provider_ai1_combo = QComboBox()
        self.provider_ai1_combo.addItems(["anthropic", "openai"])
        self.provider_ai1_combo.currentTextChanged.connect(self.on_provider_ai1_changed)
        ai1_provider_layout.addWidget(self.provider_ai1_combo)
        ai1_layout.addLayout(ai1_provider_layout)
        
        ai1_model_layout = QHBoxLayout()
        ai1_model_layout.addWidget(QLabel("Model:"))
        self.model_ai1_combo = QComboBox()
        ai1_model_layout.addWidget(self.model_ai1_combo)
        ai1_layout.addLayout(ai1_model_layout)
        
        model_layout.addLayout(ai1_layout)
        
        # AI 2 Configuration
        ai2_layout = QVBoxLayout()
        ai2_layout.addWidget(QLabel("AI 2 Settings:"))
        
        ai2_provider_layout = QHBoxLayout()
        ai2_provider_layout.addWidget(QLabel("Provider:"))
        self.provider_ai2_combo = QComboBox()
        self.provider_ai2_combo.addItems(["anthropic", "openai"])
        self.provider_ai2_combo.currentTextChanged.connect(self.on_provider_ai2_changed)
        ai2_provider_layout.addWidget(self.provider_ai2_combo)
        ai2_layout.addLayout(ai2_provider_layout)
        
        ai2_model_layout = QHBoxLayout()
        ai2_model_layout.addWidget(QLabel("Model:"))
        self.model_ai2_combo = QComboBox()
        ai2_model_layout.addWidget(self.model_ai2_combo)
        ai2_layout.addLayout(ai2_model_layout)
        
        model_layout.addLayout(ai2_layout)
        
        # Initialize model options
        self.update_model_options()
        
        layout.addWidget(model_group)
        
        # AI Personas
        persona_group = QGroupBox("AI Personas")
        persona_layout = QVBoxLayout(persona_group)
        
        persona_layout.addWidget(QLabel("AI 1 Persona:"))
        self.persona_ai1_input = QTextEdit()
        self.persona_ai1_input.setMaximumHeight(80)
        self.persona_ai1_input.setPlaceholderText("Describe AI 1's personality/role...")
        persona_layout.addWidget(self.persona_ai1_input)
        
        persona_layout.addWidget(QLabel("AI 2 Persona:"))
        self.persona_ai2_input = QTextEdit()
        self.persona_ai2_input.setMaximumHeight(80)
        self.persona_ai2_input.setPlaceholderText("Describe AI 2's personality/role...")
        persona_layout.addWidget(self.persona_ai2_input)
        
        persona_layout.addWidget(QLabel("Initial Prompt for AI 1:"))
        self.initial_prompt_input = QTextEdit()
        self.initial_prompt_input.setMaximumHeight(60)
        self.initial_prompt_input.setPlaceholderText("Starting message...")
        persona_layout.addWidget(self.initial_prompt_input)
        
        layout.addWidget(persona_group)
        
        # Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.start_button = QPushButton("Start Conversation")
        self.start_button.clicked.connect(self.start_conversation)
        controls_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_conversation)
        self.pause_button.setEnabled(False)
        controls_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_conversation)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Export Conversation")
        self.export_button.clicked.connect(self.export_conversation)
        controls_layout.addWidget(self.export_button)
        
        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setMaximumWidth(120)
        theme_layout.addWidget(self.theme_button)
        theme_layout.addStretch()
        controls_layout.addLayout(theme_layout)
        
        layout.addWidget(controls_group)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return config_widget
        
    def create_conversation_area(self) -> QWidget:
        """Create the conversation display area."""
        conversation_widget = QWidget()
        layout = QVBoxLayout(conversation_widget)
        
        # Title
        title_label = QLabel("AI Group Conversation")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Unified conversation view
        conversation_group = QGroupBox("Live Conversation")
        conversation_layout = QVBoxLayout(conversation_group)
        
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setFont(QFont("Monaco", 12))
        self.conversation_display.setMinimumHeight(650)
        
        # Enable rich text formatting for colored messages
        self.conversation_display.setAcceptRichText(True)
        
        # Set dark mode styling
        self.conversation_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a202c;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 15px;
                selection-background-color: #4a5568;
            }
        """)
        
        conversation_layout.addWidget(self.conversation_display)
        layout.addWidget(conversation_group)
        
        # Participants info - will be updated dynamically
        self.participants_label = QLabel("Participants: AI-1 (Blue), AI-2 (Green)")
        self.participants_label.setFont(QFont("Arial", 10))
        self.participants_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.participants_label)
        
        # Status bar
        self.status_label = QLabel("Ready to start conversation")
        layout.addWidget(self.status_label)
        
        return conversation_widget
        
    def update_model_options(self):
        """Update available models based on selected providers."""
        # Anthropic models
        anthropic_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        
        # OpenAI models
        openai_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        # Update AI 1 models
        self.model_ai1_combo.clear()
        if self.provider_ai1_combo.currentText() == "anthropic":
            self.model_ai1_combo.addItems(anthropic_models)
        else:
            self.model_ai1_combo.addItems(openai_models)
            
        # Update AI 2 models
        self.model_ai2_combo.clear()
        if self.provider_ai2_combo.currentText() == "anthropic":
            self.model_ai2_combo.addItems(anthropic_models)
        else:
            self.model_ai2_combo.addItems(openai_models)
            
    def on_provider_ai1_changed(self):
        """Handle AI 1 provider change."""
        self.update_model_options()
        
    def on_provider_ai2_changed(self):
        """Handle AI 2 provider change."""
        self.update_model_options()
        
    def update_participants_info(self):
        """Update the participants info with current model selections."""
        ai1_info = f"{self.provider_ai1_combo.currentText().title()}/{self.model_ai1_combo.currentText()}"
        ai2_info = f"{self.provider_ai2_combo.currentText().title()}/{self.model_ai2_combo.currentText()}"
        self.participants_label.setText(f"Participants: AI-1 ({ai1_info}, Blue) | AI-2 ({ai2_info}, Green)")
        
    def start_conversation(self):
        """Start a new conversation."""
        # Check if required API keys are available
        import os
        
        provider_ai1 = self.provider_ai1_combo.currentText()
        provider_ai2 = self.provider_ai2_combo.currentText()
        
        # Validate API keys
        missing_keys = []
        if provider_ai1 == "anthropic" and not os.getenv('ANTHROPIC_API_KEY'):
            missing_keys.append("ANTHROPIC_API_KEY")
        if provider_ai1 == "openai" and not os.getenv('OPENAI_API_KEY'):
            missing_keys.append("OPENAI_API_KEY")
        if provider_ai2 == "anthropic" and not os.getenv('ANTHROPIC_API_KEY'):
            missing_keys.append("ANTHROPIC_API_KEY")
        if provider_ai2 == "openai" and not os.getenv('OPENAI_API_KEY'):
            missing_keys.append("OPENAI_API_KEY")
            
        # Remove duplicates
        missing_keys = list(set(missing_keys))
        
        if missing_keys:
            QMessageBox.warning(self, "Warning", 
                f"Missing environment variables: {', '.join(missing_keys)}")
            return
            
        # Prepare configuration
        config = {
            'message_limit': self.message_limit_spin.value(),
            'message_delay': self.message_delay_spin.value(),
            'max_tokens': self.max_tokens_spin.value(),
            'persona_ai1': self.persona_ai1_input.toPlainText(),
            'persona_ai2': self.persona_ai2_input.toPlainText(),
            'initial_prompt_ai1': self.initial_prompt_input.toPlainText(),
            'provider_ai1': provider_ai1,
            'model_ai1': self.model_ai1_combo.currentText(),
            'provider_ai2': provider_ai2,
            'model_ai2': self.model_ai2_combo.currentText()
        }
        
        # Clear previous conversation
        self.conversation_display.clear()
        self.conversation_history.clear()
        
        # Create and start conversation manager
        self.conversation_manager = ConversationManager(config)
        self.conversation_manager.message_received.connect(self.on_message_received)
        self.conversation_manager.conversation_ended.connect(self.on_conversation_ended)
        self.conversation_manager.error_occurred.connect(self.on_error_occurred)
        
        self.conversation_manager.start_conversation()
        
        # Update participants info
        self.update_participants_info()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, self.message_limit_spin.value())
        self.progress_bar.setValue(0)
        self.status_label.setText("Conversation in progress...")
        
    def pause_conversation(self):
        """Pause the current conversation."""
        if self.conversation_manager:
            if self.conversation_manager.is_paused:
                self.conversation_manager.resume_conversation()
                self.pause_button.setText("Pause")
                self.status_label.setText("Conversation resumed...")
            else:
                self.conversation_manager.pause_conversation()
                self.pause_button.setText("Resume")
                self.status_label.setText("Conversation paused...")
                
    def stop_conversation(self):
        """Stop the current conversation."""
        if self.conversation_manager:
            self.conversation_manager.stop_conversation()
            
    def on_message_received(self, sender_id: str, message: str):
        """Handle received message from AI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Define colors for each AI
        ai_colors = {
            'ai1': '#0066cc',  # Blue
            'ai2': '#28a745',  # Green
            'ai3': '#dc3545',  # Red (for future use)
            'ai4': '#6f42c1',  # Purple (for future use)
        }
        
        ai_names = {
            'ai1': 'AI-1',
            'ai2': 'AI-2',
            'ai3': 'AI-3',
            'ai4': 'AI-4',
        }
        
        color = ai_colors.get(sender_id, '#000000')
        name = ai_names.get(sender_id, sender_id.upper())
        
        # Theme-aware styling
        if self.dark_mode:
            bg_color = "#2d3748"
            text_color = "#e2e8f0"
            timestamp_color = "#a0aec0"
            shadow = "0 1px 3px rgba(0,0,0,0.3)"
        else:
            bg_color = "#ffffff"
            text_color = "#2d3748"
            timestamp_color = "#6c757d"
            shadow = "0 1px 3px rgba(0,0,0,0.1)"
        
        # Format message like a group chat
        formatted_message = f'''
        <div style="margin: 10px 0; padding: 12px; background-color: {bg_color}; border-radius: 8px; border-left: 4px solid {color}; box-shadow: {shadow};">
            <div style="margin-bottom: 6px;">
                <strong style="color: {color}; font-size: 13px;">{name}</strong> 
                <span style="color: {timestamp_color}; font-size: 11px; margin-left: 8px;">{timestamp}</span>
            </div>
            <div style="color: {text_color}; line-height: 1.5; font-size: 12px;">
                {message}
            </div>
        </div>
        '''
        
        # Add to conversation display
        cursor = self.conversation_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Add a line break before each new message if there's already content
        if self.conversation_display.toPlainText():
            cursor.insertHtml("<br>")
        
        cursor.insertHtml(formatted_message)
        
        # Auto-scroll to bottom
        self.conversation_display.ensureCursorVisible()
        
        # Update progress
        current_messages = len(self.conversation_history) + 1
        self.progress_bar.setValue(current_messages)
        
        # Store in history
        self.conversation_history.append({
            'sender': sender_id,
            'message': message,
            'timestamp': timestamp
        })
        
    def on_conversation_ended(self):
        """Handle conversation completion."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.progress_bar.setVisible(False)
        self.status_label.setText("Conversation completed")
        
        # Enable analysis button
        self.analyze_button.setEnabled(True)
        
    def on_error_occurred(self, error_message: str):
        """Handle errors during conversation."""
        QMessageBox.critical(self, "Error", error_message)
        self.on_conversation_ended()
        
    def export_conversation(self):
        """Export conversation to JSON file."""
        if not self.conversation_history:
            QMessageBox.information(self, "Info", "No conversation to export")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Conversation", 
            f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                export_data = {
                    'metadata': {
                        'export_time': datetime.now().isoformat(),
                        'message_count': len(self.conversation_history),
                        'ai1_persona': self.persona_ai1_input.toPlainText(),
                        'ai2_persona': self.persona_ai2_input.toPlainText(),
                        'ai1_provider': self.provider_ai1_combo.currentText(),
                        'ai1_model': self.model_ai1_combo.currentText(),
                        'ai2_provider': self.provider_ai2_combo.currentText(),
                        'ai2_model': self.model_ai2_combo.currentText()
                    },
                    'conversation': self.conversation_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Success", f"Conversation exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
                
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Dark mode styling
            self.conversation_display.setStyleSheet("""
                QTextEdit {
                    background-color: #1a202c;
                    color: #e2e8f0;
                    border: 1px solid #4a5568;
                    border-radius: 8px;
                    padding: 15px;
                    selection-background-color: #4a5568;
                }
            """)
            self.theme_button.setText("☀️ Light Mode")
        else:
            # Light mode styling
            self.conversation_display.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #2d3748;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 15px;
                    selection-background-color: #e2e8f0;
                }
            """)
            self.theme_button.setText("🌙 Dark Mode")
            
    def load_settings(self):
        """Load settings from config file if it exists."""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    
                # Load conversation settings
                if 'message_limit' in settings:
                    self.message_limit_spin.setValue(settings['message_limit'])
                if 'message_delay' in settings:
                    self.message_delay_spin.setValue(settings['message_delay'])
                if 'max_tokens' in settings:
                    self.max_tokens_spin.setValue(settings['max_tokens'])
                    
                # Load provider/model settings
                if 'provider_ai1' in settings:
                    index = self.provider_ai1_combo.findText(settings['provider_ai1'])
                    if index >= 0:
                        self.provider_ai1_combo.setCurrentIndex(index)
                        
                if 'provider_ai2' in settings:
                    index = self.provider_ai2_combo.findText(settings['provider_ai2'])
                    if index >= 0:
                        self.provider_ai2_combo.setCurrentIndex(index)
                        
                # Update model options after setting providers
                self.update_model_options()
                        
                if 'model_ai1' in settings:
                    index = self.model_ai1_combo.findText(settings['model_ai1'])
                    if index >= 0:
                        self.model_ai1_combo.setCurrentIndex(index)
                        
                if 'model_ai2' in settings:
                    index = self.model_ai2_combo.findText(settings['model_ai2'])
                    if index >= 0:
                        self.model_ai2_combo.setCurrentIndex(index)
                    
            except Exception as e:
                print(f"Failed to load settings: {e}")
                
    def save_settings(self):
        """Save current settings to config file."""
        settings = {
            'message_limit': self.message_limit_spin.value(),
            'message_delay': self.message_delay_spin.value(),
            'max_tokens': self.max_tokens_spin.value(),
            'provider_ai1': self.provider_ai1_combo.currentText(),
            'model_ai1': self.model_ai1_combo.currentText(),
            'provider_ai2': self.provider_ai2_combo.currentText(),
            'model_ai2': self.model_ai2_combo.currentText()
        }
        
        try:
            with open("config.json", 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            
    def closeEvent(self, event):
        """Handle application close."""
        if self.conversation_manager and self.conversation_manager.is_running:
            self.conversation_manager.stop_conversation()
        self.save_settings()
        event.accept()


def main():
    """Main application entry point."""
    print(f"Starting AI Conversation Tool with {GUI_FRAMEWORK}")
    
    app = QApplication(sys.argv)
    app.setApplicationName("AI Self-Conversation Experiment")
    app.setApplicationVersion("1.0")
    
    window = AIConversationApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()