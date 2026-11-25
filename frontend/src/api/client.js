/**
 * Centralized API client for Eduoo backend.
 * Handles JWT token injection, token refresh, and standardized error parsing.
 */

const API_BASE = (process.env.REACT_APP_API_URL || 'http://localhost:8000/api').replace(/\/+$/, '');

class ApiClient {
  getAccessToken() {
    return localStorage.getItem('eduoo_access_token');
  }

  getRefreshToken() {
    return localStorage.getItem('eduoo_refresh_token');
  }

  setTokens(access, refresh) {
    localStorage.setItem('eduoo_access_token', access);
    if (refresh) {
      localStorage.setItem('eduoo_refresh_token', refresh);
    }
  }

  clearTokens() {
    localStorage.removeItem('eduoo_access_token');
    localStorage.removeItem('eduoo_refresh_token');
    localStorage.removeItem('eduoo_user');
  }

  async refreshAccessToken() {
    const refresh = this.getRefreshToken();
    if (!refresh) return null;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (res.ok) {
        const data = await res.json();
        const newAccess = data.access;
        this.setTokens(newAccess);
        return newAccess;
      }
    } catch {
      // Refresh failed
    }
    this.clearTokens();
    return null;
  }

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    let token = this.getAccessToken();

    const headers = {
      ...(options.headers || {}),
    };

    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
      delete headers['content-type'];
    } else if (!headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
      response = await fetch(url, {
        ...options,
        headers,
      });
    } catch (networkErr) {
      const isLocalhost = url.includes('localhost') || url.includes('127.0.0.1');
      if (isLocalhost && typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
        const err = new Error(
          'Frontend is configured to connect to localhost:8000. Please set REACT_APP_API_URL in your Vercel Environment Variables (e.g. https://your-backend.onrender.com/api) and redeploy.'
        );
        err.code = 'CONFIG_ERROR';
        throw err;
      }
      const err = new Error(`Unable to connect to backend at ${url}. Please verify your Render service is running.`);
      err.code = 'NETWORK_ERROR';
      throw err;
    }

    // Handle 401 token expiry retry once
    if (response.status === 401 && this.getRefreshToken()) {
      const newToken = await this.refreshAccessToken();
      if (newToken) {
        headers['Authorization'] = `Bearer ${newToken}`;
        response = await fetch(url, {
          ...options,
          headers,
        });
      }
    }

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await response.json() : null;

    if (!response.ok) {
      let extractedMsg = data?.error?.message || data?.detail || data?.message;
      if (!extractedMsg && data?.errors && typeof data.errors === 'object') {
        const firstVal = Object.values(data.errors)[0];
        extractedMsg = Array.isArray(firstVal) ? firstVal[0] : String(firstVal);
      }
      if (!extractedMsg && data?.error && typeof data.error === 'string') {
        extractedMsg = data.error;
      }
      if (!extractedMsg && !isJson) {
        if (response.status === 502 || response.status === 503) {
          extractedMsg = 'Backend server is booting up or spinning down on Render. Please wait 30 seconds and try again.';
        } else if (response.status === 500) {
          extractedMsg = 'Backend database or server error (HTTP 500). Please verify database connection on Render.';
        } else if (response.status === 404) {
          extractedMsg = `API endpoint not found (HTTP 404 at ${url}). Check REACT_APP_API_URL in Vercel settings.`;
        }
      }
      const errorObj = {
        code: data?.error?.code || `HTTP_${response.status}`,
        message:
          extractedMsg ||
          (response.status === 401 ? 'Invalid email/username or password.' : (response.statusText || 'An unexpected error occurred.')),
        details: data?.error?.details || data?.errors,
      };
      throw errorObj;
    }

    return data;
  }

  get(endpoint, headers) {
    return this.request(endpoint, { method: 'GET', headers });
  }

  post(endpoint, body, headers) {
    const isFormData = body instanceof FormData;
    return this.request(endpoint, {
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body),
      headers,
    });
  }

  put(endpoint, body, headers) {
    const isFormData = body instanceof FormData;
    return this.request(endpoint, {
      method: 'PUT',
      body: isFormData ? body : JSON.stringify(body),
      headers,
    });
  }

  patch(endpoint, body, headers) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
      headers,
    });
  }

  delete(endpoint, headers) {
    return this.request(endpoint, { method: 'DELETE', headers });
  }
}

export const api = new ApiClient();
