# Quick Reference

| Thing | Where |
| :--- | :--- |
| Tool definitions (7) | `agent.py` |
| AgentCore entrypoint | `agent_agentcore.py` |
| Settings / env | `config.py`, `.env.template` |
| Identity + scope | `models/session.py`, `utils/auth_helpers.py` |
| System prompt | `prompts/healthcare_assistant_prompt.py` |
| Deploy | `scripts/deploy_with_verification.py`, `scripts/deploy_agentcore.ps1` |
| IAM templates | `iam/*.json` |
| Docs | `docs/` |

## The 7 tools
FHIR: `get_datastore_info`, `search_fhir_resources`, `read_fhir_resource`, `patient_everything`
S3: `list_s3_documents`, `read_s3_document`, `generate_s3_presigned_url`

## Golden rule
Every tool receives a `SessionContext` and calls `assert_in_scope(...)` first. Access is scoped by
identity at the data layer (IAM + FHIR `_security`) AND in-app — never by prompt instruction.

## To make it real
1. `cp .env.template .env` and fill in datastore id, bucket, model id, pool id.
2. Implement the `TODO`s in `agent.py` (FHIR SigV4 + S3 boto3 calls).
3. Implement identity extraction in `agent_agentcore.py::_session_from_event`.
4. `python scripts/deploy_with_verification.py`.
