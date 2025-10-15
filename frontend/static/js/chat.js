/**
 * Customer Support Chat Client
 * Handles chat interactions with the AI support agent
 */

// Configuration
const API_BASE = window.location.origin;
const API_ENDPOINT = `${API_BASE}/api/chat`;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// DOM Elements
const messagesContainer = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const metadataDisplay = document.getElementById('metadata');
const categoryDisplay = document.getElementById('category-display');
const sentimentDisplay = document.getElementById('sentiment-display');
const statusIndicator = document.getElementById('status');
const charCount = document.getElementById('char-count');
const sampleQuestions = document.getElementById('sample-questions');

// State
let sessionId = null;
let isProcessing = false;

/**
 * Initialize the chat application
 */
function init() {
    console.log('Initializing Customer Support Chat...');
    
    // Event Listeners
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', handleKeyPress);
    userInput.addEventListener('input', updateCharacterCount);
    
    // Sample question buttons
    const sampleBtns = document.querySelectorAll('.sample-btn');
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            userInput.value = question;
            handleSend();
            // Hide sample questions after first use
            if (sampleQuestions) {
                sampleQuestions.style.display = 'none';
            }
        });
    });
    
    // Focus input on load
    userInput.focus();
    
    // Check API health
    checkHealth();
}

/**
 * Check API health status
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('online', 'Online');
            console.log('API health check: OK');
        } else {
            updateStatus('warning', 'Limited');
            console.warn('API health check: Limited functionality');
        }
    } catch (error) {
        updateStatus('offline', 'Offline');
        console.error('API health check failed:', error);
    }
}

/**
 * Update status indicator
 */
function updateStatus(status, text) {
    statusIndicator.className = `status-indicator status-${status}`;
    statusIndicator.innerHTML = `<span class="status-dot"></span>${text}`;
}

/**
 * Update character counter
 */
function updateCharacterCount() {
    const count = userInput.value.length;
    charCount.textContent = count;
    
    if (count > 450) {
        charCount.style.color = 'var(--danger-color)';
    } else if (count > 400) {
        charCount.style.color = 'var(--warning-color)';
    } else {
        charCount.style.color = 'var(--text-light)';
    }
}

/**
 * Handle Enter key press
 */
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
}

/**
 * Handle send button click
 */
async function handleSend() {
    const query = userInput.value.trim();
    
    // Validation
    if (!query) {
        shakeInput();
        return;
    }
    
    if (query.length > 500) {
        addErrorMessage('Message is too long. Please keep it under 500 characters.');
        return;
    }
    
    if (isProcessing) {
        console.log('Already processing a message...');
        return;
    }
    
    // Hide sample questions after first message
    if (sampleQuestions) {
        sampleQuestions.style.display = 'none';
    }
    
    // Add user message to UI
    addMessage(query, 'user');
    
    // Clear input
    userInput.value = '';
    updateCharacterCount();
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to API
    await sendMessage(query);
}

/**
 * Send message to API
 */
async function sendMessage(query, retryCount = 0) {
    isProcessing = true;
    
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: sessionId
            })
        });
        
        hideTypingIndicator();
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
        // Add agent response
        addMessage(data.response, 'agent');
        
        // Update metadata
        updateMetadata(data.category, data.sentiment);
        
        console.log('Response received:', {
            category: data.category,
            sentiment: data.sentiment,
            session_id: data.session_id
        });
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error sending message:', error);
        
        // Retry logic
        if (retryCount < MAX_RETRIES) {
            console.log(`Retrying... (${retryCount + 1}/${MAX_RETRIES})`);
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
            return sendMessage(query, retryCount + 1);
        }
        
        // Show error message
        addErrorMessage(
            'Sorry, I encountered an error while processing your request. ' +
            'Please try again or contact support@company.com for assistance.'
        );
        
    } finally {
        isProcessing = false;
        userInput.focus();
    }
}

/**
 * Add message to chat
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}-avatar`;
    avatar.textContent = sender === 'user' ? 'You' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Convert line breaks to <br> and handle basic formatting
    const formattedText = formatMessage(text);
    content.innerHTML = formattedText;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Format message text (basic markdown-like formatting)
 */
function formatMessage(text) {
    // Escape HTML
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Bold text (**text**)
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text (*text*)
    formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Inline code (`code`)
    formatted = formatted.replace(/`(.+?)`/g, '<code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>');
    
    return formatted;
}

/**
 * Add error message
 */
function addErrorMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent error';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar agent-avatar';
    avatar.textContent = '⚠️';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

/**
 * Update metadata display
 */
function updateMetadata(category, sentiment) {
    // Show metadata container
    metadataDisplay.style.display = 'flex';
    
    // Update category
    const categoryClass = `category-${category.toLowerCase()}`;
    categoryDisplay.textContent = `Category: ${category}`;
    categoryDisplay.className = categoryClass;
    
    // Update sentiment
    const sentimentClass = `sentiment-${sentiment.toLowerCase()}`;
    sentimentDisplay.textContent = `Sentiment: ${sentiment}`;
    sentimentDisplay.className = sentimentClass;
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Shake input on error
 */
function shakeInput() {
    userInput.style.animation = 'shake 0.5s';
    setTimeout(() => {
        userInput.style.animation = '';
    }, 500);
}

// Add shake animation to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

/**
 * Handle visibility change (tab focus)
 */
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && !isProcessing) {
        userInput.focus();
    }
});

/**
 * Handle window focus
 */
window.addEventListener('focus', () => {
    if (!isProcessing) {
        userInput.focus();
    }
});

/**
 * Service Worker Registration (for PWA - optional)
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('Service Worker registered:', reg))
        //     .catch(err => console.log('Service Worker registration failed:', err));
    });
}

/**
 * Error Handling
 */
window.addEventListener('error', (e) => {
    console.error('Global error:', e);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e);
});

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendMessage,
        addMessage,
        formatMessage,
        updateMetadata
    };
}
