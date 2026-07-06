import { useEffect, useState } from "react";
import { api } from "../api";

export default function UniversityPage() {
  const [form, setForm] = useState({ country: "", university: "", course: "", semester: "" });
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/academic-profile").then((data) => {
      setForm({ country: data.country || "", university: data.university || "", course: data.course || "", semester: data.semester || "" });
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    setMessage(null);
    try {
      const result = await api.put("/academic-profile", form);
      setMessage({ type: "success", text: result.message });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  }

  if (loading) return <p className="text-sm text-text2">Loading…</p>;

  return (
    <div className="glass-card p-6 max-w-lg">
      <label className="field-label">Country</label>
      <select className="field-input mb-3" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })}>
        <option value="">Select…</option>
        {["India","United States","United Kingdom","Canada","Australia","Other"].map((c) => <option key={c}>{c}</option>)}
      </select>

      <label className="field-label">University / Institution</label>
      <input className="field-input mb-3" placeholder="e.g. DR D Y Patil Institute of Technology" value={form.university} onChange={(e) => setForm({ ...form, university: e.target.value })} />

      <label className="field-label">Course</label>
      <input className="field-input mb-3" placeholder="e.g. Computer Engineering" value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} />

      <label className="field-label">Semester / Year</label>
      <input className="field-input mb-5" placeholder="e.g. TE Sem 5" value={form.semester} onChange={(e) => setForm({ ...form, semester: e.target.value })} />

      <button className="primary-btn w-full" onClick={handleSave}>Save profile</button>
      {message && (
        <p className={`text-sm mt-2 ${message.type === "error" ? "text-red-500" : "text-green-600"}`}>{message.text}</p>
      )}
    </div>
  );
}
