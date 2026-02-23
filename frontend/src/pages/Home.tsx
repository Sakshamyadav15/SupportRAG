import { useNavigate } from "react-router-dom";
import { WebGLShader } from "@/components/ui/web-gl-shader";
import { GradientButton } from "@/components/ui/gradient-button";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden bg-[#0a0f1c]">
      <WebGLShader />
      <div className="relative z-10 w-full max-w-4xl px-4">
        <main className="relative rounded-2xl border border-white/10 bg-[#111827]/60 p-12 backdrop-blur-xl shadow-2xl">
          <h1 className="mb-6 text-center text-5xl font-extrabold tracking-tight text-white md:text-7xl">
            SupportRAG
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-center text-lg text-gray-300 md:text-xl">
            Intelligent support resolution powered by advanced retrieval-augmented generation.
          </p>
          
          <div className="flex justify-center">
            <GradientButton 
              onClick={() => navigate("/chat")}
              className="text-lg"
            >
              Enter Workspace
            </GradientButton>
          </div>
        </main>
      </div>
    </div>
  );
}
