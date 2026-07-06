import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api";

export default function ProfilePage() {
  const { user, updateStoredUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [profileMsg, setProfileMsg] = useState(null);
  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwMsg, setPwMsg] = useState(null);

  async function handleSaveProfile() {
    setProfileMsg(null);
    try {
      await api.put("/profile", { name });
      updateStoredUser({ name });
      setProfileMsg({ type: "success", text: "Profile updated!" });
    } catch (err) {
      setProfileMsg({ type: "error", text: err.message });
    }
  }

  async function handleChangePassword() {
    setPwMsg(null);
    if (newPw !== confirmPw) { setPwMsg({ type: "error", text: "New passwords don't match." }); return; }
    try {
      const result = await api.put("/profile/password", { current_password: currentPw, new_password: newPw });
      setPwMsg({ type: "success", text: result.message });
      setCurrentPw(""); setNewPw(""); setConfirmPw("");
    } catch (err) {
      setPwMsg({ type: "error", text: err.message });
    }
  }

  return (
    <div className="space-y-6 max-w-lg">
      {/* Profile info */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-text1 mb-4">Account details</h3>
        <label className="field-label">Email</label>
        <input className="field-input mb-3 opacity-60 cursor-not-allowed" disabled value={user?.email || ""} />
        <label className="field-label">Full name</label>
        <input className="field-input mb-5" value={name} onChange={(e) => setName(e.target.value)} />
        <button className="primary-btn w-full" onClick={handleSaveProfile}>Save changes</button>
        {profileMsg && (
          <p className={`text-sm mt-2 ${profileMsg.type === "error" ? "text-red-500" : "text-green-600"}`}>{profileMsg.text}</p>
        )}
      </div>

      {/* Change password */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-text1 mb-4">Change password</h3>
        <input className="field-input mb-3" type="password" placeholder="Current password" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} />
        <input className="field-input mb-3" type="password" placeholder="New password (8+ characters)" value={newPw} onChange={(e) => setNewPw(e.target.value)} />
        <input className="field-input mb-5" type="password" placeholder="Confirm new password" value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)} />
        <button className="primary-btn w-full" onClick={handleChangePassword}>Update password</button>
        {pwMsg && (
          <p className={`text-sm mt-2 ${pwMsg.type === "error" ? "text-red-500" : "text-green-600"}`}>{pwMsg.text}</p>
        )}
      </div>
    </div>
  );
}
