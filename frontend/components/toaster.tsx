"use client";

import { useToast } from "@/hooks/use-toast";
import * as ToastPrimitives from "@radix-ui/react-toast";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export function Toaster() {
  const { toasts, dismiss } = useToast();

  return (
    <ToastPrimitives.Provider>
      {toasts.map(function ({ id, title, description, action, variant, ...props }) {
        return (
          <ToastPrimitives.Root
            key={id}
            {...props}
            className={cn(
              "group pointer-events-auto relative flex w-full items-center justify-between space-x-2 overflow-hidden rounded-lg border p-4 pr-6 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
              variant === "destructive" &&
                "destructive group border-destructive bg-destructive text-destructive-foreground",
              variant === "success" &&
                "success group border-success bg-success/15 text-success",
              variant !== "destructive" && variant !== "success" && "bg-card text-foreground border-border"
            )}
          >
            <div className="grid gap-1">
              {title && <ToastPrimitives.Title className="text-sm font-semibold">{title}</ToastPrimitives.Title>}
              {description && (
                <ToastPrimitives.Description className="text-sm opacity-90">
                  {description}
                </ToastPrimitives.Description>
              )}
            </div>
            {action}
            <ToastPrimitives.Close
              onClick={() => dismiss(id)}
              className="absolute right-1 top-1 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-1 group-hover:opacity-100"
            >
              <X className="h-4 w-4" />
            </ToastPrimitives.Close>
          </ToastPrimitives.Root>
        );
      })}
      <ToastPrimitives.Viewport className="fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]" />
    </ToastPrimitives.Provider>
  );
}
