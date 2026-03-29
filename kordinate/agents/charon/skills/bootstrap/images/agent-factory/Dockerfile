FROM node:22-alpine

RUN apk add --no-cache git gnupg pass bash

# Create claude user (match workstation UID for shared PVC)
RUN adduser -D -s /bin/bash -h /home/claude claude

USER claude
RUN mkdir -p /home/claude/.npm-global \
    && npm config set prefix /home/claude/.npm-global
ENV NPM_CONFIG_PREFIX=/home/claude/.npm-global \
    PATH="/home/claude/.npm-global/bin:$PATH"

# Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

USER claude
WORKDIR /home/claude

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["exec node $KORDINATE_HOME/lib/mcp-agent-server/server.js"]
