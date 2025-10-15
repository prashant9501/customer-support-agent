"""
LangGraph workflow for customer support agent
Orchestrates the complete support workflow with conditional routing
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from app.models.schemas import CustomerSupportState
from app.agents.classifier import categorize_inquiry
from app.agents.sentiment import analyze_sentiment
from app.agents.escalation import escalate_to_human
from app.agents.handlers import (
    generate_technical_response,
    generate_billing_response,
    generate_general_response
)

logger = logging.getLogger(__name__)


def determine_route(state: CustomerSupportState) -> Literal[
    "escalate_to_human",
    "generate_technical_response",
    "generate_billing_response",
    "generate_general_response"
]:
    """
    Determine the routing path based on sentiment and category
    
    Priority:
    1. Negative sentiment → Escalate to human
    2. Technical category → Technical response
    3. Billing category → Billing response
    4. Default → General response
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name to execute
    """
    sentiment = state.get("query_sentiment", "Neutral")
    category = state.get("query_category", "General")
    
    logger.info(f"Routing decision: sentiment={sentiment}, category={category}")
    
    # Priority 1: Escalate negative sentiment
    if sentiment == "Negative":
        logger.info("Routing to human escalation (negative sentiment)")
        return "escalate_to_human"
    
    # Priority 2: Route by category
    if category == "Technical":
        logger.info("Routing to technical response handler")
        return "generate_technical_response"
    elif category == "Billing":
        logger.info("Routing to billing response handler")
        return "generate_billing_response"
    else:
        logger.info("Routing to general response handler")
        return "generate_general_response"


def create_support_graph() -> StateGraph:
    """
    Create the LangGraph workflow for customer support
    
    Workflow:
    1. Categorize query (Technical/Billing/General)
    2. Analyze sentiment (Positive/Neutral/Negative)
    3. Route based on sentiment and category
    4. Generate appropriate response or escalate
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Creating customer support workflow graph...")
    
    # Initialize the graph with state schema
    workflow = StateGraph(CustomerSupportState)
    
    # Add nodes for each step
    workflow.add_node("categorize_inquiry", categorize_inquiry)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("escalate_to_human", escalate_to_human)
    workflow.add_node("generate_technical_response", generate_technical_response)
    workflow.add_node("generate_billing_response", generate_billing_response)
    workflow.add_node("generate_general_response", generate_general_response)
    
    # Define the workflow edges
    # Start with categorization
    workflow.set_entry_point("categorize_inquiry")
    
    # After categorization, analyze sentiment
    workflow.add_edge("categorize_inquiry", "analyze_sentiment")
    
    # After sentiment analysis, route conditionally
    workflow.add_conditional_edges(
        "analyze_sentiment",
        determine_route,
        {
            "escalate_to_human": "escalate_to_human",
            "generate_technical_response": "generate_technical_response",
            "generate_billing_response": "generate_billing_response",
            "generate_general_response": "generate_general_response"
        }
    )
    
    # All response handlers end the workflow
    workflow.add_edge("escalate_to_human", END)
    workflow.add_edge("generate_technical_response", END)
    workflow.add_edge("generate_billing_response", END)
    workflow.add_edge("generate_general_response", END)
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    logger.info("Customer support workflow graph created successfully")
    return compiled_graph


# Create a global compiled graph instance
compiled_support_agent = create_support_graph()


def run_support_agent(customer_query: str, thread_id: str = "default") -> dict:
    """
    Run the customer support agent workflow
    
    Args:
        customer_query: The customer's question or issue
        thread_id: Thread identifier for conversation context
        
    Returns:
        Final state containing response and metadata
    """
    logger.info(f"Running support agent for query: {customer_query[:100]}...")
    
    try:
        # Invoke the workflow
        result = compiled_support_agent.invoke(
            {"customer_query": customer_query},
            {"configurable": {"thread_id": thread_id}}
        )
        
        logger.info("Support agent completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error running support agent: {e}")
        raise
