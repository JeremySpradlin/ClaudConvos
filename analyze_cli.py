#!/usr/bin/env python3
"""
Command-line NLP Analysis Tool for AI Conversations
"""

import sys
import json
import argparse
from pathlib import Path

# Import our analysis modules
try:
    from analysis.nlp_analyzer import ConversationAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Analysis modules not available: {e}")
    print("Run: python -m pip install -r requirements.txt")
    ANALYSIS_AVAILABLE = False
    sys.exit(1)


def analyze_conversation(file_path: str, output_format: str = "json"):
    """Analyze a conversation file and output results."""
    if not Path(file_path).exists():
        print(f"Error: File {file_path} not found")
        return False
    
    print(f"Analyzing conversation: {file_path}")
    print("=" * 50)
    
    analyzer = ConversationAnalyzer()
    
    try:
        # Load conversation
        print("Loading conversation...")
        conversation_data = analyzer.load_conversation(file_path)
        
        # Basic statistics
        print("\\nCalculating basic statistics...")
        stats = analyzer.basic_stats(conversation_data)
        
        # Sentiment analysis
        print("Performing sentiment analysis...")
        sentiment = analyzer.sentiment_analysis(conversation_data)
        
        # Word frequency analysis
        print("Analyzing word frequency...")
        words = analyzer.word_frequency_analysis(conversation_data)
        
        # Conversation flow
        print("Analyzing conversation flow...")
        flow = analyzer.conversation_flow_analysis(conversation_data)
        
        # Topic modeling
        print("Performing topic modeling...")
        topics = analyzer.topic_modeling(conversation_data, n_topics=3)
        
        # Compile results
        results = {
            'file_analyzed': file_path,
            'basic_stats': stats,
            'sentiment_analysis': sentiment,
            'word_frequency': words,
            'conversation_flow': flow,
            'topic_modeling': topics
        }
        
        # Output results
        if output_format == "json":
            output_file = Path(file_path).stem + "_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\\n✓ Analysis complete! Results saved to: {output_file}")
        else:
            print_analysis_summary(results)
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False


def print_analysis_summary(results):
    """Print a human-readable summary of the analysis."""
    print("\\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Basic stats
    stats = results.get('basic_stats', {})
    if stats:
        print(f"\\n📊 BASIC STATISTICS:")
        print(f"   Total Messages: {stats.get('total_messages', 0)}")
        print(f"   Average Message Length: {stats.get('average_message_length', 0):.1f} words")
        print(f"   Conversation Duration: {stats.get('conversation_duration', 'Unknown')}")
        
        ai_counts = stats.get('ai_message_counts', {})
        if ai_counts:
            print(f"   Message Distribution:")
            for ai, count in ai_counts.items():
                print(f"     {ai.upper()}: {count} messages")
    
    # Sentiment
    sentiment = results.get('sentiment_analysis', {})
    overall_sentiment = sentiment.get('overall_sentiment', {})
    if overall_sentiment:
        print(f"\\n😊 SENTIMENT ANALYSIS:")
        for ai, scores in overall_sentiment.items():
            compound = scores.get('compound', 0)
            if compound > 0.1:
                mood = "Positive"
            elif compound < -0.1:
                mood = "Negative"
            else:
                mood = "Neutral"
            print(f"   {ai.upper()}: {mood} (score: {compound:.3f})")
    
    # Word frequency
    words = results.get('word_frequency', {})
    overall_freq = words.get('overall_word_frequency', {})
    if overall_freq:
        print(f"\\n📝 WORD FREQUENCY:")
        top_words = list(overall_freq.items())[:10]
        print(f"   Top 10 words: {', '.join([word for word, count in top_words])}")
        print(f"   Total unique words: {words.get('total_unique_words', 0)}")
    
    # Flow
    flow = results.get('conversation_flow', {})
    if flow:
        print(f"\\n💬 CONVERSATION FLOW:")
        print(f"   Turn changes: {flow.get('turn_changes', 0)}")
        engagement = flow.get('conversation_engagement', {})
        if engagement:
            print(f"   Engagement score: {engagement.get('engagement_score', 0):.3f}")
    
    # Topics
    topics = results.get('topic_modeling', {})
    if 'topics' in topics:
        print(f"\\n🔍 TOPIC MODELING:")
        for i, topic in enumerate(topics['topics'][:3], 1):
            top_words = topic.get('top_words', [])[:5]
            print(f"   Topic {i}: {', '.join(top_words)}")
    elif 'error' in topics:
        print(f"\\n🔍 TOPIC MODELING: {topics['error']}")


def list_conversations():
    """List available conversation files."""
    json_files = list(Path('.').glob('*.json'))
    conversation_files = [f for f in json_files if 'conversation_' in f.name]
    
    if conversation_files:
        print("Available conversation files:")
        for i, file in enumerate(conversation_files, 1):
            print(f"  {i}. {file.name}")
        return conversation_files
    else:
        print("No conversation files found in current directory.")
        return []


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Analyze AI conversation files")
    parser.add_argument('file', nargs='?', help='Conversation JSON file to analyze')
    parser.add_argument('--format', choices=['json', 'summary'], default='summary',
                       help='Output format (default: summary)')
    parser.add_argument('--list', action='store_true', help='List available conversation files')
    
    args = parser.parse_args()
    
    if args.list:
        list_conversations()
        return
    
    if not args.file:
        print("AI Conversation Analysis Tool")
        print("=" * 30)
        
        # Show available files
        files = list_conversations()
        
        if files:
            print("\\nSelect a file to analyze:")
            try:
                choice = input("Enter file number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return
                
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(files):
                    args.file = str(files[file_idx])
                else:
                    print("Invalid selection.")
                    return
            except (ValueError, KeyboardInterrupt):
                print("\\nExiting...")
                return
        else:
            print("\\nUsage: python analyze_cli.py <conversation_file.json>")
            return
    
    # Analyze the selected file
    if analyze_conversation(args.file, args.format):
        print("\\n✓ Analysis completed successfully!")
    else:
        print("\\n✗ Analysis failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()