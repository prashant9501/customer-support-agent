"""
Response generation handlers using RAG
Generates contextual responses based on knowledge base retrieval
"""
import logging
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.schemas import CustomerSupportState
from app.config.settings import get_settings
from app.database.vectordb import search_knowledge_base

logger = logging.getLogger(__name__)
settings = get_settings()


def generate_technical_response(state: CustomerSupportState) -> Dict[str, str]:
    """
    Generate technical support response using RAG
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary with final_response
    """
    query = state["customer_query"]
    category = state["query_category"]
    
    logger.info(f"Generating technical response for: {query[:100]}...")
    
    try:
        # Retrieve relevant documents with technical filter
        relevant_docs = search_knowledge_base(
            query=query,
            category_filter="technical" if category.lower() == "technical" else None
        )
        
        # Extract content from retrieved documents
        retrieved_content = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in relevant_docs
        ])
        
        if not retrieved_content:
            retrieved_content = "No specific documentation found for this query."
        
        # Technical response prompt
        TECHNICAL_PROMPT = """
        You are a technical support specialist with deep expertise in our platform.
        
        Craft a clear and detailed technical support response for the following customer query.
        Use the retrieved knowledge base information below to provide accurate, specific guidance.
        
        Guidelines:
        - Be precise and technical but also clear and understandable
        - Include specific examples, code snippets, or configuration details when relevant
        - Reference documentation sources when applicable
        - If the retrieved information doesn't fully answer the question, acknowledge what you know
          and suggest additional resources or next steps
        - Keep the response professional and helpful
        
        Retrieved Knowledge Base Information:
        {retrieved_content}
        
        Customer Query:
        {customer_query}
        
        Technical Support Response:
        """
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Generate response
        prompt = ChatPromptTemplate.from_template(TECHNICAL_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        })
        
        final_response = response.content.strip()
        logger.info("Technical response generated successfully")
        
        return {"final_response": final_response}
        
    except Exception as e:
        logger.error(f"Error generating technical response: {e}")
        return {
            "final_response": "I apologize, but I encountered an error while processing your technical question. "
                             "Please contact our technical support team at support@company.com for immediate assistance."
        }


def generate_billing_response(state: CustomerSupportState) -> Dict[str, str]:
    """
    Generate billing support response using RAG
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary with final_response
    """
    query = state["customer_query"]
    category = state["query_category"]
    
    logger.info(f"Generating billing response for: {query[:100]}...")
    
    try:
        # Retrieve relevant documents with billing filter
        relevant_docs = search_knowledge_base(
            query=query,
            category_filter="billing" if category.lower() == "billing" else None
        )
        
        # Extract content from retrieved documents
        retrieved_content = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in relevant_docs
        ])
        
        if not retrieved_content:
            retrieved_content = "No specific billing information found for this query."
        
        # Billing response prompt
        BILLING_PROMPT = """
        You are a billing support specialist focused on helping customers with financial matters.
        
        Craft a clear and detailed billing support response for the following customer query.
        Use the retrieved knowledge base information below to provide accurate answers about pricing,
        payments, invoices, refunds, or subscription matters.
        
        Guidelines:
        - Be clear about pricing, payment terms, and policies
        - Include specific details like pricing tiers, payment methods, and timeframes
        - If discussing refunds or disputes, be empathetic and helpful
        - Reference official policies when applicable
        - For account-specific issues, direct the customer to the appropriate channel
        - Keep the response professional and reassuring
        
        Retrieved Knowledge Base Information:
        {retrieved_content}
        
        Customer Query:
        {customer_query}
        
        Billing Support Response:
        """
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Generate response
        prompt = ChatPromptTemplate.from_template(BILLING_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        })
        
        final_response = response.content.strip()
        logger.info("Billing response generated successfully")
        
        return {"final_response": final_response}
        
    except Exception as e:
        logger.error(f"Error generating billing response: {e}")
        return {
            "final_response": "I apologize, but I encountered an error while processing your billing question. "
                             "Please contact our billing team at billing@company.com for immediate assistance."
        }


def generate_general_response(state: CustomerSupportState) -> Dict[str, str]:
    """
    Generate general support response using RAG
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary with final_response
    """
    query = state["customer_query"]
    category = state["query_category"]
    
    logger.info(f"Generating general response for: {query[:100]}...")
    
    try:
        # Retrieve relevant documents with general filter
        relevant_docs = search_knowledge_base(
            query=query,
            category_filter="general" if category.lower() == "general" else None
        )
        
        # Extract content from retrieved documents
        retrieved_content = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in relevant_docs
        ])
        
        if not retrieved_content:
            retrieved_content = "No specific information found for this query."
        
        # General response prompt
        GENERAL_PROMPT = """
        You are a customer support representative helping customers with general inquiries.
        
        Craft a clear and helpful response for the following customer query.
        Use the retrieved knowledge base information below to provide accurate information about
        our company, policies, support channels, or general questions.
        
        Guidelines:
        - Be friendly, professional, and helpful
        - Provide complete and accurate information
        - Include relevant links or contact information when appropriate
        - If the question is outside your knowledge, direct them to the right resource
        - Keep the response concise but thorough
        
        Retrieved Knowledge Base Information:
        {retrieved_content}
        
        Customer Query:
        {customer_query}
        
        Support Response:
        """
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Generate response
        prompt = ChatPromptTemplate.from_template(GENERAL_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        })
        
        final_response = response.content.strip()
        logger.info("General response generated successfully")
        
        return {"final_response": final_response}
        
    except Exception as e:
        logger.error(f"Error generating general response: {e}")
        return {
            "final_response": "I apologize, but I encountered an error while processing your question. "
                             "Please contact our support team at support@company.com for assistance."
        }
