# Testing Strategy

## TDD approach
Write tests before or alongside implementation for:

- schema validation
- feature encoding
- model loading and prediction service
- API response shape

## Test layers
### Unit tests
Focus on pure functions:
- arrival mode encoding
- feature frame construction
- request validation

### Service tests
Focus on model loading and output mapping:
- prediction label formatting
- probability mapping
- missing model file handling

### API tests
Focus on HTTP behavior:
- `200` for valid payloads
- `422` for invalid payloads
- `503` when the model artifact is missing

## Goal
Keep the notebook as the learning reference, but move behavior verification into automated tests.

## Coverage
Use `pytest-cov` to measure how much of the API code is exercised by tests.

```powershell
.venv\Scripts\python.exe -m pytest --cov=src/triage_api --cov-report=term-missing
```

The initial project target is `80%` coverage. This is high enough to catch large gaps while still leaving room for pragmatic evolution.

Notebook files are versioned for team reference, but they are not part of the coverage target. Coverage should focus on production code under `src/triage_api`.
