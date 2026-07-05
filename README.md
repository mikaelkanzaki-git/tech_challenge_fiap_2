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
3. Start the API
4. Send a triage payload to `POST /predict/triage`

## Local run order
1. Install dependencies
2. Train the model
3. Start the API

## Notes
- Code identifiers use English and `snake_case`
- User-facing messages are in Portuguese
