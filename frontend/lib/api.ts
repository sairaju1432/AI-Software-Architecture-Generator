export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type Project = {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
};

export type Generation = {
  id: string;
  project_id: string;
  prompt: string;
  status: string;
  error?: string;
  output?: ArchitectureOutput | null;
};

export type ArchitectureOutput = {
  functional_requirements: string[];
  non_functional_requirements: string[];
  recommended_architecture: Record<string, unknown>;
  microservices: Array<Record<string, unknown>>;
  database_schema: Record<string, unknown>;
  rest_api_design: Record<string, unknown>;
  mermaid_diagrams: Record<string, string>;
  raw: Record<string, unknown>;
};

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export function exportUrl(generationId: string, format: "markdown" | "json") {
  return `${API_URL}/generations/${generationId}/export?format=${format}`;
}
