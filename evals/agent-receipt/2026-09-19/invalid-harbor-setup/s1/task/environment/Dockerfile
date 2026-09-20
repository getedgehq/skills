FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN cp -r "$FORGE_ROOT/fixtures/agent-receipt-public-safe/." . && mkdir -p out
