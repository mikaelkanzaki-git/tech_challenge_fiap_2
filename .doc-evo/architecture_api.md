# API Architecture

## Overview
The project will follow a simple layered structure:

- `core`: shared configuration
- `ml`: dataset preparation, training, and preprocessing
- `schemas`: request and response models
- `services`: model loading and prediction orchestration
- `api`: HTTP routes
- `scripts`: one-off operational scripts, such as training
- `tests`: automated checks

## Flow
1. The training script loads the CSV dataset.
2. The training layer prepares features and target values.
3. The model is trained and saved to a local artifact file.
4. The API loads the saved artifact at startup.
5. The prediction endpoint validates input, transforms it, and returns the triage result.

## Naming rules
- Use English for code symbols, module names, functions, and variables
- Use `snake_case` everywhere in code
- Use Portuguese only for user-visible messages

## Endpoint convention
- Predict triage: `POST /predict/triage`
- Health check: `GET /health`
