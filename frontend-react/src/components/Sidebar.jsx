import { NavLink } from "react-router-dom";
import {
  Brain, LayoutDashboard, CalendarCheck, BookOpen, GraduationCap,
  History, User, LogOut, AlarmClock, HelpCircle,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/university", label: "University", icon: GraduationCap },
  { to: "/subjects", label: "Subjects", icon: BookOpen },
  { to: "/study-plan", label: "Study Plan", icon: CalendarCheck },
  { to: "/history", label: "History", icon: History },
  { to: "/profile", label: "Profile", icon: User },
];

export default function Sidebar() {
  const { logout } = useAuth();

  return (
    <aside className="w-56 min-h-screen p-4 flex flex-col gap-1 border-r border-border bg-white/70 backdrop-blur-xl sticky top-0 h-screen overflow-y-auto">
      <div className="flex items-center gap-2.5 px-2 py-3 mb-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-accent3 flex items-center justify-center">
          <Brain size={15} color="#1F2937" />
        </div>
        <span className="font-bold text-sm tracking-tight">StudyAI</span>
      </div>

      <nav className="flex flex-col gap-0.5">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
          >
            <Icon size={15} />
            <span>{label}</span>
          </NavLink>
        ))}

        <div className="sidebar-link opacity-40 cursor-not-allowed" title="Coming in a future phase">
          <AlarmClock size={15} />
          <span>Exam Planner</span>
        </div>
        <div className="sidebar-link opacity-40 cursor-not-allowed" title="Coming in a future phase">
          <HelpCircle size={15} />
          <span>Quiz Center</span>
        </div>
      </nav>

      <div className="mt-auto">
        <div className="sidebar-link" onClick={logout}>
          <LogOut size={15} />
          <span>Log out</span>
        </div>
      </div>
    </aside>
  );
}