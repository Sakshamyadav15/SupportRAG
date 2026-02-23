import { Bot } from "lucide-react";

const HeaderTitle = () => {
  return (
    <div className="flex items-center gap-3 group">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/20 blur-md rounded-full group-hover:bg-primary/30 transition-all duration-300" />
        <div className="relative h-10 w-10 rounded-xl bg-gradient-to-br from-gray-800 to-black border border-white/10 flex items-center justify-center shadow-inner group-hover:scale-105 transition-transform duration-300">
          <Bot className="h-5 w-5 text-primary drop-shadow-[0_0_8px_rgba(255,165,0,0.5)]" />
        </div>
      </div>
      <div className="flex flex-col">
        <h1 className="text-base font-bold text-white tracking-wide bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent group-hover:text-white transition-colors">
          SupportRAG <span className="text-primary font-extrabold">Enhanced</span>
        </h1>
        <div className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          <p className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">
            Dual Context RAG System
          </p>
        </div>
      </div>
    </div>
  );
};

export default HeaderTitle;
