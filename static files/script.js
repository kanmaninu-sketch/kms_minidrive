console.log('Script loaded');

const protectedPages = ['index.html', 'upload.html'];
const currentPage = location.pathname.split('/').pop();

if (protectedPages.includes(currentPage) && !localStorage.getItem('token')) {
  window.location.href = 'login.html';
}
const API_BASE = 'http://13.204.3.189:5000';
const token = localStorage.getItem('token');

// LOGIN
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const status = document.getElementById('status');

  if (!username || !password) {
    status.innerHTML = `<div class="alert alert-danger">Please enter both username and password.</div>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.token) {
      localStorage.setItem('token', data.token);
      status.innerHTML = `<div class="alert alert-success">Login successful — redirecting...</div>`;
      setTimeout(() => window.location.href = 'upload.html', 800);
    } else {
      status.innerHTML = `<div class="alert alert-danger">${data.error || 'Login failed'}</div>`;
    }
  } catch (err) {
    status.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
  }
});

// SIGNUP
document.getElementById('signupForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const status = document.getElementById('status');

  if (!username || !password) {
    status.innerHTML = `<div class="alert alert-danger">Please enter both username and password.</div>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      status.innerHTML = `<div class="alert alert-success">Signup successful — you can now login.</div>`;
    } else {
      status.innerHTML = `<div class="alert alert-danger">${data.error || 'Signup failed'}</div>`;
    }
  } catch (err) {
    status.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
  }
});

// UPLOAD
document.getElementById('uploadForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('fileInput');
  const status = document.getElementById('uploadStatus');

  const file = fileInput.files[0];

  if (!file) {
    status.innerHTML = `<div class="alert alert-danger">Please select a file to upload.</div>`;
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      status.innerHTML = `<div class="alert alert-success">File uploaded successfully.</div>`;
      loadFiles();
    } else {
      status.innerHTML = `<div class="alert alert-danger">${data.error || 'Upload failed'}</div>`;
    }
  } catch (err) {
    status.innerHTML = `<div class="alert alert-danger">Network error: ${err.message}</div>`;
  }
});

// LOAD FILES
async function loadFiles() {
  const token = localStorage.getItem('token');

  try {
    const res = await fetch('http://13.204.3.189:5000/files', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    console.log('🔍 Backend response:', data);

    const files = Array.isArray(data?.files) ? data.files : null;
    if (!files) throw new Error('Invalid response format');

    const list = document.getElementById('fileList');
    if (!list) throw new Error('Missing #fileList element');
    list.innerHTML = '';

    files.forEach(file => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.innerHTML = `
        <div class="file-meta">
          <div class="file-name fw-bold">${file.filename}</div>
          <div class="file-time text-muted">${file.uploaded}</div>
        </div>
        <div class="file-actions">
          <button class="btn btn-success btn-sm download-btn" data-filename="${file.filename}">Download</button>
          <button class="btn btn-danger btn-sm delete-btn" data-filename="${file.filename}">Delete</button>
          <button class="btn btn-secondary btn-sm share-btn" data-filename="${file.filename}">Share</button>
        </div>
      `;
      list.appendChild(li);
    });

    // ✅ Attach event listeners after rendering
    document.querySelectorAll('.download-btn').forEach(btn => {
      btn.addEventListener('click', () => downloadFile(btn.dataset.filename));
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', () => deleteFile(btn.dataset.filename));
    });

    document.querySelectorAll('.share-btn').forEach(btn => {
      btn.addEventListener('click', () => shareFile(btn.dataset.filename));
    });

  } catch (err) {
    console.error('Error loading files:', err);
    const status = document.getElementById('status');
    if (status) status.textContent = 'Failed to load files. Please check your login or token.';
  }
}

// SEARCH FILTER
document.getElementById('searchInput')?.addEventListener('input', function () {
  const query = this.value.trim().toLowerCase();
  const items = document.querySelectorAll('#fileList .list-group-item');

  items.forEach(item => {
    const name = item.querySelector('.file-name')?.textContent.toLowerCase() || '';
    item.style.display = name.includes(query) ? 'flex' : 'none';
  });
});

// REFRESH BUTTON
document.getElementById('refreshBtn')?.addEventListener('click', () => {
  document.getElementById('searchInput').value = '';
  loadFiles();
});
// LOGOUT BUTTON
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  localStorage.removeItem('token');   // clear JWT
  window.location.href = 'login.html'; // redirect to login page
});

// INITIAL LOAD
loadFiles();
// DOWNLOAD
async function downloadFile(filename) {
  try {
    const res = await fetch(`${API_BASE}/download/${filename}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      alert(data.error || 'Download failed.');
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert('Network error: ' + err.message);
  }
}

// SHARE
async function shareFile(filename) {
  try {
    const res = await fetch(`${API_BASE}/share/${filename}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json().catch(() => ({}));

    if (res.ok && data.share_url) {
      // ✅ Put link into modal textbox
      const input = document.getElementById('shareLinkInput');
input.value = data.share_url;

const copyBtn = document.getElementById('copyBtn');
copyBtn.onclick = () => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(data.share_url)
      .then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => (copyBtn.textContent = 'Copy Again'), 1500);
      })
      .catch(() => {
        input.select();
        alert("⚠️ Clipboard not supported. Please copy manually.");
      });
  } else {
    input.select();
    alert("⚠️ Clipboard not supported. Please copy manually.");
  }
};

const modal = new bootstrap.Modal(document.getElementById('shareModal'));
modal.show();
    } else {
      alert(data.error || 'Failed to generate share link.');
    }
  } catch (err) {
    alert('Network error: ' + err.message);
  }
}

// DELETE
async function deleteFile(filename) {
  try {
    const res = await fetch(`${API_BASE}/delete/${filename}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      alert('File deleted.');
      loadFiles();
    } else {
      alert(data.error || 'Delete failed.');
    }
  } catch (err) {
    alert('Network error: ' + err.message);
  }
}


// Auto-load files on page load
if (document.getElementById('fileList')) {
  loadFiles();
}
