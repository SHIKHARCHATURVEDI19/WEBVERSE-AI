"use client";

import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { ArrowLeft, ArrowUpRight, History, LoaderCircle, RotateCcw, Sparkles } from "lucide-react";
import Link from "next/link";
import { z } from "zod";

import { apiRequest, formatDate } from "@/lib/api";
import {
  persistedGenerationResponseSchema,
  projectResponseSchema,
  restoreResponseSchema,
  versionSummarySchema,
} from "@/lib/site-spec";
import type { ProjectResponse, VersionSummary } from "@/lib/site-spec";

const versionsSchema = z.array(versionSummarySchema);

export function ProjectWorkspace({ projectId }: { projectId: string }) {
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [versions, setVersions] = useState<VersionSummary[]>([]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    try {
      setError(null);
      const encodedId = encodeURIComponent(projectId);
      const [nextProject, nextVersions] = await Promise.all([
        apiRequest(`/api/projects/${encodedId}`, projectResponseSchema),
        apiRequest(`/api/projects/${encodedId}/versions`, versionsSchema),
      ]);
      setProject(nextProject);
      setVersions(nextVersions);
      setPrompt(nextProject.current_version.site_spec.project.description);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The project workspace could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => void loadWorkspace(), 0);
    return () => window.clearTimeout(initialLoad);
  }, [loadWorkspace]);

  async function generate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (prompt.trim().length < 10 || busy) return;
    setBusy(true);
    setError(null);
    try {
      await apiRequest(`/api/projects/${encodeURIComponent(projectId)}/generate`, persistedGenerationResponseSchema, {
        method: "POST",
        body: JSON.stringify({ prompt: prompt.trim(), enable_3d: true }),
      });
      await loadWorkspace();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "A new version could not be generated.");
    } finally {
      setBusy(false);
    }
  }

  async function restore(version: VersionSummary) {
    if (busy || project?.current_version_id === version.id) return;
    setBusy(true);
    setError(null);
    try {
      await apiRequest(
        `/api/projects/${encodeURIComponent(projectId)}/versions/${encodeURIComponent(version.id)}/restore`,
        restoreResponseSchema,
        { method: "POST" },
      );
      await loadWorkspace();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The version could not be restored.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <main className="workspace-shell workspace-state"><LoaderCircle className="spin" /> Loading workspace…</main>;
  if (!project) return <main className="workspace-shell workspace-state"><p role="alert">{error || "Project not found."}</p><Link href="/">Return to Studio</Link></main>;

  return (
    <main className="workspace-shell">
      <header className="workspace-topbar">
        <Link href="/"><ArrowLeft size={15} /> Back to Studio</Link>
        <span className="brand">webverse<span className="brand-ai">.ai</span></span>
      </header>
      <section className="workspace-hero">
        <div><span className="section-kicker">PROJECT WORKSPACE · {project.site_type.toUpperCase()}</span><h1>{project.name}</h1><p>Saved as an immutable sequence of validated SiteSpec snapshots.</p></div>
        <div className="workspace-current"><span>CURRENT VERSION</span><strong>v{project.current_version_number}</strong><Link href={`/preview/${project.id}/${project.current_version_id}`}>Open preview <ArrowUpRight size={14} /></Link></div>
      </section>
      {error && <p className="feedback error" role="alert">{error}</p>}
      <div className="workspace-columns">
        <section className="workspace-generate" aria-labelledby="generate-version-title">
          <span className="section-kicker">CREATE A NEW SNAPSHOT</span><h2 id="generate-version-title">Generate next version</h2>
          <form onSubmit={generate}>
            <label htmlFor="revision-prompt">Describe the revised direction</label>
            <textarea id="revision-prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={7} maxLength={4000} />
            <button className="generate-button" disabled={busy || prompt.trim().length < 10} type="submit">{busy ? <><LoaderCircle className="spin" size={15} /> Saving…</> : <><Sparkles size={15} /> Generate version {project.current_version_number + 1}</>}</button>
          </form>
        </section>
        <section className="version-history" aria-labelledby="version-history-title">
          <div className="history-heading"><div><span className="section-kicker">IMMUTABLE HISTORY</span><h2 id="version-history-title">Version history</h2></div><History size={19} /></div>
          <div className="version-list">
            {versions.map((version) => (
              <article className={version.id === project.current_version_id ? "current" : ""} key={version.id}>
                <div className="version-number"><strong>v{version.version_number}</strong>{version.id === project.current_version_id && <span>Current</span>}</div>
                <div className="version-meta"><strong>{version.change_description}</strong><span>{formatDate(version.created_at)}</span></div>
                <div className="version-actions"><Link href={`/preview/${project.id}/${version.id}`}>Preview</Link><button type="button" disabled={busy || version.id === project.current_version_id} onClick={() => void restore(version)}><RotateCcw size={12} /> Restore</button></div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
