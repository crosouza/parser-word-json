"""
Optional Flask server for the parser.
"""
import base64
import tempfile
import os
from flask import Flask, request, jsonify
from parser.extractor import parse_docx
from parser.schema import ParsedDocument

def create_app():
    """Creates a Flask app instance."""
    app = Flask(__name__)

    @app.route("/parse", methods=["POST"])
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

            parsed_data = parse_docx(temp_filepath)
            
            os.remove(temp_filepath)

            # Validate and serialize
            validated_data = ParsedDocument(**parsed_data)
            return jsonify(validated_data.model_dump(by_alias=True))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
