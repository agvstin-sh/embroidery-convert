document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const filenameDisplay = document.getElementById('filenameDisplay');
    const removeBtn = document.getElementById('removeBtn');
    const convertBtn = document.getElementById('convertBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const formatSelect = document.getElementById('formatSelect');
    const statusMessage = document.getElementById('statusMessage');

    // Layout elements
    const mainLayout = document.getElementById('mainLayout');
    const container = document.querySelector('.container');

    let currentFile = null;

    // Drag and Drop Events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    // --- State for Units ---
    let currentStats = null;
    let isMetric = true;

    // Unit Toggle Logic
    const unitToggle = document.getElementById('unitToggle');
    const unitToggleContainer = document.getElementById('unitToggleContainer');

    if (unitToggle) {
        unitToggle.addEventListener('change', () => {
            isMetric = !unitToggle.checked;
            updateStatsDisplay();
        });
    }

    // Handle File Selection
    function handleFileSelect(file) {
        // Basic validation usually done by accept attribute, but consistent UX here
        currentFile = file;
        filenameDisplay.textContent = file.name;

        // UI Updates
        dropZone.classList.add('hidden');
        mainLayout.classList.remove('hidden');
        container.classList.add('expanded');

        // Reset specific hidden states inside if needed
        convertBtn.disabled = false;
        downloadBtn.classList.add('hidden');
        statusMessage.textContent = '';
        statusMessage.className = 'status-message';

        loadPreview(file);
    }

    async function loadPreview(file) {
        const previewContainer = document.getElementById('previewContainer');
        const previewCanvas = document.getElementById('previewCanvas');
        const previewLoader = document.getElementById('previewLoader');
        const statsGrid = document.getElementById('statsGrid');

        previewContainer.classList.remove('hidden');
        previewCanvas.classList.add('hidden');
        statsGrid.classList.add('hidden');
        previewLoader.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/preview', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                currentStats = data.stats;

                if (data.mode === 'vector' && data.pattern) {
                    drawPattern(data.pattern, data.bounds, previewCanvas);
                } else if (data.image) {
                    // Fallback for image-based (though we removed it from backend)
                    // Implementation skipped as we moved to vector
                }

                // Update Stats
                updateStatsDisplay();

                previewCanvas.classList.remove('hidden');
                statsGrid.classList.remove('hidden');
                if (unitToggleContainer) unitToggleContainer.classList.remove('hidden');
                previewLoader.classList.add('hidden');

            } else {
                previewContainer.classList.add('hidden'); // Hide if fail
            }
        } catch (e) {
            console.error(e);
            previewContainer.classList.add('hidden');
        }
    }

    function drawPattern(pattern, bounds, canvas) {
        if (!pattern || !bounds) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        ctx.clearRect(0, 0, width, height);

        // Calculate scale to fit
        const [minX, minY, maxX, maxY] = bounds;
        const patternWidth = maxX - minX;
        const patternHeight = maxY - minY;

        if (patternWidth === 0 || patternHeight === 0) return;

        // Add 10% padding
        const scaleX = (width * 0.9) / patternWidth;
        const scaleY = (height * 0.9) / patternHeight;
        const scale = Math.min(scaleX, scaleY);

        // Center the design
        const centerX = width / 2;
        const centerY = height / 2;
        const pCenterX = (minX + maxX) / 2;
        const pCenterY = (minY + maxY) / 2;

        const offsetX = centerX - (pCenterX * scale);
        const offsetY = centerY - (pCenterY * scale);

        ctx.lineWidth = 1;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // Draw each color block
        // Assuming pattern is array of objects { color: "#hex", stitches: [[x,y],...] }
        for (const block of pattern) {
            ctx.strokeStyle = block.color;
            ctx.beginPath();

            const stitches = block.stitches;
            if (stitches.length > 0) {
                const startStitch = stitches[0];
                ctx.moveTo(startStitch[0] * scale + offsetX, startStitch[1] * scale + offsetY);

                for (let i = 1; i < stitches.length; i++) {
                    const s = stitches[i];
                    ctx.lineTo(s[0] * scale + offsetX, s[1] * scale + offsetY);
                }
            }
            ctx.stroke();
        }
    }

    // Remove File
    removeBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = ''; // Reset input

        // UI Updates
        dropZone.classList.remove('hidden');
        mainLayout.classList.add('hidden');
        container.classList.remove('expanded');

        // Clear canvas
        const canvas = document.getElementById('previewCanvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        convertBtn.disabled = true;
        downloadBtn.classList.add('hidden');
        statusMessage.textContent = '';
    });

    // Convert Button
    convertBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const targetFormat = formatSelect.value;
        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('format', targetFormat);

        // UI Loading State
        // UI Loading State
        convertBtn.disabled = true;
        convertBtn.querySelector('span').textContent = translations[currentLang]['converting-btn'] || 'Converting...';
        convertBtn.querySelector('.loader').classList.remove('hidden');
        downloadBtn.classList.add('hidden');

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Conversion failed');
            }

            // Handle file download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);

            // Try to get filename from headers or generate one
            const contentDisposition = response.headers.get('Content-Disposition');
            let fileName = 'converted.' + targetFormat;
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?/);
                if (match && match[1]) fileName = match[1];
            } else {
                // Fallback name generation
                const originalName = currentFile.name.split('.')[0];
                fileName = `${originalName}.${targetFormat}`;
            }

            // Setup Download Button
            downloadBtn.href = downloadUrl;
            downloadBtn.download = fileName;
            downloadBtn.classList.remove('hidden');

            statusMessage.textContent = translations[currentLang]['status-success'] || 'Conversion successful! Ready to download.';
            statusMessage.className = 'status-message status-success';

        } catch (error) {
            statusMessage.textContent = error.message;
            statusMessage.className = 'status-message status-error';
            convertBtn.querySelector('span').textContent = translations[currentLang]['retry-btn'] || 'Try Again';
        } finally {
            // Reset Button State
            convertBtn.disabled = false;
            if (!statusMessage.className.includes('status-error')) {
                convertBtn.querySelector('span').textContent = translations[currentLang]['convert-btn'] || 'Convert File';
            }
            convertBtn.querySelector('.loader').classList.add('hidden');
        }
    });

    function updateStatsDisplay() {
        if (!currentStats) return;

        document.getElementById('statStitches').textContent = currentStats.stitches.toLocaleString();
        document.getElementById('statColors').textContent = currentStats.colors;

        if (isMetric) {
            document.getElementById('statWidth').textContent = `${currentStats.width.toFixed(1)} mm`;
            document.getElementById('statHeight').textContent = `${currentStats.height.toFixed(1)} mm`;
        } else {
            // Convert to inches
            const widthIn = currentStats.width / 25.4;
            const heightIn = currentStats.height / 25.4;
            document.getElementById('statWidth').textContent = `${widthIn.toFixed(2)} in`;
            document.getElementById('statHeight').textContent = `${heightIn.toFixed(2)} in`;
        }
    }

    function updateStatsDisplay() {
        if (!currentStats) return;

        document.getElementById('statStitches').textContent = currentStats.stitches.toLocaleString();
        document.getElementById('statColors').textContent = currentStats.colors;

        if (isMetric) {
            document.getElementById('statWidth').textContent = `${currentStats.width.toFixed(1)} mm`;
            document.getElementById('statHeight').textContent = `${currentStats.height.toFixed(1)} mm`;
        } else {
            // Convert to inches
            const widthIn = currentStats.width / 25.4;
            const heightIn = currentStats.height / 25.4;
            document.getElementById('statWidth').textContent = `${widthIn.toFixed(2)} in`;
            document.getElementById('statHeight').textContent = `${heightIn.toFixed(2)} in`;
        }
    }

    // --- Internationalization (i18n) ---
    const translations = {
        'en': {
            'header-subtitle': 'Transform your embroidery designs instantly.',
            'dropzone-title': 'Drag & Drop your file here',
            'dropzone-subtitle': 'or click to browse (.pes, .dst, .jef, .exp, etc.)',
            'convert-label': 'Convert to:',
            'convert-btn': 'Convert File',
            'download-btn': 'Download Converted File',
            'retry-btn': 'Try Again',
            'converting-btn': 'Converting...',
            'footer': 'Powered by',
            'status-success': 'Conversion successful! Ready to download.',
            'status-fail': 'Conversion failed',
            'color-warning': 'Note: DST/EXP formats save stitch data perfectly, but colors may look different on your machine (it uses default palettes). This is normal!',
            'preview-label': 'Design Preview:',
            'stat-stitches': 'Stitches',
            'stat-colors': 'Colors',
            'stat-width': 'Width',
            'stat-height': 'Height'
        },
        'es': {
            'header-subtitle': 'Transforma tus diseños de bordado al instante.',
            'dropzone-title': 'Arrastra y suelta tu archivo aquí',
            'dropzone-subtitle': 'o haz clic para buscar (.pes, .dst, .jef, .exp, etc.)',
            'convert-label': 'Convertir a:',
            'convert-btn': 'Convertir Archivo',
            'download-btn': 'Descargar Archivo Convertido',
            'retry-btn': 'Intentar de Nuevo',
            'converting-btn': 'Convirtiendo...',
            'footer': 'Impulsado por',
            'status-success': '¡Conversión exitosa! Listo para descargar.',
            'status-fail': 'La conversión falló',
            'color-warning': 'Nota: Los formatos DST/EXP guardan las puntadas perfectamente, pero los colores pueden verse distintos en tu máquina. ¡Es normal!',
            'preview-label': 'Vista Previa del Diseño:',
            'stat-stitches': 'Puntadas',
            'stat-colors': 'Colores',
            'stat-width': 'Ancho',
            'stat-height': 'Alto'
        }
    };

    let currentLang = 'en';

    function detectLanguage() {
        const userLang = navigator.language || navigator.userLanguage;
        if (userLang.startsWith('es')) {
            currentLang = 'es';
        } else {
            currentLang = 'en';
        }
        applyTranslations();
    }

    function applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[currentLang][key]) {
                element.textContent = translations[currentLang][key];
            }
        });
    }

    // Initialize Language
    detectLanguage();

    // Format Selection Change
    const colorWarning = document.getElementById('colorWarning');

    formatSelect.addEventListener('change', () => {
        checkFormatWarning();
    });

    function checkFormatWarning() {
        if (formatSelect.value === 'dst' || formatSelect.value === 'exp') {
            colorWarning.classList.remove('hidden');
        } else {
            colorWarning.classList.add('hidden');
        }
    }

    // Check initially
    checkFormatWarning();
});
