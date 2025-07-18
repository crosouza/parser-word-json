# Parser Word → JSON – Guia para a IA (Gemini 2.5 CLI)

**Objetivo**  
Converter automaticamente um arquivo **`.docx`** (material didático de cursos) em um **JSON canônico**.  
Esse JSON será usado mais adiante pelo serviço **Yumdocs** para gerar apresentações PowerPoint e por fluxos **n8n** para automação.

---

## 1. Descritivo do Projeto

A IA deve produzir uma biblioteca/CLI em **Python 3.12+** que:
1. Receba um `.docx` via argumento ou `stdin`.
2. Identifique blocos de informação (itens 1 a 9) mesmo que se repitam diversas vezes no documento.
3. Construa um JSON validado pelo esquema descrito em **§ 4**.
4. Imprima ou grave o JSON.
5. Seja empacotada em Docker para chamada externa.
6. Tenha testes automatizados.

---

## 2. Arquitetura Proposta

```
.
├── parser/
│   ├── __init__.py
│   ├── cli.py          # entrada principal: python -m parser -i file.docx
│   ├── extractor.py    # lógica de parsing
│   ├── schema.py       # modelos Pydantic / dataclasses
│   └── utils.py
├── tests/
│   └── test_extractor.py
├── samples/            # docx + json esperados
├── Dockerfile
└── README.md           # este documento
```

**Tecnologias**  
- `python-docx` para ler `.docx`  
- `pydantic` ou `dataclasses` + `jsonschema` para validar  
- `pytest` para testes  
- `argparse` para CLI  
- Imagem base `python:3.12-slim` no Docker

---

## 3. Regras de Parsing

| Ordem no Word | Campo JSON | Pode repetir? | Heurística resumida |
|---------------|------------|--------------|---------------------|
| 1 | **courseTitle** | Não | Primeira linha em CAIXA ALTA ou estilo *Heading 1* |
| 2 | **notebookTitle** | Não | Segunda linha em CAIXA ALTA ou *Heading 2* |
| 3 | **subjectPrimary** | Sim | Linha(s) seguintes; maiúsculas ou *Heading 3* |
| 3b | **subjectSecondary** | Sim (opcional) | Se houver, logo após o assunto primário |
| 4 | **theorySlides[]** | Sim | Linhas com "Teoria", "Resumo", estilo *Heading 4* |
| 5 | **exerciseIntros[]** | Sim | Texto introdutório antes das questões |
| 6 | **exercises[]** | Sim | Bloco iniciado por “Questões de Exercícios” |
| 7 | `exercises[].statement` | — | Primeiro parágrafo após número |
| 8 | `exercises[].options[]` | — | Lista de alternativas A)…E) ou bullets |
| 9 | `exercises[].answer` | — | Linha contendo “Gabarito”, “Resposta” etc. |

> **Observação:** Itens 3 → 9 se agrupam em **“seções”**; o documento pode conter muitas seções.

---

## 4. Esquema JSON (simplificado)

```jsonc
{
  "courseTitle": "RETA FINAL POLÍCIA FEDERAL",
  "notebookTitle": "CADERNO 1",
  "sections": [
    {
      "subjectPrimary": "Reconhecimento de Gêneros Textuais",
      "subjectSecondary": "Interpretação",
      "theorySlides": [
        "Identificando Gêneros",
        "Estratégias de Leitura"
      ],
      "exerciseIntros": [
        "Resolva as questões a seguir:"
      ],
      "exercises": [
        {
          "id": 1,
          "statement": "(CESPE/2024) O texto 10A2‑I é predominantemente...",
          "options": [
            "A) Narrativo",
            "B) Expositivo",
            "C) Descritivo",
            "D) Dissertativo",
            "E) Injuntivo"
          ],
          "answer": "B"
        },
        {
          "id": 2,
          "statement": "Julgue o item a seguir",
          "options": ["CERTO", "ERRADO"],
          "answer": "CERTO"
        }
      ]
    }
    /* …outras seções… */
  ],
  "warnings": []
}
```

---

## 5. Variáveis & CLI

| Flag / VAR | Default | Descrição |
|-------------|---------|-----------|
| `--input, -i` | — | Caminho do `.docx` (obrigatório) |
| `--output, -o` | `stdout` | Saída `.json` |
| `--json-indent` | `2` | Recuo no `json.dumps` |
| `--log-level` | `INFO` | TRACE, DEBUG, INFO, WARNING |
| `YUM_PARSER_TMP` | `/tmp` | Pasta tmp para mídia |

---

## 6. Lista de Tarefas para a IA

1. **Criar a estrutura de diretórios** mostrada em § 2.  
2. **Implementar `extractor.py`**<br>  • Função `parse_docx(path) -> dict` aplicando regras de § 3.<br>  • Utilizar regex robustas para capturar múltiplas seções.<br>  • Preencher `warnings` quando blocos faltarem.  
3. **Implementar `schema.py`** validando contra o esquema do § 4.  
4. **Implementar `cli.py`** com argparse, saída stdout/disco, `--serve` opcional.  
5. **Escrever testes (`tests/test_extractor.py`)** cobrindo:<br>  a. Documento com 1 seção.<br>  b. Documento com 3 seções e 20 questões.<br>  c. Documento faltando gabaritos (gera `warnings`).  
6. **Criar 3 amostras `.docx`** em `samples/` e seus JSON esperados.  
7. **Dockerizar** (imagem < 200 MB).  
8. **Documentar** comandos de build e execução:<br>  
   ```bash
   docker build -t yum-parser .
   docker run --rm -v $(pwd)/samples:/data yum-parser -i /data/sample.docx
   ```  
9. **Gerar artefato ZIP** do projeto.  

---

## 7. Entrega Esperada

- Repositório estruturado.  
- Todos os testes `pytest` passando.  
- Imagem Docker funcional.  
- README (este) claro e completo.  

---