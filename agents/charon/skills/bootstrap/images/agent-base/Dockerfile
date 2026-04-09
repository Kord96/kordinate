FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NPM_CONFIG_UPDATE_NOTIFIER=false
ENV PATH="/usr/local/bin:${PATH}"
ENV KORDINATE_HOME=/app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    gnupg \
    openssh-client \
    pass \
    python3 \
    python3-yaml \
    jq \
    ripgrep \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN cd /app/shared/klaude-daemon \
  && npm ci \
  && npm run build \
  && npm install -g . @anthropic-ai/claude-code

RUN ln -s /app/lib/scripts /app/scripts \
  && chmod +x /app/lib/scripts/setup-agent-dir.sh /app/lib/scripts/deploy-runtime.sh /app/shared/klaude-daemon/bin/klaude-daemon

CMD ["klaude-daemon"]
