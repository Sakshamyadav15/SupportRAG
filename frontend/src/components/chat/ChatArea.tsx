import { useRef, useEffect } from "react";
import { Trash2, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import ChatMessage, { ChatMsg } from "./ChatMessage";
import ChatInput from "./ChatInput";
import HeaderTitle from "./HeaderTitle";
import EmptyState from "./EmptyState";

interface Props {
  messages: ChatMsg[];
  onSend: (q: string) => void;
  onClear: () => void;
  loading: boolean;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const ChatArea = ({ messages, onSend, onClear, loading, sidebarOpen, onToggleSidebar }: Props) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className={`relative flex flex-col h-full min-w-0 flex-1 bg-background transition-all duration-300 ${sidebarOpen ? "filter blur-sm scale-[0.98] opacity-50 pointer-events-none" : ""}`}>
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-black/40 backdrop-blur-md sticky top-0 z-10 shadow-lg">
        <div className="flex items-center gap-4">
          {!sidebarOpen && (
            <button 
              onClick={onToggleSidebar} 
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all active:scale-95"
            >
              <PanelLeft className="h-5 w-5 text-gray-300" />
            </button>
          )}
          <HeaderTitle />
        </div>
        <Button variant="ghost" size="sm" onClick={onClear} className="text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-colors">
          <Trash2 className="h-5 w-5" />
        </Button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 md:px-0">
        <div className="max-w-4xl mx-auto w-full h-full flex flex-col">
          {messages.length === 0 && !loading ? (
            <EmptyState onSend={onSend} />
          ) : (
            <div className="py-6 space-y-6 pb-4">
              {messages.map((m, i) => (
                <ChatMessage key={i} msg={m} />
              ))}
              {loading && (
                <div className="flex justify-start animate-slide-up px-4">
                  <div className="glass-panel bg-black/40 border-white/10 rounded-2xl rounded-bl-sm px-5 py-4 flex gap-2 shadow-lg">
                    <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}
              <div ref={bottomRef} className="h-4" />
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={onSend} loading={loading} />
    </div>
  );
};

export default ChatArea;
