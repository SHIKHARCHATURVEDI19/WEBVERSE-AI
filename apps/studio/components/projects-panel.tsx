"use client";

import { useCallback, useEffect, useState } from "react";
import { ArrowUpRight, FolderOpen, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { z } from "zod";

import { apiRequest, formatDate } from "@/lib/api";
import { projectSummarySchema } from "@/lib/site-spec";
import type { ProjectSummary } from "@/lib/site-spec";

const projectListSchema = z.array(projectSummarySchema);

export function ProjectsPanel() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    try {
      setError(null);
      setProjects(await apiRequest("/api/projects", projectListSchema));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Projects could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => void loadProjects(), 0);
    const refresh = () => void loadProjects();
    window.addEventListener("webverse:project-created", refresh);
    return () => {
      window.clearTimeout(initialLoad);
      window.removeEventListener("webverse:project-created", refresh);
    };
  }, [loadProjects]);

  return (
    <section className="projects-section" id="projects" aria-labelledby="projects-title">
      <div className="section-heading compact-heading">
        <div><span className="section-kicker">SAVED WORLDS</span><h2 id="projects-title">My projects</h2></div>
        <span className="step-label">{projects.length.toString().padStart(2, "0")} PROJECTS</span>
      </div>
      {loading && <p className="projects-state"><LoaderCircle className="spin" size={15} /> Loading saved projects…</p>}
      {error && <p className="feedback error" role="alert">{error}</p>}
      {!loading && !error && projects.length === 0 && (
        <div className="projects-empty"><FolderOpen size={21} /><div><strong>No saved projects yet.</strong><span>Your first generated concept will appear here.</span></div></div>
      )}
      {projects.length > 0 && (
        <div className="projects-grid">
          {projects.map((project) => (
            <article className="project-card" key={project.id}>
              <div className="project-card-top"><span className="project-type">{project.site_type}</span><span className="project-status"><i /> {project.status}</span></div>
              <div><h3>{project.name}</h3><p>Version {project.current_version_number} · Updated {formatDate(project.updated_at)}</p></div>
              <Link href={`/projects/${project.id}`}>Open workspace <ArrowUpRight size={14} /></Link>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
