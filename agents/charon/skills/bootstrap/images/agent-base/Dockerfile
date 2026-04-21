FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NPM_CONFIG_UPDATE_NOTIFIER=false
ENV PATH="/usr/local/bin:${PATH}"
# Baked Kordinate code root inside the image. Keep this separate from HOME,
# which remains the standard Unix tool home for shells and CLIs.
ENV KORDINATE_HOME=/app
ENV JOERN_HOME=/opt/joern
ENV PATH="${JOERN_HOME}/joern-cli:${JOERN_HOME}/joern-cli/bin:${PATH}"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    docker.io \
    git \
    gnupg \
    openjdk-17-jre-headless \
    openssh-client \
    pass \
    python3 \
    python3-yaml \
    jq \
    ripgrep \
    unzip \
    wget \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p "${JOERN_HOME}" \
  && cd /tmp \
  && wget -q "https://github.com/joernio/joern/releases/download/v4.0.518/joern-install.sh" \
  && chmod +x joern-install.sh \
  && sed -i 's/sudo //g' joern-install.sh \
  && ./joern-install.sh \
  && rm -f joern-install.sh joern-cli.zip

WORKDIR /app

COPY . /app

RUN cd /app/shared/klaude-daemon \
  && npm ci \
  && npm run build \
  && npm install -g . \
  && cd /app/shared/kord/api \
  && npm ci \
  && npm run build \
  && npm install -g . @anthropic-ai/claude-code @gitlawb/openclaude \
  && python3 - <<'PY'
from pathlib import Path

target = Path("/usr/local/lib/node_modules/@gitlawb/openclaude/dist/cli.mjs")
text = target.read_text()

count_tokens_old = """      const response = await anthropic.beta.messages.countTokens({
        model: normalizeModelStringForAPI(model),
        messages: messages.length > 0 ? messages : [{ role: \"user\", content: \"foo\" }],
        tools,
        ...filteredBetas.length > 0 && { betas: filteredBetas },
        ...containsThinking && {
          thinking: {
            type: \"enabled\",
            budget_tokens: TOKEN_COUNT_THINKING_BUDGET
          }
        }
      });
"""

count_tokens_new = """      const countTokensFn = anthropic?.beta?.messages?.countTokens;
      if (typeof countTokensFn !== \"function\") {
        return null;
      }
      const response = await countTokensFn.call(anthropic.beta.messages, {
        model: normalizeModelStringForAPI(model),
        messages: messages.length > 0 ? messages : [{ role: \"user\", content: \"foo\" }],
        tools,
        ...filteredBetas.length > 0 && { betas: filteredBetas },
        ...containsThinking && {
          thinking: {
            type: \"enabled\",
            budget_tokens: TOKEN_COUNT_THINKING_BUDGET
          }
        }
      });
"""

retry_old = """      } else {
        delayMs = getRetryDelay(attempt, retryAfter);
      }
"""

retry_new = """      } else {
        delayMs = getRetryDelay(attempt, retryAfter);
        if (error41 instanceof APIError && error41.status === 429) {
          const errorMessageText = typeof error41.message === \"string\" ? error41.message.toLowerCase() : \"\";
          const firstTokenOverload = errorMessageText.includes(\"didn't generate first token before the given deadline\") || errorMessageText.includes(\"service is overloaded\");
          delayMs = Math.max(delayMs, firstTokenOverload ? 15000 : 5000);
        }
      }
"""

if count_tokens_old not in text:
    raise SystemExit("openclaude countTokens patch anchor not found")
if retry_old not in text:
    raise SystemExit("openclaude retry patch anchor not found")

text = text.replace(count_tokens_old, count_tokens_new, 1)
text = text.replace(retry_old, retry_new, 1)
target.write_text(text)
PY

RUN ln -s /app/lib/scripts /app/scripts \
  && chmod +x /app/lib/scripts/setup-agent-dir.sh /app/lib/scripts/deploy-runtime.sh /app/shared/klaude-daemon/bin/klaude-daemon

CMD ["klaude-daemon"]
