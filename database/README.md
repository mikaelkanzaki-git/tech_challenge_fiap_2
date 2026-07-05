# Database

The API can persist prediction requests in PostgreSQL.

## Database name
`tech_challenge_fiap_2`

## DDL scripts
Run the scripts in this order:

1. `ddl/000_create_database.sql`
2. `ddl/001_create_triage_prediction_requests.sql`

The second script must be executed while connected to the `tech_challenge_fiap_2` database.

## Application configuration
Set `DATABASE_URL` before starting the API:

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/tech_challenge_fiap_2"
```

For the Supabase connection, copy `.env.example` to `.env` and replace `<YOUR-PASSWORD>` locally. Do not commit `.env`.

If `DATABASE_URL` is not set, the API still predicts triage levels but does not persist request records.
