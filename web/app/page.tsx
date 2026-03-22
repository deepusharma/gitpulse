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
      
      <main className="w-full max-w-7xl relative z-10 flex flex-col gap-8 pb-20 min-h-[calc(100vh-12rem)]">
        <Hero />
        
        <div className="flex flex-col md:flex-row w-full gap-8 items-start">
          <div className="w-full md:w-[30%] shrink-0 md:sticky md:top-24">
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

          <div className="w-full md:w-[70%] mt-8 md:mt-0">
            <Results data={data} isLoading={isLoading} />
          </div>
        </div>
      </main>
    </div>
  );
}
