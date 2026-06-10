# HealthLake Agent — Skeleton

> **Reference scaffold, not production.** This is a sanitized starter skeleton for an
> identity-aware healthcare agent on AWS Bedrock AgentCore over AWS HealthLake (FHIR R4).
> Every tool, model call, and deploy step is a **stub with `TODO` markers** — it documents the
> shape of the architecture so you can fill in implementation per engagement. No client data, no
> real account IDs, no secrets.

## What this skeleton is for

A conversational agent that answers natural-language questions over clinical data in **AWS
HealthLake** (FHIR R4) and documents in **S3**, with access **scoped by the caller's identity** so
the agent can only ever read records the caller is entitled to. The defining design principle is:

**Scope access at the data layer, not by prompt instruction.** The authenticated identity is
propagated into every tool call; the agent literally cannot retrieve a resource outside its scope.

## Architecture (target)

```
            Caller (authenticated)  ──identity (Cognito / OIDC)──┐
                                                                 ▼
   Chat / API ──► AgentCore Runtime ──► agent.py (LLM reasoning) ──► 7 tools
                  (containerized,                                   │
                   ARM64 Lambda)                ┌──────────────────┼──────────────────┐
                                                ▼                  ▼                  ▼
                                          FHIR tools          S3 doc tools       (identity ctx
                                          (HealthLake)        (clinical docs)     rides every call)
```

| Layer | Service | Role |
| :--- | :--- | :--- |
| Runtime | Bedrock AgentCore | Serverless container (ARM64); session memory |
| Reasoning | Bedrock (Claude) | Model id via `config.py` / `MODEL_ID` env (placeholder) |
| Clinical data | AWS HealthLake | FHIR R4 datastore; SigV4 REST |
| Documents | Amazon S3 | Clinical notes / guidelines; presigned URLs |
| Registry | Amazon ECR | Container image |
| Observability | CloudWatch | Logs / metrics |

No CloudFormation/CDK — provisioning and deploy are CLI scripts (PowerShell + Python) so the
5–10 minute HealthLake datastore creation stays visible. IAM is least-privilege JSON templates in
`iam/`.

## The 7 tools (stubs in `agent.py`)

FHIR (HealthLake): `get_datastore_info`, `search_fhir_resources`, `read_fhir_resource`,
`patient_everything`.
S3 (documents): `list_s3_documents`, `read_s3_document`, `generate_s3_presigned_url`.

## Layout

```
healthlake-agent/
├── agent.py                 # Agent + 7 tool stubs
├── agent_agentcore.py       # AgentCore entrypoint wrapper
├── config.py                # Env / settings
├── models/                  # SessionContext, response, interaction log
├── utils/                   # auth, retry, FHIR code translation
├── prompts/                 # system prompt
├── scripts/                 # deploy + verify (PowerShell + Python)
├── iam/                     # least-privilege policy templates
├── docs/                    # ARCHITECTURE / DEPLOYMENT / QUICKSTART
└── examples/                # FastAPI + browser chat stubs
```

## Quick start

See `docs/QUICKSTART.md`. In short: copy `.env.template` → `.env`, fill in your datastore/bucket,
implement the `TODO`s, then `scripts/deploy_with_verification.py`.

## Status

Skeleton. Tools raise `NotImplementedError`. Wire them to your HealthLake datastore + S3 bucket and
your identity provider before any real use. **HIPAA-eligible services do not make an application
compliant** — that's on the implementation.

## License

MIT — see `LICENSE`.
