import { useEffect, useState } from "react";
import { api } from "../api";

const accentColors = ["#A8D5BA", "#A9DEF9", "#CDB4DB", "#FFD6BA", "#B8F2E6"];

export default function HistoryPage() {
  const [plans, setPlans] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/planner/history").then((data) => { setPlans(data); setLoading(false); });
  }, []);

  if (loading) return <p className="text-sm text-text2">Loading…</p>;

  if (!plans.length) return (
    <div className="glass-card p-6 text-sm text-text2">You haven't generated any study plans yet.</div>
  );

  return (
    <div className="space-y-3">
      {plans.map((record, ri) => {
        const isOpen = expandedId === record.id;
        const date = new Date(record.created_at).toLocaleString();
        return (
          <div key={record.id} className="glass-card p-4">
            <div className="flex justify-between items-center cursor-pointer" onClick={() => setExpandedId(isOpen ? null : record.id)}>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: accentColors[ri % accentColors.length] }} />
                <p className="font-semibold text-sm text-text1">{date} — {record.num_days} days, {record.hours_per_day}h/day</p>
              </div>
              <span className="text-text2 text-sm">{isOpen ? "▲" : "▼"}</span>
            </div>
            {isOpen && (
              <div className="mt-4 space-y-2">
                {record.plan_json.plan.map((day) => (
                  <div key={day.day_number} className="p-3 rounded-xl bg-[#F8F8F5] border border-border">
                    <p className="font-semibold text-xs text-text1 mb-1">Day {day.day_number}</p>
                    {day.sessions.map((s, i) => (
                      <p key={i} className="text-xs text-text2">— {s.subject}: {s.focus} ({s.duration_minutes} min)</p>
                    ))}
                    <p className="text-xs italic text-text2 mt-1.5">💡 {day.tip}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
