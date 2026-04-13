FROM eclipse-temurin:21-jdk-jammy

ARG JOERN_VERSION=4.0.518
ENV JOERN_HOME=/opt/joern
ENV PATH="${JOERN_HOME}/joern-cli:${JOERN_HOME}/joern-cli/bin:${PATH}"

RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p "${JOERN_HOME}" && \
    cd /tmp && \
    wget -q "https://github.com/joernio/joern/releases/download/v${JOERN_VERSION}/joern-install.sh" && \
    chmod +x joern-install.sh && \
    sed -i 's/sudo //g' joern-install.sh && \
    ./joern-install.sh && \
    rm -f joern-install.sh joern-cli.zip

RUN mkdir -p /workspace/cpgs /workspace/scripts /workspace/output

WORKDIR /workspace

CMD ["bash", "-lc", "sleep infinity"]
