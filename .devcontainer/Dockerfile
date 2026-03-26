FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.4.1/hadolint-Linux-x86_64 \
    && chmod 755 /usr/local/bin/hadolint