"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

export default function RepoActivityChart({ data }: { data: { repo: string, percentage: number }[] }) {
  if (!data || data.length === 0) {
    return (
      <Card className="border-white/10 bg-black/40 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-white">Repository Activity</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px] flex items-center justify-center text-zinc-400">
          No data available.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-white/10 bg-black/40 backdrop-blur-md">
      <CardHeader>
        <CardTitle className="text-white">Repository Activity (%)</CardTitle>
      </CardHeader>
      <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="percentage"
              nameKey="repo"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff', borderRadius: '8px' }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px', color: '#a1a1aa' }} />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
