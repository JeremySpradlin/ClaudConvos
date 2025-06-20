#!/usr/bin/env python3
"""
Terminal-based AI Conversation Tool
"""

import sys
import json
import asyncio
from datetime import datetime
from typing import Dict
import os

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ConversationRunner:
    """Manages AI conversations in the terminal."""
    
    def __init__(self):
        """Initialize the conversation runner."""
        # Check API keys
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        self.anthropic_client = None
        self.openai_client = None
        
        if ANTHROPIC_AVAILABLE and self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        if OPENAI_AVAILABLE and self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
        
        self.conversation_history = []
        
    def get_ai_response(self, message: str, persona: str, speaker_id: str) -> str:
        """Get response from AI."""
        system_prompt = f"""You are {speaker_id.upper()}. {persona}
        
You are having a conversation with another AI. Keep your responses conversational, 
thoughtful, and engaging. Aim for 1-3 sentences unless the topic requires more depth."""
        
        try:
            if self.anthropic_client:
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
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=200,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
            elif self.openai_client:
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
                    model='gpt-4o-mini',
                    max_tokens=200,
                    messages=messages
                )
                return response.choices[0].message.content
            else:
                return f"[Mock response from {speaker_id}: {message[:50]}... (No API available)]"
                
        except Exception as e:
            return f"[Error from {speaker_id}: {str(e)}]"
    
    def run_conversation(self, config: Dict):
        """Run a conversation between two AIs."""
        print("\\n" + "="*60)
        print("🤖 AI SELF-CONVERSATION EXPERIMENT")
        print("="*60)
        
        # Show configuration
        print(f"Message Limit: {config.get('message_limit', 10)}")
        print(f"Message Delay: {config.get('message_delay', 2)} seconds")
        print(f"AI 1 Persona: {config.get('persona_ai1', 'Default') or 'Default'}")
        print(f"AI 2 Persona: {config.get('persona_ai2', 'Default') or 'Default'}")
        print()
        
        # Check API availability
        if not self.anthropic_client and not self.openai_client:
            print("⚠️  No API keys found. Using mock responses.")
            print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables.")
        elif self.anthropic_client:
            print("✅ Using Anthropic Claude API")
        elif self.openai_client:
            print("✅ Using OpenAI GPT API")
        
        print("\\nStarting conversation...\\n")
        
        # Initialize conversation
        current_speaker = "ai1"
        message = config.get('initial_prompt', "Hello! Let's have an interesting conversation.")
        message_count = 0
        max_messages = config.get('message_limit', 10)
        
        try:
            while message_count < max_messages:
                # Get AI response
                if current_speaker == "ai1":
                    persona = config.get('persona_ai1', '')
                    next_speaker = "ai2"
                    color_code = "\\033[94m"  # Blue
                else:
                    persona = config.get('persona_ai2', '')
                    next_speaker = "ai1"
                    color_code = "\\033[92m"  # Green
                
                print(f"{color_code}🤖 {current_speaker.upper()}:\\033[0m", end=" ")
                print("Thinking...", end="", flush=True)
                
                response = self.get_ai_response(message, persona, current_speaker)
                
                # Clear "thinking" and show response
                print("\\r" + " " * 20 + "\\r", end="")  # Clear line
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{color_code}🤖 {current_speaker.upper()} [{timestamp}]:\\033[0m")
                print(f"   {response}")
                print()
                
                # Store in history
                self.conversation_history.append({
                    'speaker': current_speaker,
                    'message': response,
                    'timestamp': timestamp
                })
                
                # Switch speakers
                message = response
                current_speaker = next_speaker
                message_count += 1
                
                # Add delay
                if message_count < max_messages:
                    delay = config.get('message_delay', 2)
                    if delay > 0:
                        print(f"⏳ Waiting {delay} seconds...")
                        import time
                        time.sleep(delay)
                        print()
        
        except KeyboardInterrupt:
            print("\\n\\n⏹️  Conversation stopped by user")
        
        print("\\n" + "="*60)
        print(f"✅ Conversation completed! {len(self.conversation_history)} messages exchanged.")
        print("="*60)
        
        return self.conversation_history
    
    def export_conversation(self, filename: str = None):
        """Export conversation to JSON file."""
        if not self.conversation_history:
            print("No conversation to export")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"conversation_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'export_time': datetime.now().isoformat(),
                'message_count': len(self.conversation_history),
                'tool': 'conversation_cli'
            },
            'conversation': self.conversation_history
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"📁 Conversation exported to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None


def get_user_config():
    """Get configuration from user input."""
    print("🔧 CONVERSATION CONFIGURATION")
    print("-" * 30)
    
    config = {}
    
    try:
        # Message limit
        limit = input("Message limit (default 10): ").strip()
        config['message_limit'] = int(limit) if limit else 10
        
        # Message delay
        delay = input("Delay between messages in seconds (default 2): ").strip()
        config['message_delay'] = float(delay) if delay else 2.0
        
        # AI personas
        print("\\nAI Personas (press Enter for default):")
        config['persona_ai1'] = input("AI 1 persona: ").strip()
        config['persona_ai2'] = input("AI 2 persona: ").strip()
        
        # Initial prompt
        config['initial_prompt'] = input("Initial prompt (optional): ").strip()
        if not config['initial_prompt']:
            config['initial_prompt'] = "Hello! Let's have an interesting conversation."
        
        return config
        
    except KeyboardInterrupt:
        print("\\n\\nConfiguration cancelled.")
        return None
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None


def main():
    """Main CLI entry point."""
    print("🤖 AI Self-Conversation Tool (Terminal Edition)")
    print("=" * 50)
    
    # Check API availability
    anthropic_available = bool(os.getenv('ANTHROPIC_API_KEY'))
    openai_available = bool(os.getenv('OPENAI_API_KEY'))
    
    print("API Status:")
    print(f"  Anthropic: {'✅ Available' if anthropic_available else '❌ Missing ANTHROPIC_API_KEY'}")
    print(f"  OpenAI:    {'✅ Available' if openai_available else '❌ Missing OPENAI_API_KEY'}")
    
    if not anthropic_available and not openai_available:
        print("\\n⚠️  Warning: No API keys found. Will use mock responses for demonstration.")
        proceed = input("\\nProceed anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            print("Exiting...")
            return
    
    print()
    
    # Get configuration
    config = get_user_config()
    if not config:
        return
    
    # Run conversation
    runner = ConversationRunner()
    conversation = runner.run_conversation(config)
    
    if conversation:
        # Ask about export
        export = input("\\nExport conversation to JSON? (Y/n): ").strip().lower()
        if export != 'n':
            filename = runner.export_conversation()
            if filename:
                print("\\n🔍 You can analyze this conversation with:")
                print(f"   python analyze_cli.py {filename}")


if __name__ == "__main__":
    main()