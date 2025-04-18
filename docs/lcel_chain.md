# LCEL Chains v Memory Agent projektu

Tento dokument popisuje použití LangChain Expression Language (LCEL) v rámci Memory Agent projektu. Obsahuje kompletní přehled principů, vzorů a praktik pro efektivní implementaci LCEL řetězců.

## Verze balíčků

Tato dokumentace je aktuální pro následující verze:
* langchain: 0.3.20
* langchain-core: 0.3.x
* langchain-anthropic: 0.2.x
* langchain-openai: 0.3.4

## Základní principy LCEL

### Operátor `|` (Pipe)
* **Vždy** používejte operátor `|` pro sekvenční kompozici komponent LangChain (`Runnable`).
* Cílem je vytvořit deklarativní, čitelné a udržitelné definice toků zpracování dat.
* Příklad: `chain = prompt | llm | StrOutputParser()`

### Asynchronní operace
* Pro operace, které interagují s externími systémy (LLMs, APIs, databáze), **používejte asynchronní LCEL metody** (`ainvoke`, `abatch`, `astream`).
* Příklad z `analyzer.py`:
  ```python
  response_content = await chain.ainvoke(
      {"user_input": user_input},
      config
  )
  ```

## Klíčové komponenty a vzory

### Šablony promptů
* Používejte `ChatPromptTemplate` pro většinu případů, protože je flexibilnější než `PromptTemplate`.
* Pro víceturnové konverzace používejte `MessagesPlaceholder` pro zahrnutí historie zpráv.
  ```python
  prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
  # Nebo pro konverzaci:
  prompt = ChatPromptTemplate.from_messages([
      ("system", system_message),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{input}")
  ])
  ```

### Modely
* Inicializujte Claude modely pomocí funkce `init_chat_model` z vašeho konfiguračního modulu.
* Pro standardní operace: `model="claude-3-5-sonnet-20240620"`
* Pro složitější operace: `model="claude-3-7-sonnet-20250219"`
  ```python
  from langchain.chat_models import init_chat_model
  
  llm = init_chat_model(model="claude-3-5-sonnet-20240620")
  ```

### Konstrukce základního řetězce
* Nejjednodušší vzor je třísložkový řetězec:
  ```python
  # Příklad z analyzer.py
  chain = prompt | llm | StrOutputParser()
  ```

### Pokročilé komponenty řetězců

* **`RunnablePassthrough`:** Předává původní vstup (nebo jeho části) dál v řetězci.
  ```python
  from langchain_core.runnables import RunnablePassthrough
  
  chain = RunnablePassthrough.assign(
      llm_response=prompt | llm | StrOutputParser()
  )
  ```

* **`itemgetter`:** Extrahuje konkrétní klíče ze slovníkového vstupu.
  ```python
  from operator import itemgetter
  
  chain = {
      "query": itemgetter("user_query"),
      "context": itemgetter("retrieved_docs")
  } | prompt | llm | StrOutputParser()
  ```

* **`RunnableParallel`:** Spouští více komponent `Runnable` paralelně a slučuje výsledky.
  ```python
  from langchain_core.runnables import RunnableParallel
  
  chain = RunnableParallel(
      analysis=analyzer_chain,
      original_input=RunnablePassthrough()
  )
  ```

* **`RunnableLambda`:** Obaluje Python funkce jako kroky v řetězci.
  ```python
  from langchain_core.runnables import RunnableLambda
  
  def post_process(result: dict) -> dict:
      # Transformujeme nebo vylepšujeme výsledek
      return enhanced_result
  
  chain = base_chain | RunnableLambda(post_process)
  ```

## Integrace s LangGraph

Při použití LCEL řetězců v rámci LangGraph workflow se řiďte těmito vzory:

### V uzlech grafu
* Uzly grafu by měly přijímat parametr `state` a vracet slovník aktualizací stavu.
* Používejte LCEL řetězce pro zpracování dat v rámci uzlů:
  ```python
  async def analyze_company_input(state: State, config: Optional[RunnableConfig] = None) -> Dict:
      """Uzel pro analýzu vstupu uživatele k identifikaci společností a typů analýzy."""
      messages = state.get("messages", [])
      if not messages:
          return {"errors": ["No messages in state"]}
      
      try:
          user_message = messages[-1].content
          
          # Použití LCEL řetězce pro analýzu
          prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
          llm = init_chat_model()
          chain = prompt | llm | StrOutputParser()
          
          response = await chain.ainvoke({"user_input": user_message}, config)
          
          # Zpracování výsledku a aktualizace stavu
          analysis_result = parse_response(response, user_message)
          
          return {"company_analysis": analysis_result}
      except Exception as e:
          return {"errors": [f"Error analyzing input: {str(e)}"]}
  ```

### Post-processing LCEL výsledků
* Vždy analyzujte a validujte výsledky LCEL řetězců před aktualizací stavu grafu:
  ```python
  # Příklad funkce pro parsování použité v analyzer.py
  def parse_response(response: str, original_query: str) -> AnalysisResult:
      """Parsuje odpověď modelu a vytváří strukturovaný výsledek."""
      # Odstranění whitespace
      response = response.strip()
      
      # Parsování formátu "Company name; analysis_type"
      parts = response.split(";")
      
      # ... logika zpracování ...
      
      return {
          "companies": companies,
          "company": companies[0] if companies else "",
          "analysis_type": analysis_type,
          "query": original_query,
          "is_company_analysis": is_company_analysis,
          "confidence": confidence
      }
  ```

## Ošetřování chyb
* Vždy používejte bloky try-except kolem volání řetězců, zvláště v uzlech grafu.
* Logujte jak chybovou zprávu, tak úplný traceback pro účely debugování.
* Vracejte výchozí nebo chybový výsledek namísto toho, aby se výjimky šířily dále.
  ```python
  try:
      result = await chain.ainvoke(inputs, config)
      return process_result(result)
  except Exception as e:
      logger.error(f"Chain execution failed: {str(e)}")
      logger.error(traceback.format_exc())
      return default_result  # Nebo chybový výsledek
  ```

## Testování LCEL řetězců
* Mockujte odpověď modelu pro deterministické testování.
* Testujte celý řetězec i jednotlivé komponenty.
* Ověřujte parserovací logiku s různými formáty vstupů (včetně hraničních případů).
* Pro příklady testování LCEL řetězců nahlédněte do `tests/unit_tests/test_analyzer.py`.

## Vzorové příklady z Memory Agent

### Jednoduchý analyzační řetězec (z `analyzer.py`)
```python
async def analyze_query(user_input: str, config: Optional[RunnableConfig] = None):
    # Inicializace chat modelu
    llm = init_chat_model(model="claude-3-5-sonnet-20240620")
    
    # Vytvoření šablony promptu
    prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
    
    # Vytvoření LCEL řetězce: prompt | llm | StrOutputParser
    chain = prompt | llm | StrOutputParser()
    
    # Asynchronní volání řetězce
    response_content = await chain.ainvoke(
        {"user_input": user_input},
        config
    )
    
    # Parsování a zpracování výsledku
    result = parse_response(response_content, user_input)
    return result
```

### Komplexní řetězce s více komponentami
Pro složitější operace, zvláště ty zahrnující více datových zdrojů nebo komplexní uvažování:

```python
# Získávání dat z více zdrojů paralelně
data_chain = RunnableParallel(
    company_data=fetch_company_data_chain,
    internal_data=fetch_internal_data_chain,
    relationships=fetch_relationships_chain
)

# Kombinace s analyzačním řetězcem
full_chain = RunnableParallel(
    analysis_data=data_chain,
    original_query=RunnablePassthrough()
) | format_prompt | llm | StrOutputParser() | RunnableLambda(parse_final_output)
```

## Cíl

Vytvářet efektivní, čitelné a flexibilní řetězce pro zpracování dat a interakci s LLM pomocí standardních LCEL konstruktů.
