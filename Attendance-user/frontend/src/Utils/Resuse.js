// import localstorageEncrypt from "localstorage-encrypt";
// import axios from "axios";
// var ip = import.meta.env.BACKEND_HOST || "localhost";
// var host = import.meta.env.BACKEND_PORT || "8000";
// export const LS = localstorageEncrypt.init("Quillbot", "RGBQUILLBOT");
// export const Baseaxios = axios.create({
//   baseURL: `https://${ip}:${host}/`,
//   headers: { Authorization: `Bearer ${LS.get("access_token")}` },
// });

import axios from "axios";
import localstorageEncrypt from "localstorage-encrypt";

// Backend base URL
export const ipadr = import.meta.env.VITE_API_BASE_URL;

// LocalStorage utility with encryption
export const LS = localstorageEncrypt.init("Quillbot", "RGBQUILLBOT");

// Axios instance
export const Baseaxios = axios.create({
  baseURL: ipadr,
  headers: {
    Authorization: `Bearer ${LS.get("access_token")}`,
  },
});

