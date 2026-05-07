"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/* ─── Button ─── */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
  {
    variants: {
      variant: {
        primary:
          "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90",
        secondary:
          "bg-secondary text-secondary-foreground border border-border hover:bg-accent",
        danger:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        outline:
          "border border-border bg-transparent hover:bg-accent text-foreground",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-10 px-6",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "secondary",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || disabled}
        {...props}
      >
        {loading && <Loader2 className="animate-spin mr-2" size={16} />}
        {children}
      </Comp>
    );
  }
);
Button.displayName = "Button";

/* ─── Input ─── */
export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, type, ...props }, ref) => (
  <input
    type={type}
    className={cn(
      "flex h-9 w-full rounded-lg border border-input bg-muted px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors",
      className
    )}
    ref={ref}
    {...props}
  />
));
Input.displayName = "Input";

/* ─── Textarea ─── */
export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    className={cn(
      "flex min-h-[80px] w-full rounded-lg border border-input bg-muted px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors resize-none",
      className
    )}
    ref={ref}
    {...props}
  />
));
Textarea.displayName = "Textarea";

/* ─── Label ─── */
export function Label({
  className,
  children,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label
      className={cn("flex flex-col gap-1.5 text-sm font-medium text-foreground", className)}
      {...props}
    >
      {children}
    </label>
  );
}

/* ─── TextField (Label + Input combo) ─── */
export function TextField({
  label,
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <Label className={className}>
      <span className="text-muted-foreground">{label}</span>
      <Input {...props} />
    </Label>
  );
}

/* ─── TextArea with label ─── */
export function TextAreaField({
  label,
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  return (
    <Label className={className}>
      <span className="text-muted-foreground">{label}</span>
      <Textarea {...props} />
    </Label>
  );
}

/* ─── Badge ─── */
const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      tone: {
        neutral: "bg-muted text-muted-foreground",
        green: "bg-success/15 text-success border border-success/20",
        amber: "bg-warning/15 text-warning border border-warning/20",
        red: "bg-destructive/15 text-destructive border border-destructive/20",
        blue: "bg-primary/15 text-primary border border-primary/20",
      },
    },
    defaultVariants: {
      tone: "neutral",
    },
  }
);

export function Badge({
  children,
  tone,
  className,
}: {
  children: React.ReactNode;
  tone?: "neutral" | "green" | "amber" | "red" | "blue";
  className?: string;
}) {
  return (
    <span className={cn(badgeVariants({ tone }), className)}>{children}</span>
  );
}

/* ─── Empty State ─── */
export function EmptyState({
  title,
  text,
  action,
}: {
  title: string;
  text: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center gap-2">
      <strong className="text-foreground text-base">{title}</strong>
      <p className="text-muted-foreground text-sm max-w-xs">{text}</p>
      {action}
    </div>
  );
}

/* ─── Metric Tile ─── */
export function MetricTile({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail?: string;
}) {
  return (
    <div className="glass-panel flex flex-col gap-1 p-4">
      <span className="text-xs text-muted-foreground uppercase tracking-wider">
        {label}
      </span>
      <strong className="text-2xl font-bold text-foreground">{value}</strong>
      {detail ? (
        <small className="text-xs text-muted-foreground">{detail}</small>
      ) : null}
    </div>
  );
}

/* ─── Notice / Toast ─── */
export function NoticeBox({
  notice,
}: {
  notice: { tone: "success" | "error" | "neutral"; text: string } | null;
}) {
  if (!notice) return null;
  const toneClasses = {
    success: "bg-success/10 border-success/30 text-success",
    error: "bg-destructive/10 border-destructive/30 text-destructive",
    neutral: "bg-muted border-border text-muted-foreground",
  };
  return (
    <div
      className={cn(
        "px-4 py-3 rounded-lg border text-sm animate-in fade-in slide-in-from-top-1 duration-300",
        toneClasses[notice.tone]
      )}
    >
      {notice.text}
    </div>
  );
}

/* ─── Dialog / Modal ─── */
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";

export function Dialog({
  open,
  onOpenChange,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      {children}
    </DialogPrimitive.Root>
  );
}

export function DialogContent({
  children,
  title,
  className,
}: {
  children: React.ReactNode;
  title: string;
  className?: string;
}) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200" />
      <DialogPrimitive.Content
        className={cn(
          "fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 glass-panel p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200",
          className
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <DialogPrimitive.Title className="text-lg font-semibold text-foreground">
            {title}
          </DialogPrimitive.Title>
          <DialogPrimitive.Close className="rounded-md p-1 hover:bg-accent transition-colors">
            <X size={18} className="text-muted-foreground" />
          </DialogPrimitive.Close>
        </div>
        {children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

/* ─── Skeleton ─── */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-muted",
        className
      )}
    />
  );
}

/* ─── Status Dot ─── */
export function StatusDot({
  tone,
}: {
  tone: "green" | "amber" | "blue" | "red";
}) {
  const colors = {
    green: "bg-success",
    amber: "bg-warning",
    blue: "bg-primary",
    red: "bg-destructive",
  };
  return (
    <span
      className={cn("inline-block h-2 w-2 rounded-full", colors[tone])}
    />
  );
}
