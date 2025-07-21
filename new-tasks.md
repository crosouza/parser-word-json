# Prompt for Word-JSON Parser Modification

## Context
You need to modify the Word document (.docx) to JSON parser from the `parser-word-json`  to accept a new template format. The current format is based on simple lines, but the new format uses Markdown structure with specific hierarchy.

## New Template Format

The template follows this exact structure (which can repeat):

```
# Curso: [COURSE NAME]

## Caderno: [NOTEBOOK NAME]

## Conteúdo Programático:
[Programmatic content text]

## Assunto 1: [SUBJECT NAME]

### Título do Slide (Teoria):
[Theory content]

### Enunciado do Exercício:
[Exercise statement text]

### Questões do Exercício:
a) [question]
>answer

b) [question]
>answer

## Questões de Concurso

### Questão 1
**Enunciado da Questão:**
[Question statement text with exam board information]

**Texto:**
[Optional text for interpretation questions - text or can be empty with just []]

### Alternativas:
- A) [Alternative text]
- B) [Alternative text] (gabarito)
- C) [Alternative text]
- D) [Alternative text]
- E) [Alternative text]

### Questão 2
[Structure repeats...]
```

**Important points:**
- There can be **multiple subjects** (Assunto 1, Assunto 2, Assunto N)
- There can be **multiple questions** (Questão 1, Questão 2, Questão N)
- There can be **multiple exercises** per subject
- The answer key can be in **(gabarito)** or **>gabarito** format
- The structure repeats, changing only numbering and content

## Files to be Modified

### 1. `/parser/extractor.py`
**Main file containing the Word document parsing logic.**

### 2. `/parser/schema.py`
**File defining Pydantic/dataclasses data models for JSON validation.**

### 3. `/parser/cli.py` (if necessary)
**Command line interface file.**

## Desired JSON Output

```json
{
  "courseTitle": "Course Name",
  "notebookTitle": "Notebook Name",
  "programmaticContent": "Programmatic content text",
  "subjects": [
    {
      "subjectName": "Subject Name",
      "theorySlides": [
        {
          "title": "Slide Title",
          "content": "Theory content"
        }
      ],
      "exercises": [
        {
          "statement": "Exercise statement",
          "questions": [
            {
              "question": "Question text",
              "answer": "answer"
            }
          ]
        }
      ]
    }
  ],
  "contestQuestions": [
    {
      "id": 1,
      "statement": "Question statement",
      "text": "Optional interpretation text (can be empty string)",
      "source": "Exam board information extracted from statement",
      "options": [
        "A) Alternative text",
        "B) Alternative text",
        "C) Alternative text",
        "D) Alternative text",
        "E) Alternative text"
      ],
      "answer": "B"
    }
  ],
  "warnings": []
}
```

## Specific Modifications Required

### In `extractor.py` file:

1. **Function `extract_course_title()`**
   - Detect line starting with `# Curso:`
   - Extract text after the colon
   - Remove brackets if present: `[COURSE NAME]` → `COURSE NAME`

2. **Function `extract_notebook_title()`**
   - Detect line starting with `## Caderno:`
   - Extract text after the colon
   - Remove brackets if present

3. **New function `extract_programmatic_content()`**
   - Detect section `## Conteúdo Programático:`
   - Capture all text until next `##` section

4. **Function `extract_subjects()`** (replace `extract_sections()`)
   - Detect lines starting with `## Assunto N:`
   - For each subject, extract:
     - Subject name (after colon)
     - Theory (after `### Título do Slide (Teoria):`)
     - Exercises (after `### Enunciado do Exercício:`)

5. **Function `extract_exercises_from_subject()`**
   - Detect `### Questões do Exercício:`
   - Extract questions in format `a)`, `b)`, `c)`...
   - Detect answer key with `>answer`

6. **Function `extract_contest_questions()`**
   - Detect section `## Questões de Concurso`
   - For each `### Questão N`, extract:
     - Statement (after `**Enunciado da Questão:**`)
     - Optional text (after `**Texto:**` - can be empty or just contain `[]`)
     - Alternatives (lines starting with `- A)`, `- B)`, etc.)
     - Answer key (alternative marked with `(gabarito)`)

7. **Main function `parse_docx()`**
   - Modify to use all new functions
   - Return JSON in new format

### In `schema.py` file:

1. **Class `TheorySlide`**
   ```python
   class TheorySlide:
       title: str
       content: str
   ```

2. **Class `ExerciseQuestion`**
   ```python
   class ExerciseQuestion:
       question: str
       answer: str
   ```

3. **Class `Exercise`**
   ```python
   class Exercise:
       statement: str
       questions: List[ExerciseQuestion]
   ```

4. **Class `Subject`**
   ```python
   class Subject:
       subjectName: str
       theorySlides: List[TheorySlide]
       exercises: List[Exercise]
   ```

5. **Class `ContestQuestion`**
   ```python
   class ContestQuestion:
       id: int
       statement: str
       text: str  # Optional interpretation text
       source: str
       options: List[str]
       answer: str
   ```

6. **Class `ParsedDocument`** (update)
   ```python
   class ParsedDocument:
       courseTitle: str
       notebookTitle: str
       programmaticContent: str
       subjects: List[Subject]
       contestQuestions: List[ContestQuestion]
       warnings: List[str]
   ```

## Special Cases to Handle

1. **Multiple subjects**: Document can have `## Assunto 1:`, `## Assunto 2:`, up to `## Assunto N:`
2. **Multiple contest questions**: From `### Questão 1` to `### Questão N`
3. **Multiple exercises per subject**: Can have several `### Enunciado do Exercício:` blocks in same subject
4. **Different text content**: Questions may have optional interpretation text after `**Texto:**`
   - Can contain a text for interpretation questions
   - Can be empty (just `[]`) for direct questions
   - Parser should handle both cases gracefully
5. **Different answer key formats**: 
   - `(gabarito)` in alternatives
   - `>answer` in simple exercises
6. **Variable alternatives**: Can have A-E or just CERTO/ERRADO
7. **Optional fields**: Some subjects may not have theory or exercises

## Useful Regex Patterns

```python
import re

# Detect course
COURSE_PATTERN = r'^# Curso:\s*(.+)$'

# Detect notebook  
NOTEBOOK_PATTERN = r'^## Caderno:\s*(.+)$'

# Detect subject
SUBJECT_PATTERN = r'^## Assunto \d+:\s*(.+)$'

# Detect contest question
QUESTION_PATTERN = r'^### Questão (\d+)$'

# Detect alternative with answer
OPTION_WITH_ANSWER_PATTERN = r'^- ([A-E])\)\s*(.+?)\s*\(gabarito\)$'

# Detect normal alternative
OPTION_PATTERN = r'^- ([A-E])\)\s*(.+)$'

# Detect question text (optional)
TEXT_PATTERN = r'^\*\*Texto:\*\*\s*
```

## Task List

Execute tasks in exact order:

### Task 1: Update schema.py
- [ ] Create `TheorySlide` class with `title` and `content` fields
- [ ] Create `ExerciseQuestion` class with `question` and `answer` fields
- [ ] Create `Exercise` class with `statement` and `questions` fields
- [ ] Create `Subject` class with `subjectName`, `theorySlides`, `exercises` fields
- [ ] Create `ContestQuestion` class with `id`, `statement`, `text`, `source`, `options`, `answer` fields
- [ ] Update `ParsedDocument` class with new fields: `programmaticContent`, `subjects`, `contestQuestions`
- [ ] Remove old unused fields

### Task 2: Modify extractor.py - Basic functions
- [ ] Update `extract_course_title()` to detect `# Curso:` and remove brackets
- [ ] Update `extract_notebook_title()` to detect `## Caderno:` and remove brackets
- [ ] Create `extract_programmatic_content()` to capture text after `## Conteúdo Programático:`

### Task 3: Modify extractor.py - Subject extraction
- [ ] Create `extract_subjects()` that detects `## Assunto N:` in loop
- [ ] For each subject, create `Subject` object with extracted name
- [ ] Implement theory extraction after `### Título do Slide (Teoria):`
- [ ] Implement exercise extraction after `### Enunciado do Exercício:`

### Task 4: Modify extractor.py - Exercise extraction per subject
- [ ] Create `extract_exercises_from_subject()` 
- [ ] Detect `### Questões do Exercício:` as block start
- [ ] Extract questions in format `a)`, `b)`, `c)` etc.
- [ ] Detect answer key with pattern `>answer`
- [ ] Group questions by exercise (statement + questions)

### Task 5: Modify extractor.py - Contest question extraction
- [ ] Create `extract_contest_questions()` 
- [ ] Detect section `## Questões de Concurso`
- [ ] For each `### Questão N`, extract question number
- [ ] Extract statement after `**Enunciado da Questão:**`
- [ ] Extract optional text after `**Texto:**` (handle empty `[]` cases)
- [ ] Extract alternatives starting with `- A)`, `- B)`, etc.
- [ ] Detect answer key in alternatives marked with `(gabarito)`
- [ ] Extract exam board information from statement (CESPE, year, etc.)

### Task 6: Modify extractor.py - Main function
- [ ] Update `parse_docx()` to use all new functions
- [ ] Ensure it returns `ParsedDocument` object in new format
- [ ] Add appropriate error handling and warnings
- [ ] Test with multiple subjects and questions

### Task 7: Testing and validation
- [ ] Verify code compiles without errors
- [ ] Test with example document in new format
- [ ] Validate JSON output matches expected schema
- [ ] Check warnings are generated appropriately

### Task 8: Final adjustments
- [ ] Ensure imports are correct
- [ ] Verify all functions have docstrings
- [ ] Confirm compatibility with existing Flask server
- [ ] Test complete integration (CLI + server)

## Success Criteria

The code will be working correctly when:
1. ✅ Parser detects titles in format `# Curso:` and `## Caderno:`
2. ✅ Extracts multiple subjects (`## Assunto 1:`, `## Assunto 2:`, etc.)
3. ✅ Processes multiple contest questions (`### Questão 1`, `### Questão 2`, etc.)
4. ✅ Detects answer keys in both formats: `(gabarito)` and `>answer`
5. ✅ Generates valid JSON in new format
6. ✅ Doesn't break existing Flask server functionality

## Important Notes

- Maintain compatibility with existing Flask server in `server.py`
- Preserve rate limiting functionality and API structure
- All text between `[brackets]` should be treated as placeholders to be removed
- Parser should be robust to handle formatting variations
- Implement proper logging for easier debugging

# Detect empty text content
EMPTY_TEXT_PATTERN = r'^\[\]
```

## Task List

Execute tasks in exact order:

### Task 1: Update schema.py
- [ ] Create `TheorySlide` class with `title` and `content` fields
- [ ] Create `ExerciseQuestion` class with `question` and `answer` fields
- [ ] Create `Exercise` class with `statement` and `questions` fields
- [ ] Create `Subject` class with `subjectName`, `theorySlides`, `exercises` fields
- [ ] Create `ContestQuestion` class with `id`, `statement`, `source`, `options`, `answer` fields
- [ ] Update `ParsedDocument` class with new fields: `programmaticContent`, `subjects`, `contestQuestions`
- [ ] Remove old unused fields

### Task 2: Modify extractor.py - Basic functions
- [ ] Update `extract_course_title()` to detect `# Curso:` and remove brackets
- [ ] Update `extract_notebook_title()` to detect `## Caderno:` and remove brackets
- [ ] Create `extract_programmatic_content()` to capture text after `## Conteúdo Programático:`

### Task 3: Modify extractor.py - Subject extraction
- [ ] Create `extract_subjects()` that detects `## Assunto N:` in loop
- [ ] For each subject, create `Subject` object with extracted name
- [ ] Implement theory extraction after `### Título do Slide (Teoria):`
- [ ] Implement exercise extraction after `### Enunciado do Exercício:`

### Task 4: Modify extractor.py - Exercise extraction per subject
- [ ] Create `extract_exercises_from_subject()` 
- [ ] Detect `### Questões do Exercício:` as block start
- [ ] Extract questions in format `a)`, `b)`, `c)` etc.
- [ ] Detect answer key with pattern `>answer`
- [ ] Group questions by exercise (statement + questions)

### Task 5: Modify extractor.py - Contest question extraction
- [ ] Create `extract_contest_questions()` 
- [ ] Detect section `## Questões de Concurso`
- [ ] For each `### Questão N`, extract question number
- [ ] Extract statement after `**Enunciado da Questão:**`
- [ ] Extract alternatives starting with `- A)`, `- B)`, etc.
- [ ] Detect answer key in alternatives marked with `(gabarito)`
- [ ] Extract exam board information from statement (CESPE, year, etc.)

### Task 6: Modify extractor.py - Main function
- [ ] Update `parse_docx()` to use all new functions
- [ ] Ensure it returns `ParsedDocument` object in new format
- [ ] Add appropriate error handling and warnings
- [ ] Test with multiple subjects and questions

### Task 7: Testing and validation
- [ ] Verify code compiles without errors
- [ ] Test with example document in new format
- [ ] Validate JSON output matches expected schema
- [ ] Check warnings are generated appropriately

### Task 8: Final adjustments
- [ ] Ensure imports are correct
- [ ] Verify all functions have docstrings
- [ ] Confirm compatibility with existing Flask server
- [ ] Test complete integration (CLI + server)

## Success Criteria

The code will be working correctly when:
1. ✅ Parser detects titles in format `# Curso:` and `## Caderno:`
2. ✅ Extracts multiple subjects (`## Assunto 1:`, `## Assunto 2:`, etc.)
3. ✅ Processes multiple contest questions (`### Questão 1`, `### Questão 2`, etc.)
4. ✅ Detects answer keys in both formats: `(gabarito)` and `>answer`
5. ✅ Generates valid JSON in new format
6. ✅ Doesn't break existing Flask server functionality

## Important Notes

- Maintain compatibility with existing Flask server in `server.py`
- Preserve rate limiting functionality and API structure
- All text between `[brackets]` should be treated as placeholders to be removed
- Parser should be robust to handle formatting variations
- Implement proper logging for easier debugging
```

## Task List

Execute tasks in exact order:

### Task 1: Update schema.py
- [ ] Create `TheorySlide` class with `title` and `content` fields
- [ ] Create `ExerciseQuestion` class with `question` and `answer` fields
- [ ] Create `Exercise` class with `statement` and `questions` fields
- [ ] Create `Subject` class with `subjectName`, `theorySlides`, `exercises` fields
- [ ] Create `ContestQuestion` class with `id`, `statement`, `source`, `options`, `answer` fields
- [ ] Update `ParsedDocument` class with new fields: `programmaticContent`, `subjects`, `contestQuestions`
- [ ] Remove old unused fields

### Task 2: Modify extractor.py - Basic functions
- [ ] Update `extract_course_title()` to detect `# Curso:` and remove brackets
- [ ] Update `extract_notebook_title()` to detect `## Caderno:` and remove brackets
- [ ] Create `extract_programmatic_content()` to capture text after `## Conteúdo Programático:`

### Task 3: Modify extractor.py - Subject extraction
- [ ] Create `extract_subjects()` that detects `## Assunto N:` in loop
- [ ] For each subject, create `Subject` object with extracted name
- [ ] Implement theory extraction after `### Título do Slide (Teoria):`
- [ ] Implement exercise extraction after `### Enunciado do Exercício:`

### Task 4: Modify extractor.py - Exercise extraction per subject
- [ ] Create `extract_exercises_from_subject()` 
- [ ] Detect `### Questões do Exercício:` as block start
- [ ] Extract questions in format `a)`, `b)`, `c)` etc.
- [ ] Detect answer key with pattern `>answer`
- [ ] Group questions by exercise (statement + questions)

### Task 5: Modify extractor.py - Contest question extraction
- [ ] Create `extract_contest_questions()` 
- [ ] Detect section `## Questões de Concurso`
- [ ] For each `### Questão N`, extract question number
- [ ] Extract statement after `**Enunciado da Questão:**`
- [ ] Extract alternatives starting with `- A)`, `- B)`, etc.
- [ ] Detect answer key in alternatives marked with `(gabarito)`
- [ ] Extract exam board information from statement (CESPE, year, etc.)

### Task 6: Modify extractor.py - Main function
- [ ] Update `parse_docx()` to use all new functions
- [ ] Ensure it returns `ParsedDocument` object in new format
- [ ] Add appropriate error handling and warnings
- [ ] Test with multiple subjects and questions

### Task 7: Testing and validation
- [ ] Verify code compiles without errors
- [ ] Test with example document in new format
- [ ] Validate JSON output matches expected schema
- [ ] Check warnings are generated appropriately

### Task 8: Final adjustments
- [ ] Ensure imports are correct
- [ ] Verify all functions have docstrings
- [ ] Confirm compatibility with existing Flask server
- [ ] Test complete integration (CLI + server)

## Success Criteria

The code will be working correctly when:
1. ✅ Parser detects titles in format `# Curso:` and `## Caderno:`
2. ✅ Extracts multiple subjects (`## Assunto 1:`, `## Assunto 2:`, etc.)
3. ✅ Processes multiple contest questions (`### Questão 1`, `### Questão 2`, etc.)
4. ✅ Detects answer keys in both formats: `(gabarito)` and `>answer`
5. ✅ Generates valid JSON in new format
6. ✅ Doesn't break existing Flask server functionality

## Important Notes

- Maintain compatibility with existing Flask server in `server.py`
- Preserve rate limiting functionality and API structure
- All text between `[brackets]` should be treated as placeholders to be removed
- Parser should be robust to handle formatting variations
- Implement proper logging for easier debugging