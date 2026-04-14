import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  iconClassName?: string;
  cardClassName?: string;
  valueClassName?: string;
}

/**
 * A metric summary card for the Insights dashboard.
 *
 * @param title - The label shown above the value.
 * @param value - The primary numeric or text value to display.
 * @param icon - Lucide icon component to render in the header.
 * @param iconClassName - Optional class overrides for the icon.
 * @param cardClassName - Optional class overrides for the Card wrapper.
 * @param valueClassName - Optional class overrides for the value text.
 */
export function MetricCard({
  title,
  value,
  icon: Icon,
  iconClassName,
  cardClassName,
  valueClassName,
}: MetricCardProps) {
  return (
    <Card className={cn("bg-black/40 border-zinc-800", cardClassName)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={cn("h-4 w-4 text-zinc-500", iconClassName)} />
      </CardHeader>
      <CardContent>
        <div className={cn("text-2xl font-bold", valueClassName)}>{value}</div>
      </CardContent>
    </Card>
  );
}
