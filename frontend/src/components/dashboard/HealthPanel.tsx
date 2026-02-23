import { useEffect, useState } from "react";
import { Activity, Wifi, WifiOff, CheckCircle2, XCircle } from "lucide-react";
import { api, HealthResponse } from "@/lib/api";

const HealthPanel = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [online, setOnline] = useState(false);

  useEffect(() => {
    const check = () => {
      api.health().then((d) => { setHealth(d); setOnline(true); }).catch(() => { setHealth(null); setOnline(false); });
    };
    check();
    const id = setInterval(check, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Activity className="h-3.5 w-3.5" /> API Status
      </div>
      <div className="flex items-center gap-3">
        <div className={`h-2.5 w-2.5 rounded-full ${online ? "bg-confidence-high animate-pulse-glow" : "bg-destructive"}`} />
        <div className="flex items-center gap-2">
          {online ? <Wifi className="h-4 w-4 text-confidence-high" /> : <WifiOff className="h-4 w-4 text-destructive" />}
          <span className="text-sm font-medium">{online ? "API Connected" : "API Offline"}</span>
        </div>
      </div>
      {online && health ? (
        <div className="flex gap-2">
          <Badge ok={health.faq_store_loaded} label="FAQ Loaded" />
          <Badge ok={health.ticket_store_loaded} label="Tickets Loaded" />
        </div>
      ) : !online ? (
        <div className="rounded-lg bg-white/5 border border-white/5 p-3 text-xs text-muted-foreground font-mono break-all backdrop-blur-sm animate-pulse">
          python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
        </div>
      ) : null}
    </div>
  );
};

const Badge = ({ ok, label }: { ok: boolean; label: string }) => (
  <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${ok ? "border-confidence-high/30 text-confidence-high bg-confidence-high/10" : "border-destructive/30 text-destructive bg-destructive/10"}`}>
    {ok ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
    {label}
  </div>
);

export default HealthPanel;
