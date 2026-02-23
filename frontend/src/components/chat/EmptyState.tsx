import { Search, DollarSign, KeyRound, Package } from "lucide-react";

const suggestions = [
  { icon: Search, text: "How do I track my order?", color: "text-faq" },
  { icon: DollarSign, text: "My refund hasn't arrived in 12 days", color: "text-ticket" },
  { icon: KeyRound, text: "I can't log into my account after resetting password", color: "text-primary" },
  { icon: Package, text: "The product I received is damaged", color: "text-ticket" },
];

const EmptyState = ({ onSend }: { onSend: (q: string) => void }) => (
  <div className="flex-1 flex items-center justify-center p-6">
    <div className="max-w-lg w-full space-y-6 text-center">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">What can I help you with?</h2>
        <p className="text-sm text-muted-foreground">Ask anything about orders, refunds, accounts, or products.</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {suggestions.map((s) => (
          <button
            key={s.text}
            onClick={() => onSend(s.text)}
            className="glass-panel p-4 text-left hover:bg-accent/60 transition-all duration-200 hover:glow-primary group space-y-2"
          >
            <s.icon className={`h-5 w-5 ${s.color} transition-transform group-hover:scale-110`} />
            <p className="text-xs leading-relaxed">{s.text}</p>
          </button>
        ))}
      </div>
    </div>
  </div>
);

export default EmptyState;
