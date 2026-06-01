"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { API_URL, api, Generation, Project } from "@/lib/api";

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [prompt, setPrompt] = useState(
    "Build a scalable food delivery platform with customers, restaurants, delivery agents, payments, notifications and analytics.",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setProject(await api<Project>(`/projects/${id}`));
    setGenerations(await api<Generation[]>(`/projects/${id}/generations`));
  }

  useEffect(() => {
    load();
  }, [id]);

  async function generate() {
    setLoading(true);
    setError("");
    try {
      const generation = await api<Generation>(`/projects/${id}/generations`, {
        method: "POST",
        body: JSON.stringify({ prompt }),
      });
      setGenerations([generation, ...generations]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  async function downloadExport(generationId: string, format: "markdown" | "json") {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_URL}/generations/${generationId}/export?format=${format}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      setError(await response.text());
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `generation-${generationId}.${format === "json" ? "json" : "md"}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const latest = generations[0];

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="text-3xl font-black">{project?.name}</h1>
      <p className="text-foreground/60">{project?.description}</p>

      <Card className="mt-8">
        <h2 className="text-xl font-bold">Generate architecture</h2>
        <textarea
          className="mt-4 min-h-36 w-full rounded-md border border-border bg-background p-3"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
        />
        <Button disabled={loading} onClick={generate} className="mt-4">
          {loading ? "Generating..." : "Run Gemini agent workflow"}
        </Button>
        {error && <p className="mt-3 rounded bg-red-500/10 p-3 text-sm text-red-500">{error}</p>}
      </Card>

      {latest?.output && (
        <section className="mt-8 grid gap-6">
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-bold">Latest architecture export</h2>
              <div className="flex gap-2">
                <Button onClick={() => downloadExport(latest.id, "markdown")}>Markdown</Button>
                <Button onClick={() => downloadExport(latest.id, "json")}>JSON</Button>
              </div>
            </div>
          </Card>

          <Card>
            <h2 className="font-bold">Functional requirements</h2>
            <ul className="mt-3 list-disc pl-5">
              {latest.output.functional_requirements.map((requirement, index) => (
                <li key={index}>{requirement}</li>
              ))}
            </ul>
          </Card>

          <Card>
            <h2 className="font-bold">Microservices</h2>
            <pre className="mt-3 overflow-auto text-sm">{JSON.stringify(latest.output.microservices, null, 2)}</pre>
          </Card>

          <Card>
            <h2 className="font-bold">System diagram</h2>
            <pre className="mt-3 overflow-auto rounded bg-black p-4 text-sm text-white">
              {latest.output.mermaid_diagrams.system}
            </pre>
          </Card>

          <Card>
            <h2 className="font-bold">Complete JSON export</h2>
            <pre className="mt-3 max-h-96 overflow-auto text-xs">{JSON.stringify(latest.output.raw, null, 2)}</pre>
          </Card>
        </section>
      )}

      <section className="mt-8">
        <h2 className="text-xl font-bold">Generation history</h2>
        {generations.map((generation) => (
          <Card key={generation.id} className="mt-3">
            <p className="font-semibold">{generation.status}</p>
            <p className="text-sm text-foreground/60">{generation.prompt}</p>
            {generation.error && <p className="text-red-500">{generation.error}</p>}
          </Card>
        ))}
      </section>
    </main>
  );
}
