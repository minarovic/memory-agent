#!/bin/bash

# Nastavení pro spuštění LangGraph s Dockerem pro lokální vývoj
cd /Users/marekminarovic/claude-code/memory-agent

# Nastav PYTHONPATH pro nalezení modulů
export PYTHONPATH=/Users/marekminarovic/claude-code/memory-agent/src

# Spusť LangGraph s Dockerem na jiném portu (8124)
echo "Spouštím LangGraph s Dockerem pro lokální vývoj na portu 8124..."
echo "Pro přístup k LangGraph Studio UI otevřete v prohlížeči:"
echo -e "\033[1;36mhttps://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8124\033[0m"
echo ""

# Spuštění s odlišným prefixem pro kontejnery
/opt/homebrew/bin/langgraph up -c langgraph.json --port 8124 -d docker-compose-dev.yml