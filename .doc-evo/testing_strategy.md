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
