document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup toggle forms
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const linkShowRegister = document.getElementById('link-show-register');
    const linkShowLogin = document.getElementById('link-show-login');

    linkShowRegister.addEventListener('click', (e) => {
        e.preventDefault();
        clearAllErrors();
        formLogin.classList.add('hidden');
        formRegister.classList.remove('hidden');
    });

    linkShowLogin.addEventListener('click', (e) => {
        e.preventDefault();
        clearAllErrors();
        formRegister.classList.add('hidden');
        formLogin.classList.remove('hidden');
    });

    // 2. Setup Form Submissions
    formLogin.addEventListener('submit', handleLoginSubmit);
    formRegister.addEventListener('submit', handleRegisterSubmit);

    // Initialize icons
    lucide.createIcons();
});

// Toast Notifications helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-triangle';

    toast.innerHTML = `
        <i data-lucide="${icon}"></i>
        <span class="toast-msg">${message}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Clear Validation Errors
function clearAllErrors() {
    document.querySelectorAll('.inline-error').forEach(el => el.innerText = '');
}

// Inline error setter
function setError(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

// Email validator helper
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Handle Login API request
async function handleLoginSubmit(e) {
    e.preventDefault();
    clearAllErrors();

    const usernameVal = document.getElementById('login-username').value.trim();
    const passwordVal = document.getElementById('login-password').value;

    let hasErrors = false;

    if (!usernameVal) {
        setError('error-login-username', 'Username is required.');
        hasErrors = true;
    }
    if (!passwordVal) {
        setError('error-login-password', 'Password is required.');
        hasErrors = true;
    }

    if (hasErrors) return;

    const btn = document.getElementById('btn-login-submit');
    btn.disabled = true;
    btn.querySelector('span').innerText = 'Verifying Creds...';

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: usernameVal, password: passwordVal })
        });

        const data = await response.json();

        if (response.ok) {
            // Save Token
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_username', data.username);
            localStorage.setItem('auth_fullname', data.fullname);
            
            showToast("Login authorized. Initializing Dashboard...", "success");
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            showToast(data.detail || "Authentication failed. Try again.", "error");
            setError('error-login-username', data.detail || "Invalid login credentials.");
        }
    } catch (err) {
        showToast("Server connection error during login.", "error");
    } finally {
        btn.disabled = false;
        btn.querySelector('span').innerText = 'Login Session';
    }
}

// Handle Registration API request
async function handleRegisterSubmit(e) {
    e.preventDefault();
    clearAllErrors();

    const fullname = document.getElementById('reg-fullname').value.trim();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;

    let hasErrors = false;

    if (!fullname) {
        setError('error-reg-fullname', 'Full Name is required.');
        hasErrors = true;
    }
    if (!username) {
        setError('error-reg-username', 'Username is required.');
        hasErrors = true;
    } else if (username.length < 3) {
        setError('error-reg-username', 'Username must be at least 3 characters.');
        hasErrors = true;
    }
    if (!email) {
        setError('error-reg-email', 'Email Address is required.');
        hasErrors = true;
    } else if (!isValidEmail(email)) {
        setError('error-reg-email', 'Enter a valid email structure.');
        hasErrors = true;
    }
    if (!password) {
        setError('error-reg-password', 'Password is required.');
        hasErrors = true;
    } else if (password.length < 8) {
        setError('error-reg-password', 'Password must be at least 8 characters.');
        hasErrors = true;
    }
    if (!confirm) {
        setError('error-reg-confirm', 'Please re-type password.');
        hasErrors = true;
    } else if (password !== confirm) {
        setError('error-reg-confirm', 'Passwords do not match.');
        hasErrors = true;
    }

    if (hasErrors) return;

    const btn = document.getElementById('btn-register-submit');
    btn.disabled = true;
    btn.querySelector('span').innerText = 'Creating Profile...';

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fullname: fullname,
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Save Token issued directly on register
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_username', data.username);
            localStorage.setItem('auth_fullname', data.fullname);
            
            showToast("Candidate registered successfully! Opening dashboard...", "success");
            
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            showToast(data.detail || "Registration failed.", "error");
            if (data.detail && data.detail.toLowerCase().includes("username")) {
                setError('error-reg-username', data.detail);
            } else if (data.detail && data.detail.toLowerCase().includes("email")) {
                setError('error-reg-email', data.detail);
            }
        }
    } catch (err) {
        showToast("Server connection error during registration.", "error");
    } finally {
        btn.disabled = false;
        btn.querySelector('span').innerText = 'Register Candidate';
    }
}
