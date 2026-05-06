import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Whagent",
  description: "Dashboard operacional do Whagent",
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
