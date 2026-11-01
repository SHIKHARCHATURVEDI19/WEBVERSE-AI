"use client";

import { useEffect, useState } from "react";
import { ArrowLeft, LoaderCircle } from "lucide-react";
import Link from "next/link";

import { SiteRenderer } from "@/components/site-preview";
import { apiRequest, formatDate } from "@/lib/api";
import { previewResponseSchema } from "@/lib/site-spec";
import type { PreviewResponse } from "@/lib/site-spec";

export function SavedVersionPreview({ projectId, versionId }: { projectId: string; versionId: string }) {
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void apiRequest(
      `/api/projects/${encodeURIComponent(projectId)}/preview/${encodeURIComponent(versionId)}`,
      previewResponseSchema,
    ).then(setPreview).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "This saved preview could not be loaded.");
    });
  }, [projectId, versionId]);

  if (error) return <main className="saved-preview-state"><p role="alert">{error}</p><Link href={`/projects/${projectId}`}><ArrowLeft size={14} /> Return to project</Link></main>;
  if (!preview) return <main className="saved-preview-state"><LoaderCircle className="spin" /> Loading immutable preview…</main>;

  return (
    <main className="saved-preview-shell">
      <header className="saved-preview-header">
        <Link href={`/projects/${projectId}`}><ArrowLeft size={14} /> Project workspace</Link>
        <div><span>IMMUTABLE PREVIEW</span><strong>{preview.project_name} · Version {preview.version.version_number}</strong></div>
        <time dateTime={preview.version.created_at}>{formatDate(preview.version.created_at)}</time>
      </header>
      <SiteRenderer spec={preview.version.site_spec} />
    </main>
  );
}
