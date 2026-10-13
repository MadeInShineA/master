FROM ubuntu:26.04

ENV RUNNER_VERSION=2.334.0

LABEL RunnerVersion=${RUNNER_VERSION}
LABEL org.opencontainers.image.source="https://github.com/MadeInShineA/a-guide-to-mlops"

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y build-essential lsb-release python3 python3-pip \
    curl jq vim gpg git unzip tar gettext-base libicu-dev

# Install uv (used by dvc.yaml to run the training stages)
# UV_INSTALL_DIR puts the binary in /usr/local/bin so it's on PATH for the
# ubuntu user too (default would be /root/.local/bin, invisible to the runner)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /home/ubuntu

# Install GitHub Actions Runner
RUN curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
RUN tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Install extra dependencies for the runner
RUN ./bin/installdependencies.sh

COPY startup.sh .

RUN chmod +x startup.sh

# Ensure everything in the workdir belongs to the ubuntu user.
RUN chown -R ubuntu:ubuntu /home/ubuntu && \
    chmod -R u+rwX /home/ubuntu

USER ubuntu

ENTRYPOINT ["./startup.sh"]
