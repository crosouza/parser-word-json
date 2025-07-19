# Changelog

## [0.2.0] - 2025-07-18

### Added
- Optional `--serve` mode to run the parser as a Flask web server on port 5000.
- GitHub Actions CI for automated testing and Docker image building.
- New tests for edge cases, including documents without theory, without exercises, with missing options, exported from Google Docs, and with alternative markers.
- `pytest-cov` for code coverage reporting.

### Changed
- **BREAKING**: Parser logic now relies on heading styles (`Heading 1-4`) for structure detection, improving accuracy over the previous all-caps heuristic.
- Improved regex for detecting exercise intros, answers, and options to handle more variations.
- Pinned dependency versions in `requirements.txt` and `requirements-dev.txt`.
- Refactored `Dockerfile` to use a non-root user and improve layer caching.
- Moved helper functions from `extractor.py` to `parser/utils.py`.

### Fixed
- Handled a `pydantic-core` compilation issue by pinning to an older version with pre-built wheels.
- Added a warning for exercises that are missing options.
