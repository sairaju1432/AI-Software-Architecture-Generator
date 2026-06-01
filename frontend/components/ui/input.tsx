import * as React from "react";
import { cn } from "@/lib/utils";
export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) { return <input className={cn("w-full rounded-md border border-border bg-background px-3 py-2 outline-none ring-primary focus:ring-2", className)} {...props} />; }
