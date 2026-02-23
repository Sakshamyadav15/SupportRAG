import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Citation } from "@/lib/api";

const CitationsPanel = ({ citations }: { citations: Citation[] }) => {
  const [open, setOpen] = useState(false);

  if (!citations.length) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        {citations.length} source{citations.length > 1 ? "s" : ""}
      </button>
      {open && (
        <div className="mt-2 space-y-2 animate-slide-up">
          {citations.map((c) => (
            <div
              key={c.rank}
              className={`relative overflow-hidden rounded-xl bg-white/5 p-4 text-xs space-y-3 backdrop-blur-sm border border-white/5 group hover:bg-white/10 transition-all duration-300 shadow-md hover:shadow-lg ${
                c.source === "FAQ" 
                  ? "border-l-2 border-l-faq/70 hover:border-l-faq" 
                  : "border-l-2 border-l-ticket/70 hover:border-l-ticket"
              }`}
            >
              <div className="flex flex-wrap gap-1.5">
                <SourceBadge source={c.source} />
                {c.category && <span className="px-2 py-0.5 rounded-full bg-accent text-accent-foreground text-[10px]">{c.category}</span>}
                <span className="px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-[10px]">{(c.similarity * 100).toFixed(1)}%</span>
                {c.resolution_status && <ResolutionBadge status={c.resolution_status} />}
              </div>
              <p className="text-muted-foreground leading-relaxed">{c.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const SourceBadge = ({ source }: { source: string }) => (
  <span
    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
      source === "FAQ" ? "bg-faq/20 text-faq" : "bg-ticket/20 text-ticket"
    }`}
  >
    {source}
  </span>
);

const ResolutionBadge = ({ status }: { status: string }) => {
  const closed = status.toLowerCase() === "closed";
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${closed ? "bg-confidence-high/20 text-confidence-high" : "bg-destructive/20 text-destructive"}`}>
      {status.toUpperCase()}
    </span>
  );
};

export default CitationsPanel;
