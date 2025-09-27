import localstorageEncrypt from "localstorage-encrypt";
import axios from "axios";

// Backend host from env
export const ipadr = import.meta.env.VITE_BACKEND_HOST;

// Local storage helper
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

// Axios instance
export const Baseaxios = axios.create({
  baseURL: ipadr,  // Just the host, no port needed
  headers: { Authorization: `Bearer ${LS.get("access_token")}` },
});
