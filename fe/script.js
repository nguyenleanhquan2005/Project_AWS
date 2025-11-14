// Configuration
const API_BASE_URL = 'https://xy4iztykoa.execute-api.us-east-1.amazonaws.com/dev';

// State
let currentSessionId = null;
let isProcessing = false;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');

// Initialize
function init() {
    setupEventListeners();
    setUIEnabled(true); // Kích hoạt UI sau khi load
    showUploadStatus('Chưa có tài liệu được xử lý.', 'initial');
}

function setupEventListeners() {
    // File upload
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileUpload();
        }
    });
    
    // Chat
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) {
            sendQuestion();
        }
    });
    
    sendButton.addEventListener('click', sendQuestion);
}

async function handleFileUpload() {
    const file = fileInput.files[0];
    if (!file) return;
    
    // Validate file
    if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.txt')) {
        showUploadStatus('Chỉ hỗ trợ file PDF và TXT', 'error');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB
        showUploadStatus('File quá lớn (tối đa 10MB)', 'error');
        return;
    }
    
    // Presign + direct S3 upload flow
    showUploadStatus('Yêu cầu presigned URL...', 'processing');
    setUIEnabled(false);
    try {
        const presignRes = await fetch(`${API_BASE_URL}/presign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: file.name, content_type: file.type })
        });
        const presignJson = await presignRes.json();
        if (!presignRes.ok) throw new Error(presignJson.error || 'Presign failed');

        const { upload_url, s3_key } = presignJson;

        showUploadStatus('Đang upload trực tiếp lên S3...', 'processing');

        // Upload file to presigned URL (PUT)
        const putRes = await fetch(upload_url, {
            method: 'PUT',
            // headers: {'Content-Type': file.type} <-- Không nên đặt Content-Type nếu upload_url đã chứa nó
            body: file
        });

        if (!putRes.ok) throw new Error('S3 upload failed');

        // Tell backend to process the uploaded S3 key
        showUploadStatus('Đang xử lý tài liệu trên backend...', 'processing');
        const procRes = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ s3_key })
        });

        const procJson = await procRes.json();
        if (!procRes.ok) throw new Error(procJson.error || 'Processing failed');

        currentSessionId = procJson.session_id;
        showUploadStatus(`✅ Đã upload: ${procJson.filename} (${procJson.chunks_count} đoạn)`, 'success');
        addMessage(`Tôi đã xử lý xong file "${procJson.filename}". Bạn có thể hỏi về nội dung trong file!`, 'assistant');
        setUIEnabled(true);

    } catch (error) {
        console.error('Upload error:', error);
        showUploadStatus('❌ Upload thất bại: ' + error.message, 'error');
        setUIEnabled(true); // Mở lại UI để người dùng thử lại
    }
}

async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question || isProcessing) return;
    
    addMessage(question, 'user');
    questionInput.value = '';
    setUIEnabled(false);
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                session_id: currentSessionId // Gửi session_id (có thể là null)
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            removeTypingIndicator();
            addMessage(result.answer, 'assistant');
        } else {
            throw new Error(result.error || 'Ask failed');
        }
    } catch (error) {
        console.error('Ask error:', error);
        removeTypingIndicator();
        addMessage('❌ Lỗi: ' + error.message, 'assistant');
    } finally {
        setUIEnabled(true);
    }
}

function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (role === 'assistant') {
        // Sử dụng innerHTML để hiển thị bold từ CSS
        messageContent.innerHTML = `<strong>🤖 Assistant:</strong> ${content}`; 
    } else {
        messageContent.textContent = content;
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typingIndicator';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        typingContent.appendChild(dot);
    }
    
    // Thêm nội dung vào typingDiv
    typingDiv.appendChild(typingContent); 
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status ${type}`;
}

function setUIEnabled(enabled) {
    isProcessing = !enabled;
    questionInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    fileInput.disabled = !enabled;
    
    if (enabled) {
        questionInput.placeholder = currentSessionId 
            ? "Hỏi về nội dung trong file..." 
            : "Hỏi bất kỳ điều gì...";
    } else {
        questionInput.placeholder = "Đang xử lý...";
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', init);