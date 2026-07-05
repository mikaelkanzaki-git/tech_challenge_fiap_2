# API Migration Roadmap

## Goal
Move the project from a notebook-first workflow to a maintainable API-first service while keeping `algoritmo_genetico.ipynb` as a reference notebook.

## Principles
- Keep code identifiers in English and `snake_case`
- Keep user-facing text in Portuguese
- Separate training, inference, API, and tests
- Prefer small, testable functions

## Phases
1. Extract reusable preprocessing and training code from the notebook
2. Define the request and response contracts for the prediction API
3. Implement the FastAPI application and prediction service
4. Add unit tests for schema validation and preprocessing
5. Add integration tests for the prediction endpoint
6. Document how to train the model and run the API

## Notebook role
`algoritmo_genetico.ipynb` remains a study and traceability artifact. It should not be the production entry point.
