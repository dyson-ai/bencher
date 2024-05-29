FROM mcr.microsoft.com/devcontainers/python:0-3.10

RUN apt-get update && apt install -y git-lfs curl

RUN python -m pip install --upgrade pip \
    && python -m pip install 'flit>=3.8.0'

ENV FLIT_ROOT_INSTALL=1

ENV PIXI_VERSION=0.23.0
# download the musl build since the gnu build is not available on aarch64
RUN curl -Ls \
    "https://github.com/prefix-dev/pixi/releases/download/v${PIXI_VERSION}/pixi-$(uname -m)-unknown-linux-musl" \
    -o /pixi && chmod +x /pixi
RUN /pixi --version

COPY pyproject.toml .
RUN touch README.md \
    && mkdir -p src/bencher \
    && python -m flit install --only-deps --deps develop \
    && rm -r pyproject.toml README.md src
