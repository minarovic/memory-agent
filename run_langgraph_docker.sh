#!/bin/bash

# Nastavení pro spuštění LangGraph s Dockerem
cd /Users/marekminarovic/claude-code/memory-agent

# Nastav PYTHONPATH pro nalezení modulů
export PYTHONPATH=/Users/marekminarovic/claude-code/memory-agent/src

# Zastav existující kontejnery, pokud běží
echo "Zastavuji případné běžící kontejnery..."
docker-compose down 2>/dev/null || true

# Spusť LangGraph s Dockerem
echo "Spouštím LangGraph s Dockerem na http://127.0.0.1:8123..."
echo "Pro přístup k LangGraph Studio UI otevřete v prohlížeči:"
echo -e "\033[1;36mhttps://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123\033[0m"
echo ""

/opt/homebrew/bin/langgraph up -c langgraph.json