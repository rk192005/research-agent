// --- Global State ---
let queueData = [];
let activeTopicIndex = null;

// --- DOM Elements ---
const queueListEl = document.getElementById('queue-list');
const emptyStateEl = document.getElementById('empty-state');
const loadingStateEl = document.getElementById('loading-state');
const reportViewerEl = document.getElementById('report-viewer');
const markdownBodyEl = document.getElementById('markdown-body');
const searchInputEl = document.getElementById('search-input');

const reportTitleEl = document.getElementById('report-title');
const reportDateEl = document.getElementById('report-date');
const reportDepthEl = document.getElementById('report-depth');
const reportRawLinkEl = document.getElementById('report-raw-link');

const statPendingEl = document.getElementById('stat-pending');
const statRunningEl = document.getElementById('stat-running');
const statCompletedEl = document.getElementById('stat-completed');

const addTopicFormEl = document.getElementById('add-topic-form');
const topicInputEl = document.getElementById('topic-input');
const depthSelectEl = document.getElementById('depth-select');
const csvExportMessageEl = document.getElementById('csv-export-message');
const csvLineCodeEl = document.getElementById('csv-line-code');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    fetchAndParseQueue();
    
    // Auto-refresh queue every 60 seconds (handy during active runs)
    setInterval(fetchAndParseQueue, 60000);
    
    // Add Search/Filter Listener
    searchInputEl.addEventListener('input', filterQueue);
    
    // Add Add Topic Listener
    addTopicFormEl.addEventListener('submit', handleAddTopicSubmit);
});

// --- Fetch and Parse CSV ---
async function fetchAndParseQueue() {
    try {
        const response = await fetch('research_queue.csv?t=' + Date.now());
        if (!response.ok) {
            throw new Error('Failed to fetch research queue. Ensure research_queue.csv exists.');
        }
        const csvText = await response.text();
        parseCSV(csvText);
        renderQueue();
        updateStats();
    } catch (error) {
        console.error(error);
        queueListEl.innerHTML = `<div class="loading-spinner text-yellow"><i class="fa-solid fa-triangle-exclamation"></i> Error loading queue: ${error.message}</div>`;
    }
}

// Simple RFC 4180-compliant CSV Parser
function parseCSV(text) {
    const lines = text.split(/\r?\n/);
    if (lines.length === 0) return;
    
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        // Handle comma splitting inside quotes
        let matches = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || line.split(',');
        matches = matches.map(val => val.replace(/^"|"$/g, '').trim());
        
        const row = {};
        headers.forEach((header, index) => {
            row[header] = matches[index] || '';
        });
        
        data.push(row);
    }
    
    queueData = data;
}

// --- Render Sidebar Queue ---
function renderQueue(filterText = '') {
    queueListEl.innerHTML = '';
    
    const query = filterText.toLowerCase();
    const filteredData = queueData.filter(item => 
        item.topic && item.topic.toLowerCase().includes(query)
    );
    
    if (filteredData.length === 0) {
        queueListEl.innerHTML = `<div class="loading-spinner">No topics found.</div>`;
        return;
    }
    
    filteredData.forEach((item, index) => {
        const queueIndex = queueData.indexOf(item);
        
        const itemEl = document.createElement('div');
        itemEl.className = `queue-item ${activeTopicIndex === queueIndex ? 'active' : ''}`;
        
        // Add click listener
        itemEl.addEventListener('click', () => selectTopic(queueIndex));
        
        const leftEl = document.createElement('div');
        leftEl.className = 'queue-item-left';
        
        const titleEl = document.createElement('span');
        titleEl.className = 'queue-title';
        titleEl.textContent = item.topic;
        
        const timeEl = document.createElement('span');
        timeEl.className = 'queue-time';
        timeEl.textContent = item.completed_at || item.created_at || 'No date';
        
        leftEl.appendChild(titleEl);
        leftEl.appendChild(timeEl);
        
        const badgeEl = document.createElement('span');
        badgeEl.className = `badge ${item.status}`;
        badgeEl.textContent = item.status || 'unknown';
        
        itemEl.appendChild(leftEl);
        itemEl.appendChild(badgeEl);
        queueListEl.appendChild(itemEl);
    });
}

// --- Update Stat Metrics ---
function updateStats() {
    let pending = 0;
    let running = 0;
    let completed = 0;
    
    queueData.forEach(item => {
        if (item.status === 'pending') pending++;
        else if (item.status === 'running') running++;
        else if (item.status === 'done') completed++;
    });
    
    statPendingEl.textContent = pending;
    statRunningEl.textContent = running;
    statCompletedEl.textContent = completed;
}

// --- Filter Queue List ---
function filterQueue(e) {
    renderQueue(e.target.value);
}

// --- Select and Load Report ---
async function selectTopic(index) {
    activeTopicIndex = index;
    renderQueue(searchInputEl.value);
    
    const item = queueData[index];
    
    if (item.status !== 'done') {
        // Show alert or explanation if they click a pending/failed item
        emptyStateEl.classList.remove('hidden');
        reportViewerEl.classList.add('hidden');
        loadingStateEl.classList.add('hidden');
        
        const emptyTitle = emptyStateEl.querySelector('h2');
        const emptyDesc = emptyStateEl.querySelector('p');
        
        if (item.status === 'pending') {
            emptyTitle.textContent = "Topic is Pending";
            emptyDesc.textContent = `"${item.topic}" is queued to be researched. Run the python agent locally or wait for the cron job to trigger.`;
        } else if (item.status === 'running') {
            emptyTitle.textContent = "Research is Running";
            emptyDesc.textContent = `"${item.topic}" is currently being researched. Refresh this page in a minute to see if it has completed.`;
        } else {
            emptyTitle.textContent = "Research Failed";
            emptyDesc.textContent = `"${item.topic}" failed to complete. Check the console or local logs inside reports/logs directory for errors.`;
        }
        return;
    }
    
    // Otherwise fetch the report markdown file
    emptyStateEl.classList.add('hidden');
    reportViewerEl.classList.add('hidden');
    loadingStateEl.classList.remove('hidden');
    
    try {
        let relativePath = item.report_link;
        
        // Extract relative file path if it is absolute
        if (relativePath.includes('reports/')) {
            const index = relativePath.indexOf('reports/');
            relativePath = relativePath.substring(index);
        }
        
        // Clean URL encoded characters (e.g. spaces)
        const cleanPath = decodeURIComponent(relativePath);
        
        const response = await fetch(cleanPath);
        if (!response.ok) {
            throw new Error(`Could not find the report at ${cleanPath}`);
        }
        
        const markdown = await response.text();
        
        // Parse and render
        renderMarkdownReport(item.topic, item.completed_at, item.depth, markdown, cleanPath);
    } catch (error) {
        console.error(error);
        loadingStateEl.classList.add('hidden');
        emptyStateEl.classList.remove('hidden');
        emptyStateEl.querySelector('h2').textContent = "Error Loading Report";
        emptyStateEl.querySelector('p').textContent = error.message;
    }
}

// --- Render Markdown in Viewer ---
function renderMarkdownReport(title, date, depth, markdown, cleanPath) {
    reportTitleEl.textContent = title;
    reportDateEl.textContent = date || 'N/A';
    reportDepthEl.textContent = depth === 'deep' ? 'Deep Search' : 'Quick Search';
    reportRawLinkEl.href = cleanPath;
    
    // Marked configuration
    marked.setOptions({
        headerIds: true,
        gfm: true,
        breaks: true
    });
    
    // Parse markdown (we trim out the metadata header like Generated / Pipeline if wanted, or render full)
    let parsedContent = marked.parse(markdown);
    
    markdownBodyEl.innerHTML = parsedContent;
    
    // Switch states
    loadingStateEl.classList.add('hidden');
    reportViewerEl.classList.remove('hidden');
}

// --- Handle Add Topic Submit ---
function handleAddTopicSubmit(e) {
    e.preventDefault();
    
    const topic = topicInputEl.value.trim();
    const depth = depthSelectEl.value;
    const dateStr = new Date().toISOString().split('T')[0];
    
    if (!topic) return;
    
    // Generate CSV line for easy copy paste
    // topic,depth,status,raw_findings,report_link,created_at,completed_at
    const csvLine = `"${topic.replace(/"/g, '""')}",${depth},pending,,,${dateStr},`;
    
    csvLineCodeEl.textContent = csvLine;
    csvExportMessageEl.classList.remove('hidden');
    
    // Reset Form
    topicInputEl.value = '';
    topicInputEl.focus();
}
