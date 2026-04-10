#!/bin/sh

echo "[entrypoint] Validando credenciais AWS..."

if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "[entrypoint] Credenciais AWS válidas. Iniciando servidor..."
    exec "$@"
fi

OUTPUT=$(aws sts get-caller-identity 2>&1 || true)

echo ""
echo "================================================================"

case "$OUTPUT" in
    *SSL*|*certificate*|*CERTIFICATE*)
        echo "  ERRO: Falha de SSL ao conectar à AWS."
        echo ""
        echo "  Certificado CA não reconhecido (proxy corporativo?)."
        echo "  Verifique /etc/ssl/certs/ca-certificates.crt no container."
        echo ""
        echo "  Detalhe: $OUTPUT"
        ;;
    *ExpiredToken*|*InvalidClientTokenId*|*AuthFailure*|*NoCredentialProviders*)
        echo "  ERRO: Credenciais AWS expiradas ou inválidas."
        echo ""
        echo "  Execute no host antes de reiniciar o container:"
        echo "    aws login"
        echo ""
        echo "  Depois reinicie:"
        echo "    docker compose restart backend"
        ;;
    *)
        echo "  ERRO: Não foi possível validar as credenciais AWS."
        echo ""
        echo "  Detalhe: $OUTPUT"
        ;;
esac

echo "================================================================"
echo ""
exit 1
