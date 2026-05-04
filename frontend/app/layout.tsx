import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Car Agent Platform",
  description: "Painel SaaS para atendimento IA via WhatsApp",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
