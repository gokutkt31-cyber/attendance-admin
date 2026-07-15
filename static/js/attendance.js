// Attendance Features: Webcam photo capture, GPS coordinates retrieval, check-in submission, and QR scanner controller

let webcamStream = null;
let userLatitude = null;
let userLongitude = null;

// Initialize camera feed for selfie validation
async function initWebcam(videoId = 'webcam-feed') {
    const videoEl = document.getElementById(videoId);
    if (!videoEl) return;
    
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' },
            audio: false
        });
        videoEl.srcObject = webcamStream;
    } catch (err) {
        console.error("Camera access error: ", err);
        showToast("Unable to access webcam. Please check permissions.", "danger");
    }
}

// Stop camera feed
function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
}

// Retrieve GPS coordinates
function initGPS() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            showToast("Geolocation is not supported by your browser.", "danger");
            reject("Not supported");
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLatitude = position.coords.latitude;
                userLongitude = position.coords.longitude;
                
                // Display coordinates in UI if elements exist
                const latEl = document.getElementById('gps-lat-val');
                const lngEl = document.getElementById('gps-lng-val');
                if (latEl) latEl.textContent = userLatitude.toFixed(6);
                if (lngEl) lngEl.textContent = userLongitude.toFixed(6);
                
                resolve({ lat: userLatitude, lng: userLongitude });
            },
            (error) => {
                console.error("GPS access error: ", error);
                let msg = "Failed to fetch GPS coordinates. Please enable Location.";
                if (error.code === error.PERMISSION_DENIED) {
                    msg = "Location permission denied. Please allow GPS access to log attendance.";
                }
                showToast(msg, "danger");
                reject(error);
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
}

// Capture photo frame from video and convert to base64 DataURL
function captureSelfie(videoId = 'webcam-feed', canvasId = 'selfie-canvas') {
    const videoEl = document.getElementById(videoId);
    const canvasEl = document.getElementById(canvasId);
    
    if (!videoEl || !canvasEl) return null;
    
    const context = canvasEl.getContext('2d');
    canvasEl.width = videoEl.videoWidth || 640;
    canvasEl.height = videoEl.videoHeight || 480;
    
    // Draw mirrored image if capturing front camera selfie
    context.translate(canvasEl.width, 0);
    context.scale(-1, 1);
    context.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    
    // Convert canvas image frame to base64 data string
    return canvasEl.toDataURL('image/jpeg', 0.85);
}

// Handle Check-In Event
async function triggerCheckIn() {
    const checkInBtn = document.getElementById('checkin-btn');
    if (checkInBtn) checkInBtn.disabled = true;
    
    try {
        // Step 1: Initialize GPS
        showToast("Fetching location...", "info");
        const location = await initGPS();
        
        // Step 2: Capture Webcam Frame
        const selfieData = captureSelfie();
        if (!selfieData) {
            showToast("Camera frame capture failed. Start webcam feed.", "danger");
            if (checkInBtn) checkInBtn.disabled = false;
            return;
        }
        
        // Step 3: Post Check-In Log
        showToast("Verifying check-in...", "info");
        const response = await postData('/attendance/checkin', {
            latitude: location.lat,
            longitude: location.lng,
            selfie: selfieData
        });
        
        if (response.success) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Check-In Registered!',
                    text: response.message,
                    icon: 'success',
                    confirmButtonText: 'Great'
                }).then(() => {
                    location.reload();
                });
            } else {
                alert(response.message);
                location.reload();
            }
        } else {
            showToast(response.message, "danger");
            if (checkInBtn) checkInBtn.disabled = false;
        }
    } catch (err) {
        console.error("Check-in error:", err);
        if (checkInBtn) checkInBtn.disabled = false;
    }
}

// Handle Check-Out Event
async function triggerCheckOut() {
    const checkOutBtn = document.getElementById('checkout-btn');
    if (checkOutBtn) checkOutBtn.disabled = true;
    
    try {
        showToast("Fetching location...", "info");
        const location = await initGPS();
        
        const selfieData = captureSelfie();
        if (!selfieData) {
            showToast("Camera frame capture failed. Start camera.", "danger");
            if (checkOutBtn) checkOutBtn.disabled = false;
            return;
        }
        
        showToast("Verifying check-out...", "info");
        const response = await postData('/attendance/checkout', {
            latitude: location.lat,
            longitude: location.lng,
            selfie: selfieData
        });
        
        if (response.success) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Check-Out Registered!',
                    text: response.message + `\nHours: ${response.working_hours} hrs. Overtime: ${response.overtime} hrs.`,
                    icon: 'success',
                    confirmButtonText: 'Done'
                }).then(() => {
                    location.reload();
                });
            } else {
                alert(response.message);
                location.reload();
            }
        } else {
            showToast(response.message, "danger");
            if (checkOutBtn) checkOutBtn.disabled = false;
        }
    } catch (err) {
        console.error("Check-out error:", err);
        if (checkOutBtn) checkOutBtn.disabled = false;
    }
}

// Setup QR Code Scanner terminal using Html5Qrcode library
let qrScannerInstance = null;

function startQRScanner(containerId = 'qr-reader', statusCallback = null) {
    if (typeof Html5Qrcode === 'undefined') {
        showToast("QR Reader library is not loaded.", "danger");
        return;
    }
    
    const qrContainer = document.getElementById(containerId);
    if (!qrContainer) return;
    
    qrContainer.style.display = 'block';
    
    qrScannerInstance = new Html5Qrcode(containerId);
    qrScannerInstance.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: { width: 250, height: 250 }
        },
        async (decodedText) => {
            // Found QR token - stop scan first
            await stopQRScanner(containerId);
            
            showToast("Decoding QR code...", "info");
            
            try {
                // Post QR scan verification
                const res = await postData('/attendance/qr-checkin', { qr_token: decodedText });
                if (res.success) {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: 'QR Scan Attendance Logged',
                            text: res.message,
                            icon: 'success'
                        });
                    } else {
                        alert(res.message);
                    }
                    if (statusCallback) statusCallback(true);
                } else {
                    showToast(res.message, "danger");
                    if (statusCallback) statusCallback(false);
                }
            } catch (err) {
                showToast("Request failed. Invalid token schema.", "danger");
                if (statusCallback) statusCallback(false);
            }
        },
        (errorMessage) => {
            // parse logs silently during camera sweep
        }
    ).catch((err) => {
        console.error("Unable to start scanning:", err);
        showToast("Failed to initialize scanner. Check camera permissions.", "danger");
    });
}

async function stopQRScanner(containerId = 'qr-reader') {
    if (qrScannerInstance) {
        try {
            await qrScannerInstance.stop();
            qrScannerInstance = null;
            const container = document.getElementById(containerId);
            if (container) container.style.display = 'none';
        } catch (e) {
            console.error("Stop scanner error:", e);
        }
    }
}

// Load dynamic ID QR Code inside element
function renderIDCardQRCode(elementId, tokenText) {
    const qrContainer = document.getElementById(elementId);
    if (!qrContainer || !tokenText) return;
    
    qrContainer.innerHTML = ""; // Clear
    
    if (typeof QRCode !== 'undefined') {
        new QRCode(qrContainer, {
            text: tokenText,
            width: 120,
            height: 120,
            colorDark : "#000000",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H
        });
    } else {
        qrContainer.innerHTML = "<p class='text-muted small'>QR lib failed to load</p>";
    }
}
