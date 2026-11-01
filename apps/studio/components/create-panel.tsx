"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { ArrowUpRight, LoaderCircle, Sparkles } from "lucide-react";
import Link from "next/link";

import { SitePreview } from "@/components/site-preview";
import { apiRequest } from "@/lib/api";
import { persistedGenerationResponseSchema } from "@/lib/site-spec";
import type { PersistedGenerationResponse } from "@/lib/site-spec";

type SiteCategory = "portfolio" | "restaurant" | "other";
const starterPrompts: Record<SiteCategory, string> = {
  portfolio: "Create a distinctive developer portfolio with an abstract 3D sculpture in the hero, a selected-work gallery, skills, experience and a contact section. Use a warm cream and burnt-orange palette.",
  restaurant: "Create a premium Italian restaurant website with a warm cream palette, a floating 3D pizza hero, signature menu, gallery, reservation form and location details.",
  other: "Create an immersive website for my idea. Give it a strong visual identity, useful pages, responsive layouts and one memorable interactive 3D moment.",
};

export function CreatePanel() {
  const [category, setCategory] = useState<SiteCategory>("portfolio");
  const [prompt, setPrompt] = useState(starterPrompts.portfolio);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<PersistedGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function chooseCategory(next: SiteCategory) {
    setCategory(next);
    setPrompt(starterPrompts[next]);
    setResult(null);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (prompt.trim().length < 10 || busy) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiRequest("/api/projects", persistedGenerationResponseSchema, {
        method: "POST",
        body: JSON.stringify({ prompt: prompt.trim(), category, enable_3d: true }),
      });
      setResult(data);
      window.dispatchEvent(new CustomEvent("webverse:project-created", { detail: data.project.id }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="composer-wrap">
      <div className="category-row" role="group" aria-label="Website category">
        {(["portfolio", "restaurant", "other"] as SiteCategory[]).map((item) => (
          <button className={`category-chip ${category === item ? "selected" : ""}`} key={item} type="button" onClick={() => chooseCategory(item)}>
            <span className="chip-mark" />{item === "other" ? "Something else" : item[0].toUpperCase() + item.slice(1)}
          </button>
        ))}
      </div>
      <form className="prompt-card" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="website-prompt">Describe the website you want to create</label>
        <textarea id="website-prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={4} maxLength={4000} placeholder="Describe the website you have in mind..." />
        <div className="prompt-footer">
          <span className="prompt-hint"><Sparkles size={14} /> Be specific. The details make it yours.</span>
          <button className="generate-button" type="submit" disabled={busy || prompt.trim().length < 10}>
            {busy ? <><LoaderCircle className="spin" size={16} /> Working...</> : <>Generate concept <ArrowUpRight size={16} /></>}
          </button>
        </div>
      </form>
      {error && <p className="feedback error" role="alert">{error}</p>}
      {result && (
        <div className="feedback success" role="status">
          <div><strong>Project saved as version 1.</strong><span> The validated SiteSpec and generation run are now persisted.</span></div>
          <code>Project {result.project.id} · Run {result.run_id}</code>
          <div className="feedback-actions">
            <Link href={`/projects/${result.project.id}`}>Open workspace <ArrowUpRight size={13} /></Link>
            <Link href={`/preview/${result.project.id}/${result.version.id}`}>Open saved preview</Link>
          </div>
          <details><summary>View saved SiteSpec</summary><pre>{JSON.stringify(result.version.site_spec, null, 2)}</pre></details>
        </div>
      )}
      {result && <SitePreview spec={result.version.site_spec} />}
    </div>
  );
}
