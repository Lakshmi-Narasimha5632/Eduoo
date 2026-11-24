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

    let response = await fetch(url, {
      ...options,
      headers,
    });

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
