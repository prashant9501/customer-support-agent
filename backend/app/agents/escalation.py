"""
Human escalation handler
Escalates negative sentiment queries to human agents
"""
import logging
from typing import Dict

from app.models.schemas import CustomerSupportState

logger = logging.getLogger(__name__)


def escalate_to_human(state: CustomerSupportState) -> Dict[str, str]:
    """
    Escalate query to human agent (for negative sentiment)
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary with final_response indicating escalation
    """
    query = state["customer_query"]
    logger.warning(f"Escalating negative sentiment query to human agent: {query[:100]}...")
    
    escalation_message = (
        "We sincerely apologize for any frustration or inconvenience you've experienced. "
        "Your concern is very important to us, and we want to ensure you receive the best possible support. "
        "\n\n"
        "A member of our customer success team will reach out to you within the next 2 hours to address "
        "your issue personally. In the meantime, if you need immediate assistance, please contact us at "
        "support@company.com or call our priority support line at 1-800-SUPPORT."
        "\n\n"
        "Thank you for your patience and for bringing this to our attention."
    )
    
    logger.info("Human escalation message generated")
    
    return {"final_response": escalation_message}
