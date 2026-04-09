"use client";

import { useState } from "react";
import { deliverSlack } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

interface SlackDeliveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  summaryText: string;
}

export function SlackDeliveryModal({ isOpen, onClose, summaryText }: SlackDeliveryModalProps) {
  const [webhookUrl, setWebhookUrl] = useState("");
  const [channel, setChannel] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSend = async () => {
    if (!webhookUrl.startsWith("https://hooks.slack.com/")) {
      setStatus("error");
      setErrorMsg("Invalid Webhook URL. Must start with https://hooks.slack.com/");
      return;
    }
    
    setIsSending(true);
    setStatus("idle");
    setErrorMsg("");

    try {
      await deliverSlack(summaryText, webhookUrl, channel || undefined);
      setStatus("success");
      setTimeout(() => {
        onClose();
        setStatus("idle");
      }, 2000);
    } catch (e: unknown) {
      setStatus("error");
      if (e instanceof Error) {
        setErrorMsg(e.message || "Failed to deliver payload to Slack");
      } else {
        setErrorMsg("Failed to deliver payload to Slack");
      }
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Send to Slack</DialogTitle>
          <DialogDescription>
            Deliver the generated team standup to a Slack channel via an Incoming Webhook.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Webhook URL (Required)</Label>
            <Input 
              type="password" 
              placeholder="https://hooks.slack.com/services/T000.../B000.../XXXX..." 
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
            />
            <p className="text-[10px] text-muted-foreground">URL is never stored. We send the request directly to Slack.</p>
          </div>

          <div className="space-y-2">
            <Label>Channel Override (Optional)</Label>
            <Input 
              placeholder="#engineering" 
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
            />
          </div>

          {status === "error" && (
            <Alert variant="destructive">
              <AlertCircle className="w-4 h-4"/>
              <AlertTitle>Delivery Failed</AlertTitle>
              <AlertDescription>{errorMsg}</AlertDescription>
            </Alert>
          )}

          {status === "success" && (
            <Alert className="bg-green-500/10 text-green-500 border-green-500/20">
              <CheckCircle2 className="w-4 h-4 text-green-500"/>
              <AlertTitle>Sent Successfully!</AlertTitle>
              <AlertDescription>Your team standup has been delivered.</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSending}>Cancel</Button>
          <Button onClick={handleSend} disabled={isSending || !webhookUrl}>
            {isSending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Send to Slack
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
