ARG REGISTRY=local
ARG BASE_IMAGE=${REGISTRY}/agent-base:latest
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.title="agent-augur"
LABEL org.opencontainers.image.description="Augur specialization layered on the shared agent-base runtime"

RUN ln -sfn /app/agents/augur/bundles /app/bundles \
  && ln -sfn /app/agents/augur/memory /app/memory
