"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("ChangeMe123!");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [googleIdToken, setGoogleIdToken] = useState("");
  const [error, setError] = useState("");

  function finish(accessToken: string) {
    localStorage.setItem("token", accessToken);
    router.push("/dashboard");
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const token = await api<{ access_token: string }>(`/auth/${mode === "login" ? "login" : "register"}`, {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: "Demo User" }),
      });
      finish(token.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  async function submitGoogle() {
    setError("");
    try {
      const token = await api<{ access_token: string }>("/auth/google", {
        method: "POST",
        body: JSON.stringify({ id_token: googleIdToken }),
      });
      finish(token.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google authentication failed");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl font-bold">Welcome to ArchGen AI</h1>
        <p className="mt-2 text-sm text-foreground/70">
          Sign in with email/password or paste a Google ID token from your OAuth client integration.
        </p>

        <form onSubmit={submit} className="mt-6 space-y-4">
          <Input value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="Email" />
          <Input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            placeholder="Password"
          />
          {error && <p className="rounded bg-red-500/10 p-2 text-sm text-red-500">{error}</p>}
          <Button className="w-full">{mode === "login" ? "Sign in" : "Create account"}</Button>
        </form>

        <div className="mt-6 space-y-3 border-t border-border pt-6">
          <Input
            value={googleIdToken}
            onChange={(event) => setGoogleIdToken(event.target.value)}
            placeholder="Google ID token"
          />
          <Button className="w-full bg-foreground text-background" disabled={!googleIdToken} onClick={submitGoogle}>
            Continue with Google
          </Button>
        </div>

        <button className="mt-4 text-sm text-primary" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
        </button>
      </Card>
    </main>
  );
}
