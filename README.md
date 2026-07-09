# Projeto Triage API

Este repositório evoluiu de experimentos em notebook para um serviço de API menor e mais organizado.

## O que permanece
- `algoritmo_genetico.ipynb` segue como notebook de referência
- o dataset sintético continua sendo a base de treinamento

## O que foi adicionado
- uma árvore de código em `src/triage_api`
- um script de treinamento em `scripts/train_model.py`
- schemas tipados de requisição e resposta
- uma API de predição com FastAPI
- testes para a nova camada de serviços

## Fluxo principal
1. Execute `algoritmo_genetico.ipynb` para reproduzir a otimização por algoritmo genético
2. O notebook salva os melhores hiperparâmetros em `models/optimized_params.json`
3. Treine o modelo Random Forest a partir do CSV do dataset
4. Salve o artefato do modelo treinado em `models/`
5. Configure o PostgreSQL quando quiser persistir as requisições
6. Inicie a API
7. Faça login no frontend ou solicite um token com `POST /token`
8. Use a tela de chat ou envie um payload de triagem para `POST /predict/triage`

## Ordem de execução local
1. Instale as dependências
2. Opcionalmente, execute `algoritmo_genetico.ipynb` para gerar `models/optimized_params.json`
3. Treine o modelo
4. Inicie a API

## Integração do algoritmo genético
`algoritmo_genetico.ipynb` é o principal artefato técnico dos experimentos com algoritmo genético. Ele define a representação dos genes, seleção, crossover, mutação, função de fitness, três configurações de experimento e a comparação entre o modelo base e o otimizado.

A última célula do notebook exporta o indivíduo vencedor para:

```text
models/optimized_params.json
```

`scripts/train_model.py` lê esse arquivo automaticamente e treina o modelo da API com os hiperparâmetros otimizados. Se o arquivo não existir, o fluxo de treino usa os parâmetros padrão definidos em `src/triage_api/ml/training.py`.

## Banco de dados
O nome do banco PostgreSQL é `tech_challenge_fiap_2`. Use esse nome no final de `DATABASE_URL`.

Os scripts DDL estão em `database/ddl`:

```text
database/ddl/000_create_database.sql
database/ddl/001_create_triage_prediction_requests.sql
database/ddl/002_create_api_users.sql
```

Configure a conexão da API com:

```powershell
.\.venv\Scripts\python.exe scripts\train_model.py
```

Para desenvolvimento local com Supabase e rede IPv4, prefira a string de conexão do Session Pooler:

```text
DATABASE_URL=postgresql://postgres.<PROJECT-REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres
```

Para desenvolvimento local, use `.env.example` como base e crie um arquivo `.env` com a senha real. O arquivo `.env` é ignorado pelo Git e carregado automaticamente quando a API inicia. Reinicie o Uvicorn após alterar o `.env`.

Quando `DATABASE_URL` está configurado, cada `POST /predict/triage` é salvo em `triage_prediction_requests`.

## Frontend e agente de chat
A API serve um frontend simples a partir da pasta `frontend`:

```text
http://127.0.0.1:8000/
```

Telas:

- Tela de login: autentica com `/token`
- Tela de chat: envia mensagens para `/chat/message`

O agente de chat coleta os campos obrigatórios da triagem um por um:

- age
- heart_rate
- systolic_blood_pressure
- oxygen_saturation
- body_temperature
- pain_level
- chronic_disease_count
- previous_er_visits
- arrival_mode

Quando todos os campos estão preenchidos, o backend chama o mesmo serviço de modelo usado por `POST /predict/triage` e devolve a categoria de risco para o usuário.

A integração com OpenAI é obrigatória para interpretar o resultado do modelo. Configure `OPENAI_API_KEY` antes de usar fluxos de predição que retornam o resultado final da triagem. O backend usa a OpenAI Responses API para gerar uma interpretação em apoio clínico a partir da saída do modelo e dos dados do paciente. Se a chave estiver ausente ou a OpenAI não retornar texto, a API responde com `503` em vez de gerar uma interpretação fixa local.

Durante a coleta dos campos, o agente de chat ainda usa parsing determinístico para capturar respostas numéricas e categóricas, mas a explicação final da triagem é sempre produzida pela LLM.

## Autenticação
Os endpoints protegidos usam autenticação OAuth2 Bearer com um JWT retornado por `/token` ou `/login`.

Crie a tabela de autenticação e o usuário inicial com:

```text
database/ddl/002_create_api_users.sql
```

Usuário inicial:

```text
username: fiap@tech2.com
password: fiap@Tech_2
```

Gerar um token:

```bash
curl --location "http://127.0.0.1:8000/token" \
--header "Content-Type: application/x-www-form-urlencoded" \
--data-urlencode "username=fiap@tech2.com" \
--data-urlencode "password=fiap@Tech_2"
```

Chamar o endpoint protegido de predição:

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

Chamar o endpoint protegido de chat:

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
A API escreve logs estruturados no terminal usando este padrão:

```text
[date_time] - [triage_api] - [LEVEL] - [step] - [message] - [payload=...] - [server_response=...]
```

Etapas importantes da predição:

- `predict_triage_received`: a API recebeu o payload da requisição
- `predict_triage_completed`: o modelo retornou uma predição
- `prediction_persistence_skipped`: `DATABASE_URL` não estava configurado
- `prediction_persistence_completed`: a predição foi salva com sucesso
- `prediction_persistence_failed`: a API não conseguiu salvar a predição no PostgreSQL

## Testes e cobertura
Executar os testes automatizados:

```powershell
$env:PYTHONPATH="src"
```

Executar os testes com cobertura:

```powershell
.venv\Scripts\python.exe -m pytest --cov=src/triage_api --cov-report=term-missing
```

A meta mínima atual de cobertura é `80%`.

## Observações
- Os identificadores do código usam inglês e `snake_case`
- As mensagens exibidas ao usuário estão em português
