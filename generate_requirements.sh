#!/bin/bash

echo "📦️ generating common.txt"
poetry export -o requirements/common.txt --without-hashes

for env in dev test preprod prod;
do
echo "📦️ generating $env.txt"
poetry export -o requirements/$env.txt --with $env --without-hashes
done
