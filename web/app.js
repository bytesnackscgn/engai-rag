// ===== DOM Elements =====
const apiKeyInput = document.getElementById('api-key');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');

// ===== Constants =====
const API_ENDPOINT = '/api/chat';
const STORAGE_KEYS = {
    API_KEY: 'engai-rag-api-key',
    CHAT_HISTORY: 'engai-rag-chat-history'
};

// ===== State =====
let chatHistory = [];

// ===== Initialization =====
function init() {
    // Load API key from localStorage
    const savedApiKey = localStorage.getItem(STORAGE_KEYS.API_KEY);
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // Load chat history from sessionStorage
    const savedHistory = sessionStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    if (savedHistory) {
        try {
            chatHistory = JSON.parse(savedHistory);
            renderChatHistory();
        } catch (e) {
            console.error('Failed to parse chat history:', e);
            chatHistory = [];
        }
    }

    // Update send button state
    updateSendButton();

    // Event listeners
    apiKeyInput.addEventListener('input', handleApiKeyChange);
    chatForm.addEventListener('submit', handleSubmit);
    messageInput.addEventListener('input', handleMessageInput);
    messageInput.addEventListener('keydown', handleTextareaKeydown);

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
}

// ===== Event Handlers =====
function handleApiKeyChange() {
    const apiKey = apiKeyInput.value.trim();
    localStorage.setItem(STORAGE_KEYS.API_KEY, apiKey);
    updateSendButton();
}

function handleMessageInput() {
    updateSendButton();
}

function handleTextareaKeydown(e) {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (sendButton.disabled === false) {
            chatForm.dispatchEvent(new Event('submit'));
        }
    }
}

function handleSubmit(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    const apiKey = apiKeyInput.value.trim();

    if (!message || !apiKey) {
        return;
    }

    // Add user message to history
    const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    };
    chatHistory.push(userMessage);

    // Clear input and reset height
    messageInput.value = '';
    messageInput.style.height = 'auto';
    updateSendButton();

    // Save history
    saveChatHistory();

    // Render user message
    renderMessage(userMessage);

    // Scroll to bottom
    scrollToBottom();

    // Send to API
    sendMessage(message, apiKey);
}

// ===== API Communication =====
async function sendMessage(message, apiKey) {
    // Create loading message
    const loadingMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        loading: true
    };
    chatHistory.push(loadingMessage);
    renderMessage(loadingMessage);
    scrollToBottom();

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({ query: message })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Remove loading message
        chatHistory.pop();
        chatHistory.push(loadingMessage, {
            role: 'assistant',
            content: data.answer || '',
            sources: data.sources || [],
            timestamp: new Date().toISOString()
        });

        // Re-render the last messages
        renderChatHistory();
        scrollToBottom();
        saveChatHistory();

    } catch (error) {
        // Remove loading message
        chatHistory.pop();

        const errorMessage = {
            role: 'assistant',
            content: `Error: ${error.message}`,
            error: true,
            timestamp: new Date().toISOString()
        };
        chatHistory.push(errorMessage);
        renderMessage(errorMessage);
        scrollToBottom();
        saveChatHistory();
    }
}

// ===== Rendering =====
function renderChatHistory() {
    // Clear all messages except welcome
    const welcome = chatMessages.querySelector('.welcome-message');
    chatMessages.innerHTML = '';
    if (welcome) {
        chatMessages.appendChild(welcome);
    }

    // Render all messages
    chatHistory.forEach(message => {
        renderMessage(message);
    });
}

function renderMessage(message) {
    // Remove existing message with same timestamp if updating
    const existing = document.querySelector(`[data-timestamp="${message.timestamp}"]`);
    if (existing) {
        existing.remove();
    }

    const messageEl = document.createElement('div');
    messageEl.className = `message ${message.role}`;
    messageEl.setAttribute('data-timestamp', message.timestamp);

    if (message.loading) {
        messageEl.classList.add('loading');
    }

    if (message.error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message.content;
        chatMessages.appendChild(errorDiv);
        return;
    }

    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';

    // Header
    const header = document.createElement('div');
    header.className = 'message-header';
    header.innerHTML = `
        <span>${message.role === 'user' ? 'You' : 'Assistant'}</span>
        <span class="message-time">${formatTime(message.timestamp)}</span>
    `;
    contentEl.appendChild(header);

    // Text content
    const textEl = document.createElement('div');
    textEl.className = 'message-text';
    textEl.textContent = message.content;
    contentEl.appendChild(textEl);

    // Sources
    if (message.sources && message.sources.length > 0) {
        const sourcesSection = createSourcesSection(message.sources);
        contentEl.appendChild(sourcesSection);
    }

    messageEl.appendChild(contentEl);
    chatMessages.appendChild(messageEl);
}

function createSourcesSection(sources) {
    const section = document.createElement('div');
    section.className = 'sources-section';

    const toggle = document.createElement('div');
    toggle.className = 'sources-toggle';
    toggle.innerHTML = `
        <span class="icon">▼</span>
        <span>Sources (${sources.length})</span>
    `;

    const list = document.createElement('div');
    list.className = 'sources-list';

    sources.forEach(source => {
        const card = document.createElement('div');
        card.className = 'source-card';
        card.innerHTML = `
            <div class="source-header">
                <div class="source-title">${escapeHtml(source.title || 'Untitled')}</div>
                <div class="source-meta">
                    <span>ID: ${escapeHtml(source.doc_id || 'N/A')}</span>
                    <span>Page: ${source.page || 'N/A'}</span>
                </div>
            </div>
            ${source.text ? `<div class="source-text">${escapeHtml(truncateText(source.text, 200))}</div>` : ''}
        `;
        list.appendChild(card);
    });

    toggle.addEventListener('click', () => {
        const isExpanded = toggle.classList.toggle('expanded');
        list.classList.toggle('expanded', isExpanded);
    });

    section.appendChild(toggle);
    section.appendChild(list);

    return section;
}

// ===== Utilities =====
function updateSendButton() {
    const hasMessage = messageInput.value.trim().length > 0;
    const hasApiKey = apiKeyInput.value.trim().length > 0;
    sendButton.disabled = !(hasMessage && hasApiKey);
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function saveChatHistory() {
    try {
        sessionStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(chatHistory));
    } catch (e) {
        console.error('Failed to save chat history:', e);
    }
}

// ===== Start Application =====
document.addEventListener('DOMContentLoaded', init);
