// Research Assistant Client JavaScript

class ResearchAssistantClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.sessionId = this.generateSessionId();
        this.eventHandlers = new Map();

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadAgents();
        this.loadTools();
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    setupWebSocketHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            this.emit('connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.emit('disconnected');
            this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.showError('Unable to connect to server. Please refresh the page.');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connectWebSocket(), delay);
    }

    handleMessage(data) {
        const { event_type, agent, status, message, data: eventData, timestamp } = data;

        // Emit specific event
        this.emit(event_type, data);

        // Update UI based on event type
        switch (event_type) {
            case 'acknowledgment':
                this.showProcessing(message);
                break;
            case 'start':
                this.clearResults();
                this.addEventCard(data);
                break;
            case 'plan':
                this.showExecutionPlan(eventData.plan);
                break;
            case 'agent_call':
            case 'tool_use':
                this.addEventCard(data);
                break;
            case 'progress':
                this.updateProgress(data);
                break;
            case 'result':
                this.showResults(eventData);
                break;
            case 'complete':
                this.onQueryComplete(data);
                break;
            case 'error':
                this.showError(message);
                break;
            default:
                this.addEventCard(data);
        }
    }

    sendQuery(query, parameters = {}) {
        if (!this.isConnected) {
            this.showError('Not connected to server. Please wait...');
            return false;
        }

        const request = {
            query,
            parameters,
            session_id: this.sessionId
        };

        try {
            this.ws.send(JSON.stringify(request));
            this.disableSubmit(true);
            return true;
        } catch (error) {
            console.error('Failed to send query:', error);
            this.showError('Failed to send query');
            return false;
        }
    }

    // UI Update Methods
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connectionStatus');
        const indicators = document.querySelectorAll('.status-indicator');

        if (connected) {
            statusEl.textContent = 'Connected';
            indicators.forEach(el => {
                el.classList.remove('disconnected');
                el.classList.add('connected');
            });
        } else {
            statusEl.textContent = `Disconnected (Reconnecting... ${this.reconnectAttempts}/${this.maxReconnectAttempts})`;
            indicators.forEach(el => {
                el.classList.remove('connected');
                el.classList.add('disconnected');
            });
        }
    }

    showProcessing(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="event-card">
                <div class="loading-spinner"></div>
                <span style="margin-left: 1rem;">${message}</span>
            </div>
        `;
    }

    clearResults() {
        document.getElementById('results').innerHTML = '';
    }

    addEventCard(event) {
        const resultsDiv = document.getElementById('results');
        const card = this.createEventCard(event);
        resultsDiv.appendChild(card);
        resultsDiv.scrollTop = resultsDiv.scrollHeight;
    }

    createEventCard(event) {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.dataset.eventType = event.event_type;
        card.dataset.agent = event.agent || 'system';

        const timestamp = new Date(event.timestamp || Date.now()).toLocaleTimeString();

        let statusIcon = '';
        if (event.status === 'completed') {
            statusIcon = '<span style="color: var(--success-color);">✓</span>';
        } else if (event.status === 'error') {
            statusIcon = '<span style="color: var(--error-color);">✗</span>';
        } else if (event.status === 'started' || event.status === 'running') {
            statusIcon = '<div class="loading-spinner" style="display: inline-block; width: 16px; height: 16px;"></div>';
        }

        card.innerHTML = `
            <div class="event-header">
                <span class="event-type">
                    ${statusIcon}
                    ${event.agent || 'System'} - ${event.event_type}
                </span>
                <span class="event-time">${timestamp}</span>
            </div>
            <div class="event-message">${event.message}</div>
            ${event.data && Object.keys(event.data).length > 0 ? `
                <details class="event-data-container">
                    <summary style="cursor: pointer; padding: 0.5rem 0;">Show Details</summary>
                    <div class="event-data">
                        <pre>${JSON.stringify(event.data, null, 2)}</pre>
                    </div>
                </details>
            ` : ''}
        `;

        return card;
    }

    showExecutionPlan(plan) {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.style.borderLeftColor = 'var(--warning-color)';

        let stepsHtml = '<ol>';
        plan.steps.forEach(step => {
            stepsHtml += `<li>${step.agent || step.tool}: ${step.action}</li>`;
        });
        stepsHtml += '</ol>';

        card.innerHTML = `
            <div class="event-header">
                <span class="event-type">Execution Plan</span>
            </div>
            <div class="event-message">
                Query: ${plan.query}
                ${stepsHtml}
            </div>
        `;

        document.getElementById('results').appendChild(card);
    }

    showResults(results) {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.style.borderLeftColor = 'var(--success-color)';

        card.innerHTML = `
            <div class="event-header">
                <span class="event-type">Results</span>
            </div>
            <div class="event-message">
                ${results.synthesis || 'Results processed successfully'}
            </div>
            ${results.sources && results.sources.length > 0 ? `
                <details class="event-data-container">
                    <summary style="cursor: pointer; padding: 0.5rem 0;">
                        Sources (${results.sources.length})
                    </summary>
                    <div class="event-data">
                        ${results.sources.map(s => `
                            <div style="margin-bottom: 0.5rem;">
                                <strong>${s.title || 'Untitled'}</strong><br>
                                ${s.authors ? s.authors.join(', ') : ''}<br>
                                ${s.year || ''} ${s.journal || ''}
                            </div>
                        `).join('')}
                    </div>
                </details>
            ` : ''}
        `;

        document.getElementById('results').appendChild(card);
    }

    showError(message) {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.style.borderLeftColor = 'var(--error-color)';

        card.innerHTML = `
            <div class="event-header">
                <span class="event-type" style="color: var(--error-color);">Error</span>
            </div>
            <div class="event-message">${message}</div>
        `;

        document.getElementById('results').appendChild(card);
        this.disableSubmit(false);
    }

    onQueryComplete(data) {
        this.disableSubmit(false);
        this.addEventCard(data);
    }

    disableSubmit(disabled) {
        document.getElementById('submitBtn').disabled = disabled;
        if (disabled) {
            document.getElementById('submitBtn').innerHTML = '<div class="loading-spinner"></div> Processing...';
        } else {
            document.getElementById('submitBtn').innerHTML = 'Search';
        }
    }

    // Event System
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    // Setup Methods
    setupEventListeners() {
        // Submit button
        document.getElementById('submitBtn').addEventListener('click', () => this.handleSubmit());

        // Enter key in input
        document.getElementById('queryInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSubmit();
            }
        });

        // Option chips
        document.querySelectorAll('.option-chip').forEach(chip => {
            chip.addEventListener('click', () => this.toggleChip(chip));
        });
    }

    handleSubmit() {
        const query = document.getElementById('queryInput').value.trim();
        if (!query) {
            alert('Please enter a query');
            return;
        }

        const databases = Array.from(document.querySelectorAll('.option-chip[data-db].active'))
            .map(el => el.dataset.db);

        const action = document.querySelector('.option-chip[data-action].active')?.dataset.action || 'search';

        const parameters = {
            databases: databases.length > 0 ? databases : ['arxiv', 'semantic_scholar'],
            action: action,
            max_results: 20
        };

        this.sendQuery(query, parameters);
    }

    toggleChip(chip) {
        if (chip.dataset.db) {
            chip.classList.toggle('active');
        } else if (chip.dataset.action) {
            document.querySelectorAll('.option-chip[data-action]').forEach(c => {
                c.classList.remove('active');
            });
            chip.classList.add('active');
        }
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const agents = await response.json();
            this.updateAgentList(agents);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    }

    async loadTools() {
        try {
            const response = await fetch('/api/tools');
            const tools = await response.json();
            console.log('Available tools:', tools);
        } catch (error) {
            console.error('Failed to load tools:', error);
        }
    }

    updateAgentList(agents) {
        const agentList = document.getElementById('agentList');
        agentList.innerHTML = '';

        Object.entries(agents).forEach(([name, description]) => {
            const item = document.createElement('div');
            item.className = 'agent-item';
            item.dataset.agent = name;
            item.innerHTML = `
                <div class="agent-name">${name.charAt(0).toUpperCase() + name.slice(1)} Agent</div>
                <div class="agent-description">${description}</div>
            `;
            item.addEventListener('click', () => this.selectAgent(name));
            agentList.appendChild(item);
        });
    }

    selectAgent(agentName) {
        console.log('Selected agent:', agentName);
        // Could add functionality to filter or highlight events by agent
    }
}

// Initialize client when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.researchClient = new ResearchAssistantClient();
});