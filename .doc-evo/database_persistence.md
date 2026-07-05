# Database Persistence

## Goal
Persist every `POST /predict/triage` request and its model response in PostgreSQL.

## Database
- Name: `tech_challenge_fiap_2`
- Main table: `triage_prediction_requests`

## Stored data
The table stores:

- patient input fields
- predicted triage level
- predicted triage label
- prediction probabilities as `JSONB`
- model version
- creation timestamp

## Runtime behavior
The API enables persistence only when `DATABASE_URL` is configured. This keeps local prediction and tests simple while allowing production-like environments to store request history.
