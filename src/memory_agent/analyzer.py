

import logging
import traceback

# Standardní Python importy
from typing import Dict, List, Literal, Optional, Union, Any, Callable, TypedDict

# LangChain Core importy
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_core.runnables import RunnableConfig, chain
from langchain_core.tools import BaseTool, StructuredTool, tool
from langchain_core.runnables.utils import ConfigurableFieldSpec

# LangChain importy
from langchain.chat_models import init_chat_model

logger = logging.getLogger(__name__)

# Definition of analysis types
AnalysisType = Literal["risk_comparison", "common_suppliers", "general"]

class AnalysisResult(TypedDict):
    """Result of user input analysis."""
    companies: List[str]
    company: str  # Primary company (first in the list)
    analysis_type: AnalysisType
    query: str
    is_company_analysis: bool  # Indicates whether the query is about company analysis
    confidence: float  # Analysis confidence level (0.0 - 1.0)

class CompanyAnalysisRequest(BaseModel):
    """Schema for company analysis request when passing to LLM."""
    
    companies: List[str] = Field(
        description="List of identified companies in the user query",
        default_factory=list
    )
    
    analysis_type: AnalysisType = Field(
        description="Type of requested analysis (risk comparison, common suppliers, general analysis)",
        default="general"
    )
    
    is_company_analysis: bool = Field(
        description="Whether the query is about company analysis",
        default=False
    )
    
    confidence: float = Field(
        description="Analysis confidence level (0.0 - 1.0)",
        default=0.0
    )
    
    @validator("confidence")
    def validate_confidence(cls, value):
        """Verifies that the confidence value is between 0-1."""
        if not 0 <= value <= 1:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return value

# System prompt for the analyzer
# List of valid analysis types for validation
VALID_ANALYSIS_TYPES = ["risk_comparison", "common_suppliers", "general"]

# Enhanced prompt inspired by React approach - supports more structured reasoning
ANALYZER_PROMPT = """You are a specialized query analyzer that identifies companies and analysis types in user queries.

For each input, follow these steps:
1. REASONING: Identify whether the query relates to company analysis, and if so, which companies are mentioned.
2. ANALYSIS: Determine what type of analysis the user is requesting, based on keywords and context.
3. FORMATTING: Provide a response in the exact format "Company name; analysis_type"

The analysis type can be one of these:
- risk_comparison (for risk analysis and security factors)
- common_suppliers (for supplier-customer relationship analysis)
- general (for general information about the company or other queries)

Examples:
- Input: "Find risks for Fuyao Group"
  Reasoning: The query is about risk analysis for Fuyao Group.
  Output: "Fuyao Group; risk_comparison"
  
- Input: "Show me suppliers for Adis Tachov"
  Reasoning: The query is about suppliers for Adis Tachov.
  Output: "Adis Tachov; common_suppliers"
  
- Input: "I need information about tesa"
  Reasoning: The query asks for general information about tesa.
  Output: "tesa; general"
  
- Input: "What are the risks of Hauk compared to Fuyao Group?"
  Reasoning: The query requests a comparison of risks between two companies: Hauk and Fuyao Group.
  Output: "Hauk, Fuyao Group; risk_comparison"

- Input: "I want to check the weather in Prague"
  Reasoning: The query is not about any company, but about the weather in Prague.
  Output: "; general"

User input: {user_input}

First, perform reasoning and analysis (DO NOT PRINT THIS ANYWHERE), and then respond ONLY in the structured format:
"Company name; analysis_type"
"""

async def analyze_query(
    user_input: str, 
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = "claude-3-5-sonnet-20240620"
) -> AnalysisResult:
    """Analyzes user input and identifies companies and analysis types.
    
    Args:
        user_input: User query
        config: Runtime configuration (optional)
        model: Model to use for analysis
        
    Returns:
        AnalysisResult containing extracted information
    """
    logger.info(f"Analyzing query: {user_input}")
    
    # Initialize default result
    default_result: AnalysisResult = {
        "companies": [],
        "company": "",
        "analysis_type": "general",
        "query": user_input,
        "is_company_analysis": False,
        "confidence": 0.0
    }
    
    try:
        # Initialize chat model
        llm = init_chat_model(model=model)
        
        # Create analyzer tool (inspired by React agent)
        # According to requirements from query_analyzer.prompt.md we'll use LCEL chain
        
        # 1. ChatPromptTemplate for formatting the prompt
        prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
        
        # 2. Create LCEL chain: prompt | llm | StrOutputParser
        # This approach follows guidelines in query_analyzer.prompt.md
        chain = prompt | llm | StrOutputParser()
        
        # 3. Asynchronous chain invocation
        response_content = await chain.ainvoke(
            {"user_input": user_input},
            config
        )
        
        logger.info(f"Model response: {response_content}")
        
        # Parse response and return structured result
        result = parse_response(response_content, user_input)
        logger.info(f"Parsed result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during query analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return default_result

def parse_response(response: str, original_query: str) -> AnalysisResult:
    """Parses model response and creates structured result.
    
    Args:
        response: Response from LLM
        original_query: Original user query
        
    Returns:
        AnalysisResult containing extracted information
    """
    # Remove whitespace
    response = response.strip()
    
    # Parse the "Company name; analysis_type" format
    parts = response.split(";")
    
    companies = []
    analysis_type: AnalysisType = "general"
    is_company_analysis = False
    confidence = 0.0
    
    if len(parts) >= 1 and parts[0].strip():
        # Split first part into companies (if it contains commas)
        companies = [c.strip() for c in parts[0].split(",") if c.strip()]
        if companies:
            is_company_analysis = True
            confidence = 0.8  # Base confidence level when we have identified companies
    
    if len(parts) >= 2 and parts[1].strip():
        analysis_type_raw = parts[1].strip().lower()
        # Validate analysis type
        if analysis_type_raw in ["risk_comparison", "common_suppliers", "general"]:
            analysis_type = analysis_type_raw
            if analysis_type != "general" and companies:
                confidence = 0.9  # Higher confidence with specific analysis type
    
    # Create result
    return {
        "companies": companies,
        "company": companies[0] if companies else "",
        "analysis_type": analysis_type,
        "query": original_query,
        "is_company_analysis": is_company_analysis,
        "confidence": confidence
    }