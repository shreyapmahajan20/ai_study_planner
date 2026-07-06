import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";
import { Bell, Search } from "lucide-react";
import { useLocation } from "react-router-dom";

const pageTitles = {
  "/dashboard":  { title: "Dashboard",          sub: "Welcome back! Here's your study overview." },
  "/study-plan": { title: "Study Plan",          sub: "Generate a personalized AI study schedule." },
  "/subjects":   { title: "Subjects & Syllabus", sub: "Upload syllabi and track your topics." },
  "/university": { title: "University Profile",  sub: "Tell us where you study for better plans." },
  "/history":    { title: "Past Plans",          sub: "Review all your previously generated plans." },
  "/profile":    { title: "Your Profile",        sub: "Manage your account and password." },
};

export default function ProtectedLayout() {
  const { user } = useAuth();
  const location = useLocation();
  const meta = pageTitles[location.pathname] || { title: "StudyAI", sub: "" };

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex w-full min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-bold text-xl text-text1">{meta.title}</h1>
            <p className="text-sm text-text2 mt-1">{meta.sub}</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="glass-card p-2.5"><Bell size={16} color="#6B7280" /></button>
            <button className="glass-card p-2.5"><Search size={16} color="#6B7280" /></button>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
