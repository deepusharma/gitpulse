"use client";

import { useState } from "react";
import { Hero } from "@/components/Hero";
import { SummaryForm } from "@/components/SummaryForm";
import { Results } from "@/components/Results";
import { SummariseResponse } from "@/lib/api";

export default function Home() {
  const [data, setData] = useState<SummariseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Background ambient light effects */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-primary/10 to-transparent w-full pointer-events-none" />
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
      
      <main className="w-full max-w-7xl relative z-10 flex flex-col items-center gap-6 pb-20">
        <Hero />
        
        <div className="w-full">
          <SummaryForm 
            onSuccess={(response) => {
              setData(response);
              setIsLoading(false);
            }} 
            onClear={() => {
              setData(null);
            }}
            setIsLoading={setIsLoading}
          />
        </div>

        <div className="w-full flex justify-center">
          <Results data={data} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}
