import { useState, useCallback } from "react";
import Sidebar from "@/components/dashboard/Sidebar";
import ChatArea from "@/components/chat/ChatArea";
import { ChatMsg } from "@/components/chat/ChatMessage";
import { api } from "@/lib/api";
import { toast } from "sonner";

const Index = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(3);
  const [apiUrl, setApiUrl] = useState(localStorage.getItem("supportrag-api-url") || "http://127.0.0.1:8000");
  const [statsKey, setStatsKey] = useState(0);

  const handleSend = useCallback(async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const res = await api.query(question, topK);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer, data: res }]);
      setStatsKey((k) => k + 1);
    } catch (e: any) {
      toast.error(e.message || "Query failed");
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I couldn't process that request. Please check the API connection." }]);
    } finally {
      setLoading(false);
    }
  }, [topK]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        open={sidebarOpen}
        setOpen={setSidebarOpen}
        topK={topK}
        setTopK={setTopK}
        apiUrl={apiUrl}
        setApiUrl={setApiUrl}
        statsRefreshKey={statsKey}
      />
      <ChatArea
        messages={messages}
        onSend={handleSend}
        onClear={() => setMessages([])}
        loading={loading}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(true)}
      />
    </div>
  );
};

export default Index;
