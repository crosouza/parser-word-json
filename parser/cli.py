"""
Command-Line Interface for the parser.
"""
import argparse
import json
import sys
import os
import logging
from parser.extractor import parse_docx
from parser.schema import ParsedDocument


def main():
    """
    Main function for the CLI.
    """
    # Set up logging
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Reconfigure stdout to use utf-8 encoding
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Parse a .docx file to a canonical JSON format.")
    parser.add_argument("-i", "--input", help="Path to the .docx file. Required if not in serve mode.")
    parser.add_argument("-o", "--output", help="Path to the output .json file. Defaults to stdout.")
    parser.add_argument("--json-indent", type=int, default=2, help="Indentation for the JSON output.")
    parser.add_argument("--serve", action="store_true", help="Run as a web server.")
    
    args = parser.parse_args()

    if args.serve:
        try:
            from parser.server import create_app
            app = create_app()
            port = int(os.getenv("PORT", 5000))
            logging.info(f"Starting server on port {port}...")
            app.run(host="0.0.0.0", port=port)
        except ImportError:
            logging.error("Flask is not installed. Please install it with 'pip install Flask'")
            sys.exit(1)
        return

    if not args.input:
        parser.error("--input is required when not in --serve mode.")

    try:
        logging.info(f"Parsing document: {args.input}")
        parsed_data = parse_docx(args.input)
        
        # Validate with Pydantic
        validated_data = ParsedDocument(**parsed_data)
        
        output_json = validated_data.model_dump_json(indent=args.json_indent, by_alias=True)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            logging.info(f"Successfully parsed {args.input} to {args.output}")
        else:
            # For stdout, we keep the print to just output the JSON
            print(output_json)

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
