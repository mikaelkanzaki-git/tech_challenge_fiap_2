# Tech Challenge FIAP 2 - Triage API

Projeto de triagem hospitalar com modelo de Machine Learning, API FastAPI, autenticação JWT, persistência em PostgreSQL/Supabase e frontend com entrevista guiada por agente conversacional.

O notebook original continua no projeto como material de consulta, mas a execução principal agora acontece pela API e pelo frontend.

## Visão Geral

Este projeto permite:

- Treinar um modelo `RandomForestClassifier` com a base sintética do projeto.
- Expor uma API para predição de categoria de risco.
- Autenticar usuários com OAuth2 Bearer e JWT.
- Persistir predições no PostgreSQL.
- Usar uma tela de login e uma tela de atendimento conversacional.
- Opcionalmente usar OpenAI para melhorar a linguagem do agente de triagem.
- Fazer deploy demonstrável na Vercel usando o plano gratuito.

## Estrutura

```text
api/                  Entrypoint usado pela Vercel
data/                 Base sintética usada no treinamento
database/ddl/         Scripts SQL para banco, tabela de predições e usuários
frontend/             Telas HTML, CSS e JavaScript servidas pela API
models/               Artefatos do modelo usados pela API
scripts/              Scripts auxiliares, incluindo treinamento do modelo
src/triage_api/       Código principal da API
tests/                Testes automatizados
algoritmo_genetico.ipynb
                      Notebook de referência do experimento original
```

## Pré-Requisitos

- Python `3.14.6` ou compatível com as dependências do projeto.
- PostgreSQL local ou Supabase.
- Git.
- PowerShell no Windows.
- Conta Vercel, caso queira publicar a demo.
- Chave OpenAI opcional, apenas se quiser respostas mais naturais no chat.

## Configuração Local no Windows

Clone o repositório e entre na pasta do projeto:

```powershell
git clone https://github.com/mikaelkanzaki-git/tech_challenge_fiap_2.git
cd tech_challenge_fiap_2
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências de desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements-dev.txt
```

Crie o arquivo local de variáveis de ambiente:

```powershell
Copy-Item .env.example .env
```

Depois edite `.env` com os dados reais do seu ambiente.

Nunca envie `.env` para o Git. O arquivo correto para versionar é apenas `.env.example`.

## Dependências

O projeto separa dependências por finalidade:

- `requirements.txt`: runtime da API, treinamento do modelo e deploy na Vercel.
- `requirements-dev.txt`: inclui `requirements.txt` mais notebooks, testes e ferramentas de qualidade.

Use `requirements-dev.txt` para desenvolvimento local.

## Variáveis de Ambiente

Exemplo esperado no `.env`:

```text
DATABASE_URL=postgresql://postgres.<PROJECT-REF>:<YOUR-PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres
MODEL_VERSION=local
JWT_SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

Descrição:

- `DATABASE_URL`: conexão PostgreSQL usada para autenticação e persistência das predições.
- `MODEL_VERSION`: identificação do modelo salvo junto com cada predição.
- `JWT_SECRET_KEY`: segredo usado para assinar tokens JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: tempo de validade do token.
- `OPENAI_API_KEY`: chave opcional para integração com OpenAI.
- `OPENAI_MODEL`: modelo usado pelo agente quando `OPENAI_API_KEY` estiver configurado.

Para gerar um bom `JWT_SECRET_KEY` no PowerShell:

```powershell
$bytes = New-Object byte[] 64
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

## Banco de Dados

O banco do projeto é `tech_challenge_fiap_2`.

Scripts disponíveis:

```text
database/ddl/000_create_database.sql
database/ddl/001_create_triage_prediction_requests.sql
database/ddl/002_create_api_users.sql
```

Ordem recomendada:

1. Execute `000_create_database.sql` conectado a uma base administrativa, como `postgres`.
2. Conecte no banco `tech_challenge_fiap_2`.
3. Execute `001_create_triage_prediction_requests.sql`.
4. Execute `002_create_api_users.sql`.

O script `002_create_api_users.sql` cria o usuário inicial:

```text
username: fiap@tech2.com
password: fiap@Tech_2
```

Observação para Supabase:

- Em projetos Supabase, a connection string pode terminar com `/postgres`.
- Se estiver usando o banco padrão do Supabase, aplique as tabelas nele.
- Em redes sem IPv6 funcional, prefira a connection string do Session Pooler.

## Treinar o Modelo

Antes de subir a API pela primeira vez, gere o artefato do modelo:

```powershell
.\.venv\Scripts\python.exe scripts\train_model.py
```

Esse comando cria ou atualiza:

```text
models/triage_model.joblib
models/triage_model_metadata.json
```

Para o deploy demonstrável na Vercel, estes dois arquivos são versionados porque são pequenos o suficiente para o projeto atual e evitam treinar o modelo durante o build.

## Subir a Aplicação Localmente

Defina o `PYTHONPATH` para que o layout `src/` seja encontrado:

```powershell
$env:PYTHONPATH="src"
```

Inicie a API com Uvicorn:

```powershell
.\.venv\Scripts\python.exe -m uvicorn triage_api.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000/
```

Endpoints úteis:

```text
GET  /health
POST /token
POST /login
POST /chat/message
POST /predict/triage
```

## Frontend

A API serve o frontend automaticamente a partir da pasta `frontend/`.

Telas disponíveis:

- Login: `http://127.0.0.1:8000/`
- Atendimento: redirecionamento após login bem-sucedido

O fluxo recomendado é:

1. Entrar com o usuário de teste.
2. Responder a entrevista guiada.
3. Conferir os campos preenchidos no painel lateral.
4. Obter a categoria de risco ao final da coleta.
5. Usar `Nova entrevista` para reiniciar o atendimento.

## Autenticação

Os endpoints protegidos exigem token JWT.

Gerar token:

```bash
curl --location "http://127.0.0.1:8000/token" \
--header "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "username=fiap@tech2.com" \
--data-urlencode "password=fiap@Tech_2"
```

Resposta esperada:

```json
{
  "access_token": "<ACCESS_TOKEN>",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Predição Via API

Exemplo para Postman ou curl:

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

Valores aceitos em `arrival_mode`:

```text
walk_in
wheelchair
ambulance
```

## Chat Via API

O chat recebe a mensagem do usuário e os dados já coletados:

```bash
curl --location "http://127.0.0.1:8000/chat/message" \
--header "Content-Type: application/json" \
--header "Authorization: Bearer <ACCESS_TOKEN>" \
--data '{
  "message": "79",
  "patient_data": {}
}'
```

Campos coletados pelo agente:

- `age`
- `heart_rate`
- `systolic_blood_pressure`
- `oxygen_saturation`
- `body_temperature`
- `pain_level`
- `chronic_disease_count`
- `previous_er_visits`
- `arrival_mode`

O backend valida as faixas esperadas antes de montar o payload final para o modelo.

## OpenAI

A integração com OpenAI é opcional.

Sem `OPENAI_API_KEY`, o sistema usa uma resposta local determinística para conduzir a entrevista.

Com `OPENAI_API_KEY`, o backend usa a Responses API para deixar a conversa mais natural, mantendo o controle dos campos obrigatórios no backend.

Para desenvolvimento local, `gpt-4.1-mini` é suficiente para este fluxo porque o backend continua responsável por validação, estado da entrevista e chamada ao modelo.

## Deploy na Vercel

Esta branch prepara uma versão demonstrável para Vercel usando:

- `api/index.py`: entrypoint FastAPI compatível com Vercel.
- `vercel.json`: roteia todas as requisições para a API e inclui `frontend/` e `models/` no bundle.
- `requirements.txt`: dependências enxutas de runtime.
- `models/triage_model.joblib`: modelo pronto para uso em produção demo.

Passos recomendados:

1. Faça login na Vercel.
2. Importe o repositório pelo GitHub.
3. Selecione a branch que contém os ajustes de deploy.
4. Configure as variáveis de ambiente no painel da Vercel.
5. Faça o deploy.

Variáveis mínimas na Vercel:

```text
DATABASE_URL
JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
MODEL_VERSION
OPENAI_API_KEY
OPENAI_MODEL
```

`OPENAI_API_KEY` pode ficar vazia se a demo usar apenas o fallback local do agente.

Pontos de atenção:

- O plano gratuito pode ter cold start.
- Dependências como `numpy`, `pandas` e `scikit-learn` aumentam o tempo de inicialização.
- Se o bundle crescer muito no futuro, mova o modelo para storage externo ou use uma plataforma dedicada para API Python.

## Logs

A API imprime logs estruturados no terminal:

```text
[date_time] - [triage_api] - [LEVEL] - [step] - [message] - [payload=...] - [server_response=...]
```

Passos comuns:

- `application_started`: aplicação iniciada.
- `auth_login_received`: tentativa de login recebida.
- `auth_login_completed`: login realizado.
- `predict_triage_received`: payload de predição recebido.
- `predict_triage_completed`: predição calculada.
- `prediction_repository_insert_started`: início da persistência.
- `prediction_persistence_completed`: predição salva.
- `prediction_persistence_failed`: falha ao salvar predição.
- `chat_message_received`: mensagem do chat recebida.
- `chat_message_completed`: mensagem do chat processada.

## Testes

Executar todos os testes:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Executar testes com cobertura:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=src/triage_api --cov-report=term-missing
```

A cobertura mínima configurada é `80%`.

Os notebooks são mantidos no Git para consulta da equipe, mas são ignorados pela cobertura via `pyproject.toml`.

## Problemas Comuns

### `Repositorio de usuarios nao configurado`

Verifique se `DATABASE_URL` está configurado no `.env` e reinicie o Uvicorn.

### Login retorna `401`

Confirme se `database/ddl/002_create_api_users.sql` foi executado e se está usando:

```text
fiap@tech2.com
fiap@Tech_2
```

### Erro ao resolver host do Supabase

Se a connection string direta retornar apenas IPv6 e sua rede não suportar IPv6, use a connection string do Session Pooler do Supabase.

### API não encontra `triage_api`

Defina o `PYTHONPATH` antes de iniciar o Uvicorn:

```powershell
$env:PYTHONPATH="src"
```

### Modelo não encontrado

Execute novamente:

```powershell
.\.venv\Scripts\python.exe scripts\train_model.py
```

## Convenções do Projeto

- Código, variáveis, rotas, métodos e nomes técnicos usam inglês com `snake_case`.
- Mensagens exibidas ao usuário ficam em português.
- `.env` nunca deve ser versionado.
- Alterações devem entrar por Pull Request para preservar a branch `main`.
