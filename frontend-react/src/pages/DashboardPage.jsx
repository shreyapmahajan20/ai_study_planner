import { useEffect, useState } from "react";
import { Flame, Target, Clock, CheckCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [topicsCount, setTopicsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [planHistory, subjectList] = await Promise.all([
          api.get("/planner/history"),
          api.get("/syllabus/subjects"),
        ]);
        setPlans(planHistory);
        setSubjects(subjectList);
        const topicData = await Promise.all(
          subjectList.map((s) => api.get(`/syllabus/${encodeURIComponent(s)}`))
        );
        setTopicsCount(topicData.reduce((sum, s) => sum + s.topics.length, 0));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const totalHours = plans.reduce((sum, p) => sum + p.hours_per_day * p.num_days, 0);
  const mostRecentPlan = plans[0];
  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div>
      {/* KPI Cards */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <KpiCard icon={Flame}       value={loading ? "…" : `${plans.length}`}    label="Plans generated"      from="from-primary"    to="to-accent3"    delay="stagger-1" />
        <KpiCard icon={Target}      value={loading ? "…" : `${subjects.length}`} label="Subjects uploaded"    from="from-secondary"  to="to-accent1"    delay="stagger-2" />
        <KpiCard icon={Clock}       value={loading ? "…" : `${totalHours}h`}     label="Total planned hours"  from="from-accent2"    to="to-accent4"    delay="stagger-3" />
        <KpiCard icon={CheckCircle} value={loading ? "…" : `${topicsCount}`}     label="Topics extracted"     from="from-accent1"    to="to-secondary"  delay="stagger-4" />
      </section>

      {/* Schedule + Exams row */}
      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <h2 className="font-bold text-text1 mb-4">Today's Schedule</h2>
          {!mostRecentPlan ? (
            <div className="glass-card p-5 text-sm text-text2">
              No plans yet — head to <b>Study Plan</b> to generate one.
            </div>
          ) : (
            <div className="space-y-3">
              {mostRecentPlan.plan_json.plan.slice(0, 3).map((day, di) => {
                const colors = ["#A8D5BA", "#CDB4DB", "#A9DEF9"];
                const chipBg = ["bg-[#A9DEF9]/25", "bg-[#B8F2E6]/30", "bg-[#FFF3B0]/40"];
                const s = day.sessions[0];
                if (!s) return null;
                return (
                  <div key={di} className="glass-card p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-1 h-12 rounded-full" style={{ background: colors[di % 3] }} />
                      <div>
                        <p className="font-semibold text-sm text-text1">{s.subject}</p>
                        <p className="text-xs text-text2 mt-0.5">{s.focus}</p>
                        <div className="flex gap-2 mt-1.5">
                          <span className={`chip ${chipBg[di % 3]} text-text2`}>{s.duration_minutes} min</span>
                          <span className="chip bg-[#FFD6BA]/35 text-text2">Day {day.day_number}</span>
                        </div>
                      </div>
                    </div>
                    <button className="px-4 py-2 rounded-xl font-semibold text-xs bg-primary/20 text-text1 hover:bg-primary transition-colors">
                      Start
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Upcoming exams placeholder */}
        <div>
          <h2 className="font-bold text-text1 mb-4">Upcoming Exams</h2>
          <div className="space-y-3">
            {subjects.slice(0, 2).map((subject, i) => (
              <div key={i} className="glass-card p-4">
                <p className="font-semibold text-sm text-text1">{subject}</p>
                <p className="text-xs text-text2 mt-1">Add exam date in Exam Planner</p>
                <div className="flex items-center gap-2 mt-3">
                  <div className="flex-1 h-2 rounded-full bg-[#EAEAEA]">
                    <div className="h-2 rounded-full bg-primary" style={{ width: `${40 + i * 30}%` }} />
                  </div>
                  <span className="text-xs font-semibold text-text2">{40 + i * 30}%</span>
                </div>
              </div>
            ))}
            {subjects.length === 0 && (
              <div className="glass-card p-4 text-sm text-text2">Upload a syllabus to track exam readiness.</div>
            )}
          </div>
        </div>
      </div>

      {/* Analytics mini */}
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="glass-card p-5">
          <h2 className="font-bold text-text1 mb-4">Analytics</h2>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <MiniStat value={`${totalHours}h`}        label="Total hours"    bg="bg-[#A8D5BA]/20" />
            <MiniStat value={`${plans.length}`}        label="Plans made"     bg="bg-[#A9DEF9]/20" />
            <MiniStat value={`${subjects.length}`}     label="Subjects"       bg="bg-[#CDB4DB]/20" />
            <MiniStat value={`${topicsCount}`}         label="Topics"         bg="bg-[#FFD6BA]/20" />
          </div>
          {/* Mini bar chart */}
          <p className="text-[10px] font-medium text-text2 mb-2">Weekly Study Hours</p>
          <div className="flex items-end gap-1.5 h-16">
            {["#A8D5BA","#A9DEF9","#CDB4DB","#FFD6BA","#B8F2E6","#FFF3B0","#A8D5BA"].map((c, i) => (
              <div key={i} className="flex-1 rounded-t-md" style={{ background: c, height: `${[60,80,45,90,70,55,75][i]}%` }} />
            ))}
          </div>
          <div className="flex gap-1.5 mt-1 text-[9px] text-text2">
            {["M","T","W","T","F","S","S"].map((d, i) => (
              <span key={i} className="flex-1 text-center">{d}</span>
            ))}
          </div>
        </div>

        <div className="glass-card p-5">
          <h2 className="font-bold text-text1 mb-4">Daily Motivation</h2>
          <div className="p-4 rounded-xl bg-[#FFF3B0]/40 mb-4">
            <p className="text-xs italic text-center text-text2">
              "The secret of getting ahead is getting started." — Mark Twain
            </p>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-2.5 rounded-xl bg-[#A8D5BA]/20">
              <p className="font-bold text-sm text-text1">{plans.length * 10} XP</p>
              <p className="text-[10px] text-text2">XP Earned</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#CDB4DB]/20">
              <p className="font-bold text-sm text-text1">{Math.min(plans.length, 5)}</p>
              <p className="text-[10px] text-text2">Badges</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#A9DEF9]/20">
              <p className="font-bold text-sm text-text1">{subjects.length}</p>
              <p className="text-[10px] text-text2">Challenges</p>
            </div>
          </div>
        </div>

        <div className="glass-card p-5">
          <h2 className="font-bold text-text1 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {[
              { label: "Generate a new study plan", color: "#A8D5BA", href: "/study-plan" },
              { label: "Upload a syllabus",          color: "#A9DEF9", href: "/subjects" },
              { label: "Update university profile",  color: "#CDB4DB", href: "/university" },
              { label: "View plan history",          color: "#FFD6BA", href: "/history" },
            ].map((t) => (
              <a key={t.label} href={t.href} className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-[#F0F0EC] transition-colors no-underline">
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: t.color }} />
                <p className="text-[11px] text-text1">{t.label}</p>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, value, label, from, to, delay }) {
  return (
    <div className={`glass-card p-5 animate-in ${delay}`}>
      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${from} ${to} flex items-center justify-center mb-3`}>
        <Icon size={18} color="#1F2937" />
      </div>
      <p className="font-bold text-lg text-text1">{value}</p>
      <p className="text-xs text-text2 mt-0.5">{label}</p>
    </div>
  );
}

function MiniStat({ value, label, bg }) {
  return (
    <div className={`p-3 rounded-xl ${bg} text-center`}>
      <p className="font-bold text-text1">{value}</p>
      <p className="text-[10px] text-text2 mt-0.5">{label}</p>
    </div>
  );
}
