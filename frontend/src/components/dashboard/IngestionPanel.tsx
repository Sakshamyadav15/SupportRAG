import { useState } from "react";
import { Database, Loader2, FolderOpen } from "lucide-react";
import { GradientButton } from "@/components/ui/gradient-button";
import { api } from "@/lib/api";
import { toast } from "sonner";

const IngestionPanel = () => {
  const [loading, setLoading] = useState(false);

  const handleIngest = async (rebuild: boolean) => {
    setLoading(true);
    try {
      const res = await api.ingest(rebuild);
      toast.success(res.message || `Loaded ${res.faq_count} FAQs and ${res.ticket_count} tickets`);
    } catch (e: any) {
      toast.error(e.message || "Ingestion failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Database className="h-3.5 w-3.5" /> Data Ingestion
      </div>
      <GradientButton className="w-full min-w-0 px-4 py-2 text-xs h-9 rounded-md" disabled={loading} onClick={() => handleIngest(true)}>
        {loading ? <Loader2 className="h-3 w-3 animate-spin mr-2" /> : <Database className="h-3 w-3 mr-2" />}
        Build Vector Stores
      </GradientButton>
      <GradientButton variant="variant" className="w-full min-w-0 px-4 py-2 text-xs h-9 rounded-md" disabled={loading} onClick={() => handleIngest(false)}>
        {loading ? <Loader2 className="h-3 w-3 animate-spin mr-2" /> : <FolderOpen className="h-3 w-3 mr-2" />}
        Load Existing Stores
      </GradientButton>
    </div>
  );
};

export default IngestionPanel;
