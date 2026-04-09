import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ConditionalLayoutWrapper } from "@/components/ConditionalLayoutWrapper";
import { Providers } from "@/components/Providers";
import { TooltipProvider } from "@/components/ui/tooltip";
const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "gitpulse - AI standup generator",
  description: "AI-powered standup summaries from git commit history",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased min-h-screen bg-background text-foreground flex flex-col`}
      >
        <Providers>
          <TooltipProvider>
            <ConditionalLayoutWrapper>
              {children}
            </ConditionalLayoutWrapper>
          </TooltipProvider>
        </Providers>
      </body>
    </html>
  );
}

