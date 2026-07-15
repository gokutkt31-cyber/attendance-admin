// Main UI Interactions: Dark/Light Mode, Sidebar Toggle, Notification setups, and CSRF AJAX helpers.

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }

    // 2. Dark/Light Theme Handler
    const themeToggleBtn = document.getElementById('theme-toggle');
    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) return savedTheme;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update Toggle Icon
        if (themeToggleBtn) {
            const icon = themeToggleBtn.querySelector('i');
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                themeToggleBtn.title = 'Switch to Light Mode';
            } else {
                icon.className = 'fas fa-moon';
                themeToggleBtn.title = 'Switch to Dark Mode';
            }
        }
    };

    // Apply preferred theme immediately
    setTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }

    // 3. Sidebar Responsive Drawer Toggler
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside of it on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 991 && sidebar.classList.contains('show')) {
                if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // 4. Alert Notifications Handler (SweetAlert2 & Toastify JS)
    // Render Flash Messages from Flask templates using Toastify
    const flashMessages = document.querySelectorAll('.flask-flash-msg');
    flashMessages.forEach(msg => {
        const text = msg.getAttribute('data-message');
        const category = msg.getAttribute('data-category'); // success, danger, warning, info
        
        showToast(text, category);
    });
});

// Toast Notification Helper
function showToast(message, type = 'info') {
    if (typeof Toastify === 'undefined') {
        console.warn('Toastify library not loaded. Falling back to alert.');
        alert(message);
        return;
    }
    
    let background = '#3b82f6'; // Info blue
    if (type === 'success') background = '#10b981'; // Green
    if (type === 'danger') background = '#ef4444'; // Red
    if (type === 'warning') background = '#f59e0b'; // Orange

    Toastify({
        text: message,
        duration: 3500,
        close: true,
        gravity: "top",
        position: "right",
        stopOnFocus: true,
        style: {
            background: background,
            borderRadius: '12px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px 0 rgba(0,0,0,0.1)'
        }
    }).showToast();
}

// CSRF AJAX POST Helper using Fetch API
async function postData(url = '', data = {}) {
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    });
    
    return response.json();
}

// Delete Confirmation Helper via SweetAlert2
function confirmDelete(title, text, confirmButtonText, callback) {
    if (typeof Swal === 'undefined') {
        if (confirm(text)) callback();
        return;
    }
    
    Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#64748b',
        confirmButtonText: confirmButtonText,
        background: document.documentElement.getAttribute('data-theme') === 'dark' ? '#1e1b4b' : '#ffffff',
        color: document.documentElement.getAttribute('data-theme') === 'dark' ? '#f8fafc' : '#1e293b'
    }).then((result) => {
        if (result.isConfirmed) {
            callback();
        }
    });
}
