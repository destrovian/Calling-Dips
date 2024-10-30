#!/bin/bash
# Load .env file into the environment
export $(grep -v '^#' .env | xargs)

# Then you can run your commands here, e.g., docker build
docker-compose build
docker-compose up -d
