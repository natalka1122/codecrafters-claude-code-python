FROM mcr.microsoft.com/devcontainers/base:ubuntu26.04

ENV DEBIAN_FRONTEND=noninteractive
# Install packages
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg python3 python3-pip python3-venv git iputils-ping net-tools telnet tcpdump redis-tools netcat-openbsd dnsutils && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN pip install --break-system-packages --upgrade argcomplete mypy pytest pytest-cov pytest-asyncio wemake-python-styleguide

# Copy project files and install dependencies
WORKDIR /workspace
COPY pyproject.toml .
RUN pip install --break-system-packages -e .

# Install Codecrafters Python
RUN curl -fsSL https://codecrafters.io/install.sh | bash
