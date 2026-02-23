import { useEffect, useState, useCallback } from "react";
import { BarChart3, Zap, Target } from "lucide-react";
import { api, StatsResponse } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const StatsPanel = ({ refreshKey }: { refreshKey: number }) => {
  const [stats, setStats] = useState<StatsResponse | null>(null);

  const load = useCallback(() => {
    api.stats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [refreshKey, load]);

  if (!stats) return null;

  const pieData = [
    { name: "FAQ", value: stats.source_breakdown.FAQ },
    { name: "Ticket", value: stats.source_breakdown.Ticket },
  ];
  // Using brand colors: FAQ (Grey) and Ticket (Orange)
  const COLORS = ["hsl(240, 5%, 60%)", "hsl(35, 100%, 55%)"];

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <BarChart3 className="h-3.5 w-3.5" /> Statistics
      </div>
      <div className="grid grid-cols-3 gap-2">
        <StatCard icon={<BarChart3 className="h-3.5 w-3.5 text-primary" />} label="Queries" value={String(stats.total_queries)} />
        <StatCard icon={<Zap className="h-3.5 w-3.5 text-ticket" />} label="Latency" value={`${stats.avg_latency_ms.toFixed(0)}ms`} />
        <StatCard icon={<Target className="h-3.5 w-3.5 text-confidence-high" />} label="Confidence" value={`${(stats.avg_confidence * 100).toFixed(0)}%`} />
      </div>
      {(stats.source_breakdown.FAQ > 0 || stats.source_breakdown.Ticket > 0) && (
        <div className="flex items-center gap-3">
          <ResponsiveContainer width="100%" height={100}>
            <PieChart>
              <Pie 
                data={pieData} 
                cx="50%" 
                cy="50%" 
                innerRadius={25} 
                outerRadius={40} 
                dataKey="value" 
                strokeWidth={0}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-col gap-1 text-xs">
            <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-faq" /> FAQ: {stats.source_breakdown.FAQ}</div>
            <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-ticket" /> Ticket: {stats.source_breakdown.Ticket}</div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) => (
  <div className="rounded-lg bg-muted/40 p-2.5 text-center space-y-1">
    <div className="flex justify-center">{icon}</div>
    <div className="text-sm font-bold">{value}</div>
    <div className="text-[10px] text-muted-foreground">{label}</div>
  </div>
);

export default StatsPanel;
