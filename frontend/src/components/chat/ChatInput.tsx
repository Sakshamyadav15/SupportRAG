import { useState } from "react";
import { ArrowUp, Loader2 } from "lucide-react";
import { GradientButton } from "@/components/ui/gradient-button";

interface Props {
  onSend: (text: string) => void;
  loading: boolean;
}

const ChatInput = ({ onSend, loading }: Props) => {
  const [text, setText] = useState("");

  const send = () => {
    const q = text.trim();
    if (!q || loading) return;
    onSend(q);
    setText("");
  };

  return (
    <div className="border-t border-white/10 p-5 bg-black/40 backdrop-blur-xl">
      <div className="flex items-center gap-3 glass-panel bg-white/5 border border-white/10 p-2 pl-5 rounded-2xl shadow-xl">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about orders, refunds, account issues..."
          disabled={loading}
          className="flex-1 bg-transparent text-sm text-foreground bg-transparent border-0 placeholder:text-muted-foreground focus:ring-0 focus:outline-none disabled:opacity-50"
        />
        <GradientButton
          onClick={send}
          disabled={!text.trim() || loading}
          className="h-9 w-9 p-0 min-w-0 rounded-lg flex items-center justify-center disabled:opacity-40"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowUp className="h-4 w-4" />}
        </GradientButton>
      </div>
    </div>
  );
};

export default ChatInput;
