FROM node:22-alpine

RUN apk add --no-cache git gnupg pass bash python3 py3-yaml curl

# Create claude user (match workstation UID for shared PVC)
RUN adduser -D -s /bin/bash -h /home/claude claude

# Platform code — baked into image, no runtime cloning needed
COPY lib/agent-pod-daemon /app/daemon
COPY lib/agent-scribe /app/scribe
COPY lib/job-router /app/router
COPY lib/scripts /app/scripts
COPY lib/hooks /app/hooks
COPY lib/templates /app/templates
COPY shared /app/shared
COPY agents /app/agents

# Install dependencies
RUN cd /app/daemon && npm install --production \
    && cd /app/scribe && npm install --production \
    && cd /app/router && npm install --production

# Claude Code CLI
USER claude
RUN mkdir -p /home/claude/.npm-global \
    && npm config set prefix /home/claude/.npm-global
ENV NPM_CONFIG_PREFIX=/home/claude/.npm-global \
    PATH="/home/claude/.npm-global/bin:$PATH"
RUN npm install -g @anthropic-ai/claude-code

WORKDIR /home/claude

ENTRYPOINT ["/bin/bash", "-c"]
