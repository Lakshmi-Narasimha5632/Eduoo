import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(undefined);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = async () => {
    try {
      const res = await api.get('/auth/profile/');
      if (res.user) {
        setUser(res.user);
        localStorage.setItem('eduoo_user', JSON.stringify(res.user));
      }
    } catch {
      api.clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const cached = localStorage.getItem('eduoo_user');
    const token = localStorage.getItem('eduoo_access_token');
    if (cached && token) {
      try {
        setUser(JSON.parse(cached));
      } catch {}
    }
    if (token) {
      refreshProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    api.clearTokens();
    const res = await api.post('/auth/login/', { email, password });
    if (res.access && res.user) {
      api.setTokens(res.access, res.refresh);
      setUser(res.user);
      localStorage.setItem('eduoo_user', JSON.stringify(res.user));
    }
  };

  const register = async (data) => {
    api.clearTokens();
    const res = await api.post('/auth/register/', data);
    if (res.access && res.user) {
      api.setTokens(res.access, res.refresh);
      setUser(res.user);
      localStorage.setItem('eduoo_user', JSON.stringify(res.user));
    }
    return res;
  };

  const verifyOtp = async (email, otp) => {
    const res = await api.post('/auth/verify-email/', { email, otp });
    if (res.access && res.user) {
      api.setTokens(res.access, res.refresh);
      setUser(res.user);
      localStorage.setItem('eduoo_user', JSON.stringify(res.user));
    }
    return res;
  };

  const resendOtp = async (email) => {
    return await api.post('/auth/resend-otp/', { email });
  };

  const logout = async () => {
    const refresh = localStorage.getItem('eduoo_refresh_token');
    if (refresh) {
      try {
        await api.post('/auth/logout/', { refresh });
      } catch {}
    }
    api.clearTokens();
    setUser(null);
  };

  const updateProfile = async (data) => {
    const res = await api.put('/auth/profile/', data);
    if (res.user) {
      setUser(res.user);
      localStorage.setItem('eduoo_user', JSON.stringify(res.user));
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verifyOtp, resendOtp, logout, updateProfile, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
