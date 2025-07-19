import base64
import tempfile
import os
import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from parser.extractor import parse_docx
from parser.schema import ParsedDocument

def create_app():
    """Creates a Flask app instance."""
    app = Flask(__name__)

    # Set up rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["60 per minute"],
        storage_uri="memory://",
    )

    @app.route("/parse", methods=["POST"])
    @limiter.limit("60/minute")
    def parse_endpoint():
        """
        Parses a .docx file provided as a base64 string.
        """
        data = request.get_json()
        if not data or "file" not in data:
            return jsonify({"error": "Missing 'file' in request body."}), 400

        try:
            decoded_file = base64.b64decode(data["file"])
            
            # Use a temporary file to save the docx content
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_f:
                temp_f.write(decoded_file)
                temp_filepath = temp_f.name
            
            logging.info(f"Parsing temporary file: {temp_filepath}")
            parsed_data = parse_docx(temp_filepath)
            
            os.remove(temp_filepath)

            # Validate and serialize
            validated_data = ParsedDocument(**parsed_data)
            logging.info("Successfully parsed document from request.")
            return jsonify(validated_data.model_dump(by_alias=True))

        except Exception as e:
            logging.error(f"An error occurred during parsing: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
