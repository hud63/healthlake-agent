# Quickstart (local)

Set up a virtualenv and install dependencies:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.template .env   # then edit values
```

List the tools the agent exposes:

```bash
python agent.py
```

Then point `.env` at a HealthLake datastore loaded with synthetic data and deploy per
`docs/DEPLOYMENT.md`.
