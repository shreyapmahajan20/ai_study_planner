import { useEffect, useState } from "react";
import { api } from "../api";

export default function StudyPlanPage() {
  const [subjects, setSubjects] = useState([{ name: "", difficulty: "Medium", priority: "Medium" }]);
  const [syllabusSubjects, setSyllabusSubjects] = useState([]);
  const [hoursPerDay, setHoursPerDay] = useState(4);
  const [numDays, setNumDays] = useState(5);
  const [examContext, setExamContext] = useState("");
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/syllabus/subjects").then(setSyllabusSubjects).catch(() => {});
  }, []);

  function updateSubject(index, field, value) {
    const next = [...subjects];
    next[index][field] = value;
    setSubjects(next);
  }

  function addSubject() {
    setSubjects([...subjects, { name: "", difficulty: "Medium", priority: "Medium" }]);
  }

  function quickAddFromSyllabus(name) {
    // Skip if already added
    if (subjects.some((s) => s.name === name)) return;

    setSubjects((prev) => {
      // If the only row so far is the empty placeholder, replace it instead of stacking
      const isJustPlaceholder = prev.length === 1 && !prev[0].name.trim();
      const base = isJustPlaceholder ? [] : prev;
      return [...base, { name, difficulty: "Medium", priority: "Medium" }];
    });
  }

  function removeSubject(index) {
    if (subjects.length === 1) return;
    setSubjects(subjects.filter((_, i) => i !== index));
  }

  async function handleGenerate() {
    setError(null);
    const validSubjects = subjects.filter((s) => s.name.trim());
    if (validSubjects.length === 0) {
      setError("Add at least one subject before generating a plan.");
      return;
    }

    setLoading(true);
    try {
      const result = await api.post("/planner/generate", {
        subjects: validSubjects,
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

  return (
    <div>
      <header className="mb-6">
        <h1 className="font-bold text-2xl">💡 Study Plan</h1>
        <p className="text-sm text-text2 mt-1">Tell it what you're studying — Gemini builds the schedule.</p>
      </header>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-3">Your subjects</h3>

          {syllabusSubjects.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-text2 mb-2">Quick-add from your uploaded syllabi:</p>
              <div className="flex flex-wrap gap-2">
                {syllabusSubjects.map((name) => {
                  const alreadyAdded = subjects.some((s) => s.name === name);
                  return (
                    <button
                      type="button"
                      key={name}
                      onClick={() => quickAddFromSyllabus(name)}
                      disabled={alreadyAdded}
                      className={`chip border ${
                        alreadyAdded
                          ? "bg-primary/20 border-primary text-text2 cursor-default"
                          : "border-border hover:bg-primary/10 cursor-pointer"
                      }`}
                    >
                      {alreadyAdded ? "✓ " : "+ "}{name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
          {subjects.map((subject, i) => (
            <div key={i} className="flex gap-2 mb-2">
              <input
                className="field-input flex-[2]"
                placeholder="e.g. Data Structures"
                value={subject.name}
                onChange={(e) => updateSubject(i, "name", e.target.value)}
              />
              <select className="field-input flex-1" value={subject.difficulty} onChange={(e) => updateSubject(i, "difficulty", e.target.value)}>
                <option>Easy</option><option>Medium</option><option>Hard</option>
              </select>
              <select className="field-input flex-1" value={subject.priority} onChange={(e) => updateSubject(i, "priority", e.target.value)}>
                <option>Low</option><option>Medium</option><option>High</option>
              </select>
              <button onClick={() => removeSubject(i)} className="px-2 text-text2 hover:text-red-600">✕</button>
            </div>
          ))}
          <button onClick={addSubject} className="text-sm font-semibold mb-4">+ Add another subject</button>

          <label className="field-label">Hours per day</label>
          <input type="number" className="field-input mb-3" min={1} max={12} step={0.5} value={hoursPerDay} onChange={(e) => setHoursPerDay(e.target.value)} />

          <label className="field-label">Number of days</label>
          <input type="number" className="field-input mb-3" min={1} max={14} value={numDays} onChange={(e) => setNumDays(e.target.value)} />

          <label className="field-label">Anything else Gemini should know? (optional)</label>
          <textarea className="field-input mb-4" rows={3} placeholder="e.g. Exam in 10 days, weakest at dynamic programming" value={examContext} onChange={(e) => setExamContext(e.target.value)} />

          <button className="primary-btn w-full" onClick={handleGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate my study plan →"}
          </button>
          {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
        </div>

        <div>
          {!plan ? (
            <div className="glass-card p-6 text-sm text-text2">
              Fill in your subjects and hit Generate — your plan will appear here.
            </div>
          ) : (
            plan.plan.map((day) => (
              <div key={day.day_number} className="day-card">
                <div className="flex items-center mb-3">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-accent3 flex items-center justify-center font-bold text-sm mr-3">
                    {day.day_number}
                  </div>
                  <h4 className="font-bold">Day {day.day_number}</h4>
                </div>
                {day.sessions.map((s, i) => (
                  <div key={i} className="session-row">
                    <div>
                      <p className="font-semibold text-sm">{s.subject}</p>
                      <p className="text-xs text-text2">{s.focus}</p>
                    </div>
                    <p className="text-xs font-mono text-primary whitespace-nowrap ml-3">{s.duration_minutes} min</p>
                  </div>
                ))}
                <div className="mt-3 p-3 bg-accent3/10 border-l-2 border-accent3 rounded text-xs italic text-text2">
                  💡 {day.tip}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}