# Triage API Project

This repository is moving from notebook-driven experimentation to a small API service.

## What stays
- `algoritmo_genetico.ipynb` stays as a reference notebook
- the synthetic dataset stays as the training source

## What was added
- a source tree under `src/triage_api`
- a training script in `scripts/train_model.py`
- typed request and response schemas
- a prediction endpoint scaffold using FastAPI
- tests for the new service layer

## Main flow
1. Train a Random Forest model from the CSV dataset
2. Save the trained model artifact under `models/`
3. Configure the PostgreSQL database when request persistence is needed
4. Start the API
5. Send a triage payload to `POST /predict/triage`

## Local run order
1. Install dependencies
2. Train the model
3. Start the API

## Database
The PostgreSQL database name is `tech_challenge_fiap_2`.

DDL scripts are available in `database/ddl`:

```text
database/ddl/000_create_database.sql
database/ddl/001_create_triage_prediction_requests.sql
```

Configure the API connection with:

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/tech_challenge_fiap_2"
```

When `DATABASE_URL` is configured, each `POST /predict/triage` is saved in `triage_prediction_requests`.

## Tests and coverage
Run the automated tests:

```powershell
.venv\Scripts\python.exe -m pytest
```

Run the tests with coverage:

```powershell
.venv\Scripts\python.exe -m pytest --cov=src/triage_api --cov-report=term-missing
```

The current minimum coverage target is `80%`.

## Notes
- Code identifiers use English and `snake_case`
- User-facing messages are in Portuguese
