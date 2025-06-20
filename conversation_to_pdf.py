#!/usr/bin/env python3
"""
Standalone Conversation JSON to PDF Converter
Usage: python conversation_to_pdf.py <conversation.json> [output.pdf]
"""

import sys
import argparse
from pathlib import Path

try:
    from pdf_export import export_conversation_from_json_file, is_pdf_export_available
except ImportError:
    print("Error: pdf_export module not found. Make sure pdf_export.py is in the same directory.")
    sys.exit(1)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Convert AI conversation JSON files to PDF format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python conversation_to_pdf.py conversation_20250531_182120.json
  python conversation_to_pdf.py conversation.json my_conversation.pdf
  python conversation_to_pdf.py *.json  # Convert all JSON files
        """
    )
    
    parser.add_argument('input_files', nargs='+', 
                       help='Input JSON conversation file(s)')
    parser.add_argument('-o', '--output', 
                       help='Output PDF file (for single input file)')
    parser.add_argument('--check', action='store_true',
                       help='Check if PDF export is available')
    
    args = parser.parse_args()
    
    # Check PDF export availability
    if args.check or not is_pdf_export_available():
        if is_pdf_export_available():
            print("✅ PDF export is available")
            if args.check:
                return
        else:
            print("❌ PDF export is not available")
            print("Install reportlab with: pip install reportlab")
            sys.exit(1)
    
    # Handle multiple input files
    if len(args.input_files) > 1 and args.output:
        print("❌ Error: Cannot specify output file when processing multiple inputs")
        sys.exit(1)
    
    success_count = 0
    total_count = 0
    
    for input_file in args.input_files:
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"❌ Error: File '{input_file}' not found")
            continue
            
        if not input_path.suffix.lower() == '.json':
            print(f"⚠️  Warning: '{input_file}' doesn't appear to be a JSON file, skipping")
            continue
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            output_file = input_path.parent / f"{input_path.stem}.pdf"
        
        print(f"🔄 Converting '{input_file}' to '{output_file}'...")
        
        try:
            success = export_conversation_from_json_file(str(input_path), str(output_file))
            
            if success:
                print(f"✅ Successfully created '{output_file}'")
                success_count += 1
            else:
                print(f"❌ Failed to create '{output_file}'")
                
        except Exception as e:
            print(f"❌ Error processing '{input_file}': {e}")
        
        total_count += 1
    
    # Summary
    print(f"\n📊 Summary: {success_count}/{total_count} files converted successfully")
    
    if success_count == total_count and total_count > 0:
        print("🎉 All conversions completed successfully!")
    elif success_count > 0:
        print("⚠️  Some conversions completed with errors")
    else:
        print("💥 No files were converted successfully")


if __name__ == "__main__":
    main() 