# 🏥 HealthLake Agent

**An identity-aware healthcare agent on AWS Bedrock AgentCore: it answers natural-language questions over clinical data in AWS HealthLake (FHIR R4) and documents in S3, and it can only ever read records the caller is entitled to.**

Bridges conversational reasoning (Bedrock Claude) with governed clinical data access, where the caller's identity rides into every tool call so entitlement is enforced at the data layer, not by prompt instruction.

---

## The problem this solves

- Front-desk and clinical staff burn hours on routine lookups, "what's this patient's immunization history", "find the latest visit note", that don't need a human to run.
- The data is there (FHIR resources in HealthLake, documents in S3) but it takes a query, not a question, and the people who need it don't speak FHIR.
- The hard part isn't reasoning, it's scope: a scheduling mistake is recoverable, returning a record that belongs to someone else is a breach.
- So access is scoped by the authenticated identity on every call, the model never sees a resource the caller isn't entitled to, and every turn is auditable.

---

## What it does

- **Answers questions** over clinical data using seven tools, four for FHIR (HealthLake), three for documents (S3).
- **Resolves entitlement** from the caller's verified identity (role plus the patients they're allowed to see) before any data call runs.
- **Translates codes** so SNOMED, LOINC and RxNorm values come back as readable text instead of raw codes.
- **Reads documents** directly or hands back a time-limited presigned URL for large files.
- **Logs every turn** with a prompt digest and the tools invoked, never raw PHI, so the access trail is queryable.

---

## Architecture

```
        Caller (authenticated)
               │  identity (Cognito / OIDC claims)
               ▼
   ┌─────────────────────┐
   │  AgentCore Runtime  │   containerized ARM64, session memory
   │  agent_agentcore.py │   builds a scoped SessionContext per request
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │      agent.py       │   Bedrock Claude reasons, selects tools
   └──────────┬──────────┘
     ┌─────────┴──────────┐
     ▼                    ▼
  FHIR tools           S3 tools          every tool calls assert_in_scope(ctx)
  (HealthLake)         (documents)       before any AWS request
```

Each tool runs `assert_in_scope` against the request's `SessionContext` first, then makes a SigV4-signed FHIR call or a boto3 S3 call. Data-layer scoping (IAM plus FHIR `_security` filters) enforces the same boundary independently, so a prompt can't talk the agent past it.

---

## Tech stack

| Layer | Tooling |
| :--- | :--- |
| Agent runtime | **Bedrock AgentCore** (containerized ARM64 Lambda) |
| Reasoning | **Bedrock Claude** (model id via `MODEL_ID`) |
| Agent + tools | **Strands** (`@tool`) in `agent.py` |
| Clinical data | **AWS HealthLake** FHIR R4, SigV4-signed REST |
| Documents | **Amazon S3** (read + presigned URLs) |
| Identity | **Cognito / OIDC** claims, propagated per call |
| Deploy | **AWS CLI + boto3** scripts (PowerShell + Python) |

---

## Project structure

```
healthlake-agent/
├── agent.py                 # Agent + 7 tools (4 FHIR, 3 S3)
├── agent_agentcore.py       # AgentCore entrypoint, builds the scoped session
├── config.py                # Env / settings
├── models/                  # SessionContext + UserRole, response, interaction log
├── utils/                   # auth scope checks, retry, FHIR code translation
├── prompts/                 # system prompt
├── scripts/                 # deploy + verify (PowerShell + Python)
├── iam/                     # least-privilege policy templates
├── docs/                    # ARCHITECTURE / DEPLOYMENT / QUICKSTART
└── examples/                # FastAPI + browser chat
```

---

## Key engineering decisions

- **Scope at the data layer, not the prompt.** The verified identity is propagated into every tool call and checked with `assert_in_scope` before any AWS request, with IAM and FHIR `_security` enforcing the same boundary underneath. Scope errors, not reasoning errors, are the risk that matters in clinical data.
- **Identity comes from the request context, never the prompt body.** `agent_agentcore.py` builds the `SessionContext` from verified claims, so nothing the user types can widen their access.
- **Codes become language.** A translation pass turns coded FHIR values into readable text before they reach the model or the user.
- **No CloudFormation.** Provisioning is CLI plus boto3 so the multi-minute HealthLake datastore creation stays visible and re-runnable step by step. IAM lives as reviewable JSON in `iam/`.
- **Auditable by construction.** Each turn writes an interaction log with a prompt digest and the tools used, so compliance reads the access trail without a separate logging retrofit.

---

## Deploy (outline)

```bash
cp .env.template .env          # set datastore id, bucket, model id, pool id
python scripts/deploy_with_verification.py
# or, on Windows:
# .\scripts\deploy_agentcore.ps1
```

See `docs/DEPLOYMENT.md` for the full sequence and `docs/ARCHITECTURE.md` for the design.

---

> **Note:** Portfolio extract. No credentials are committed, deployment uses your own AWS
> auth, and the datastore id, bucket and identifiers are placeholders you set in `.env`. Point it at
> a HealthLake datastore loaded with synthetic data (for example Synthea) before any real use.
> HIPAA-eligible services do not make an application compliant, that's on the deployment.
