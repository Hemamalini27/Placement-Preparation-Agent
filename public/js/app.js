// Session Guard: Instant redirect if unauthenticated to avoid screen flashing
if (!localStorage.getItem('auth_token')) {
    window.location.replace('login.html');
}

// Global State
const STATE = {
    activeTab: 'dashboard',
    charts: {
        cadence: null,
        skills: null
    },
    interview: {
        sessionId: null,
        role: null,
        type: null,
        currentQuestion: null
    }
};

// API Base URL (Relative for proxying or absolute fallback for local runs)
const API_BASE = window.location.origin;

// DOM Elements
const elements = {
    tabs: document.querySelectorAll('.nav-item'),
    panels: document.querySelectorAll('.tab-panel'),
    tabTitle: document.getElementById('tab-title'),
    tabSubtitle: document.getElementById('tab-subtitle'),
    systemStatus: document.getElementById('system-status'),
    
    // Dashboard Panel
    metricInterviews: document.getElementById('metric-interviews'),
    metricProblems: document.getElementById('metric-problems'),
    metricPlans: document.getElementById('metric-plans'),
    metricSkills: document.getElementById('metric-skills'),
    btnRefreshDashboard: document.getElementById('btn-refresh-dashboard'),
    
    // Study Planner Tab
    formStudyPlan: document.getElementById('form-study-plan'),
    plannerRole: document.getElementById('planner-role'),
    plannerLevel: document.getElementById('planner-level'),
    plannerHours: document.getElementById('planner-hours'),
    plannerDate: document.getElementById('planner-date'),
    plannerEmptyState: document.getElementById('planner-empty-state'),
    plannerLoadingState: document.getElementById('planner-loading-state'),
    plannerResults: document.getElementById('planner-results'),
    planTitleRole: document.getElementById('plan-title-role'),
    planBadgeHours: document.getElementById('plan-badge-hours'),
    planDaysTimeline: document.getElementById('plan-days-timeline'),
    
    // Coding Arena Tab
    formCodingArena: document.getElementById('form-coding-arena'),
    arenaRole: document.getElementById('arena-role'),
    arenaLevel: document.getElementById('arena-level'),
    arenaEmptyState: document.getElementById('arena-empty-state'),
    arenaLoadingState: document.getElementById('arena-loading-state'),
    arenaResults: document.getElementById('arena-results'),
    
    // Mock Interview Tab
    interviewSetupCard: document.getElementById('interview-setup-card'),
    formInterviewSetup: document.getElementById('form-interview-setup'),
    interviewRole: document.getElementById('interview-role'),
    interviewType: document.getElementById('interview-type'),
    interviewChatContainer: document.getElementById('interview-chat-container'),
    chatHeaderRole: document.getElementById('chat-header-role'),
    chatMessagesWindow: document.getElementById('chat-messages-window'),
    btnRequestHint: document.getElementById('btn-request-hint'),
    formSubmitAnswer: document.getElementById('form-submit-answer'),
    userAnswerText: document.getElementById('user-answer-text'),
    btnSubmitAnswer: document.getElementById('btn-submit-answer'),
    interviewEvaluationCard: document.getElementById('interview-evaluation-card'),
    evalScore: document.getElementById('eval-score'),
    evalStrengthsList: document.getElementById('eval-strengths-list'),
    evalWeaknessesList: document.getElementById('eval-weaknesses-list'),
    evalTipsList: document.getElementById('eval-tips-list'),
    evalNextDifficulty: document.getElementById('eval-next-difficulty'),
    btnResetInterview: document.getElementById('btn-reset-interview'),
    
    // Agent Activity Log Tab
    logsTimelineContainer: document.getElementById('logs-timeline-container'),
    toastContainer: document.getElementById('toast-container'),
    btnLogout: document.getElementById('btn-logout')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Navigation Toggles
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.getAttribute('data-tab'));
        });
    });

    // 2. Setup Refresh Metrics Button
    elements.btnRefreshDashboard.addEventListener('click', loadDashboardData);

    // 3. Setup Form Submissions
    elements.formStudyPlan.addEventListener('submit', handleStudyPlanSubmit);
    elements.formCodingArena.addEventListener('submit', handleCodingArenaSubmit);
    elements.formInterviewSetup.addEventListener('submit', handleInterviewSetupSubmit);
    elements.formSubmitAnswer.addEventListener('submit', handleAnswerSubmit);
    elements.btnRequestHint.addEventListener('click', handleRequestHint);
    elements.btnResetInterview.addEventListener('click', resetInterviewInterface);

    // 4. Run Startup Checks & Fetch initial dashboard
    checkBackendHealth();
    loadDashboardData();
    loadAgentLogs();

    // Setup periodic polling for activity logs (every 10 seconds)
    setInterval(loadAgentLogs, 10000);

    // 5. Setup Logout Click
    if (elements.btnLogout) {
        elements.btnLogout.addEventListener('click', () => {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_username');
            localStorage.removeItem('auth_fullname');
            window.location.replace('login.html');
        });
    }
});

// Toast Notification Manager
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-triangle';

    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <span class="toast-msg">${message}</span>
    `;
    elements.toastContainer.appendChild(toast);
    lucide.createIcons();

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Health Check
async function checkBackendHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/dashboard`);
        if (res.ok) {
            elements.systemStatus.innerText = "System Active";
            elements.systemStatus.previousElementSibling.className = "pulse-dot green";
        } else {
            throw new Error();
        }
    } catch (e) {
        elements.systemStatus.innerText = "Connection Failed";
        elements.systemStatus.previousElementSibling.className = "pulse-dot";
        showToast("Cannot connect to FastAPI backend server.", "error");
    }
}

// Navigation Tab Switcher
function switchTab(tabId) {
    // Update active tab buttons
    elements.tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Toggle panel visibility
    elements.panels.forEach(panel => {
        if (panel.id === `panel-${tabId}`) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });

    STATE.activeTab = tabId;

    // Update Headers Text
    const tabMetaData = {
        dashboard: { title: "Dashboard Overview", subtitle: "Real-time placement prep metrics and analytics" },
        planner: { title: "Study Planner", subtitle: "Build tailored schedules with the Planner Agent" },
        arena: { title: "Coding Arena", subtitle: "Access recommended challenges optimized for your targeted roles" },
        interview: { title: "Mock Interview Simulation", subtitle: "Adaptive role-play dialogue evaluated by AI Agents" },
        logs: { title: "Agent Activity Log", subtitle: "Live execution telemetry and state logs" }
    };

    if (tabMetaData[tabId]) {
        elements.tabTitle.innerText = tabMetaData[tabId].title;
        elements.tabSubtitle.innerText = tabMetaData[tabId].subtitle;
    }

    // Refresh context if logs or dashboard selected
    if (tabId === 'logs') {
        loadAgentLogs();
    } else if (tabId === 'dashboard') {
        loadDashboardData();
    }
}

// Fetch and Populate Dashboard Data
async function loadDashboardData() {
    elements.btnRefreshDashboard.classList.add('spinning');
    try {
        const response = await fetch(`${API_BASE}/api/dashboard`);
        if (!response.ok) throw new Error("Failed to fetch dashboard data");
        const json = await response.json();
        
        if (json.status === "success") {
            const data = json.data;
            
            // Populate Counters
            elements.metricInterviews.innerText = data.metrics.interviews_taken;
            elements.metricProblems.innerText = data.metrics.problems_advised;
            elements.metricPlans.innerText = data.metrics.plans_executed;
            elements.metricSkills.innerText = `${data.metrics.skill_quotient}%`;

            // Draw Charts
            renderCharts(data.charts);
        }
    } catch (e) {
        loggerError("Dashboard Fetch", e);
        showToast("Error retrieving metrics from servers.", "error");
    } finally {
        elements.btnRefreshDashboard.classList.remove('spinning');
    }
}

// Render Line & Radar Charts using Chart.js
function renderCharts(chartData) {
    const isDark = true; // Premium theme is dark-mode
    const gridColor = 'rgba(255, 255, 255, 0.05)';
    const textColor = '#9ca3af';

    // 1. Cadence Line Chart
    if (STATE.charts.cadence) STATE.charts.cadence.destroy();
    
    const ctxCadence = document.getElementById('chart-cadence').getContext('2d');
    STATE.charts.cadence = new Chart(ctxCadence, {
        type: 'line',
        data: {
            labels: chartData.cadence.labels,
            datasets: [{
                label: 'Activity Volume',
                data: chartData.cadence.data,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.15)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#fff',
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, stepSize: 1 },
                    beginAtZero: true
                }
            }
        }
    });

    // 2. Skill Proficiencies Radar Chart
    if (STATE.charts.skills) STATE.charts.skills.destroy();

    const ctxSkills = document.getElementById('chart-skills').getContext('2d');
    STATE.charts.skills = new Chart(ctxSkills, {
        type: 'radar',
        data: {
            labels: chartData.skills.labels,
            datasets: [{
                label: 'Score Index',
                data: chartData.skills.data,
                backgroundColor: 'rgba(168, 85, 247, 0.2)',
                borderColor: '#a855f7',
                borderWidth: 2,
                pointBackgroundColor: '#06b6d4'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    grid: { color: gridColor },
                    angleLines: { color: gridColor },
                    ticks: { display: false },
                    pointLabels: { color: textColor, font: { size: 10, family: 'Inter' } },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Generate Study Plan Form Submission
async function handleStudyPlanSubmit(e) {
    e.preventDefault();

    elements.plannerEmptyState.classList.add('hidden');
    elements.plannerResults.classList.add('hidden');
    elements.plannerLoadingState.classList.remove('hidden');

    const payload = {
        role: elements.plannerRole.value,
        skill_level: elements.plannerLevel.value,
        hours_per_day: parseFloat(elements.plannerHours.value),
        target_date: elements.plannerDate.value || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/generate-study-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("API responded with an error status.");
        const json = await response.json();

        if (json.status === 'success') {
            const plan = json.data;
            renderStudyPlan(plan);
            showToast("7-Day Study Plan created successfully!", "success");
        } else {
            throw new Error(json.message);
        }
    } catch (err) {
        loggerError("Planner Submission", err);
        showToast("Error generating study plan. Try again.", "error");
        elements.plannerEmptyState.classList.remove('hidden');
    } finally {
        elements.plannerLoadingState.classList.add('hidden');
    }
}

// Render generated study plan UI cards
function renderStudyPlan(plan) {
    elements.planTitleRole.innerText = `${plan.role} Plan (${elements.plannerLevel.value})`;
    elements.planBadgeHours.innerText = `${plan.estimated_hours} Hours Total`;
    elements.planDaysTimeline.innerHTML = '';

    plan.days.forEach(day => {
        const card = document.createElement('div');
        card.className = 'day-card glass';

        // Map list of topics into badges
        const topicsHTML = day.topics.map(t => `<span class="topic-tag">${t}</span>`).join('');
        
        // Map list of practice tasks into checklist
        const tasksHTML = day.practice_tasks.map(task => `
            <div class="task-item">
                <i data-lucide="check-square"></i>
                <span>${task}</span>
            </div>
        `).join('');

        card.innerHTML = `
            <div class="day-card-header">
                <h4>${day.day}</h4>
                <i data-lucide="book-open" class="text-indigo"></i>
            </div>
            <div class="day-card-body">
                <div class="day-topics">${topicsHTML}</div>
                <div class="tasks-list">${tasksHTML}</div>
                <div class="revision-text"><strong>Review Milestone:</strong> ${day.revision}</div>
            </div>
        `;
        elements.planDaysTimeline.appendChild(card);
    });

    lucide.createIcons();
    elements.plannerResults.classList.remove('hidden');
}

// Generate Coding Challenge Recommendations Form Submission
async function handleCodingArenaSubmit(e) {
    e.preventDefault();

    elements.arenaEmptyState.classList.add('hidden');
    elements.arenaResults.classList.add('hidden');
    elements.arenaLoadingState.classList.remove('hidden');

    const payload = {
        role: elements.arenaRole.value,
        level: elements.arenaLevel.value
    };

    try {
        const response = await fetch(`${API_BASE}/api/recommend-problems`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("API call error");
        const json = await response.json();

        if (json.status === 'success') {
            renderCodingChallenges(json.data);
            showToast("Coding problems curated successfully!", "success");
        } else {
            throw new Error(json.message);
        }
    } catch (err) {
        loggerError("Arena Submission", err);
        showToast("Error generating coding challenges.", "error");
        elements.arenaEmptyState.classList.remove('hidden');
    } finally {
        elements.arenaLoadingState.classList.add('hidden');
    }
}

// Render challenges to DOM
function renderCodingChallenges(challenges) {
    elements.arenaResults.innerHTML = '';

    challenges.forEach(challenge => {
        const card = document.createElement('div');
        card.className = 'challenge-card glass';

        let badgeClass = 'badge-medium';
        if (challenge.difficulty.toLowerCase() === 'easy') badgeClass = 'badge-easy';
        if (challenge.difficulty.toLowerCase() === 'hard') badgeClass = 'badge-hard';

        card.innerHTML = `
            <div class="challenge-card-header">
                <div>
                    <span class="challenge-topic">${challenge.topic}</span>
                    <h4 class="challenge-title">${challenge.name}</h4>
                </div>
                <span class="badge ${badgeClass}">${challenge.difficulty}</span>
            </div>
            <p class="challenge-desc">${challenge.description}</p>
            <div class="challenge-reason">
                <strong>Why Recommended:</strong> ${challenge.reason}
            </div>
        `;
        elements.arenaResults.appendChild(card);
    });

    elements.arenaResults.classList.remove('hidden');
}

// Start AI Mock Interview Setup Submission
async function handleInterviewSetupSubmit(e) {
    e.preventDefault();

    const role = elements.interviewRole.value;
    const type = elements.interviewType.value;

    elements.interviewSetupCard.classList.add('hidden');
    elements.interviewChatContainer.classList.remove('hidden');
    
    // Clear chat layout
    elements.chatMessagesWindow.innerHTML = '';
    appendTypingIndicator();

    const payload = {
        role: role,
        type: type
    };

    try {
        const response = await fetch(`${API_BASE}/api/start-interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("API call error");
        const json = await response.json();

        removeTypingIndicator();

        if (json.status === 'success') {
            const session = json.data;
            STATE.interview.sessionId = session.session_id;
            STATE.interview.role = role;
            STATE.interview.type = type;
            STATE.interview.currentQuestion = session.question;

            // Configure layout titles
            elements.chatHeaderRole.innerText = `${type === 'tech' ? 'Technical' : 'HR / Behavioral'} Simulation - ${role}`;
            
            // Append Interviewer Question to dialogue
            appendChatMessage(session.question, 'bot');
            showToast("Interview simulation started!", "success");
        } else {
            throw new Error(json.message);
        }
    } catch (err) {
        removeTypingIndicator();
        loggerError("Interview Setup", err);
        showToast("Error starting interview.", "error");
        resetInterviewInterface();
    }
}

// Request Interview Question Hint
async function handleRequestHint() {
    if (!STATE.interview.sessionId) return;
    
    elements.btnRequestHint.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/request-hint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: STATE.interview.sessionId })
        });

        if (!response.ok) throw new Error("API call error");
        const json = await response.json();

        if (json.status === 'success') {
            appendChatMessage(`💡 Hint: ${json.data.hint}`, 'hint');
            showToast("Hint revealed!", "info");
        }
    } catch (err) {
        loggerError("Hint Retrieval", err);
        showToast("Error looking up hint.", "error");
    } finally {
        elements.btnRequestHint.disabled = false;
    }
}

// Answer submission
async function handleAnswerSubmit(e) {
    e.preventDefault();

    const answer = elements.userAnswerText.value.trim();
    if (!answer || !STATE.interview.sessionId) return;

    // Display candidate message
    appendChatMessage(answer, 'user');
    elements.userAnswerText.value = '';
    elements.formSubmitAnswer.classList.add('hidden'); // Hide input during evaluation

    appendTypingIndicator();

    const payload = {
        session_id: STATE.interview.sessionId,
        answer: answer
    };

    try {
        const response = await fetch(`${API_BASE}/api/submit-answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("API error");
        const json = await response.json();

        removeTypingIndicator();

        if (json.status === 'success') {
            const report = json.data;
            renderEvaluationReport(report);
            showToast("Answer evaluated successfully!", "success");
        }
    } catch (err) {
        removeTypingIndicator();
        elements.formSubmitAnswer.classList.remove('hidden');
        loggerError("Answer Submission", err);
        showToast("Error evaluating answer.", "error");
    }
}

// Render performance score card
function renderEvaluationReport(report) {
    elements.interviewChatContainer.classList.add('hidden');
    
    elements.evalScore.innerText = report.score;
    elements.evalNextDifficulty.innerText = report.next_difficulty;

    // Pop lists
    elements.evalStrengthsList.innerHTML = report.strengths.map(s => `<li>${s}</li>`).join('');
    elements.evalWeaknessesList.innerHTML = report.weaknesses.map(w => `<li>${w}</li>`).join('');
    elements.evalTipsList.innerHTML = report.tips.map(t => `<li>${t}</li>`).join('');

    elements.interviewEvaluationCard.classList.remove('hidden');
}

// Reset view back to setup panel
function resetInterviewInterface() {
    STATE.interview.sessionId = null;
    STATE.interview.role = null;
    STATE.interview.type = null;
    STATE.interview.currentQuestion = null;

    elements.interviewEvaluationCard.classList.add('hidden');
    elements.interviewChatContainer.classList.add('hidden');
    elements.formSubmitAnswer.classList.remove('hidden');
    elements.interviewSetupCard.classList.remove('hidden');
}

// Chat UI Append helpers
function appendChatMessage(text, role) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    
    if (role === 'hint') {
        bubble.innerHTML = `<i data-lucide="lightbulb" style="width: 1.1rem; height:1.1rem;"></i> <span>${text}</span>`;
    } else {
        bubble.innerText = text;
    }
    
    elements.chatMessagesWindow.appendChild(bubble);
    elements.chatMessagesWindow.scrollTop = elements.chatMessagesWindow.scrollHeight;
    lucide.createIcons();
}

function appendTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator-bubble';
    indicator.className = 'chat-bubble bot';
    indicator.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    elements.chatMessagesWindow.appendChild(indicator);
    elements.chatMessagesWindow.scrollTop = elements.chatMessagesWindow.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator-bubble');
    if (indicator) indicator.remove();
}

// Fetch and Render Agent Execution logs
async function loadAgentLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/agent-logs?limit=30`);
        if (!response.ok) throw new Error();
        const json = await response.json();
        
        if (json.status === 'success') {
            renderLogsTimeline(json.data);
        }
    } catch (e) {
        loggerError("Logs Timeline Fetch", e);
    }
}

// Render log cards in logs tab timeline
function renderLogsTimeline(logs) {
    if (logs.length === 0) {
        elements.logsTimelineContainer.innerHTML = `
            <div class="empty-state">
                <i data-lucide="database" class="empty-icon text-muted"></i>
                <h3>No Logs Found</h3>
                <p>Run study plan generations or mock interview questions to see agent orchestrator logs here.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    elements.logsTimelineContainer.innerHTML = '';

    logs.forEach((log, index) => {
        const logItem = document.createElement('div');
        logItem.className = `log-item ${log.status}`;

        const isSuccess = log.status === 'success';
        const statusText = isSuccess ? 'Success' : 'Failure';
        const formattedTime = new Date(log.timestamp).toLocaleTimeString();
        const uniqueId = `json-block-${index}`;

        // Convert payloads safely
        const displayParams = JSON.stringify(log.input_params, null, 2);
        const displayResponse = log.output_response ? JSON.stringify(log.output_response, null, 2) : (log.error || 'N/A');

        logItem.innerHTML = `
            <div class="log-meta">
                <span class="log-agent">${log.agent_name}</span>
                <span class="log-time">${formattedTime}</span>
                <span class="log-status ${log.status}">${statusText}</span>
            </div>
            <div class="log-content">
                <p class="log-text">Triggered execution payload. Expand details below to view input parameters and structural state responses.</p>
                <button class="log-details-toggle" onclick="toggleLogJSON('${uniqueId}')">Toggle Details (JSON)</button>
                <pre class="log-json-block hidden" id="${uniqueId}"><strong>INPUT:</strong>\n${displayParams}\n\n<strong>OUTPUT / RESPONSE:</strong>\n${displayResponse}</pre>
            </div>
        `;
        elements.logsTimelineContainer.appendChild(logItem);
    });

    lucide.createIcons();
}

// Global Toggle helper for log details (bind to window scope so onclick works)
window.toggleLogJSON = function(elementId) {
    const block = document.getElementById(elementId);
    if (block) {
        block.classList.toggle('hidden');
    }
}

// Diagnostic logger
function loggerError(context, err) {
    console.error(`[Error Context - ${context}]:`, err);
}
