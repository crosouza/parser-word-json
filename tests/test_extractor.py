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

    assert len(parsed_data['warnings']) >= 2
    assert "Course title might be incorrect" in parsed_data['warnings'][0]
    assert "is missing an answer" in parsed_data['warnings'][1]

def test_no_theory_document():
    """Tests a document with no theory slides."""
    docx_path = os.path.join(SAMPLES_DIR, 'sample_no_theory.docx')
    parsed_data = parse_docx(docx_path)
    assert not parsed_data['sections'][0]['theorySlides']
    assert parsed_data['sections'][0]['exercises']

def test_no_exercises_document():
    """Tests a document with subjects but no exercises."""
    docx_path = os.path.join(SAMPLES_DIR, 'sample_no_exercises.docx')
    parsed_data = parse_docx(docx_path)
    assert len(parsed_data['sections']) == 2
    assert not parsed_data['sections'][0]['exercises']
    assert not parsed_data['sections'][1]['exercises']

def test_missing_alternatives_warning():
    """Tests that a warning is generated for an exercise with no options."""
    docx_path = os.path.join(SAMPLES_DIR, 'sample_missing_alternatives.docx')
    parsed_data = parse_docx(docx_path)
    assert "is missing options" in parsed_data['warnings'][0]

def test_google_docs_export():
    """Tests parsing of a document exported from Google Docs (no styles)."""
    docx_path = os.path.join(SAMPLES_DIR, 'sample_google_docs.docx')
    parsed_data = parse_docx(docx_path)
    assert parsed_data['courseTitle'] == "COURSE TITLE"
    assert parsed_data['notebookTitle'] == "NOTEBOOK 1"
    assert parsed_data['sections'][0]['subjectPrimary'] == "SUBJECT 1"

def test_alternative_markers():
    """Tests parsing with alternative exercise markers."""
    docx_path = os.path.join(SAMPLES_DIR, 'sample_alt_markers.docx')
    parsed_data = parse_docx(docx_path)
    exercises = parsed_data['sections'][0]['exercises']
    assert len(exercises) == 1
    assert len(exercises[0]['options']) == 3
    assert exercises[0]['answer'] == "B"
