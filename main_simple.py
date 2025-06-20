#!/usr/bin/env python3
"""
AI Self-Conversation Experiment Tool - Simplified Version
"""

import sys
import json
from datetime import datetime
from typing import Dict
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSpinBox, QGroupBox,
    QTabWidget, QFileDialog, QMessageBox, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QTextCursor

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
            max_messages = self.config.get('message_limit', 10)
            
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
                return self._get_anthropic_response(message, system_prompt, model, speaker_id)
            elif provider == 'openai':
                return self._get_openai_response(message, system_prompt, model, speaker_id)
            else:
                raise Exception(f"Unknown provider: {provider}")
                
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")
            
    def _get_anthropic_response(self, message: str, system_prompt: str, model: str, speaker_id: str) -> str:
        """Get response from Anthropic API."""
        if not self.anthropic_client:
            raise Exception("Anthropic API key not found in environment")
            
        try:
            # Build conversation history for context
            messages = []
            
            # Add all previous messages from conversation history
            for entry in self.conversation_history:
                if entry['speaker'] == speaker_id:
                    # This speaker's previous messages are "assistant" role
                    messages.append({"role": "assistant", "content": entry['message']})
                else:
                    # Other speaker's messages are "user" role
                    messages.append({"role": "user", "content": entry['message']})
            
            # Add the current message
            messages.append({"role": "user", "content": message})
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=self.config.get('max_tokens', 200),
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
            
    def _get_openai_response(self, message: str, system_prompt: str, model: str, speaker_id: str) -> str:
        """Get response from OpenAI API."""
        if not self.openai_client:
            raise Exception("OpenAI API key not found in environment")
            
        try:
            # Build conversation history for context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add all previous messages from conversation history
            for entry in self.conversation_history:
                if entry['speaker'] == speaker_id:
                    # This speaker's previous messages are "assistant" role
                    messages.append({"role": "assistant", "content": entry['message']})
                else:
                    # Other speaker's messages are "user" role
                    messages.append({"role": "user", "content": entry['message']})
            
            # Add the current message
            messages.append({"role": "user", "content": message})
            
            response = self.openai_client.chat.completions.create(
                model=model,
                max_tokens=self.config.get('max_tokens', 200),
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class SimpleApp(QMainWindow):
    """Simplified main application window."""
    
    def __init__(self):
        super().__init__()
        self.conversation_manager = None
        self.conversation_history = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("AI Self-Conversation Tool (Simple)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Configuration panel
        config_panel = self.create_config_panel()
        layout.addWidget(config_panel, 1)
        
        # Conversation display
        conversation_panel = self.create_conversation_panel()
        layout.addWidget(conversation_panel, 3)
        
    def create_config_panel(self) -> QWidget:
        """Create the configuration panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        settings_layout.addWidget(QLabel("Message Limit:"))
        self.message_limit_spin = QSpinBox()
        self.message_limit_spin.setRange(1, 100)
        self.message_limit_spin.setValue(10)
        settings_layout.addWidget(self.message_limit_spin)
        
        settings_layout.addWidget(QLabel("Delay (ms):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(100, 10000)
        self.delay_spin.setValue(2000)
        settings_layout.addWidget(self.delay_spin)
        
        layout.addWidget(settings_group)
        
        # Personas
        persona_group = QGroupBox("AI Personas")
        persona_layout = QVBoxLayout(persona_group)
        
        persona_layout.addWidget(QLabel("AI 1:"))
        self.persona1_input = QTextEdit()
        self.persona1_input.setMaximumHeight(60)
        self.persona1_input.setPlaceholderText("AI 1 personality...")
        persona_layout.addWidget(self.persona1_input)
        
        persona_layout.addWidget(QLabel("AI 2:"))
        self.persona2_input = QTextEdit()
        self.persona2_input.setMaximumHeight(60)
        self.persona2_input.setPlaceholderText("AI 2 personality...")
        persona_layout.addWidget(self.persona2_input)
        
        layout.addWidget(persona_group)
        
        # Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.start_button = QPushButton("Start Conversation")
        self.start_button.clicked.connect(self.start_conversation)
        controls_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_conversation)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_conversation)
        controls_layout.addWidget(self.export_button)
        
        layout.addWidget(controls_group)
        layout.addStretch()
        
        return widget
    
    def create_conversation_panel(self) -> QWidget:
        """Create the conversation display panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Conversation:"))
        
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setFont(QFont("Monaco", 11))
        layout.addWidget(self.conversation_display)
        
        return widget
    
    def start_conversation(self):
        """Start a new conversation."""
        # Check for API keys
        import os
        if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'):
            QMessageBox.warning(self, "Warning", 
                "No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables.")
            return
        
        # Prepare config
        config = {
            'message_limit': self.message_limit_spin.value(),
            'message_delay': self.delay_spin.value(),
            'max_tokens': 200,
            'persona_ai1': self.persona1_input.toPlainText(),
            'persona_ai2': self.persona2_input.toPlainText(),
            'provider_ai1': 'anthropic',
            'model_ai1': 'claude-3-5-sonnet-20241022',
            'provider_ai2': 'anthropic', 
            'model_ai2': 'claude-3-5-sonnet-20241022'
        }
        
        # Clear display
        self.conversation_display.clear()
        self.conversation_history.clear()
        
        # Start conversation
        self.conversation_manager = ConversationManager(config)
        self.conversation_manager.message_received.connect(self.on_message_received)
        self.conversation_manager.conversation_ended.connect(self.on_conversation_ended)
        self.conversation_manager.error_occurred.connect(self.on_error)
        
        self.conversation_manager.start_conversation()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def stop_conversation(self):
        """Stop the conversation."""
        if self.conversation_manager:
            self.conversation_manager.stop_conversation()
    
    def on_message_received(self, sender: str, message: str):
        """Handle received message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#0066cc" if sender == "ai1" else "#28a745"
        
        formatted = f'<p><strong style="color: {color}">{sender.upper()}</strong> <small>{timestamp}</small><br>{message}</p>'
        
        cursor = self.conversation_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted)
        
        self.conversation_display.ensureCursorVisible()
        
        # Store in history
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
    
    def on_conversation_ended(self):
        """Handle conversation end."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def on_error(self, error: str):
        """Handle errors."""
        QMessageBox.critical(self, "Error", error)
        self.on_conversation_ended()
    
    def export_conversation(self):
        """Export conversation to JSON."""
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
                        'message_count': len(self.conversation_history)
                    },
                    'conversation': self.conversation_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
                    
                QMessageBox.information(self, "Success", f"Exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("AI Conversation Tool")
    
    window = SimpleApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()