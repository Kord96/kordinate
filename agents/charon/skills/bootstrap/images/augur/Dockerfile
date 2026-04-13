ARG REGISTRY=local
ARG BASE_IMAGE=${REGISTRY}/agent-base:latest
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.title="agent-augur"
LABEL org.opencontainers.image.description="Augur specialization layered on the shared agent-base runtime"

RUN python3 /app/agents/augur/scripts/build_skill_bundles.py \
  && python3 /app/agents/augur/scripts/build_memory_bundles.py \
  && python3 /app/agents/augur/scripts/build_detector_bundles.py \
  && python3 /app/agents/augur/scripts/build_runtime_bundles.py

RUN ln -sfn /app/agents/augur/.generated/bundles /app/bundles \
  && ln -sfn /app/agents/augur/memory /app/memory
