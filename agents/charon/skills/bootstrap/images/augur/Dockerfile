ARG REGISTRY=local
ARG BASE_IMAGE=${REGISTRY}/agent-base:latest
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.title="agent-augur"
LABEL org.opencontainers.image.description="Augur specialization layered on the shared agent-base runtime"

# Augur now installs from published releases under $AGENT_HOME_DIR/.augur/current
# during runtime seeding. Keep the specialization image lightweight and avoid
# depending on the in-repo source tree at image-build time.
RUN mkdir -p /app/bundles /app/memory
