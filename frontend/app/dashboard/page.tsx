"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, Project } from "@/lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("Food delivery platform");
  const [description, setDescription] = useState(
    "Customers, restaurants, drivers, payments, notifications and analytics",
  );
  const [error, setError] = useState("");

  async function load() {
    try {
      setProjects(await api<Project[]>("/projects"));
    } catch {
      setError("Sign in to view projects.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function create() {
    const project = await api<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    });
    setProjects([project, ...projects]);
  }

  async function upgrade() {
    const checkout = await api<{ checkout_url: string }>("/billing/checkout", { method: "POST" });
    window.location.href = checkout.checkout_url;
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black">Dashboard</h1>
          <p className="text-foreground/60">Recent projects, saved architectures, generation history and usage analytics.</p>
        </div>
        <Button onClick={() => localStorage.removeItem("token")}>Sign out</Button>
      </div>

      <section className="mt-8 grid gap-6 md:grid-cols-3">
        <Card>
          <p className="text-sm text-foreground/60">Projects</p>
          <p className="text-4xl font-bold">{projects.length}</p>
        </Card>
        <Card>
          <p className="text-sm text-foreground/60">Free tier</p>
          <p className="text-4xl font-bold">5/mo</p>
        </Card>
        <Card>
          <p className="text-sm text-foreground/60">Provider</p>
          <p className="text-4xl font-bold">Gemini</p>
        </Card>
      </section>

      <Card className="mt-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">Upgrade to Pro</h2>
            <p className="text-sm text-foreground/60">Connect Stripe env vars to enable subscription checkout.</p>
          </div>
          <Button onClick={upgrade}>Upgrade</Button>
        </div>
      </Card>

      <Card className="mt-8">
        <h2 className="text-xl font-bold">Create project</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_2fr_auto]">
          <Input value={name} onChange={(event) => setName(event.target.value)} />
          <Input value={description} onChange={(event) => setDescription(event.target.value)} />
          <Button onClick={create}>Create</Button>
        </div>
        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      </Card>

      <section className="mt-8 grid gap-4">
        {projects.map((project) => (
          <Link key={project.id} href={`/projects/${project.id}`}>
            <Card className="transition hover:border-primary">
              <h3 className="font-bold">{project.name}</h3>
              <p className="text-sm text-foreground/60">{project.description}</p>
            </Card>
          </Link>
        ))}
      </section>
    </main>
  );
}
