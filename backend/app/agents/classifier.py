"""
Query classification agent
Categorizes customer queries into Technical, Billing, or General
"""
import logging
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.schemas import CustomerSupportState
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def categorize_inquiry(state: CustomerSupportState) -> Dict[str, str]:
    """
    Categorize customer query into: Technical, Billing, or General
    
    Args:
        state: Current workflow state containing customer_query
        
    Returns:
        Dictionary with query_category field
    """
    query = state["customer_query"]
    logger.info(f"Categorizing query: {query[:100]}...")
    
    # Category classification prompt
    CATEGORY_PROMPT = """
    You are a customer support query classifier. Your job is to categorize the incoming customer query
    into one of the following categories:

    1. **Technical**: Queries related to technical issues, integrations, APIs, SDKs, deployment, 
       infrastructure, performance, security, or any technology-related topics.

    2. **Billing**: Queries related to pricing, payments, invoices, subscriptions, refunds, 
       upgrades, downgrades, or any financial matters.

    3. **General**: Queries about company information, support channels, policies, general questions,
       or anything that doesn't fit Technical or Billing categories.

    Analyze the customer query and return ONLY the category name (Technical, Billing, or General).
    Do not include any explanation, just the category name.

    Customer Query:
    {customer_query}

    Category:
    """
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Create prompt and invoke
        prompt = ChatPromptTemplate.from_template(CATEGORY_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({"customer_query": query})
        category = response.content.strip()
        
        # Validate category
        valid_categories = ["Technical", "Billing", "General"]
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}', defaulting to 'General'")
            category = "General"
        
        logger.info(f"Query categorized as: {category}")
        
        return {"query_category": category}
        
    except Exception as e:
        logger.error(f"Error categorizing query: {e}")
        # Default to General on error
        return {"query_category": "General"}
