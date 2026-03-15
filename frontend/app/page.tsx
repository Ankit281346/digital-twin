"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  Terminal, Send, Upload, RefreshCw, 
  Code, GraduationCap, PenTool, Coffee, Compass, ArrowLeft,
  Plus, Mic, MicOff, Volume2, VolumeX, Copy, ThumbsUp, ThumbsDown, RotateCcw, Share2, Sparkles, ChevronDown,
  FileText, Mail, X, Download
} from "lucide-react";
import clsx from "clsx";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [bootStep, setBootStep] = useState(0);
  const [isBooting, setIsBooting] = useState(true);
  const [hasStarted, setHasStarted] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  
  const bottomRef = useRef<HTMLDivElement>(null);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);
  const recognitionRef = useRef<any>(null);

  const bootSequence = [
    "Initializing digital environment...",
    "Loading configuration matrix...",
    "Connecting to Groq Neural Network...",
    "Verifying security tokens...",
    "System Ready."
  ];

  const [mode, setMode] = useState<"normal" | "recruiter">("normal");

  const [modalType, setModalType] = useState<"cover-letter" | "resume" | null>(null);
  const [formData, setFormData] = useState({ company: "", role: "" });
  const [isGenerating, setIsGenerating] = useState(false);

  // Stop speech if switching modes
  useEffect(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [mode]);

  // Voice Mode Functions
  const speak = (text: string) => {
    if (!text) return;
    
    // Cleanup previous speech
    window.speechSynthesis.cancel();
    
    // Basic sanitization (remove markdown symbols)
    const cleanText = text.replace(/[#*`]/g, '');
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Attempt to select a better voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => voice.name.includes("Google US English") || voice.name.includes("Microsoft David"));
    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    speechRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // Unified Voice Toggle Function
  const toggleVoiceMode = () => {
    // If currently listening, stop everything
    if (isListening || voiceMode) {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            recognitionRef.current = null;
        }
        stopSpeaking();
        setIsListening(false);
        setVoiceMode(false);
        return;
    }

    // Otherwise, start everything
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Your browser does not support speech recognition. Try Chrome.");
        return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Changing to false to stabilize connection. 'Continuous' often causes network dropouts on localhost.
    // We will keep 'Voice Mode' ON (for output) even if the mic stops after one sentence.
    recognition.continuous = false; 
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        setIsListening(true);
        setVoiceMode(true); // Ensure output is enabled
    };
    
    recognition.onend = () => {
        setIsListening(false);
        // Do NOT turn off voiceMode here. Keep it on so the AI speaks back.
    };

    recognition.onerror = (event: any) => {
        // Silently ignore network errors to prevent console spam for minor blips
        if (event.error !== 'no-speech' && event.error !== 'network') {
            console.error("Speech error", event.error);
        }
        
        // Only stop if it's a fatal error
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            setIsListening(false);
            setVoiceMode(false);
        }
        // For network errors on some browsers, we might just want to let it retry or stop silently
        if (event.error === 'network') {
             setIsListening(false);
             setVoiceMode(false);
        }
    };
    
    recognition.onresult = (event: any) => {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        if (transcript) {
            setInput(transcript);
        }
    };
    
    recognitionRef.current = recognition;
    try {
        recognition.start();
    } catch (e) {
        console.error("Failed to start recognition", e);
    }
  };

  // Deprecated individual toggleListening
  // Now both buttons use toggleVoiceMode

  const handleGenerate = async () => {
    if (!formData.company || !formData.role) return;
    setIsGenerating(true);
    setModalType(null); // Close modal immediately
    
    // Construct a specialized prompt based on the tool
    let prompt;
    if (modalType === "cover-letter") {
        prompt = `Draft a cold email to a recruiter at ${formData.company} for the role of ${formData.role}. Use my real experience from the resume. Keep it professional, concise, and ready to send.`;
    } else {
        prompt = `Tailor my resume summary and key skills for the role of ${formData.role} at ${formData.company}. Format it clearly.`;
    }

    // Call the standard chat endpoint instead of the PDF generator
    await handleSubmit(undefined, prompt);
    
    setFormData({ company: "", role: "" });
    setIsGenerating(false);
  };

  useEffect(() => {
    setMounted(true);
    let step = 0;
    const interval = setInterval(() => {
      if (step < bootSequence.length) {
        setBootStep(step);
        step++;
      } else {
        clearInterval(interval);
        setTimeout(() => setIsBooting(false), 800);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, hasStarted]);

  const handleSubmit = async (e?: React.FormEvent, customPrompt?: string) => {
    // Determine the message to send (from input or customPrompt)
    const activeInput = customPrompt || input;

    if (!activeInput.trim() || loading) return;
    if (e) e.preventDefault();
    
    // Switch to chat mode if first time
    if (!hasStarted) setHasStarted(true);

    const userMsg = activeInput.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const url = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
      const res = await fetch(`${url}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg,
          history: messages.map(m => ({ role: m.role, content: m.content })),
          mode: mode 
        })
      });

      if (!res.ok) throw new Error("Connection failed");
      
      const data = await res.json();
      const aiResponse = data.response;
      setMessages(prev => [...prev, { role: "assistant", content: aiResponse }]);

      // Speak back if in voice mode
      if (voiceMode) {
        // Strip markdown roughly for speech
        const speechText = aiResponse.replace(/[*_`#>]/g, '');
        // Split if too long
        if (speechText.length > 200) {
           speak(speechText.substring(0, 200) + "..."); // Just speak start for now to avoid annoyance
        } else {
           speak(speechText);
        }
      }

    } catch (error) {
      setMessages(prev => [...prev, { role: "system", content: "Error: Could not connect to Digital Twin backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const SuggestionChip = ({ icon: Icon, label, prompt }: { icon: any, label: string, prompt: string }) => (
    <button 
      onClick={() => handleSubmit(undefined, prompt)}
      className="flex items-center gap-2 rounded-lg border border-[#E5E3DF] bg-white hover:bg-[#F8F7F5] px-3 py-2 text-sm text-[#5D5D5D] transition-colors shadow-sm"
    >
      <Icon size={16} />
      <span>{label}</span>
    </button>
  );

  const LoadingStar = () => (
    <div className="text-[#D97757] animate-spin-slow origin-center">
       <Sparkles size={24} fill="#D97757" />
    </div>
  );

  if (!mounted) return null;

  // -- BOOT SEQUENCE UI --
  if (isBooting) {
    return (
      <div className="flex h-screen w-full flex-col items-center justify-center bg-[#FDFBF8] font-mono text-[#403E3E]">
        <div className="w-96 border border-[#E5E3DF] bg-white p-6 shadow-xl rounded-lg">
          <div className="mb-4 flex items-center gap-2 border-b border-[#E5E3DF] pb-2 text-[#D97757]">
            <Terminal size={18} />
            <span className="font-bold tracking-wider text-xs">SYSTEM_INITIALIZATION</span>
          </div>
          <div className="space-y-2">
            {bootSequence.map((text, i) => (
              <div key={i} className={clsx("text-xs transition-opacity duration-300", i > bootStep ? "opacity-0" : i === bootStep ? "text-[#D97757] font-semibold" : "text-[#9CA3AF]")}>
                 {i <= bootStep && <span className="mr-2">[{i === bootStep ? "*" : "✓"}]</span>}
                 {text}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // -- MAIN UI (Start Screen or Chat Screen) --
  return (
    <main className="flex h-screen w-full flex-col bg-[#FDFBF8] text-[#403E3E] font-sans overflow-hidden items-center">
      
      {/* Top Navbar */}
      <header className="w-full flex items-center p-6 gap-4 justify-between">
         <div className="flex items-center gap-4">
             {hasStarted && (
                <button 
                    onClick={() => setHasStarted(false)}
                    className="text-[#5D5D5D] hover:text-[#D97757] hover:bg-[#F3F1ED] p-2 rounded-full transition-all active:scale-95"
                    title="Back to Start"
                >
                    <ArrowLeft size={20} />
                </button>
             )}
             
             <div className="flex items-center gap-2 text-[#D97757]">
                <Sparkles size={18} fill="#D97757" />
                <span className="font-serif-custom font-bold text-lg tracking-tight text-[#2D2D2D]">Digital Twin</span>
             </div>
         </div>
         
         <div className="flex items-center gap-2">
            <button 
                onClick={toggleVoiceMode}
                className={clsx(
                    "p-2 rounded-full transition-colors flex items-center gap-2 text-xs font-semibold uppercase tracking-wider",
                    voiceMode ? "bg-[#D97757] text-white" : "bg-[#F3F1ED] text-[#9CA3AF] hover:text-[#5D5D5D]"
                )}
                title="Toggle Voice Conversation"
            >
                {voiceMode ? <Mic size={16} /> : <MicOff size={16} />}
                <span>{voiceMode ? "Voice On" : "Voice Off"}</span>
            </button>
         </div>
      </header>

      {/* Content Area */}
      <div className="flex-1 w-full max-w-3xl flex flex-col items-center overflow-y-auto w-full px-4 md:px-0 pb-32 scrollbar-thin">
        
        {/* START SCREEN CONTENT */}
        {!hasStarted ? (
          <div className="flex-1 flex flex-col items-center justify-center w-full gap-8 mt-12">
             <div className="flex flex-col items-center gap-6 text-center">
                {/* Mode Switcher */}
                <div className="bg-[#F3F1ED] p-1 rounded-full flex items-center gap-1 shadow-inner">
                    <button 
                        onClick={() => setMode("normal")}
                        className={clsx(
                            "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
                            mode === "normal" 
                                ? "bg-white text-[#2D2D2D] shadow-sm" 
                                : "text-[#9CA3AF] hover:text-[#5D5D5D]"
                        )}
                    >
                        Robot Assistant
                    </button>
                    <button 
                        onClick={() => setMode("recruiter")}
                        className={clsx(
                            "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
                            mode === "recruiter" 
                                ? "bg-white text-[#D97757] shadow-sm" 
                                : "text-[#9CA3AF] hover:text-[#5D5D5D]"
                        )}
                    >
                        Recruiter View
                    </button>
                </div>

                <h1 className="font-serif-custom text-3xl md:text-4xl text-[#2D2D2D]">
                    {mode === "normal" ? "How can I help you today?" : "Review my professional portfolio"}
                </h1>
             </div>

             {/* Main Start Input */}
             <div className="w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-[#E5E3DF] p-4 group focus-within:ring-1 focus-within:ring-[#D97757]/30 transition-shadow hover:shadow-md">
                <form onSubmit={(e) => handleSubmit(e)} className="flex items-center gap-3">
                   <input
                      className="flex-1 bg-transparent border-none outline-none text-lg text-[#2D2D2D] placeholder-[#9CA3AF] font-light px-2"
                      placeholder={mode === "normal" ? (isListening ? "Listening..." : "Ask anything...") : (isListening ? "Listening..." : "Ask about my experience...")}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      autoFocus
                   />
                   <button 
                        type="button" 
                        onClick={toggleVoiceMode}
                        className={clsx(
                            "p-2 rounded-full transition-colors",
                            (isListening || voiceMode) ? "bg-red-500 text-white animate-pulse shadow-md" : "text-[#9CA3AF] hover:bg-[#F3F1ED]"
                        )}
                   >
                        <Mic size={20} />
                   </button>
                   <button type="submit" disabled={!input.trim()} className="text-[#D97757] hover:bg-[#F3F1ED] p-2 rounded-lg transition-colors disabled:opacity-50">
                      <Send size={20} />
                   </button>
                </form>
             </div>

             {/* Suggestion Chips */}
             <div className="flex flex-wrap justify-center gap-3 max-w-2xl">
                {mode === "normal" ? (
                    <>
                        <SuggestionChip icon={Coffee} label="About Me" prompt="Tell me about yourself." />
                        <SuggestionChip icon={Compass} label="Web Search" prompt="Search for the latest AI news." />
                        <SuggestionChip icon={Code} label="Calculator" prompt="Calculate 15% of 850." />
                    </>
                ) : (
                    <>
                        <SuggestionChip icon={Code} label="Projects" prompt="List your top 3 projects and explain their tech stack." />
                        <SuggestionChip icon={GraduationCap} label="Portfolio Pitch" prompt="Why should we hire you? Give me a professional pitch." />
                        <SuggestionChip icon={PenTool} label="Technology" prompt="What technologies are you proficient in?" />
                        <button 
                            onClick={() => { setModalType("cover-letter"); setFormData({ company: "", role: "" }); }}
                            className="flex items-center gap-2 rounded-lg border border-[#E5E3DF] bg-white hover:bg-[#F8F7F5] px-3 py-2 text-sm text-[#5D5D5D] transition-colors shadow-sm"
                        >
                            <Mail size={16} />
                            <span>Cold Email</span>
                        </button>
                    </>
                )}
             </div>
          </div>
        ) : (
          /* CHAT SCREEN CONTENT */
          <div className="w-full space-y-8 py-8">
            {messages.map((msg, idx) => (
              <div key={idx} className={clsx("flex w-full", msg.role === "user" ? "justify-end" : "justify-start")}>
                 <div className={clsx("max-w-[85%] md:max-w-[75%]", msg.role === "assistant" ? "w-full" : "")}>
                    {/* User Message Bubble */}
                    {msg.role === "user" && (
                       <div className="bg-[#F3F1ED] text-[#2D2D2D] px-5 py-3 rounded-2xl text-[15px] leading-relaxed">
                          {msg.content}
                       </div>
                    )}

                    {/* AI Message Text */}
                    {msg.role === "assistant" && (
                       <div className="space-y-3">
                          <div className="prose prose-p:text-[#2D2D2D] prose-headings:text-[#2D2D2D] prose-strong:text-[#2D2D2D] prose-code:text-[#D97757] max-w-none text-[16px] font-serif-custom leading-7">
                             <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {msg.content}
                             </ReactMarkdown>
                          </div>
                          
                          {/* Action Toolbar */}
                          <div className="flex items-center gap-3 pt-1">
                             <button className="text-[#9CA3AF] hover:text-[#5D5D5D] transition-colors"><Copy size={14} /></button>
                             <button className="text-[#9CA3AF] hover:text-[#5D5D5D] transition-colors"><ThumbsUp size={14} /></button>
                             <button 
                                onClick={() => speak(msg.content)}
                                className={clsx("transition-colors", isSpeaking ? "text-[#D97757] animate-pulse" : "text-[#9CA3AF] hover:text-[#5D5D5D]")}
                                title="Read Aloud"
                             >
                                <Volume2 size={14} />
                             </button>
                             <button className="text-[#9CA3AF] hover:text-[#5D5D5D] transition-colors"><RotateCcw size={14} /></button>
                          </div>
                       </div>
                    )}
                 </div>
              </div>
            ))}
            
            {/* Loading Indicator */}
            {loading && (
               <div className="flex w-full justify-start py-4">
                  <LoadingStar />
               </div>
            )}
            
            <div ref={bottomRef} className="h-4" />
          </div>
        )}
      </div>

      {/* GENERATOR MODAL */}
      {modalType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl animate-in fade-in zoom-in duration-200 flex flex-col items-center">
                <div className="w-full flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3 text-[#D97757]">
                        <Mail size={24} />
                        <h2 className="text-xl font-bold font-serif-custom text-[#2D2D2D]">
                            Cold Email Generator
                        </h2>
                    </div>
                    <button onClick={() => setModalType(null)} className="text-[#9CA3AF] hover:text-[#5D5D5D] transition-colors"><X size={20} /></button>
                </div>
                
                <div className="w-full space-y-4">
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-[#9CA3AF] mb-1">
                            Target Company
                        </label>
                        <input 
                            className="w-full bg-[#F3F1ED] rounded-lg p-3 text-[#2D2D2D] outline-none focus:ring-1 focus:ring-[#D97757]"
                            placeholder="e.g. Google, Anthropic..."
                            value={formData.company}
                            onChange={(e) => setFormData({...formData, company: e.target.value})}
                        />
                    </div>
                    
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-[#9CA3AF] mb-1">
                            Target Role
                        </label>
                        <input 
                            className="w-full bg-[#F3F1ED] rounded-lg p-3 text-[#2D2D2D] outline-none focus:ring-1 focus:ring-[#D97757]"
                            placeholder="e.g. Senior Frontend Engineer"
                            value={formData.role}
                            onChange={(e) => setFormData({...formData, role: e.target.value})}
                        />
                    </div>
                    
                    <button 
                        onClick={handleGenerate}
                        disabled={!formData.company || !formData.role || isGenerating}
                        className="w-full bg-[#D97757] hover:bg-[#C26344] text-white font-medium py-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
                    >
                        {isGenerating ? (
                            <>
                                <LoadingStar />
                                <span>Generating...</span>
                            </>
                        ) : (
                            <>
                                <Sparkles size={18} />
                                <span>Generate Draft</span>
                            </>
                        )}
                    </button>
                    
                    <p className="text-xs text-center text-[#9CA3AF]">
                        This will generate a tailored cold email using your RAG knowledge base.
                    </p>
                </div>
            </div>
        </div>
      )}

      {/* Bottom Input Area (Only visible in Chat Mode) */}
      {hasStarted && (
         <div className="w-full bg-[#FDFBF8] sticky bottom-0 pb-6 pkg-4">
            <div className="max-w-3xl mx-auto px-4">
               <div className="w-full bg-white rounded-2xl shadow-sm border border-[#E5E3DF] p-3 group focus-within:ring-1 focus-within:ring-[#D97757]/30 transition-shadow hover:shadow-md flex items-center gap-3">
                  <button type="button" className="text-[#5D5D5D] hover:bg-[#F3F1ED] p-2 rounded-full transition-colors">
                      <Plus size={20} />
                  </button>
                  <form onSubmit={(e) => handleSubmit(e)} className="flex-1 flex items-center gap-2">
                     <input
                        className="w-full bg-transparent border-none outline-none text-[16px] text-[#2D2D2D] placeholder-[#9CA3AF]"
                        placeholder={isListening ? "Listening..." : "Reply to Digital Twin..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        autoFocus={!loading}
                     />
                     <button 
                        type="button" 
                        onClick={toggleVoiceMode}
                         className={clsx(
                             "p-2 rounded-full transition-colors",
                             (isListening || voiceMode) ? "bg-red-500 text-white animate-pulse shadow-md" : "text-[#9CA3AF] hover:bg-[#F3F1ED]"
                         )}
                         title={voiceMode ? "Stop Conversation" : "Start Conversation"}
                    >
                         <Mic size={18} />
                    </button>
                  </form>
                  <button type="submit" disabled={!input.trim() || loading} className="text-[#D97757] hover:bg-[#F3F1ED] p-2 rounded-lg transition-colors disabled:opacity-50">
                      <Send size={18} />
                  </button>
               </div>
               <div className="mt-2 text-center text-xs text-[#9CA3AF]">
                  Digital Twin can make mistakes. Please double check responses.
               </div>
            </div>
         </div>
      )}
    </main>
  );
}
