"use client";

import * as React from "react";
import { X, Check, ChevronsUpDown, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = "Select items...",
  disabled = false,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const containerRef = React.useRef<HTMLDivElement>(null);

  const filteredOptions = options.filter((opt) =>
    opt.toLowerCase().includes(query.toLowerCase())
  );

  const toggleOption = (option: string) => {
    const newSelected = selected.includes(option)
      ? selected.filter((s) => s !== option)
      : [...selected, option];
    onChange(newSelected);
  };

  const removeOption = (e: React.MouseEvent, option: string) => {
    e.stopPropagation();
    onChange(selected.filter((s) => s !== option));
  };

  // Close when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative w-full" ref={containerRef}>
      <div
        className={cn(
          "min-h-[40px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background flex flex-wrap gap-1 items-center cursor-pointer",
          disabled && "opacity-50 cursor-not-allowed",
          open && "ring-2 ring-ring ring-offset-2"
        )}
        onClick={() => !disabled && setOpen(!open)}
      >
        {selected.length > 0 ? (
          <div className="flex flex-wrap gap-1">
            {selected.map((item) => (
              <Badge
                key={item}
                variant="secondary"
                className="rounded-sm px-1 font-normal"
              >
                {item}
                <button
                  className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 hover:bg-muted"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      removeOption(e as any, item);
                    }
                  }}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                  }}
                  onClick={(e) => removeOption(e, item)}
                >
                  <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                </button>
              </Badge>
            ))}
          </div>
        ) : (
          <span className="text-muted-foreground">{placeholder}</span>
        )}
        <div className="ml-auto flex items-center shrink-0 opacity-50">
           <ChevronsUpDown className="h-4 w-4" />
        </div>
      </div>

      {open && (
        <div className="absolute z-50 mt-2 w-full rounded-md border bg-popover text-popover-foreground shadow-md outline-none animate-in fade-in-0 zoom-in-95 overflow-hidden">
          <div className="flex items-center border-b px-3">
             <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
             <input
                className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Search repositories..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
             />
          </div>
          <div className="max-h-[200px] overflow-y-auto p-1 custom-scrollbar">
            {filteredOptions.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">
                No repositories found.
              </div>
            ) : (
              filteredOptions.map((option) => (
                <div
                  key={option}
                  className={cn(
                    "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
                    selected.includes(option) && "bg-accent/50"
                  )}
                  onClick={() => toggleOption(option)}
                >
                  <div
                    className={cn(
                      "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                      selected.includes(option)
                        ? "bg-primary text-primary-foreground"
                        : "opacity-50 [&_svg]:invisible"
                    )}
                  >
                    <Check className={cn("h-4 w-4")} />
                  </div>
                  <span>{option}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
