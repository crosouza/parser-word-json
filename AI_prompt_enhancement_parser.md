# Prompt for Gemini 2.5 – **Enhance “parser-word-json” Project**

> **Context**  
> We already have a working Python project that converts `.docx` files into a canonical JSON used by Yumdocs and n8n.  
> Repository: `https://github.com/crosouza/parser-word-json` (public).  
> Your mission is to **improve robustness, coverage, and deployment** according to the items below.

---

## 1. Objectives

1. Harden the parser against formatting variations (alternative headings, answer keywords, option markers, etc.).  
2. Increase test coverage for edge‑cases.  
3. Pin dependency versions and polish Dockerfile.  
4. Provide an optional lightweight HTTP server mode (`--serve`) so other services can call the parser over REST.  
5. Add CI: automatic tests + Docker build on every push via GitHub Actions.

---

## 2. Detailed Change List

### 2.1 Improve regular expressions
| Area | Current Limitation | Required Fix |
|------|-------------------|--------------|
| **Exercise intro** | Only matches “questões de exercícios” (exact) | Use a case‑insensitive pattern that catches variations such as “Questões – Exercício”, “Questões de Exercício”, “Questão de Exercícios”.<br>`re.search(r'quest(ões|ão)[^\n]{0,20}exerc', flags=re.I)` |
| **Answer line** | Looks for “gabarito” or “resposta” | Add synonyms: `alternativa correta`, `correto`. |
| **Option markers** | Accepts `A)` only | Accept also `A.`, `(A)`, `[A]`.<br>`re.match(r'^[A-Ea-e][\)\.\]]')` |
| **Heading fallback** | Relies on Word styles or ALL CAPS | If paragraph style is `Normal` but text is all caps **and** length < 60 chars, treat as heading. |

### 2.2 Pin dependency versions
Add a **`requirements.txt`** with fixed versions:  
```text
python-docx==1.1.0
pydantic==2.7.*
pytest==8.*
```
and a matching `requirements-dev.txt` if extra packages are needed.

### 2.3 Dockerfile polish
* Break long `RUN` commands into multiple lines for readability.  
* Switch to `--user 1000:1000` for non‑root execution.  
* Copy only needed layers to keep image < 200 MB.

### 2.4 Expand test suite
Add tests for:
1. **Document without theory slides** (no `theorySlides`).  
2. **Two subjects, zero exercises.**  
3. **Exercise missing alternatives** (should raise warning).  
4. **Google Docs export** (headings lost).  
5. **Alternative option markers** `(A)`.

### 2.5 Optional HTTP server
* Add a flag `--serve` to `cli.py`; when passed, start a **Flask** (or FastAPI) app:  
  * `POST /parse` → JSON body `{ "file": base64 }` returns parsed JSON.  
* Keep dependencies optional (import inside block) to avoid increasing image size if unused.

### 2.6 GitHub Actions CI
* Workflow: on **push** and **pull_request**  
* Jobs:  
  1. **Test**: `pip install -r requirements.txt -r requirements-dev.txt` → `pytest -q`.  
  2. **Docker Build**: `docker build -t parser-word-json:$GITHUB_SHA .`.  
  3. (optional) **Docker Push** to Docker Hub or GHCR if secrets provided.

---

## 3. Tasks Checklist (for the AI)

1. **Clone** `https://github.com/crosouza/parser-word-json`.  
2. **Create a feature branch** `enhancement/parser-robustness`.  
3. **Update `extractor.py`** implementing all regex improvements (§2.1).  
4. **Modify `utils.py`** adding helper functions for the new regex logic.  
5. **Add/Update tests** in `tests/` to cover cases listed in §2.4.  
6. **Pin versions** by creating/updating `requirements*.txt` (§2.2).  
7. **Refactor Dockerfile** per §2.3; verify image size (`docker images`).  
8. **Implement `--serve` mode** in `cli.py` plus minimal `server.py`.  
9. **Add GitHub Action** `.github/workflows/ci.yml` as described (§2.6).  
10. **Run tests locally**; ensure all pass.  
11. **Build Docker image** and confirm size < 200 MB.  
12. **Commit & push**; open a pull request to `main`.  
13. **Write release notes** describing the improvements.

---

## 4. Acceptance Criteria

* All unit tests (old + new) pass.  
* `pytest --cov` shows ≥ 90 % code coverage.  
* `docker build` succeeds and image is < 200 MB.  
* `--serve` flag works: `curl -X POST /parse` returns valid JSON.  
* CI workflow passes on the PR.  

---

## 5. Deliverables

* Updated source code in `enhancement/parser-robustness` branch.  
* Pull Request with body summarizing changes and linking to CI run.  
* Short **CHANGELOG.md** entry for version `0.2.0`.

---

### Ready to go!

Follow the checklist; once the PR passes CI, the project will be ready for production deployment in the Yumdocs + n8n pipeline.