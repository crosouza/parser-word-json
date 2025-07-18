"""
Utility functions for the parser.
"""
import re
from docx.text.paragraph import Paragraph

def is_subject_primary(p: Paragraph) -> bool:
    """
    Checks if a paragraph is a primary subject.
    Heuristic: Heading 3 style, or all caps and length < 60.
    """
    text = p.text.strip()
    if text in ["CERTO", "ERRADO"]:
        return False
    if p.style.name == 'Heading 3':
        return True
    if p.style.name == 'Normal' and text.isupper() and len(text) < 60:
        return True
    return False

def is_theory_slide(p: Paragraph) -> bool:
    """Checks if a paragraph is a theory slide."""
    return p.style.name == 'Heading 4'

def is_exercise_intro(p: str) -> bool:
    """
    Checks if a paragraph is an exercise intro.
    Catches variations like 'Questões – Exercício', 'Questões de Exercício', etc.
    """
    return bool(re.search(r'quest(ões|ão)[^\n]{0,20}exerc', p, re.IGNORECASE))

def is_answer(p: str) -> bool:
    """
    Checks if a paragraph is an answer.
    Looks for 'gabarito', 'resposta', 'alternativa correta', 'correto'.
    """
    return bool(re.search(r'gabarito|resposta|alternativa correta|correto', p, re.IGNORECASE))

def is_option(p: str) -> bool:
    """
    Checks if a paragraph is an exercise option.
    Accepts 'A)', 'A.', '(A)', '[A]'.
    """
    return bool(re.match(r'^[A-Ea-e][\)\.\]]|^•', p)) or p in ["CERTO", "ERRADO"]
