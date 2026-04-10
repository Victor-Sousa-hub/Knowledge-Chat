#!/bin/bash
set -e

echo "[up] Verificando credenciais AWS..."

if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "[up] Credenciais expiradas. Iniciando login..."
    aws login
fi

echo "[up] Exportando credenciais temporárias para o container..."
eval "$(aws configure export-credentials --format env)"

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN

echo "[up] Credenciais OK. Subindo containers..."
docker compose up "$@"
