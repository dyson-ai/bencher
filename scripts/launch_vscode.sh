#! /bin/bash
set -e

export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #gets the current directory

#move to the project root folder
cd "$SCRIPT_DIR"/..

git submodule update --init --recursive

CONTAINER_NAME=${PWD##*/}  
# CONTAINER_NAME="${PWD##*/}_$(date +%Y-%m-%d_%H-%M-%S)"  

echo "stopping existing container" "$CONTAINER_NAME" 
# docker stop "$CONTAINER_NAME" || true 
docker rename "$CONTAINER_NAME" "${CONTAINER_NAME}_$(date +%Y-%m-%d_%H-%M-%S)" || true 


CONTAINER_HEX=$(printf $CONTAINER_NAME | xxd -p | tr '\n' ' ' | sed 's/\\s//g' | tr -d ' ');


# Set the virtual environment directory name
VENV_DIR="venv"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    # Create the virtual environment
    python3 -m venv $VENV_DIR
    echo "Virtual environment created in $VENV_DIR"
else
    echo "Virtual environment already exists in $VENV_DIR"
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install the deps_rocker package if not already installed
if ! pip show deps_rocker > /dev/null 2>&1; then
    pip install deps_rocker
    echo "deps_rocker package installed"
else
    echo "deps_rocker package already installed"
fi

# Run the rocker command with the specified parameters
CONTAINER_NAME="my_container"  # Replace with your desired container name
rocker --nvidia --x11 --user --pull --git --image-name "$CONTAINER_NAME" --name "$CONTAINER_NAME" --volume "${PWD}":/workspaces/"${CONTAINER_NAME}":Z --deps --oyr-run-arg "--detach" ubuntu:22.04

# Deactivate the virtual environment
deactivate


#this follows the same convention as if it were opened by a vscode devcontainer
code --folder-uri vscode-remote://attached-container+"$CONTAINER_HEX"/workspaces/"${CONTAINER_NAME}"