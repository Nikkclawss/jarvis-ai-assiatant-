// Jarvis AI Assistant - Frontend Application

const API_BASE = '';  // Same origin

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const knowledgeInput = document.getElementById('knowledgeInput');
const addKnowledgeBtn = document.getElementById('addKnowledgeBtn');
const clearKnowledgeBtn = document.getElementById('clearKnowledgeBtn');
const knowledgeItems = document.getElementById('knowledgeItems');
const refreshStatusBtn = document.getElementById('refreshStatusBtn');
const useKnowledgeBase = document.getElementById('useKnowledgeBase');
const statusIndicator = document.getElementById('statusIndicator');

// State
let isLoading = false;
let welcomeMessageVisible = true;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    initKnowledge();
    initSettings();
    checkStatus();
});

// Navigation
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewId = btn.dataset.view + 'View';

            // Update active states
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            views.forEach(v => v.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');

            // Load data for specific views
            if (btn.dataset.view === 'knowledge') {
                loadKnowledge();
            } else if (btn.dataset.view === 'settings') {
                checkStatus();
            }
        });
    });
}

// Chat Functions
function initChat() {
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
        sendBtn.disabled = !messageInput.value.trim();
    });

    // Send on Enter (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled && !isLoading) {
                sendMessage();
            }
        }
    });

    // Send button click
    sendBtn.addEventListener('click', () => {
        if (!sendBtn.disabled && !isLoading) {
            sendMessage();
        }
    });
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    // Remove welcome message
    if (welcomeMessageVisible) {
        const welcomeMsg = chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
        welcomeMessageVisible = false;
    }

    // Add user message
    addMessage(message, 'user');

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Show loading
    isLoading = true;
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                use_knowledge_base: useKnowledgeBase.checked
            })
        });

        if (!response.ok) throw new Error('Failed to get response');

        const data = await response.json();

        // Remove loading
        removeLoadingMessage(loadingId);

        // Add assistant message
        addMessage(data.response, 'assistant', data.context_used, data.retrieved_documents);

    } catch (error) {
        console.error('Chat error:', error);
        removeLoadingMessage(loadingId);
        addMessage('Sorry, I encountered an error. Please check if the server is running.', 'assistant');
        showToast('Failed to send message', 'error');
    }

    isLoading = false;
}

function addMessage(content, role, contextUsed = false, documents = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'J';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    // Add context indicator for assistant messages
    if (role === 'assistant' && contextUsed && documents.length > 0) {
        const contextDiv = document.createElement('div');
        contextDiv.className = 'message-context';
        contextDiv.textContent = `Used ${documents.length} knowledge base document(s)`;
        contentDiv.appendChild(contextDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(content) {
    // Convert markdown-style code blocks
    content = content.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    // Convert inline code
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Convert line breaks
    content = content.replace(/\n/g, '<br>');
    return content;
}

function addLoadingMessage() {
    const id = 'loading-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = id;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'J';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeLoadingMessage(id) {
    const loadingMsg = document.getElementById(id);
    if (loadingMsg) loadingMsg.remove();
}

// Knowledge Base Functions
function initKnowledge() {
    addKnowledgeBtn.addEventListener('click', addKnowledge);
    clearKnowledgeBtn.addEventListener('click', clearKnowledge);
}

async function loadKnowledge() {
    try {
        const response = await fetch(`${API_BASE}/api/knowledge`);
        if (!response.ok) throw new Error('Failed to load knowledge');

        const data = await response.json();
        renderKnowledgeItems(data.documents);
    } catch (error) {
        console.error('Load knowledge error:', error);
        showToast('Failed to load knowledge base', 'error');
    }
}

function renderKnowledgeItems(data) {
    if (!data.ids || data.ids.length === 0) {
        knowledgeItems.innerHTML = `
            <div class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                <p>No knowledge added yet</p>
            </div>
        `;
        return;
    }

    knowledgeItems.innerHTML = data.ids.map((id, index) => `
        <div class="knowledge-item" data-id="${id}">
            <div class="knowledge-item-content">${escapeHtml(data.documents[index])}</div>
            <button class="knowledge-item-delete" onclick="deleteKnowledge('${id}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        </div>
    `).join('');
}

async function addKnowledge() {
    const content = knowledgeInput.value.trim();
    if (!content) {
        showToast('Please enter some knowledge to add', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/knowledge/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ documents: [content] })
        });

        if (!response.ok) throw new Error('Failed to add knowledge');

        knowledgeInput.value = '';
        loadKnowledge();
        showToast('Knowledge added successfully', 'success');
    } catch (error) {
        console.error('Add knowledge error:', error);
        showToast('Failed to add knowledge', 'error');
    }
}

async function deleteKnowledge(id) {
    try {
        const response = await fetch(`${API_BASE}/api/knowledge/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete knowledge');

        loadKnowledge();
        showToast('Knowledge deleted', 'success');
    } catch (error) {
        console.error('Delete knowledge error:', error);
        showToast('Failed to delete knowledge', 'error');
    }
}

async function clearKnowledge() {
    if (!confirm('Are you sure you want to clear all knowledge? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/knowledge`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to clear knowledge');

        loadKnowledge();
        showToast('Knowledge base cleared', 'success');
    } catch (error) {
        console.error('Clear knowledge error:', error);
        showToast('Failed to clear knowledge base', 'error');
    }
}

// Settings Functions
function initSettings() {
    refreshStatusBtn.addEventListener('click', checkStatus);
}

async function checkStatus() {
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');

    try {
        const response = await fetch(`${API_BASE}/api/status`);
        if (!response.ok) throw new Error('Failed to get status');

        const data = await response.json();

        // Update sidebar status
        statusDot.className = 'status-dot ' + (data.status === 'connected' ? 'connected' : 'error');
        statusText.textContent = data.status === 'connected' ? 'Connected' : 'Connection issue';

        // Update settings view
        document.getElementById('providerValue').textContent = data.provider?.toUpperCase() || '-';
        document.getElementById('modelValue').textContent = data.model || '-';

        const connectionStatus = document.getElementById('connectionStatus');
        connectionStatus.textContent = data.status || '-';
        connectionStatus.className = 'status-value ' + (data.status === 'connected' ? 'success' : 'error');

        document.getElementById('kbCount').textContent = `${data.knowledge_base_count || 0} documents`;

    } catch (error) {
        console.error('Status check error:', error);
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Disconnected';

        document.getElementById('providerValue').textContent = '-';
        document.getElementById('modelValue').textContent = '-';
        document.getElementById('connectionStatus').textContent = 'Error';
        document.getElementById('connectionStatus').className = 'status-value error';
        document.getElementById('kbCount').textContent = '-';
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make deleteKnowledge available globally
window.deleteKnowledge = deleteKnowledge;
