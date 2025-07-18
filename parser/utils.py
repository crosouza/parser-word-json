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
    Accepts markers like 'A)', 'A.', '(A)', '[A]', and bullet points.
    """
    # Regex explained:
    # ^\s*         - Start of string with optional whitespace
    # [\(\[]?      - Optional opening parenthesis or bracket
    # [A-Ea-e]     - An uppercase or lowercase letter from A to E
    # [\.\)\]]     - A literal dot, closing parenthesis, or closing bracket
    # |^•          - OR a bullet point at the start of the string
    p_stripped = p.strip()
    return bool(re.match(r'^\s*[\(\[]?[A-Ea-e][\.\)\]]|^•', p_stripped)) or p_stripped in ["CERTO", "ERRADO"]
