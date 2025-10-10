// import localstorageEncrypt from "localstorage-encrypt";
// import axios from "axios";
// var ip = import.meta.env.BACKEND_HOST || "localhost";
// var host = import.meta.env.BACKEND_PORT || "8000";
// export const LS = localstorageEncrypt.init("Quillbot", "RGBQUILLBOT");
// export const Baseaxios = axios.create({
//   baseURL: `https://${ip}:${host}/`,
//   headers: { Authorization: `Bearer ${LS.get("access_token")}` },
// });

import localstorageEncrypt from "localstorage-encrypt";
import axios from "axios";

// FORCE HTTPS - Production fix for Mixed Content Error
const envUrl = import.meta.env.VITE_HOST_IP;
const defaultUrl = "https://e-connect-host-production.up.railway.app";

// Ensure HTTPS protocol regardless of environment variable value
export const ipadr = envUrl ? envUrl.replace(/^http:/, "https:") : defaultUrl;

console.log("API Base URL (Production Safe):", ipadr);
console.log("Original Env Value:", envUrl);

export const LS = {
  save: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
  get: (key) => {
    const val = localStorage.getItem(key);
    try {
      return JSON.parse(val);
    } catch {
      return val;
    }
  },
  remove: (key) => localStorage.removeItem(key),
};

export const Baseaxios = axios.create({
  baseURL: `${ipadr}/`,
  headers: { 
    'Content-Type': 'application/json'
  },
  withCredentials: true, // Enable credentials for CORS
});

// Add request interceptor to ensure headers are always fresh
Baseaxios.interceptors.request.use(
  (config) => {
    const token = LS.get("access_token");
    
    // Only add Authorization header if token exists and is not null/undefined
    // Skip auth for login/signup endpoints
    const authExcludedPaths = ['/Gsignin', '/admin_Gsignin', '/signup', '/signin'];
    const isAuthExcluded = authExcludedPaths.some(path => config.url?.includes(path));
    
    if (token && token !== 'null' && token !== 'undefined' && !isAuthExcluded) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      // Remove Authorization header if it was set
      delete config.headers.Authorization;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
Baseaxios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error("API Error:", error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error("Network Error:", error.request);
    } else {
      // Something else happened
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);