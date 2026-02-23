import { Settings, SlidersHorizontal } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";

interface Props {
  topK: number;
  setTopK: (v: number) => void;
  apiUrl: string;
  setApiUrl: (v: string) => void;
}

const SettingsPanel = ({ topK, setTopK, apiUrl, setApiUrl }: Props) => (
  <div className="glass-panel p-4 space-y-4">
    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      <Settings className="h-3.5 w-3.5" /> Settings
    </div>
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs text-muted-foreground flex items-center gap-1.5">
          <SlidersHorizontal className="h-3 w-3" /> Results per Query
        </label>
        <span className="text-xs font-bold text-primary">{topK}</span>
      </div>
      <Slider value={[topK]} onValueChange={([v]) => setTopK(v)} min={1} max={10} step={1} />
    </div>
    <div className="space-y-2">
      <label className="text-xs text-muted-foreground">API URL</label>
      <Input
        value={apiUrl}
        onChange={(e) => {
          setApiUrl(e.target.value);
          localStorage.setItem("supportrag-api-url", e.target.value);
        }}
        className="text-xs h-8 bg-white/20 border-white/30 backdrop-blur-sm focus-visible:ring-primary/50"
      />
    </div>
  </div>
);

export default SettingsPanel;
