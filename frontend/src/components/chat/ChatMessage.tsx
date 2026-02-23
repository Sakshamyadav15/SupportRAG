import { CheckCircle2, AlertTriangle, XCircle, Zap } from "lucide-react";
import { QueryResponse } from "@/lib/api";
import CitationsPanel from "./CitationsPanel";

export interface ChatMsg {
  role: "user" | "assistant";
  content: string;
  data?: QueryResponse;
}

const ChatMessage = ({ msg }: { msg: ChatMsg }) => {
  const isUser = msg.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-slide-up`}>
      <div className={`max-w-[80%] space-y-2 ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-2xl px-5 py-3.5 text-sm leading-relaxed tracking-wide shadow-sm backdrop-blur-md transition-all duration-300 ${
            isUser 
              ? "bg-white/10 border border-white/10 text-white rounded-br-sm" 
              : "glass-panel rounded-bl-sm text-gray-200"
          }`}
        >
          {msg.content}
        </div>
        {msg.data && (
          <div className="flex flex-wrap gap-1.5 px-1">
            <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${msg.data.source === "FAQ" ? "bg-faq/20 text-faq" : "bg-ticket/20 text-ticket"}`}>
              {msg.data.source}
            </span>
            <ConfidenceBadge value={msg.data.confidence} />
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-[10px]">
              <Zap className="h-2.5 w-2.5" /> {msg.data.latency_ms.toFixed(0)}ms
            </span>
          </div>
        )}
        {msg.data?.citations && <CitationsPanel citations={msg.data.citations} />}
      </div>
    </div>
  );
};

const ConfidenceBadge = ({ value }: { value: number }) => {
  const pct = (value * 100).toFixed(0);
  if (value >= 0.7) return <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-confidence-high/20 text-confidence-high text-[10px] font-semibold"><CheckCircle2 className="h-2.5 w-2.5" />{pct}%</span>;
  if (value >= 0.5) return <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-confidence-mid/20 text-confidence-mid text-[10px] font-semibold"><AlertTriangle className="h-2.5 w-2.5" />{pct}%</span>;
  return <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-confidence-low/20 text-confidence-low text-[10px] font-semibold"><XCircle className="h-2.5 w-2.5" />{pct}%</span>;
};

export default ChatMessage;
