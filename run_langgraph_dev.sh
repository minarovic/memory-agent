#!/bin/bash

# Nastavení pro spuštění LangGraph vývojového serveru
cd /Users/marekminarovic/claude-code/memory-agent

# Nastav PYTHONPATH pro nalezení modulů
export PYTHONPATH=/Users/marekminarovic/claude-code/memory-agent/src

# Spusť LangGraph vývojový server
echo "Spouštím LangGraph vývojový server na http://127.0.0.1:2024..."
echo "Pro přístup k LangGraph Studio UI otevřete v prohlížeči:"
echo -e "\033[1;36mhttps://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024\033[0m"
echo ""

/opt/homebrew/bin/langgraph dev --host 127.0.0.1 --config langgraph.json