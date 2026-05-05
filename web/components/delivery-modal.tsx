"use client";

import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2, Send, Github, Mail, Hash } from "lucide-react";
import { deliverSlack, deliverEmail, deliverGist } from "@/lib/api";
import { useSession } from "next-auth/react";

interface DeliveryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  summary: string;
}

export function DeliveryModal({ open, onOpenChange, summary }: DeliveryModalProps) {
  const { data: session } = useSession();
  const [activeTab, setActiveTab] = useState("slack");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Slack state
  const [webhookUrl, setWebhookUrl] = useState("");
  const [channel, setChannel] = useState("");

  // Email state
  const [emailTo, setEmailTo] = useState("");

  // Gist state
  const [gistPublic, setGistPublic] = useState(false);

  const resetStatus = () => {
    setError(null);
    setSuccess(null);
  };

  const handleSlack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!webhookUrl) {
      setError("Webhook URL is required");
      return;
    }
    setIsLoading(true);
    resetStatus();
    try {
      await deliverSlack(summary, webhookUrl, channel || undefined);
      setSuccess("Successfully delivered to Slack!");
      setWebhookUrl("");
      setChannel("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to deliver to Slack");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailTo) {
      setError("Email address is required");
      return;
    }
    setIsLoading(true);
    resetStatus();
    try {
      await deliverEmail(summary, emailTo);
      setSuccess("Successfully sent email!");
      setEmailTo("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to send email");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGist = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    resetStatus();
    try {
      const response = await deliverGist(summary, gistPublic, session?.accessToken);
      setSuccess(`Successfully created Gist! URL: ${response.url}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create Gist. Are you signed in with proper permissions?");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(val) => {
      onOpenChange(val);
      if (!val) resetStatus();
    }}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Share Summary</DialogTitle>
          <DialogDescription>
            Choose how you want to deliver your standup summary.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={(v) => { setActiveTab(v); resetStatus(); }} className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="slack"><Hash className="w-4 h-4 mr-2"/> Slack</TabsTrigger>
            <TabsTrigger value="email"><Mail className="w-4 h-4 mr-2"/> Email</TabsTrigger>
            <TabsTrigger value="gist"><Github className="w-4 h-4 mr-2"/> Gist</TabsTrigger>
          </TabsList>
          
          <div className="mt-4 min-h-[200px]">
            {error && <div className="mb-4 text-sm text-red-500 bg-red-500/10 p-3 rounded">{error}</div>}
            {success && <div className="mb-4 text-sm text-green-500 bg-green-500/10 p-3 rounded break-all">{success}</div>}

            <TabsContent value="slack">
              <form onSubmit={handleSlack} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Webhook URL</label>
                  <Input 
                    placeholder="https://hooks.slack.com/services/..." 
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Channel (Optional)</label>
                  <Input 
                    placeholder="#standups" 
                    value={channel}
                    onChange={(e) => setChannel(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={isLoading} className="w-full">
                  {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                  Send to Slack
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="email">
              <form onSubmit={handleEmail} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email Address</label>
                  <Input 
                    type="email"
                    placeholder="team@example.com" 
                    value={emailTo}
                    onChange={(e) => setEmailTo(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" disabled={isLoading} className="w-full">
                  {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
                  Send Email
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="gist">
              <form onSubmit={handleGist} className="space-y-4">
                <div className="space-y-2 p-4 bg-muted/30 rounded border">
                  <p className="text-sm text-muted-foreground mb-4">
                    This will create a new GitHub Gist using your connected GitHub account.
                  </p>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="publicGist" 
                      checked={gistPublic}
                      onCheckedChange={(c) => setGistPublic(!!c)}
                    />
                    <label htmlFor="publicGist" className="text-sm font-medium cursor-pointer">
                      Make this Gist public
                    </label>
                  </div>
                </div>
                <Button type="submit" disabled={isLoading} className="w-full">
                  {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Github className="w-4 h-4 mr-2" />}
                  Create Gist
                </Button>
              </form>
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
