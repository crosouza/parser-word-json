"""
Core parsing logic for DOCX files based on a new Markdown-like format.
"""
import re
from typing import List, Tuple
from docx import Document
from docx.text.paragraph import Paragraph
from parser.schema import (
    ParsedDocument,
    Subject,
    TheorySlide,
    Exercise,
    ExerciseQuestion,
    ContestQuestion,
)

# Regex patterns for the new format
COURSE_PATTERN = r"^#\s*Curso:\s*\[?([^\]]+)\]?$"
NOTEBOOK_PATTERN = r"^##\s*Caderno:\s*\[?([^\]]+)\]?$"
PROGRAMMATIC_CONTENT_PATTERN = r"^##\s*Conteúdo Programático:$"
SUBJECT_PATTERN = r"^##\s*Assunto\s*\d+:\s*\[?([^\]]+)\]?$"
THEORY_SLIDE_PATTERN = r"^###\s*Título do Slide \(Teoria\):$"
EXERCISE_STATEMENT_PATTERN = r"^###\s*Enunciado do Exercício:$"
EXERCISE_QUESTIONS_PATTERN = r"^###\s*Questões do Exercício:$"
SIMPLE_QUESTION_PATTERN = r"^[a-z]\)\s*(.+)$"
SIMPLE_ANSWER_PATTERN = r"^>(\w+)$"
CONTEST_QUESTIONS_SECTION_PATTERN = r"^##\s*Questões de Concurso$"
CONTEST_QUESTION_ID_PATTERN = r"^###\s*Questão\s*(\d+)$"
CONTEST_STATEMENT_PATTERN = r"^\*\*Enunciado da Questão:\*\*\s*(.+)$"
CONTEST_TEXT_PATTERN = r"^\*\*Texto:\*\*\s*(.*)$"
CONTEST_ALTERNATIVES_PATTERN = r"^###\s*Alternativas:$"
OPTION_WITH_ANSWER_PATTERN = r"^-\s*([A-E])\)\s*(.+?)\s*\(gabarito\)$"
OPTION_PATTERN = r"^-\s*([A-E])\)\s*(.+)$"
EMPTY_TEXT_PATTERN = r"^\[\]$"


def _clean_text(text: str) -> str:
    """Removes leading/trailing brackets and whitespace."""
    return text.strip().strip("[]").strip()


def _extract_exam_source(statement: str) -> str:
    """Extracts exam source like (CESPE/2024) from statement."""
    match = re.search(r"\(([^)]+)\)", statement)
    return match.group(1) if match else ""


def _parse_paragraph_text(paragraphs: List[Paragraph]) -> List[str]:
    """Extracts stripped text from a list of Paragraph objects."""
    return [p.text.strip() for p in paragraphs if p.text.strip()]


def _find_next_section(lines: List[str], patterns: List[str]) -> int:
    """Finds the index of the next line matching any of the given patterns."""
    for i, line in enumerate(lines):
        if any(re.match(pattern, line) for pattern in patterns):
            return i
    return len(lines)


def extract_course_title(lines: List[str], warnings: List[str]) -> str:
    """Extracts the course title."""
    for line in lines:
        match = re.match(COURSE_PATTERN, line)
        if match:
            return _clean_text(match.group(1))
    warnings.append("Course title not found.")
    return ""


def extract_notebook_title(lines: List[str], warnings: List[str]) -> str:
    """Extracts the notebook title."""
    for line in lines:
        match = re.match(NOTEBOOK_PATTERN, line)
        if match:
            return _clean_text(match.group(1))
    warnings.append("Notebook title not found.")
    return ""


def extract_programmatic_content(lines: List[str], warnings: List[str]) -> str:
    """Extracts the programmatic content."""
    try:
        start_index = lines.index(next(l for l in lines if re.match(PROGRAMMATIC_CONTENT_PATTERN, l))) + 1
        end_index = _find_next_section(lines[start_index:], [SUBJECT_PATTERN, CONTEST_QUESTIONS_SECTION_PATTERN])
        content = "\n".join(lines[start_index : start_index + end_index]).strip()
        if not content:
            warnings.append("Programmatic content is empty.")
        return content
    except (StopIteration, ValueError):
        warnings.append("Programmatic content section not found.")
        return ""


def extract_exercises_from_subject(lines: List[str], warnings: List[str]) -> List[Exercise]:
    """Extracts exercises from a subject's content."""
    exercises = []
    while True:
        try:
            statement_start = lines.index(next(l for l in lines if re.match(EXERCISE_STATEMENT_PATTERN, l))) + 1
            statement_end = lines.index(next(l for l in lines[statement_start:] if re.match(EXERCISE_QUESTIONS_PATTERN, l)))
            statement = "\n".join(lines[statement_start:statement_end]).strip()

            questions_start = statement_end + 1
            questions_end = _find_next_section(lines[questions_start:], [THEORY_SLIDE_PATTERN, EXERCISE_STATEMENT_PATTERN])
            
            questions_block = lines[questions_start : questions_start + questions_end]
            
            exercise_questions = []
            for i, line in enumerate(questions_block):
                if re.match(SIMPLE_QUESTION_PATTERN, line):
                    question_text = _clean_text(line)
                    answer = ""
                    if i + 1 < len(questions_block):
                        answer_match = re.match(SIMPLE_ANSWER_PATTERN, questions_block[i+1])
                        if answer_match:
                            answer = answer_match.group(1)
                    if not answer:
                        warnings.append(f"Answer not found for question: '{question_text[:30]}...'")
                    
                    exercise_questions.append(ExerciseQuestion(question=question_text, answer=answer))

            if not statement:
                warnings.append("Exercise found with empty statement.")
            if not exercise_questions:
                warnings.append(f"No questions found for exercise with statement: '{statement[:30]}...'")

            exercises.append(Exercise(statement=statement, questions=exercise_questions))
            lines = lines[questions_start + questions_end:]
        except (StopIteration, ValueError):
            break
    return exercises


def extract_theory_slides(lines: List[str], warnings: List[str]) -> List[TheorySlide]:
    """Extracts theory slides from a subject's content."""
    slides = []
    while True:
        try:
            title_start = lines.index(next(l for l in lines if re.match(THEORY_SLIDE_PATTERN, l))) + 1
            # Assuming title is a single line
            title = lines[title_start].strip()
            
            content_start = title_start + 1
            content_end = _find_next_section(lines[content_start:], [THEORY_SLIDE_PATTERN, EXERCISE_STATEMENT_PATTERN])
            content = "\n".join(lines[content_start : content_start + content_end]).strip()

            if not title:
                warnings.append("Theory slide found with empty title.")
            if not content:
                warnings.append(f"Theory slide '{title}' has empty content.")

            slides.append(TheorySlide(title=title, content=content))
            lines = lines[content_start + content_end:]
        except (StopIteration, ValueError):
            break
    return slides


def extract_subjects(lines: List[str], warnings: List[str]) -> List[Subject]:
    """Extracts all subjects from the document."""
    subjects = []
    subject_indices = [i for i, line in enumerate(lines) if re.match(SUBJECT_PATTERN, line)]
    
    for i, start_index in enumerate(subject_indices):
        subject_match = re.match(SUBJECT_PATTERN, lines[start_index])
        subject_name = _clean_text(subject_match.group(1))
        
        end_index = subject_indices[i+1] if i + 1 < len(subject_indices) else _find_next_section(lines[start_index+1:], [CONTEST_QUESTIONS_SECTION_PATTERN]) + start_index + 1
        
        subject_content = lines[start_index + 1 : end_index]
        
        theory_slides = extract_theory_slides(subject_content, warnings)
        exercises = extract_exercises_from_subject(subject_content, warnings)

        if not theory_slides and not exercises:
            warnings.append(f"Subject '{subject_name}' has no theory slides or exercises.")

        subjects.append(
            Subject(
                subjectName=subject_name,
                theorySlides=theory_slides,
                exercises=exercises,
            )
        )
    return subjects


def extract_contest_questions(lines: List[str], warnings: List[str]) -> List[ContestQuestion]:
    """Extracts all contest questions from the document."""
    questions = []
    try:
        start_index = lines.index(next(l for l in lines if re.match(CONTEST_QUESTIONS_SECTION_PATTERN, l))) + 1
    except (StopIteration, ValueError):
        return questions # No contest questions section found

    question_indices = [i for i, line in enumerate(lines) if re.match(CONTEST_QUESTION_ID_PATTERN, line)]

    for i, q_start_index in enumerate(question_indices):
        id_match = re.match(CONTEST_QUESTION_ID_PATTERN, lines[q_start_index])
        q_id = int(id_match.group(1))

        q_end_index = question_indices[i+1] if i + 1 < len(question_indices) else len(lines)
        q_content = lines[q_start_index + 1 : q_end_index]

        statement, text, options, answer = "", "", [], ""
        
        try:
            # Statement
            statement_line = next(l for l in q_content if re.match(CONTEST_STATEMENT_PATTERN, l))
            statement = _clean_text(re.match(CONTEST_STATEMENT_PATTERN, statement_line).group(1))
            
            # Optional Text
            text_line_index = next((i for i, l in enumerate(q_content) if re.match(CONTEST_TEXT_PATTERN, l)), -1)
            if text_line_index != -1:
                text_content = re.match(CONTEST_TEXT_PATTERN, q_content[text_line_index]).group(1).strip()
                text = "" if re.match(EMPTY_TEXT_PATTERN, text_content) else text_content

            # Alternatives
            alternatives_start = next((i for i, l in enumerate(q_content) if re.match(CONTEST_ALTERNATIVES_PATTERN, l)), -1)
            if alternatives_start != -1:
                for line in q_content[alternatives_start + 1:]:
                    option_match = re.match(OPTION_PATTERN, line)
                    answer_match = re.match(OPTION_WITH_ANSWER_PATTERN, line)
                    
                    if answer_match:
                        answer = answer_match.group(1)
                        options.append(f"{answer_match.group(1)}) {answer_match.group(2)}")
                    elif option_match:
                        options.append(f"{option_match.group(1)}) {option_match.group(2)}")

        except (StopIteration, ValueError):
            warnings.append(f"Could not parse all parts of Contest Question ID {q_id}.")
            continue

        if not statement: warnings.append(f"Contest Question ID {q_id} is missing a statement.")
        if not options: warnings.append(f"Contest Question ID {q_id} is missing options.")
        if not answer: warnings.append(f"Contest Question ID {q_id} is missing an answer.")

        questions.append(
            ContestQuestion(
                id=q_id,
                statement=statement,
                text=text,
                source=_extract_exam_source(statement),
                options=options,
                answer=answer,
            )
        )
    return questions


def parse_docx(path: str) -> dict:
    """
    Parses a .docx file and returns a dictionary conforming to the new schema.
    """
    try:
        document = Document(path)
        lines = _parse_paragraph_text(list(document.paragraphs))
    except Exception as e:
        return {"warnings": [f"Failed to read DOCX file: {e}"]}

    warnings = []

    course_title = extract_course_title(lines, warnings)
    notebook_title = extract_notebook_title(lines, warnings)
    programmatic_content = extract_programmatic_content(lines, warnings)
    subjects = extract_subjects(lines, warnings)
    contest_questions = extract_contest_questions(lines, warnings)

    # Final validation
    if not subjects and not contest_questions:
        warnings.append("No subjects or contest questions were found in the document.")

    return {
        "courseTitle": course_title,
        "notebookTitle": notebook_title,
        "programmaticContent": programmatic_content,
        "subjects": [s.model_dump() for s in subjects],
        "contestQuestions": [cq.model_dump() for cq in contest_questions],
        "warnings": warnings,
    }
