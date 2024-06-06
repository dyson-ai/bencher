FROM ghcr.io/prefix-dev/pixi:0.23.0-jammy AS build
# FROM ghcr.io/prefix-dev/pixi:pixi:0.23.0-jammy-cuda-11.7.1 AS build
# docker pull ghcr.io/prefix-dev/pixi:0.23.0-focal-cuda-11.7.1


# # copy source code, pixi.toml and pixi.lock to the container
COPY . /workspaces
WORKDIR /workspaces
# RUN pixi install
# # run some compilation / build task (if needed)
# RUN pixi run build
# # run the `install` command (or any other). This will also install the dependencies into `/workspaces/.pixi`
# # assumes that you have a `prod` environment defined in your pixi.toml
# RUN pixi run install -e prod
# Create the shell-hook bash script to activate the environment
RUN pixi shell-hook  > /shell-hook.sh

# extend the shell-hook script to run the command passed to the container
RUN echo 'exec "$@"' >> /shell-hook.sh

FROM ubuntu:22.04 AS production

# only copy the production environment into prod container
# please note that the "prefix" (path) needs to stay the same as in the build container
COPY --from=build /workspaces/.pixi/envs/prod /workspaces/.pixi/envs/prod
COPY --from=build /shell-hook.sh /shell-hook.sh
WORKDIR /workspaces
EXPOSE 8000

# set the entrypoint to the shell-hook script (activate the environment and run the command)
# no more pixi needed in the prod container
ENTRYPOINT ["/bin/bash", "/shell-hook.sh"]