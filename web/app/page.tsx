"use client";

import { useState } from "react";
import { Hero } from "@/components/Hero";
import { SummaryForm } from "@/components/SummaryForm";
import { Results } from "@/components/Results";
import { SummariseResponse } from "@/lib/api";

export default function Home() {
  const [data, setData] = useState<SummariseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);

  const hasDataOrLoading = isLoading || data !== null;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Background ambient light effects */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-primary/10 to-transparent w-full pointer-events-none" />
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      
      <main className="w-full max-w-7xl relative z-10 flex flex-col gap-8 pb-20 min-h-[calc(100vh-12rem)]">
        <Hero />
        
        <div className={`flex flex-col md:flex-row w-full items-start transition-all duration-500 ease-in-out ${hasDataOrLoading ? (drawerOpen ? 'gap-8' : 'gap-0 mt-8 md:mt-0') : 'justify-center gap-0'}`}>
          <div 
            className={`transition-all duration-500 ease-in-out overflow-hidden md:sticky md:top-24 shrink-0 ${
              hasDataOrLoading 
                ? (drawerOpen ? "w-full md:w-[30%] opacity-100" : "w-full md:w-0 opacity-100 md:opacity-0")
                : "w-full md:w-full max-w-xl mx-auto opacity-100"
            }`}
          >
            <div className="w-full min-w-full md:min-w-[300px]">
              <SummaryForm 
                onSuccess={(response) => {
                  setData(response);
                  setIsLoading(false);
                  setDrawerOpen(true);
                }} 
                onClear={() => {
                  setData(null);
                }}
                setIsLoading={setIsLoading}
              />
            </div>
          </div>

          <div 
            className={`transition-all duration-500 ease-in-out relative ${
              hasDataOrLoading 
                ? (drawerOpen ? "w-full md:w-[70%]" : "w-full md:w-full") 
                : "w-0 h-0 overflow-hidden opacity-0"
            }`}
          >
            {hasDataOrLoading && (
              <>
                <button
                  onClick={() => setDrawerOpen(!drawerOpen)}
                  className={`hidden md:flex absolute ${drawerOpen ? '-left-4' : 'left-0'} top-4 z-20 h-8 w-8 items-center justify-center rounded-full border border-border bg-background shadow-sm hover:bg-muted text-muted-foreground transition-all duration-500 ease-in-out`}
                  title={drawerOpen ? "Collapse form" : "Expand form"}
                >
                  <span className="text-xs">{drawerOpen ? "◀" : "▶"}</span>
                </button>
                <div className={drawerOpen ? "" : "pl-12"}>
                  <Results data={data} isLoading={isLoading} />
                </div>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
