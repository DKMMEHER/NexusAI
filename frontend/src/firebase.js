// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, GithubAuthProvider } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBBsYV-7xp3Dbzy4JzWxY74SOYi_-bp7p0",
    authDomain: "gen-lang-client-0250626520.firebaseapp.com",
    projectId: "gen-lang-client-0250626520",
    storageBucket: "gen-lang-client-0250626520.firebasestorage.app",
    messagingSenderId: "962267416185",
    appId: "1:962267416185:web:6b367a4e1cda87dabf76a8",
    measurementId: "G-ZQ561CQ65W"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Initialize Authentication
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

export { auth, googleProvider, githubProvider, analytics };
