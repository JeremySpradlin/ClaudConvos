#!/usr/bin/env python3
"""
PDF Export Utility for AI Conversations
Converts conversation data to formatted PDF files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import Color, black, blue, green, grey
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def is_pdf_export_available() -> bool:
    """Check if PDF export is available."""
    return REPORTLAB_AVAILABLE


def create_pdf_styles():
    """Create custom styles for the PDF."""
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles for different speakers
    styles.add(ParagraphStyle(
        name='AI1_Message',
        parent=styles['Normal'],
        leftIndent=15,
        rightIndent=100,
        spaceAfter=16,
        spaceBefore=4,
        fontSize=12,
        leading=16,
        textColor=Color(0.1, 0.2, 0.7),  # Darker blue for better readability
        borderColor=Color(0.2, 0.4, 0.8),
        borderWidth=1.5,
        borderPadding=14,
        backColor=Color(0.97, 0.98, 1.0),  # Very light blue background
    ))
    
    styles.add(ParagraphStyle(
        name='AI2_Message',
        parent=styles['Normal'],
        leftIndent=100,
        rightIndent=15,
        spaceAfter=16,
        spaceBefore=4,
        fontSize=12,
        leading=16,
        textColor=Color(0.1, 0.5, 0.2),  # Darker green for better readability
        borderColor=Color(0.2, 0.6, 0.3),
        borderWidth=1.5,
        borderPadding=14,
        backColor=Color(0.97, 1.0, 0.97),  # Very light green background
    ))
    
    styles.add(ParagraphStyle(
        name='Timestamp',
        parent=styles['Normal'],
        fontSize=10,
        textColor=Color(0.5, 0.5, 0.5),
        alignment=1,  # Center alignment
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Oblique'
    ))
    
    # Full-width speaker labels that won't get cut off
    styles.add(ParagraphStyle(
        name='AI1_SpeakerLabel',
        parent=styles['Normal'],
        fontSize=12,
        textColor=Color(0.1, 0.2, 0.7),
        fontName='Helvetica-Bold',
        spaceAfter=2,
        spaceBefore=4,
        leftIndent=15,
        rightIndent=15,  # Don't restrict the right side too much
        alignment=0  # Left alignment
    ))
    
    styles.add(ParagraphStyle(
        name='AI2_SpeakerLabel',
        parent=styles['Normal'],
        fontSize=12,
        textColor=Color(0.1, 0.5, 0.2),
        fontName='Helvetica-Bold',
        spaceAfter=2,
        spaceBefore=4,
        leftIndent=15,
        rightIndent=15,
        alignment=2  # Right alignment for AI2
    ))
    
    # Add a style for metadata with better formatting
    styles.add(ParagraphStyle(
        name='MetadataBox',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=16,
        spaceBefore=8,
        borderColor=Color(0.6, 0.6, 0.6),
        borderWidth=1,
        borderPadding=12,
        backColor=Color(0.98, 0.98, 0.98)
    ))
    
    return styles


def clean_model_name(model_name: str) -> str:
    """Convert technical model names to friendly names."""
    if not model_name:
        return ""
    
    model_mapping = {
        'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
        'claude-3-5-sonnet': 'Claude 3.5 Sonnet', 
        'gpt-4o-mini': 'GPT-4o Mini',
        'gpt-4o': 'GPT-4o',
        'gpt-4': 'GPT-4',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo'
    }
    
    return model_mapping.get(model_name.lower(), model_name)


def export_conversation_to_pdf(conversation_data: Dict, output_file: str) -> bool:
    """
    Export conversation data to PDF format.
    
    Args:
        conversation_data: Dictionary containing conversation data
        output_file: Path to output PDF file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab library not installed. Install with: pip install reportlab")
    
    try:
        # Create PDF document with better margins
        doc = SimpleDocTemplate(
            str(output_file), 
            pagesize=A4,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch
        )
        story = []
        styles = create_pdf_styles()
        
        # Add title with better styling
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=22,
            spaceAfter=0.25*inch,
            textColor=Color(0.2, 0.2, 0.2),
            alignment=1  # Center alignment
        )
        story.append(Paragraph("🤖 AI Conversation Report", title_style))
        
        # Add metadata information in a box
        metadata = conversation_data.get('metadata', {})
        if metadata:
            # Create metadata content
            export_time = metadata.get('export_time', 'Unknown')
            if export_time != 'Unknown':
                try:
                    dt = datetime.fromisoformat(export_time.replace('Z', '+00:00'))
                    export_time = dt.strftime('%Y-%m-%d at %H:%M:%S')
                except:
                    pass
            
            metadata_content = [
                f"<b>📅 Export Time:</b> {export_time}",
                f"<b>💬 Message Count:</b> {metadata.get('message_count', 'Unknown')}",
            ]
            
            # Add AI information with cleaned model names
            ai1_provider = metadata.get('ai1_provider', '')
            ai1_model = clean_model_name(metadata.get('ai1_model', ''))
            ai2_provider = metadata.get('ai2_provider', '')
            ai2_model = clean_model_name(metadata.get('ai2_model', ''))
            
            if ai1_provider and ai1_model:
                ai1_info = f"AI1 ({ai1_provider.title()} - {ai1_model})"
            elif ai1_model:
                ai1_info = f"AI1 ({ai1_model})"
            else:
                ai1_info = "AI1"
            
            if ai2_provider and ai2_model:
                ai2_info = f"AI2 ({ai2_provider.title()} - {ai2_model})"
            elif ai2_model:
                ai2_info = f"AI2 ({ai2_model})"
            else:
                ai2_info = "AI2"
            
            metadata_content.extend([
                f"<b>🔵 {ai1_info}</b>",
                f"<b>🟢 {ai2_info}</b>"
            ])
            
            # Add persona information if available
            if metadata.get('ai1_persona'):
                metadata_content.append(f"<b>🎭 AI1 Persona:</b> {metadata['ai1_persona']}")
            if metadata.get('ai2_persona'):
                metadata_content.append(f"<b>🎭 AI2 Persona:</b> {metadata['ai2_persona']}")
            
            # Combine metadata into a single paragraph
            metadata_text = "<br/>".join(metadata_content)
            story.append(Paragraph(metadata_text, styles['MetadataBox']))
            story.append(Spacer(1, 0.2*inch))
        
        # Add conversation header
        conversation_header = ParagraphStyle(
            'ConversationHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=0.15*inch,
            textColor=Color(0.3, 0.3, 0.3),
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("💬 Conversation", conversation_header))
        
        # Process messages with enhanced formatting
        messages = conversation_data.get('conversation', [])
        
        # Get clean model information for speaker labels
        ai1_model_clean = clean_model_name(metadata.get('ai1_model', ''))
        ai2_model_clean = clean_model_name(metadata.get('ai2_model', ''))
        
        for i, msg in enumerate(messages):
            sender = msg.get('sender', msg.get('speaker', 'unknown'))
            message = msg.get('message', '')
            timestamp = msg.get('timestamp', '')
            
            # Add timestamp with better formatting
            if timestamp:
                story.append(Paragraph(f"⏰ {timestamp}", styles['Timestamp']))
            
            # Create enhanced speaker label with clean model info
            if sender.lower() == 'ai1':
                if ai1_model_clean:
                    speaker_label = f"🔵 AI1 • {ai1_model_clean}"
                else:
                    speaker_label = "🔵 AI1"
                speaker_style = styles['AI1_SpeakerLabel']
                msg_style = styles['AI1_Message']
            else:
                if ai2_model_clean:
                    speaker_label = f"🟢 AI2 • {ai2_model_clean}"
                else:
                    speaker_label = "🟢 AI2"
                speaker_style = styles['AI2_SpeakerLabel']
                msg_style = styles['AI2_Message']
            
            story.append(Paragraph(speaker_label, speaker_style))
            
            # Clean and format message text with better handling
            clean_message = message.replace('\n', '<br/>')
            clean_message = clean_message.replace('&', '&amp;')
            clean_message = clean_message.replace('<', '&lt;')
            clean_message = clean_message.replace('>', '&gt;')
            clean_message = clean_message.replace('<br/>', '<br/>')  # Restore line breaks
            
            story.append(Paragraph(clean_message, msg_style))
            
            # Add spacing between messages
            if i < len(messages) - 1:
                story.append(Spacer(1, 0.12*inch))
        
        # Add footer
        story.append(Spacer(1, 0.25*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=Color(0.6, 0.6, 0.6),
            alignment=1
        )
        story.append(Paragraph("Generated by AI Conversation Tool", footer_style))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False


def export_conversation_from_json_file(json_file: str, output_file: str) -> bool:
    """
    Export conversation from JSON file to PDF.
    
    Args:
        json_file: Path to JSON conversation file
        output_file: Path to output PDF file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        return export_conversation_to_pdf(conversation_data, output_file)
    except Exception as e:
        print(f"Error loading conversation file: {e}")
        return False


def get_pdf_filename_from_json_filename(json_filename: str) -> str:
    """Generate a PDF filename from a JSON filename."""
    json_path = Path(json_filename)
    return str(json_path.parent / f"{json_path.stem}.pdf") 