#!/bin/bash

# Garante que o script rode na raiz do projeto (mesmo se for chamado de dentro da pasta scripts)
cd "$(dirname "$0")/.." || exit 1

# Este script carrega as variáveis do arquivo .env para o ambiente do shell
# e então executa o docker stack deploy.
# Isso garante que as variáveis como ${API_DOMAIN} no docker-stack.yml
# sejam substituídas corretamente pelas configurações do seu .env.

if [ ! -f .env ]; then
  echo "Erro: Arquivo .env não encontrado na raiz do projeto!"
  echo "Copie o .env.example para .env e configure-o primeiro."
  exit 1
fi

# Exporta as variáveis do .env ignorando comentários
export $(grep -v '^#' .env | xargs)

# Nome da stack
STACK_NAME=${STACK_NAME:-whagent}

echo "Iniciando deploy da stack: $STACK_NAME ..."
docker stack deploy -c docker-stack.yml $STACK_NAME

echo "Deploy enviado! Para acompanhar os logs do backend, use:"
echo "docker service logs -f ${STACK_NAME}_backend"
