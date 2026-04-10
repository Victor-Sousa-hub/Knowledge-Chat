# Knowledge Chat — AI Agent com AWS Bedrock

Sistema de chat inteligente que permite ao usuário fazer upload de documentos (PDF, TXT, Markdown) e conversar com um agente de IA que consulta esses documentos como base de conhecimento. O agente é alimentado pelo **AWS Bedrock Agent** integrado a uma **Knowledge Base** vetorial, com isolamento de contexto por sessão.

---

## Visão Geral

```
Usuário → Frontend (Next.js) → Backend (FastAPI) → AWS Bedrock Agent
                                                  ↕
                                          AWS S3 + Knowledge Base
```

- O **frontend** oferece uma interface de chat onde o usuário inicia sessões, envia documentos e faz perguntas.
- O **backend** expõe uma API REST, processa os documentos (upload para S3, sync na Knowledge Base) e delega as perguntas ao Bedrock Agent.
- O **Bedrock Agent** raciocina sobre os documentos da sessão e retorna respostas com citações de fontes.

---

## Estrutura do Projeto

```
knowledge_DDD/
├── docker-compose.yml          # Orquestração dos serviços
├── up.sh                       # Script auxiliar para subir com credenciais AWS
└── app/
    ├── frontend/
    │   └── my-app/             # Aplicação Next.js (TypeScript)
    │       ├── app/
    │       │   ├── components/ # Componentes React (ChatInterface, SessionGate)
    │       │   ├── lib/api.ts  # Cliente HTTP para o backend
    │       │   └── page.tsx    # Página principal
    │       └── Dockerfile
    └── backend/
        ├── main.py             # Entrypoint (desenvolvimento local)
        ├── pyproject.toml      # Dependências Python (uv)
        ├── .env.example        # Template de variáveis de ambiente
        ├── Dockerfile
        ├── entrypoint.sh
        └── src/
            ├── Domain/         # Núcleo do negócio (sem dependências externas)
            │   ├── Entities/
            │   ├── Interfaces/
            │   ├── Services/
            │   └── ValueObjects/
            ├── application/    # Casos de uso e DTOs
            │   ├── dtos/
            │   └── use_cases/
            ├── infrastructure/ # Implementações concretas (AWS)
            │   ├── aws/
            │   └── utils/
            └── presentation/   # Controllers FastAPI e injeção de dependências
                └── api/
                    ├── controllers/
                    ├── dependencies.py
                    └── main.py
```

---

## Arquitetura DDD

O backend segue os princípios do **Domain-Driven Design**, organizado em quatro camadas com dependências de fora para dentro:

```
Presentation → Application → Domain ← Infrastructure
```

### Domain (Núcleo)

Contém as regras de negócio puras, sem nenhuma dependência de frameworks ou serviços externos.

| Camada | Descrição |
|---|---|
| **Entities** | Objetos com identidade e ciclo de vida (`Session`, `KnowledgeSource`) |
| **Value Objects** | Objetos imutáveis definidos por valor (`SessionId`, `DocumentKey`) |
| **Interfaces** | Contratos abstratos que a infraestrutura deve implementar |
| **Services** | Orquestração de lógica de domínio que envolve múltiplas entidades (`ChatManager`) |

### Application

Coordena os casos de uso da aplicação. Cada caso de uso representa uma ação do sistema, recebe DTOs de entrada e produz DTOs de saída. Não contém lógica de negócio — delega ao Domain.

### Infrastructure

Implementa as interfaces definidas no Domain usando serviços externos (AWS SDK). Nenhuma lógica de negócio reside aqui.

### Presentation

Controllers FastAPI que traduzem requisições HTTP em chamadas aos casos de uso. A injeção de dependências (`dependencies.py`) é responsável por montar o grafo de objetos.

---

## Estruturas Abstratas (Interfaces do Domain)

As interfaces garantem que a camada de domínio nunca dependa de implementações concretas, tornando os provedores substituíveis e testáveis de forma isolada.

### `IAgentProvider`
```python
# src/Domain/Interfaces/IAgentProvider.py
def ask_agent(agent_id, agent_alias_id, session_id, prompt, knowledge_base_id) -> dict
```
Abstrai o provedor de agente de IA. Implementado por `BedrockAgentProvider`.

### `IKnowledgeBaseProvider`
```python
# src/Domain/Interfaces/IKnowledgeBaseProvider.py
def sync_data_source(kb_id, data_source_id) -> str
```
Abstrai o disparo de ingestion jobs na base de conhecimento. Implementado por `BedrockKnowledgeBaseProvider`.

### `IStorageProvider`
```python
# src/Domain/Interfaces/IStorageProvider.py
def ensure_bucket_exists(bucket_name) -> None
def upload_knowledge_document(file_path, bucket, key) -> None
def upload_document_metadata(bucket, key, session_id) -> None
def list_session_documents(bucket, session_id) -> list[dict]
def delete_session_documents(bucket, session_id) -> int
```
Abstrai o armazenamento de documentos. Implementado por `S3StorageProvider`.

### `ISessionRepository`
```python
# src/Domain/Interfaces/ISessionRepository.py
def save(session) -> None
def find_by_id(session_id) -> Optional[Session]
def delete(session_id) -> None
```
Contrato de persistência de sessões (interface preparada para futura implementação).

---

## Endpoints da API

A documentação interativa completa está disponível em `http://localhost:8000/docs` após subir a aplicação.

### Health

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Verifica se a API está no ar |

**Resposta:**
```json
{ "status": "online", "message": "O Agente está ouvindo." }
```

---

### Chat

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/chat/` | Envia uma pergunta ao Bedrock Agent |

**Body:**
```json
{
  "session_id": "minha-sessao-123",
  "question": "Qual é o tema principal do documento?"
}
```

**Resposta:**
```json
{
  "answer": "O documento aborda...",
  "session_id": "minha-sessao-123",
  "sources": [
    { "file": "relatorio.pdf", "uri": "s3://bucket/...", "pages": [3, 7] }
  ]
}
```

> O `session_id` é usado tanto para manter memória de curto prazo no agente quanto para filtrar os documentos da Knowledge Base — garantindo que cada sessão só consulte seus próprios arquivos.

---

### Knowledge (Documentos)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/sessions/{session_id}/documents/` | Faz upload de um documento para a sessão |

**Parâmetros:**
- `session_id` (path): identificador da sessão
- `file` (form-data): arquivo a ser enviado (PDF, TXT ou Markdown)

**Resposta:**
```json
{
  "file_name": "relatorio.pdf",
  "s3_key": "sessions/minha-sessao-123/relatorio.pdf",
  "bucket": "meu-bucket",
  "ingestion_job_id": "abc-123",
  "message": "Documento 'relatorio.pdf' enviado e sync da Knowledge Base iniciado."
}
```

---

### Sessions

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/session/sessions/{session_id}/history` | Lista documentos carregados na sessão |
| `DELETE` | `/session/sessions/{session_id}` | Encerra a sessão e remove todos os documentos |

**Resposta do GET:**
```json
{
  "session_id": "minha-sessao-123",
  "documents": [
    { "name": "relatorio.pdf", "size": 204800 }
  ],
  "total": 1
}
```

**Resposta do DELETE:**
```json
{
  "session_id": "minha-sessao-123",
  "deleted_documents": 1,
  "message": "Sessão 'minha-sessao-123' encerrada. 1 documento(s) removido(s) e Knowledge Base sincronizada."
}
```

---

## Rodando com Docker Compose

### Pré-requisitos

- Docker e Docker Compose instalados
- AWS CLI configurado com credenciais válidas
- Arquivo `app/backend/.env` preenchido (ver seção abaixo)

### Opção 1 — Script auxiliar (recomendado)

O script `up.sh` verifica e exporta automaticamente as credenciais AWS temporárias antes de subir os containers:

```bash
./up.sh
```

Para reconstruir as imagens:
```bash
./up.sh --build
```

### Opção 2 — Docker Compose direto

Se suas credenciais AWS já estiverem exportadas no shell (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`):

```bash
docker compose up --build
```

### Serviços disponíveis após subir

| Serviço | URL |
|---|---|
| Frontend (Next.js) | http://localhost:3000 |
| Backend (FastAPI) | http://localhost:8000 |
| Docs interativos | http://localhost:8000/docs |

### Parando os containers

```bash
docker compose down
```

---

## Variáveis de Ambiente (`.env.example`)

Copie o arquivo de exemplo e preencha com os valores do seu ambiente AWS:

```bash
cp app/backend/.env.example app/backend/.env
```

| Variável | Descrição |
|---|---|
| `AWS_BEARER_TOKEN_BEDROCK` | Token de autenticação para o serviço Bedrock (gerado via `aws sts`) |
| `BUCKET_NAME` | Nome do bucket S3 onde os documentos das sessões serão armazenados |
| `REGION` | Região AWS onde os recursos estão provisionados (ex: `us-east-1`) |
| `AGENT_ID` | ID do Bedrock Agent criado no console AWS |
| `KNOWLEDGE_BASE_ID` | ID da Knowledge Base associada ao agente no Bedrock |
| `DATA_SOURCE_ID` | ID do Data Source (S3) configurado na Knowledge Base |

> As credenciais de acesso AWS (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) são injetadas pelo docker-compose diretamente do ambiente do host — não precisam estar no `.env`.
