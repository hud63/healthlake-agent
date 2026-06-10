# Quickstart (local)

This skeleton does not run end-to-end until the `TODO`s are implemented. To explore the structure:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   *nix: source .venv/bin/activate
pip install -r requirements.txt

cp .env.template .env   # then edit values
```

Import the agent module (tools will raise `NotImplementedError` until wired):

```python
from agent import TOOLS
print([t.__name__ for t in TOOLS])
```

Next: implement FHIR/S3 calls in `agent.py`, identity extraction in `agent_agentcore.py`, then
deploy per `docs/DEPLOYMENT.md`.
