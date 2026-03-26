FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/home/claude \
    TERM=xterm-256color

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget openssh-client openssh-server tmux gnupg pass \
    python3 python3-pip python3-yaml \
    jq unzip ca-certificates sudo iptables \
    && rm -rf /var/lib/apt/lists/*

# Node.js (LTS) — needed for claude-code and MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (pinned — apt latest builds with Go 1.26 which has runtime bugs)
ARG GH_VERSION=2.67.0
ARG TARGETARCH
RUN GH_ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "arm64" || echo "amd64") \
    && curl -sL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${GH_ARCH}.tar.gz" \
      | tar xz -C /tmp \
    && mv "/tmp/gh_${GH_VERSION}_linux_${GH_ARCH}/bin/gh" /usr/local/bin/gh \
    && rm -rf "/tmp/gh_${GH_VERSION}_linux_${GH_ARCH}"

# Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg \
      -o /usr/share/keyrings/tailscale-archive-keyring.gpg \
    && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list \
      -o /etc/apt/sources.list.d/tailscale.list \
    && apt-get update && apt-get install -y tailscale \
    && rm -rf /var/lib/apt/lists/*

# Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Create claude user and give ownership of claude-code install (enables auto-updates)
RUN useradd -m -s /bin/bash -d /home/claude claude \
    && echo "claude ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/claude \
    && chown -R claude:claude /usr/lib/node_modules/@anthropic-ai /usr/bin/claude

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER claude
WORKDIR /home/claude

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
