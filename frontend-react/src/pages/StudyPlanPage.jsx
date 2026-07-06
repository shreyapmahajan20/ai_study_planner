import { useState } from "react";
import { api } from "../api";

export default function StudyPlanPage() {
  const [subjects, setSubjects] = useState([{ name: "", difficulty: "Medium", priority: "Medium" }]);
  const [hoursPerDay, setHoursPerDay] = useState(4);
  const [numDays, setNumDays] = useState(5);
  const [examContext, setExamContext] = useState("");
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  function updateSubject(i, field, value) {
    const next = [...subjects];
    next[i][field] = value;
    setSubjects(next);
  }

  async function handleGenerate() {
    setError(null);
    const valid = subjects.filter((s) => s.name.trim());
    if (!valid.length) { setError("Add at least one subject."); return; }
    setLoading(true);
    try {
      const result = await api.post("/planner/generate", {
        subjects: valid,
        hours_per_day: Number(hoursPerDay),
        num_days: Number(numDays),
        exam_context: examContext,
      });
      setPlan(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const accentColors = ["#A8D5BA", "#CDB4DB", "#A9DEF9", "#FFD6BA", "#B8F2E6"];

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      {/* Form */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-text1 mb-4">Your subjects</h3>
        {subjects.map((s, i) => (
          <div key={i} className="flex gap-2 mb-2">
            <input className="field-input flex-[2]" placeholder="e.g. Data Structures" value={s.name} onChange={(e) => updateSubject(i, "name", e.target.value)} />
            <select className="field-input flex-1" value={s.difficulty} onChange={(e) => updateSubject(i, "difficulty", e.target.value)}>
              <option>Easy</option><option>Medium</option><option>Hard</option>
            </select>
            <select className="field-input flex-1" value={s.priority} onChange={(e) => updateSubject(i, "priority", e.target.value)}>
              <option>Low</option><option>Medium</option><option>High</option>
            </select>
            <button onClick={() => subjects.length > 1 && setSubjects(subjects.filter((_, j) => j !== i))} className="px-2 text-text2 hover:text-red-500 text-lg leading-none">✕</button>
          </div>
        ))}
        <button onClick={() => setSubjects([...subjects, { name: "", difficulty: "Medium", priority: "Medium" }])} className="text-sm font-semibold text-primary mb-5 hover:underline">
          + Add another subject
        </button>

        <label className="field-label">Hours per day</label>
        <input type="number" className="field-input mb-3" min={1} max={12} step={0.5} value={hoursPerDay} onChange={(e) => setHoursPerDay(e.target.value)} />

        <label className="field-label">Number of days</label>
        <input type="number" className="field-input mb-3" min={1} max={14} value={numDays} onChange={(e) => setNumDays(e.target.value)} />

        <label className="field-label">Anything else Gemini should know? (optional)</label>
        <textarea className="field-input mb-5" rows={3} placeholder="e.g. Exam in 10 days, weakest at dynamic programming" value={examContext} onChange={(e) => setExamContext(e.target.value)} />

        <button className="primary-btn w-full" onClick={handleGenerate} disabled={loading}>
          {loading ? "Generating…" : "Generate my study plan →"}
        </button>
        {error && <p className="text-sm text-red-500 mt-2">{error}</p>}
        {loading && <p className="text-xs text-text2 mt-2">Gemini is building your plan…</p>}
      </div>

      {/* Results */}
      <div>
        {!plan ? (
          <div className="glass-card p-6 text-sm text-text2">
            Fill in your subjects and hit <b>Generate</b> — your plan will appear here.
          </div>
        ) : (
          plan.plan.map((day, di) => (
            <div key={day.day_number} className="glass-card p-5 mb-4">
              <div className="flex items-center mb-3">
                <div className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm mr-3 text-text1"
                  style={{ background: accentColors[di % accentColors.length] }}>
                  {day.day_number}
                </div>
                <h4 className="font-bold text-text1">Day {day.day_number}</h4>
              </div>
              {day.sessions.map((s, i) => (
                <div key={i} className="flex justify-between py-2 border-b border-border last:border-b-0">
                  <div>
                    <p className="font-semibold text-sm text-text1">{s.subject}</p>
                    <p className="text-xs text-text2">{s.focus}</p>
                  </div>
                  <p className="text-xs font-semibold text-text2 whitespace-nowrap ml-3 self-center">{s.duration_minutes} min</p>
                </div>
              ))}
              <div className="mt-3 p-3 rounded-xl bg-[#FFF3B0]/40 text-xs italic text-text2">
                💡 {day.tip}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
