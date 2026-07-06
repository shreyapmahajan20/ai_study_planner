import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Brain } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api";

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const resetToken = searchParams.get("reset_token");
  const [tab, setTab] = useState(resetToken ? "reset" : "login");
  const [message, setMessage] = useState(null);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const tabs = resetToken ? [] : [
    { key: "login",  label: "Log In" },
    { key: "signup", label: "Sign Up" },
    { key: "forgot", label: "Forgot Password" },
  ];

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-accent3 flex items-center justify-center mx-auto mb-3">
            <Brain size={22} color="#1F2937" />
          </div>
          <h1 className="font-bold text-xl text-text1">AI Study Planner</h1>
          <p className="text-sm text-text2 mt-1">Sign in to build and save your study plans</p>
        </div>

        <div className="glass-card p-6">
          {/* Tabs */}
          {tabs.length > 0 && (
            <div className="flex gap-2 mb-6">
              {tabs.map((t) => (
                <button
                  key={t.key}
                  onClick={() => { setTab(t.key); setMessage(null); }}
                  className={`px-4 py-2 rounded-xl font-semibold text-xs transition-colors border-0 cursor-pointer ${
                    tab === t.key ? "bg-primary text-text1" : "text-text2 hover:bg-border"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          )}

          {/* Message */}
          {message && (
            <div className={`text-sm px-3 py-2 rounded-lg mb-4 ${
              message.type === "error"
                ? "bg-red-50 text-red-600 border border-red-100"
                : "bg-green-50 text-green-700 border border-green-100"
            }`}>
              {message.text}
            </div>
          )}

          {tab === "login"  && <LoginForm  login={login}   onSuccess={() => navigate("/dashboard")} setMessage={setMessage} />}
          {tab === "signup" && <SignupForm signup={signup} onSuccess={() => navigate("/dashboard")} setMessage={setMessage} />}
          {tab === "forgot" && <ForgotForm setMessage={setMessage} />}
          {tab === "reset"  && <ResetForm  token={resetToken} setMessage={setMessage} onSuccess={() => setTimeout(() => navigate("/login"), 1800)} />}
        </div>
      </div>
    </div>
  );
}

function LoginForm({ login, onSuccess, setMessage }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage(null);
    setLoading(true);
    try {
      await login(email, password);
      onSuccess();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input className="field-input" type="email" placeholder="Email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className="field-input" type="password" placeholder="Password" required value={password} onChange={(e) => setPassword(e.target.value)} />
      <button className="primary-btn w-full mt-1" disabled={loading}>{loading ? "Logging in…" : "Log in"}</button>
    </form>
  );
}

function SignupForm({ signup, onSuccess, setMessage }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage(null);
    if (password !== confirm) { setMessage({ type: "error", text: "Passwords don't match." }); return; }
    setLoading(true);
    try {
      await signup(name, email, password);
      onSuccess();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input className="field-input" placeholder="Full name" required value={name} onChange={(e) => setName(e.target.value)} />
      <input className="field-input" type="email" placeholder="Email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className="field-input" type="password" placeholder="Password (8+ characters)" required value={password} onChange={(e) => setPassword(e.target.value)} />
      <input className="field-input" type="password" placeholder="Confirm password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
      <button className="primary-btn w-full mt-1" disabled={loading}>{loading ? "Creating account…" : "Create account"}</button>
    </form>
  );
}

function ForgotForm({ setMessage }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await api.post("/auth/forgot-password", { email });
      setMessage({ type: "success", text: result.message });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <p className="text-sm text-text2">Enter your email and we'll send a reset link.</p>
      <input className="field-input" type="email" placeholder="Email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      <button className="primary-btn w-full" disabled={loading}>{loading ? "Sending…" : "Send reset link"}</button>
    </form>
  );
}

function ResetForm({ token, setMessage, onSuccess }) {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (password !== confirm) { setMessage({ type: "error", text: "Passwords don't match." }); return; }
    setLoading(true);
    try {
      const result = await api.post("/auth/reset-password", { token, new_password: password });
      setMessage({ type: "success", text: `${result.message} Redirecting…` });
      onSuccess();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <p className="text-sm text-text2">Set a new password for your account.</p>
      <input className="field-input" type="password" placeholder="New password (8+ characters)" required value={password} onChange={(e) => setPassword(e.target.value)} />
      <input className="field-input" type="password" placeholder="Confirm new password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
      <button className="primary-btn w-full" disabled={loading}>{loading ? "Resetting…" : "Reset password"}</button>
    </form>
  );
}
