#!/bin/bash

docker compose -f docker-compose.test.yml run --rm onboarding-app /bin/bash -c "poetry install --sync && pytest" 
docker compose -f docker-compose.test.yml down