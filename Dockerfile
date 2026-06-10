# Container image for Bedrock AgentCore Runtime (ARM64).
FROM public.ecr.aws/lambda/python:3.12-arm64

WORKDIR /var/task

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# AgentCore invokes the handler in agent_agentcore.py.
CMD ["agent_agentcore.handler"]
