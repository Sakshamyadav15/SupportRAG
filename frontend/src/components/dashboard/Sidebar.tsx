import { PanelLeftClose, PanelLeft } from "lucide-react";
import HealthPanel from "./HealthPanel";
import IngestionPanel from "./IngestionPanel";
import StatsPanel from "./StatsPanel";
import SettingsPanel from "./SettingsPanel";

interface Props {
  open: boolean;
  setOpen: (v: boolean) => void;
  topK: number;
  setTopK: (v: number) => void;
  apiUrl: string;
  setApiUrl: (v: string) => void;
  statsRefreshKey: number;
}

const Sidebar = ({ open, setOpen, topK, setTopK, apiUrl, setApiUrl, statsRefreshKey }: Props) => (
  <>
    {/* Mobile toggle */}
    {!open && (
      <button
        onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 lg:hidden glass-panel p-2 hover:bg-accent transition-colors"
      >
        <PanelLeft className="h-5 w-5" />
      </button>
    )}
    {/* Overlay for mobile */}
    {open && (
      <div className="fixed inset-0 bg-background/60 backdrop-blur-sm z-40 lg:hidden" onClick={() => setOpen(false)} />
    )}
    <aside
      className={`fixed z-50 top-0 left-0 h-full w-80 bg-black/60 backdrop-blur-2xl border-r border-white/10 flex flex-col transition-transform duration-300 shadow-[0_0_40px_rgba(0,0,0,0.5)] ${
        open ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        <span className="text-sm font-semibold tracking-wide">Control Panel</span>
        <button onClick={() => setOpen(false)} className="p-1 rounded-md hover:bg-sidebar-accent transition-colors">
          <PanelLeftClose className="h-4 w-4" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-3">
        <HealthPanel />
        <IngestionPanel />
        <StatsPanel refreshKey={statsRefreshKey} />
        <SettingsPanel topK={topK} setTopK={setTopK} apiUrl={apiUrl} setApiUrl={setApiUrl} />
      </div>
    </aside>
  </>
);

export default Sidebar;
