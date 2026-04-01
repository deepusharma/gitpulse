"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CommitFrequencyChart({ data }: { data: { date: string, count: number }[] }) {
  if (!data || data.length === 0) {
    return (
      <Card className="col-span-1 border-white/10 bg-black/40 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-white">Commit Frequency</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px] flex items-center justify-center text-zinc-400">
          No data available.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-1 border-white/10 bg-black/40 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-white">Commit Frequency</CardTitle>
      </CardHeader>
      <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
            <Tooltip
              cursor={{ fill: 'rgba(255, 255, 255, 0.1)' }}
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff', borderRadius: '8px' }}
              itemStyle={{ color: '#10b981' }}
            />
            <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
