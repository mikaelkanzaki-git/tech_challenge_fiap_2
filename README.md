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
5. Login in the frontend or request a token with `POST /token`
6. Use the chat screen or send a triage payload to `POST /predict/triage`

## Local run order
1. Install dependencies
2. Train the model
3. Start the API

## Database
The PostgreSQL database name is `tech_challenge_fiap_2`. Use this database name in the final path of `DATABASE_URL`.

DDL scripts are available in `database/ddl`:

```text
database/ddl/000_create_database.sql
database/ddl/001_create_triage_prediction_requests.sql
database/ddl/002_create_api_users.sql
```

Configure the API connection with:

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/tech_challenge_fiap_2"
```

For Supabase local development on IPv4 networks, prefer the Session Pooler connection string:

```text
DATABASE_URL=postgresql://postgres.<PROJECT-REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres
```

For local development, use `.env.example` as a template and create a local `.env` file with the real password. The `.env` file is ignored by Git and loaded automatically when the API starts. Restart Uvicorn after changing `.env`.

When `DATABASE_URL` is configured, each `POST /predict/triage` is saved in `triage_prediction_requests`.

## Frontend and Chat Agent
The API serves a small frontend from the `frontend` directory:

```text
http://127.0.0.1:8000/
```

Screens:

- Login screen: authenticates with `/token`
- Chat screen: sends messages to `/chat/message`

The chat agent collects the required triage fields one by one:

- age
- heart_rate
- systolic_blood_pressure
- oxygen_saturation
- body_temperature
- pain_level
- chronic_disease_count
- previous_er_visits
- arrival_mode

When all fields are present, the backend calls the same model service used by `POST /predict/triage` and returns the risk category to the user.

OpenAI integration is optional for local development. If `OPENAI_API_KEY` is configured, the backend uses the OpenAI Responses API to phrase the next chat message more naturally. If it is not configured, the local fallback agent still conducts the conversation.

## Authentication
Protected endpoints use OAuth2 Bearer authentication with a JWT returned by `/token` or `/login`.

Create the authentication table and seed user with:

```text
database/ddl/002_create_api_users.sql
```

Initial user:

```text
username: fiap@tech2.com
password: fiap@Tech_2
```

Generate a token:

```bash
curl --location "http://127.0.0.1:8000/token" \
--header "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "username=fiap@tech2.com" \
--data-urlencode "password=fiap@Tech_2"
```

Call the protected prediction endpoint:

```bash
curl --location "http://127.0.0.1:8000/predict/triage" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer <ACCESS_TOKEN>" \
--data '{
  "age": 79.2,
  "heart_rate": 147.9,
  "systolic_blood_pressure": 158.6,
  "oxygen_saturation": 96.0,
  "body_temperature": 39.35,
  "pain_level": 10,
  "chronic_disease_count": 4,
  "previous_er_visits": 2,
  "arrival_mode": "ambulance"
}'
```

Call the protected chat endpoint:

```bash
curl --location "http://127.0.0.1:8000/chat/message" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer <ACCESS_TOKEN>" \
--data '{
  "message": "79",
  "patient_data": {}
}'
```

## Logs
The API writes structured logs to the terminal using this pattern:

```text
[date_time] - [triage_api] - [LEVEL] - [step] - [message] - [payload=...] - [server_response=...]
```

Important prediction steps:

- `predict_triage_received`: the API received the request payload
- `predict_triage_completed`: the model returned a prediction
- `prediction_persistence_skipped`: `DATABASE_URL` was not configured
- `prediction_persistence_completed`: the prediction was saved successfully
- `prediction_persistence_failed`: the API could not save the prediction in PostgreSQL

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
