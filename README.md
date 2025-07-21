# Parser Word → JSON

[![CI](https://github.com/crosouza/parser-word-json/actions/workflows/ci.yml/badge.svg)](https://github.com/crosouza/parser-word-json/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/crosouza/parser-word-json/graph/badge.svg)](https://codecov.io/gh/crosouza/parser-word-json)

**Objetivo**  
Converter um arquivo **`.docx`** estruturado com marcações específicas (estilo Markdown) em um **JSON canônico**.  
Esse JSON será usado mais adiante por outros serviços para automação e geração de conteúdo.

---

## 1. Formato do Documento Word

O parser não usa mais heurísticas complexas, mas sim um formato bem definido dentro do `.docx`, inspirado em Markdown. A estrutura é identificada por títulos e marcações específicas:

- **Curso**: `# Curso: [Nome do Curso]`
- **Caderno**: `## Caderno: [Nome do Caderno]`
- **Conteúdo Programático**: `## Conteúdo Programático:` (seguido pelo conteúdo)
- **Assunto**: `## Assunto X: [Nome do Assunto]`
- **Slide de Teoria**: `### Título do Slide (Teoria):` (seguido pelo título e conteúdo)
- **Exercício (Enunciado)**: `### Enunciado do Exercício:` (seguido pelo enunciado)
- **Exercício (Questões)**: `### Questões do Exercício:` (seguido por questões `a) ...` e respostas `> ...`)
- **Questões de Concurso**: `## Questões de Concurso`
- **Questão de Concurso (ID)**: `### Questão X`
- **Questão de Concurso (Enunciado)**: `**Enunciado da Questão:** ...`
- **Questão de Concurso (Alternativas)**: `### Alternativas:` (seguido por `- A) ...`, com a correta marcada por `(gabarito)`)

> Veja os arquivos em `samples/` para exemplos práticos.

---

## 2. Arquitetura

```
.
├── parser/
│   ├── __init__.py
│   ├── cli.py          # Ponto de entrada (CLI e servidor)
│   ├── extractor.py    # Lógica principal de parsing do DOCX
│   ├── schema.py       # Modelos de dados Pydantic
│   ├── server.py       # Servidor Flask para a API
│   └── utils.py        # Funções utilitárias
├── tests/
│   └── test_new_format.py # Testes para o novo formato
├── samples/            # Arquivos .docx de exemplo e seus JSONs
├── Dockerfile
└── README.md
```

**Tecnologias**
- `python-docx` para ler `.docx`
- `pydantic` para validação de dados e schema
- `Flask` e `Flask-Limiter` para o servidor web
- `pytest` e `pytest-cov` para testes e cobertura
- `argparse` para a CLI
- Imagem base `python:3.12-slim` no Docker

---

## 3. Esquema JSON de Saída

O JSON gerado segue a estrutura abaixo, validada pelos modelos em `parser/schema.py`.

```jsonc
{
  "courseTitle": "Sample Course Name",
  "notebookTitle": "Sample Notebook Name",
  "programmaticContent": "This is the programmatic content.",
  "subjects": [
    {
      "subjectName": "Subject 1",
      "theorySlides": [
        {
          "title": "Title for Theory 1",
          "content": "Content for Theory 1."
        }
      ],
      "exercises": [
        {
          "statement": "Solve the following questions.",
          "questions": [
            {
              "question": "a) What is 1+1?",
              "answer": "2"
            }
          ]
        }
      ]
    }
  ],
  "contestQuestions": [
    {
      "id": 1,
      "statement": "(CESPE/2024) This is a contest question.",
      "text": "",
      "source": "CESPE/2024",
      "options": [
        "A) Option A",
        "B) Option B",
        "C) Option C"
      ],
      "answer": "B"
    }
  ],
  "warnings": []
}
```

---

## 4. Como Usar

### Via Linha de Comando (CLI)

Você pode converter um arquivo localmente.

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute o parser
python -m parser.cli -i "path/to/your/document.docx" -o "path/to/output.json"
```

| Flag / VAR | Default | Descrição |
|-------------|---------|-----------|
| `--input, -i` | — | Caminho do `.docx` (obrigatório) |
| `--output, -o` | `stdout` | Saída `.json` |
| `--json-indent` | `2` | Recuo no `json.dumps` |
| `--serve` | `false` | Inicia o servidor web em vez de converter um arquivo |
| `LOG_LEVEL` | `INFO` | Nível de log (e.g., `DEBUG`, `INFO`, `WARNING`) |

### Via Servidor Web (API)

O projeto pode ser executado como um servidor que aceita requisições `POST` para converter arquivos.

**Endpoint**: `POST /parse`  
**Body**: `{ "file": "<base64_encoded_docx>" }`

O modo servidor possui um limite de **60 requisições por minuto** por IP.

---

## 5. Como Executar (Docker)

A forma mais simples de executar o projeto é via Docker.

### 1. Construir a Imagem

```bash
docker build -t parser-word-json .
```

### 2. Executar o Servidor

```bash
docker run -d -p 5000:5000 --name parser-server parser-word-json --serve
```

O servidor estará disponível em `http://localhost:5000`.

### 3. Fazer uma Requisição

Exemplo de como enviar um arquivo para o servidor (usando Python):

```python
import base64
import requests

file_path = 'samples/sample_new_format.docx'

with open(file_path, 'rb') as f:
    encoded_file = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    'http://localhost:5000/parse',
    json={'file': encoded_file}
)

print(response.json())
```

---

## 6. Versionamento

O projeto segue o [Versionamento Semântico](https://semver.org/). As versões são tagueadas no Git e as imagens Docker são construídas com a tag de versão correspondente.

