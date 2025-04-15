# Specific Instructions for Copilot: Query Analyzer (`analyzer.py`)

When working with the `analyzer.py` file and its components, follow these guidelines:

## Main Purpose
* Components in `analyzer.py` are responsible for **processing the initial user query**.
* The main goal is to **identify** whether the query relates to company analysis, and if so, **extract the company name (or multiple names) and the requested analysis type**.

## Key Function: `analyze_query`
* **Input:** Accepts the user query (`query: str`), configuration (`config: RunnableConfig`), and model name (`model: str`).
* **Logic:**
    1.  **Quick Keyword Check:** May include an optimization to quickly reject queries clearly unrelated to company analysis (function `_contains_company_analysis_keywords`).
    2.  **LLM Call:**
        * Use a **specific prompt** designed for extracting the company and analysis type. The prompt must instruct the LLM to respond in the **strict format "Company Name; analysis_type"** (or "Company1, Company2; analysis_type").
        * Create an LCEL chain: `ChatPromptTemplate | ChatModel | StrOutputParser`.
        * Invoke the chain asynchronously (`chain.ainvoke`).
    3.  **Response Parsing (function `parse_response`):**
        * Process the string response from the LLM.
        * Split the string by the `;` delimiter.
        * Extract company names (handle the case of multiple comma-separated companies).
        * Extract and validate the analysis type (use a predefined list of valid types, e.g., `VALID_ANALYSIS_TYPES = ["risk_comparison", "supplier_analysis", "general", ...]`, return "general" for invalid types).
        * Calculate a confidence score (`confidence`) - can be based on keyword presence or set fixed if the LLM identifies a company.
* **Return Value:** The function **must** return an `AnalysisResult` (`TypedDict`) with clearly defined fields: `company: Optional[str]`, `companies: List[str]`, `analysis_type: str`, `query: str`, `is_company_analysis: bool`, `confidence: float`.

## Function `parse_response`
* **Purpose:** Process the raw LLM response (string) and convert it into a structured `AnalysisResult`.
* **Robustness:** Must be able to handle various response formats (missing company, missing type, multiple companies).

## Testing (`tests/unit_tests/test_analyzer.py`)
* **LLM Mocking:** Tests must mock the `chain.ainvoke` call and simulate various LLM responses (valid, invalid, no company, multiple companies).
* **Verification:** Tests must verify that `analyze_query` and `parse_response` correctly parse the responses and return the expected `AnalysisResult` dictionary.

**Goal:** Ensure reliable and accurate extraction of information about the requested company analysis from user input, serving as the foundation for subsequent steps in the workflow.
