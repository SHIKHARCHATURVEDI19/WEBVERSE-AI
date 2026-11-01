import { z } from "zod";

const hexColor = z.string().regex(/^#[0-9A-Fa-f]{6}$/);

export const sectionTypeSchema = z.enum([
  "3d-hero", "hero", "about", "project-grid", "menu-grid", "gallery",
  "booking-form", "contact", "faq", "testimonials", "footer",
]);

const sceneSchema = z.object({
  preset: z.string(), enabled: z.boolean(), rotationSpeed: z.number().min(0).max(2),
}).strict();

const sectionSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/),
  type: sectionTypeSchema,
  title: z.string().max(180),
  scene: sceneSchema.optional(),
}).strict();

const pageSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/),
  path: z.string().startsWith("/"),
  title: z.string().max(120),
  sections: z.array(sectionSchema).max(40),
}).strict();

export const siteSpecSchema = z.object({
  schemaVersion: z.string(),
  project: z.object({
    name: z.string().min(1).max(120),
    category: z.enum(["portfolio", "restaurant", "other"]),
    description: z.string().max(4000),
  }).strict(),
  theme: z.object({
    colors: z.object({
      primary: hexColor, background: hexColor, surface: hexColor,
      text: hexColor, muted: hexColor,
    }).strict(),
    fonts: z.object({ display: z.string(), body: z.string() }).strict(),
    radius: z.enum(["small", "medium", "large"]),
  }).strict(),
  pages: z.array(pageSchema).min(1).max(20),
  assets: z.array(z.record(z.string(), z.unknown())),
  metadata: z.record(z.string(), z.unknown()),
}).strict();

export const generationResponseSchema = z.object({
  project_id: z.string(),
  run_id: z.string(),
  status: z.literal("completed"),
  provider: z.literal("mock"),
  site_spec: siteSpecSchema,
}).strict();

export const versionSummarySchema = z.object({
  id: z.string(),
  project_id: z.string(),
  version_number: z.number().int().positive(),
  change_description: z.string(),
  created_at: z.string(),
}).strict();

export const versionResponseSchema = versionSummarySchema.extend({
  site_spec: siteSpecSchema,
}).strict();

export const projectSummarySchema = z.object({
  id: z.string(),
  name: z.string(),
  slug: z.string(),
  site_type: z.enum(["portfolio", "restaurant", "other"]),
  status: z.enum(["active", "archived"]),
  current_version_id: z.string(),
  current_version_number: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
}).strict();

export const projectResponseSchema = projectSummarySchema.extend({
  current_version: versionResponseSchema,
}).strict();

export const persistedGenerationResponseSchema = z.object({
  project: projectResponseSchema,
  version: versionResponseSchema,
  run_id: z.string(),
  status: z.literal("completed"),
  provider: z.literal("mock"),
}).strict();

export const restoreResponseSchema = z.object({
  project: projectResponseSchema,
  version: versionResponseSchema,
  run_id: z.string(),
}).strict();

export const previewResponseSchema = z.object({
  project_id: z.string(),
  project_name: z.string(),
  version: versionResponseSchema,
}).strict();

export type SectionType = z.infer<typeof sectionTypeSchema>;
export type SiteSpec = z.infer<typeof siteSpecSchema>;
export type SiteSection = SiteSpec["pages"][number]["sections"][number];
export type GenerationResponse = z.infer<typeof generationResponseSchema>;
export type VersionSummary = z.infer<typeof versionSummarySchema>;
export type VersionResponse = z.infer<typeof versionResponseSchema>;
export type ProjectSummary = z.infer<typeof projectSummarySchema>;
export type ProjectResponse = z.infer<typeof projectResponseSchema>;
export type PersistedGenerationResponse = z.infer<typeof persistedGenerationResponseSchema>;
export type PreviewResponse = z.infer<typeof previewResponseSchema>;
