"use client";

import { useEffect, useState, useMemo } from "react";
import { TeamSummariseResponse } from "@/lib/api";
import { ChevronLeft, ChevronRight, X, Play, Pause } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function PresentPage() {
  const [data] = useState<TeamSummariseResponse | null>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("gitpulse_team_presentation");
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch (e) {
          console.error(e);
        }
      }
    }
    return null;
  });
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const slides = useMemo(() => {
    if (!data) return [];
    // Split markdown by H1 or H2 boundaries
    const rawSlides = data.summary.split(/(?=\n?#{1,2} )/m);
    return rawSlides
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }, [data]);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isPlaying && slides.length > 0) {
      interval = setInterval(() => {
        setCurrentSlide(curr => (curr + 1) % slides.length);
      }, 8000); // 8 seconds per slide
    }
    return () => clearInterval(interval);
  }, [isPlaying, slides.length]);

  if (!data) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center flex-col gap-4">
        <h1 className="text-2xl font-bold">No Presentation Data Found</h1>
        <p className="text-muted-foreground">Go to the Team page and generate a standup first.</p>
        <Link href="/team" className="text-primary hover:underline">Return to Team</Link>
      </div>
    );
  }

  if (slides.length === 0) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center flex-col gap-4">
        <h1 className="text-xl">Standup summary is empty.</h1>
        <Link href="/team" className="text-primary hover:underline">Return</Link>
      </div>
    );
  }

  const nextSlide = () => setCurrentSlide((c) => (c + 1) % slides.length);
  const prevSlide = () => setCurrentSlide((c) => (c - 1 + slides.length) % slides.length);

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative flex flex-col items-center justify-center">
      {/* Top Bar Navigation */}
      <div className="absolute top-4 right-4 z-50 flex gap-4 opacity-50 hover:opacity-100 transition-opacity">
        <Link href="/team" className="bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors">
          <X className="w-6 h-6" />
        </Link>
      </div>

      <div className="absolute bottom-10 z-50 flex items-center gap-6 opacity-30 hover:opacity-100 transition-opacity">
        <button onClick={prevSlide} className="bg-white/10 hover:bg-white/20 p-3 rounded-full transition-colors">
          <ChevronLeft className="w-8 h-8" />
        </button>
        <button onClick={() => setIsPlaying(!isPlaying)} className="bg-white/10 hover:bg-white/20 p-4 rounded-full transition-colors">
          {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8 ml-1" />}
        </button>
        <button onClick={nextSlide} className="bg-white/10 hover:bg-white/20 p-3 rounded-full transition-colors">
          <ChevronRight className="w-8 h-8" />
        </button>
      </div>

      {/* Slide Indicators */}
      <div className="absolute bottom-4 z-50 flex gap-2">
        {slides.map((_, i) => (
          <div 
            key={i} 
            className={`h-1.5 rounded-full transition-all duration-300 ${i === currentSlide ? "bg-white w-8" : "bg-white/30 w-3 cursor-pointer"}`}
            onClick={() => setCurrentSlide(i)}
          />
        ))}
      </div>

      {/* Main Slide Content */}
      <main className="w-full max-w-4xl px-8 md:px-16 mx-auto h-[80vh] flex items-center justify-center">
        <div key={currentSlide} className="animate-in fade-in zoom-in-95 duration-500 w-full prose prose-invert prose-2xl prose-headings:text-primary max-w-none text-left">
          <ReactMarkdown>
            {slides[currentSlide]}
          </ReactMarkdown>
        </div>
      </main>

      {/* Context info corner */}
      <div className="absolute bottom-4 left-4 text-white/30 text-xs font-mono">
        <p>TEAM: {data.contributors.join(", ")}</p>
        <p>REPOS: {data.repos.join(", ")}</p>
      </div>
    </div>
  );
}
