#!/bin/bash

# Get username from command line
if [ $# -eq 0 ]; then
    echo "No username supplied. Please supply a github username as the first argument."
    exit 1
fi

# Store username in variable
USERNAME=$1

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "You have uncommitted changes. Please commit or stash them and try again."
    exit 1
fi

# Get the appropriate version of the container using git
VERSION=$(git rev-parse --abbrev-ref HEAD)-$(git describe)

# Build the container. Add the version as a tag and as ENV variable SOURCE_VERSION
docker build -t ghcr.io/$USERNAME/karaoqueue:$VERSION --build-arg SOURCE_VERSION=$VERSION .

# Ask the user if they want to push the container. Confirm Version.
read -p "Push container to ghcr.io/$USERNAME/karaoqueue:$VERSION? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker push ghcr.io/$USERNAME/karaoqueue:$VERSION
fi

# Ask the user if they want to push the container as latest
read -p "Push container to ghcr.io/$USERNAME/karaoqueue:latest? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker tag ghcr.io/$USERNAME/karaoqueue:$VERSION ghcr.io/$USERNAME/karaoqueue:latest
    docker push ghcr.io/$USERNAME/karaoqueue:latest
fi
