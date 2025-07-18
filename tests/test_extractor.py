"""
Tests for the extractor.
"""
import os
import json
from parser.extractor import parse_docx

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'samples')

def test_document_with_multiple_sections():
    """
    Tests parsing of a document with multiple sections.
    """
    docx_path = os.path.join(SAMPLES_DIR, 'sample1.docx')
    json_path = os.path.join(SAMPLES_DIR, 'sample1.json')

    parsed_data = parse_docx(docx_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        expected_data = json.load(f)

    assert parsed_data == expected_data

def test_document_with_warnings():
    """
    Tests parsing of a document that should generate warnings.
    """
    docx_path = os.path.join(SAMPLES_DIR, 'sample2.docx')
    
    parsed_data = parse_docx(docx_path)

    assert len(parsed_data['warnings']) == 2
    assert "Course title might be incorrect" in parsed_data['warnings'][0]
    assert "is missing an answer" in parsed_data['warnings'][1]
