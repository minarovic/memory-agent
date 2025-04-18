# LCEL Guidelines

Tyto guidelines jsou určeny k začlenění do hlavních Copilot instrukcí.

## LCEL Guidelines

### Basic Principles
* **Vždy používej pipe operátor (`|`)** pro skládání komponent LangChain.
* **Používej asynchronní metody** (`ainvoke`, `abatch`, `astream`) pro operace s externími systémy.
* **Preferuj `ChatPromptTemplate`** nad `PromptTemplate` pro větší flexibilitu.
* **Používej `MessagesPlaceholder`** pro víceturnové konverzace.

### Základní komponenty
* **Prompt Templates**: `ChatPromptTemplate.from_template()` nebo `ChatPromptTemplate.from_messages()`
* **Model inicializace**: `llm = init_chat_model(model="claude-3-7-sonnet-20250219")`
* **Output Parsery**: Pro většinu případů `StrOutputParser()`
* **Standardní volání**: `await chain.ainvoke(inputs, config)`

### Pokročilé komponenty
* **`RunnablePassthrough`**: Pro předání původních vstupů
* **`RunnableLambda`**: Pro zapouzdření Python funkcí
* **`RunnableParallel`**: Pro paralelní zpracování
* **`itemgetter`**: Pro extrakci klíčů ze slovníku

### Error Handling
* **Vždy používej try-except** bloky kolem volání řetězců
* **Loguj jak chybovou zprávu, tak full traceback**
* **Vrať výchozí nebo chybový výsledek** místo propagace výjimek

### Integrace s LangGraph
* **Uzly grafu** by měly přijímat `state` parametr a vracet slovník s aktualizacemi stavu
* **Vždy zpracuj a validuj** výsledky LCEL řetězců před aktualizací stavu grafu
