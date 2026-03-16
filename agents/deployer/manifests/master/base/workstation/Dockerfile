FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/home/claude \
    TERM=xterm-256color

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget openssh-client tmux gnupg pass \
    python3 python3-pip python3-yaml \
    jq unzip ca-certificates sudo \
    && rm -rf /var/lib/apt/lists/*

# Node.js (LTS) — needed for claude-code and MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg \
      -o /usr/share/keyrings/tailscale-archive-keyring.gpg \
    && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list \
      -o /etc/apt/sources.list.d/tailscale.list \
    && apt-get update && apt-get install -y tailscale \
    && rm -rf /var/lib/apt/lists/*

# Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Create claude user
RUN useradd -m -s /bin/bash -d /home/claude claude \
    && echo "claude ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/claude

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER claude
WORKDIR /home/claude

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
