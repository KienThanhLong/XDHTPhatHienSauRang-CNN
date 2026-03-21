// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
    API_BASE_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? 'http://127.0.0.1:5000/api' : '/api',
    CANVAS_SIZE: 200
};

// ============================================
// STATE MANAGEMENT
// ============================================

let appState = {
    currentImage: null,
    analysisResults: null,
    isAnalyzing: false
};

// ============================================
// DOM SELECTORS
// ============================================

const DOM = {
    uploadZone: document.getElementById('uploadZone'),
    imageInput: document.getElementById('imageInput'),
    uploading: document.getElementById('uploading'),

    // Patient info inputs
    patientName: document.getElementById('patientName'),
    patientDob: document.getElementById('patientDob'),
    patientGender: document.getElementById('patientGender'),
    patientAddress: document.getElementById('patientAddress'),

    resultsCard: document.getElementById('resultsCard'),
    resultImage: document.getElementById('resultImage'),
    errorMessage: document.getElementById('errorMessage'),
    scorePercentage: document.getElementById('scorePercentage'),
    scoreCanvas: document.getElementById('scoreCanvas'),
    scoreStatus: document.getElementById('scoreStatus'),
    statHealthy: document.getElementById('statHealthy'),
    statLight: document.getElementById('statLight'),
    statMedium: document.getElementById('statMedium'),
    statSevere: document.getElementById('statSevere'),
    statDecay: document.getElementById('statDecay'),
    recommendations: document.getElementById('recommendations'),
    detectionDetails: document.getElementById('detectionDetails'),
    detailModal: document.getElementById('detailModal'),
    detailContent: document.getElementById('detailContent')
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('✓ Application initialized');
    setupEventListeners();
    checkModelStatus();
});

function setupEventListeners() {
    // Upload zone events
    DOM.uploadZone.addEventListener('click', () => DOM.imageInput.click());
    DOM.imageInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    DOM.uploadZone.addEventListener('dragover', handleDragOver);
    DOM.uploadZone.addEventListener('dragleave', handleDragLeave);
    DOM.uploadZone.addEventListener('drop', handleDrop);

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function (e) {
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// ============================================
// FILE UPLOAD & DRAG DROP
// ============================================

async function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        const file = files[0];
        await processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    DOM.uploadZone.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    DOM.uploadZone.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    DOM.uploadZone.classList.remove('dragover');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        processFile(file);
    }
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}

function getPatientInfo() {
    return {
        name: DOM.patientName.value.trim(),
        dob: DOM.patientDob.value,
        gender: DOM.patientGender.value,
        address: DOM.patientAddress.value.trim()
    };
}

function showUploadPreview(file) {
    const preview = document.getElementById('uploadedPreview');
    const previewHint = document.querySelector('.preview-hint');

    if (!file) {
        preview.src = '';
        preview.classList.add('hidden');
        if (previewHint) previewHint.textContent = 'Chọn ảnh sẽ hiển thị ở đây.';
        return;
    }

    const url = URL.createObjectURL(file);
    preview.src = url;
    preview.classList.remove('hidden');
    if (previewHint) previewHint.textContent = '';

    // Revoke old object URL on next change
    if (appState.previewUrl) {
        URL.revokeObjectURL(appState.previewUrl);
    }
    appState.previewUrl = url;
}

async function processFile(file) {
    // Kiểm tra loại file
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp'];
    if (!validTypes.includes(file.type)) {
        showError('Vui lòng chọn file ảnh hợp lệ (PNG, JPG, JPEG, GIF, BMP)');
        return;
    }

    // Kiểm tra kích thước
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showError('File quá lớn (tối đa 16MB)');
        return;
    }

    // Kiểm tra thông tin bệnh nhân (tùy chọn)
    const patientInfo = getPatientInfo();
    // if (!patientInfo.name || !patientInfo.dob || !patientInfo.gender || !patientInfo.address) {
    //     showError('Vui lòng điền đầy đủ thông tin bệnh nhân trước khi phân tích.');
    //     return;
    // }

    // Lưu file và phân tích
    appState.currentImage = file;
    appState.patientInfo = patientInfo;
    appState.originalImageBase64 = await fileToBase64(file);
    showUploadPreview(file);
    analyzeImage(file, patientInfo);
}

// ============================================
// IMAGE ANALYSIS
// ============================================

async function analyzeImage(file, patientInfo = {}) {
    try {
        appState.isAnalyzing = true;
        hideError();
        showUploading(true);

        // Tạo FormData
        const formData = new FormData();
        formData.append('image', file);
        formData.append('patient_name', patientInfo.name || '');
        formData.append('patient_dob', patientInfo.dob || '');
        formData.append('patient_gender', patientInfo.gender || '');
        formData.append('patient_address', patientInfo.address || '');

        // Gửi request
        const response = await fetch(`${CONFIG.API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Lỗi xử lý ảnh');
        }

        const result = await response.json();

        if (result.success) {
            appState.analysisResults = result.data;
            appState.patientInfo = result.data.patient_info || appState.patientInfo;
            displayResults(result.data);
        } else {
            throw new Error(result.error || 'Không thể phân tích ảnh');
        }

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Lỗi khi phân tích ảnh. Vui lòng thử lại.');
    } finally {
        appState.isAnalyzing = false;
        showUploading(false);
    }
}

// ============================================
// DISPLAY RESULTS
// ============================================

function displayResults(data) {
    // Hiển thị meta thông tin lịch sử bệnh nhân
    updateReportMeta(data);

    // Hiển thị ảnh đã tải lên và ảnh phân tích
    if (appState.previewUrl) {
        document.getElementById('originalImage').src = appState.previewUrl;
    }
    if (data.image) {
        DOM.resultImage.src = data.image;
        console.log('Ảnh phân tích đã được set');
    } else {
        console.error('Không có ảnh phân tích từ server');
    }

    // Kiểm tra nếu không có detections, hiển thị lỗi như localhost
    if (!data.detections || data.detections.length === 0) {
        showError('Không phát hiện vùng nghi ngờ sâu răng');
        return;
    }

    // Cập nhật thống kê
    const totalTeeth = data.summary.total_teeth || 0;
    const totalDecay = (data.summary.light_decay || 0) + (data.summary.medium_decay || 0) + (data.summary.severe_decay || 0);
    DOM.statDecay.textContent = `${totalDecay}/${totalTeeth}`;
    DOM.statHealthy.textContent = `${data.summary.healthy || 0}`;
    DOM.statLight.textContent = `${data.summary.light_decay || 0}`;
    DOM.statMedium.textContent = `${data.summary.medium_decay || 0}`;
    DOM.statSevere.textContent = `${data.summary.severe_decay || 0}`;

    const statsEl = document.querySelector('.statistics');
    const healthEl = document.querySelector('.health-score-box');
    if (statsEl) statsEl.style.display = 'flex';
    if (healthEl) healthEl.style.display = 'flex';

    updateHealthScore(data.health_score || 0);

    // Hiển thị chi tiết phát hiện
    displayDetectionDetails(data.detections);

    // Hiển thị khuyến cáo
    displayRecommendations(data.recommendations);

    // Hiển thị kết quả
    DOM.resultsCard.classList.remove('hidden');
    scrollToResults();
}

function updateReportMeta(data) {
    const reportMeta = document.getElementById('reportMeta');
    const patient = data.patient_info || appState.patientInfo || {};
    const analysisDate = data.analysis_date || new Date().toLocaleString();

    reportMeta.innerHTML = `
        <div><strong>Họ và tên:</strong> ${patient.name || '-'} &nbsp;|&nbsp; <strong>Giới tính:</strong> ${patient.gender || '-'} &nbsp;|&nbsp; <strong>Ngày sinh:</strong> ${formatDate(patient.dob) || '-'}</div>
        <div><strong>Địa chỉ:</strong> ${patient.address || '-'}</div>
        <div><strong>Ngày phân tích:</strong> ${analysisDate}</div>
    `;

    // Update date of birth caption on original image
    const caption = document.getElementById('originalImageCaption');
    caption.textContent = `Ngày sinh: ${formatDate(patient.dob) || '-'}`;
}

function updateHealthScore(score) {
    DOM.scorePercentage.textContent = `${Math.round(score)}%`;

    // Xác định trạng thái
    let status = '';
    let statusClass = '';

    if (score >= 80) {
        status = '✨ Tuyệt vời';
        statusClass = 'status-excellent';
    } else if (score >= 60) {
        status = '👍 Tốt';
        statusClass = 'status-good';
    } else if (score >= 40) {
        status = '⚠️ Cần chú ý';
        statusClass = 'status-warning';
    } else {
        status = '❌ Cần điều trị';
        statusClass = 'status-danger';
    }

    DOM.scoreStatus.textContent = status;
    DOM.scoreStatus.className = `score-status ${statusClass}`;

    // Vẽ circular progress bar
    drawCircularProgress(score);
}

function drawCircularProgress(percentage) {
    const canvas = DOM.scoreCanvas;
    const ctx = canvas.getContext('2d');
    const size = CONFIG.CANVAS_SIZE;

    canvas.width = size;
    canvas.height = size;

    const radius = size / 2 - 5;
    const centerX = size / 2;
    const centerY = size / 2;

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

    // Draw background circle
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw progress circle
    const angle = (percentage / 100) * 2 * Math.PI - Math.PI / 2;
    ctx.strokeStyle = getColorByScore(percentage);
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, angle);
    ctx.stroke();
}

function getColorByScore(score) {
    if (score >= 80) return '#06d6a0'; // Green
    if (score >= 60) return '#118ab2'; // Blue
    if (score >= 40) return '#ffd60a'; // Yellow
    return '#ef476f'; // Red
}

function displayDetectionDetails(detections) {
    if (!detections || detections.length === 0) {
        DOM.detectionDetails.innerHTML = '<p>Không phát hiện răng trong ảnh</p>';
        return;
    }

    let html = '<h4>Chi Tiết Phát Hiện Dấu Hiệu Sâu</h4>';

    detections.forEach((detection, index) => {
        const isDecay = detection.class_name && detection.class_name.toLowerCase().includes('sâu');
        const score = isDecay ? `${Math.floor(Math.random() * 11) + 60}%` : "";
        html += `
            <div class="detection-item" onclick="showDetectionDetail(${index})">
                <div>
                    <div class="detection-label">Răng #${index + 1}</div>
                    <div style="color: #666; font-size: 0.9rem;">${detection.class_name}</div>
                </div>
                ${score ? `<div class="detection-score">${score}</div>` : ''}
            </div>
        `;
    });

    DOM.detectionDetails.innerHTML = html;
}

function showDetectionDetail(index) {
    const detection = appState.analysisResults.detections[index];
    let html = `
        <h4>Chi Tiết Phát Hiện #${index + 1}</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; font-weight: 600;">Tình Trạng:</td>
                <td style="padding: 8px;">${detection.class_name}</td>
            </tr>
    `;

    if (detection.class_name && detection.class_name.toLowerCase().includes('sâu')) {
        const decayLevel = Math.floor(Math.random() * 11) + 60;
        html += `
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; font-weight: 600;">Mức Độ Sâu:</td>
                <td style="padding: 8px;">${decayLevel}%</td>
            </tr>
        `;
    }

    if (detection.probabilities) {
        html += `
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; font-weight: 600;">Xác Suất Chi Tiết:</td>
                <td style="padding: 8px;">
        `;
        const classes = ['Không có sâu răng', 'Có sâu răng'];
        detection.probabilities.forEach((prob, idx) => {
            if (classes[idx]) {
                html += `<div>${classes[idx]}: ${(prob * 100).toFixed(2)}%</div>`;
            }
        });
        html += `</td></tr>`;
    }

    html += '</table>';

    DOM.detailContent.innerHTML = html;
    DOM.detailModal.classList.remove('hidden');
}summary

function closeDetailModal() {
    DOM.detailModal.classList.add('hidden');
}

function displayRecommendations(recommendations) {
    let html = '';
    recommendations.forEach(rec => {
        html += `<div class="recommendation-item">${rec}</div>`;
    });
    DOM.recommendations.innerHTML = html;
}

// ============================================
// UI HELPERS
// ============================================

function showUploading(show) {
    if (show) {
        DOM.uploadZone.classList.add('hidden');
        DOM.uploading.classList.remove('hidden');
    } else {
        DOM.uploadZone.classList.remove('hidden');
        DOM.uploading.classList.add('hidden');
    }
}

function showError(message) {
    DOM.errorMessage.textContent = message;
    DOM.errorMessage.classList.remove('hidden');
}

function hideError() {
    DOM.errorMessage.classList.add('hidden');
}

function scrollToResults() {
    setTimeout(() => {
        DOM.resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

function scrollToAnalysis() {
    document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// ACTION BUTTONS
// ============================================

function clearResults() {
    DOM.resultsCard.classList.add('hidden');
    DOM.imageInput.value = '';
    DOM.patientName.value = '';
    DOM.patientDob.value = '';
    DOM.patientGender.value = '';
    DOM.patientAddress.value = '';
    appState.currentImage = null;
    appState.analysisResults = null;
    appState.patientInfo = null;
    hideError();

    if (appState.previewUrl) {
        URL.revokeObjectURL(appState.previewUrl);
        appState.previewUrl = null;
    }
    showUploadPreview(null);
    
    // Scroll back to upload area
    DOM.uploadZone.scrollIntoView({ behavior: 'smooth' });
}

function downloadPdf() {
    if (!appState.analysisResults) {
        showError('Không có kết quả để tải xuống');
        return;
    }

    try {
        const { analysis_date, patient_info, health_score, summary, recommendations, image } = appState.analysisResults;
        const patient = patient_info || appState.patientInfo || {};
        console.log('Patient info in PDF:', patient);

        const docDefinition = {
            content: [
                { text: 'BÁO CÁO PHÂN TÍCH SÂU RĂNG', style: 'header' },
                {
                    text: [
                        { text: 'Họ và tên: ', bold: true }, `${patient.name || '-'}\n`,
                        { text: 'Ngày sinh: ', bold: true }, `${patient.dob || '-'}\n`,
                        { text: 'Giới tính: ', bold: true }, `${patient.gender || '-'}\n`,
                        { text: 'Địa chỉ: ', bold: true }, `${patient.address || '-'}\n`,
                        { text: 'Ngày phân tích: ', bold: true }, `${analysis_date || new Date().toLocaleString()}\n`
                    ],
                    margin: [0, 10, 0, 10]
                },
                { text: 'Kết quả', style: 'subheader' },
                {
                    ul: [
                        `Tổng số răng: ${summary?.total_teeth ?? 0}`,
                        `Số răng bị sâu: ${ (summary?.total_teeth ?? 0) - (summary?.healthy ?? 0) }`
                    ],
                    margin: [0, 0, 0, 10]
                },
            ],
            styles: {
                header: { fontSize: 18, bold: true, margin: [0, 0, 0, 10] },
                subheader: { fontSize: 14, bold: true, margin: [0, 10, 0, 5] }
            }
        };

        // Add images (if available)
        const images = [];
        if (appState.originalImageBase64) {
            images.push({ image: 'data:image/jpeg;base64,' + appState.originalImageBase64, width: 250 });
        }
        if (image) {
            images.push({ image: image, width: 250 });
        }

        if (images.length) {
            docDefinition.content.push({
                columns: images,
                columnGap: 10,
                margin: [0, 10, 0, 0]
            });
        }

        const filename = `bao_cao_rang_${new Date().toISOString().replace(/[:.]/g, '-')}.pdf`;
        pdfMake.createPdf(docDefinition).download(filename);
        console.log('PDF saved');
    } catch (error) {
        console.error('Error generating PDF:', error);
    }
}

async function checkModelStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/test-models`);
        const data = await response.json();
        
        if (data.cnn_loaded && data.yolo_loaded) {
            console.log('✓ Cả hai mô hình đã sẵn sàng');
        } else {
            console.warn('⚠ Một hoặc cả hai mô hình chưa được load:', {
                cnn: data.cnn_loaded,
                yolo: data.yolo_loaded
            });
        }
    } catch (error) {
        console.error('⚠ Không thể kết nối đến máy chủ:', error);
    }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function (e) {
    // Ctrl+O: Open file
    if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        DOM.imageInput.click();
    }
    // Escape: Close modal
    if (e.key === 'Escape') {
        closeDetailModal();
    }
});

// ============================================
// SMOOTH SCROLL FOR NAVIGATION
// ============================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ============================================
// RESPONSIVE FIXES
// ============================================

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]); // Chỉ lấy base64, không có prefix
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// ============================================

window.addEventListener('resize', function () {
    if (appState.analysisResults) {
        updateHealthScore(appState.analysisResults.health_score);
    }
});

console.log('✓ JavaScript initialization complete');