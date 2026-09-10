import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAijj3VMMkKPchhjhnHIZ6aKLXE6f7Gmkc",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "trukly-bb5f5.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "trukly-bb5f5",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "trukly-bb5f5.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "633980188100",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:633980188100:web:c373557766449d9ed32091",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
