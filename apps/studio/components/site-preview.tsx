"use client";

import { useState } from "react";
import type { CSSProperties, ComponentType } from "react";
import { ArrowRight, CalendarDays, ExternalLink, MapPin } from "lucide-react";

import { ThreeHero } from "@/components/three-hero";
import type { SectionType, SiteSection, SiteSpec } from "@/lib/site-spec";

type SectionProps = {
  section: SiteSection;
  category: SiteSpec["project"]["category"];
  description: string;
};

function HeroSection({ section, category, description }: SectionProps) {
  const hasScene = section.type === "3d-hero" && section.scene?.enabled;
  return (
    <section className="preview-hero">
      <div className="preview-hero-copy">
        <span className="preview-kicker">{category === "restaurant" ? "WELCOME TO OUR TABLE" : "DESIGN · CODE · DIMENSION"}</span>
        <h3>{section.title}</h3>
        <p>{description.slice(0, 240)}</p>
        <button type="button" className="preview-cta">{category === "restaurant" ? "Explore the menu" : "See selected work"}<ArrowRight size={14} /></button>
      </div>
      {hasScene ? <ThreeHero /> : <div className="preview-hero-art" aria-hidden="true"><span>W</span></div>}
    </section>
  );
}

function GridSection({ section, category }: SectionProps) {
  const menu = section.type === "menu-grid" || category === "restaurant";
  const labels = menu ? ["Burrata & citrus", "Wild mushroom ravioli", "Tiramisu classico"] : ["Lumen identity", "Forma commerce", "Atlas interactive"];
  return (
    <section className="preview-section">
      <span className="preview-kicker">{menu ? "FROM THE KITCHEN" : "RECENT PROJECTS"}</span>
      <h4>{section.title}</h4>
      <div className="preview-card-grid">
        {labels.map((label, index) => <article key={label}><span className={`preview-card-art art-${index + 1}`} /><small>0{index + 1}</small><strong>{label}</strong></article>)}
      </div>
    </section>
  );
}

function AboutSection({ section, category }: SectionProps) {
  return <section className="preview-section preview-about"><span className="preview-kicker">OUR POINT OF VIEW</span><h4>{section.title}</h4><p>{category === "restaurant" ? "We cook the food we grew up around: generous, uncomplicated, and made slowly enough to matter." : "I combine expressive visual systems with dependable engineering to make digital work that feels clear, human, and memorable."}</p></section>;
}

function BookingSection({ section }: SectionProps) {
  return <section className="preview-section preview-booking"><div><span className="preview-kicker">RESERVATIONS</span><h4>{section.title}</h4></div><button type="button"><CalendarDays size={15} /> Choose a date</button></section>;
}

function ContactSection({ section, category }: SectionProps) {
  return <section className="preview-section preview-contact"><div><span className="preview-kicker">LET&apos;S CONNECT</span><h4>{section.title}</h4></div><p>{category === "restaurant" ? <><MapPin size={14} /> 28 Via del Sole · Open Tuesday–Sunday</> : <>hello@example.com <ExternalLink size={13} /></>}</p></section>;
}

function GenericSection({ section, category, description }: SectionProps) {
  return section.type === "gallery" || section.type === "testimonials" || section.type === "faq"
    ? <GridSection section={section} category={category} description={description} />
    : <AboutSection section={section} category={category} description={description} />;
}

const sectionRegistry: Record<SectionType, ComponentType<SectionProps>> = {
  "3d-hero": HeroSection,
  hero: HeroSection,
  about: AboutSection,
  "project-grid": GridSection,
  "menu-grid": GridSection,
  gallery: GenericSection,
  "booking-form": BookingSection,
  contact: ContactSection,
  faq: GenericSection,
  testimonials: GenericSection,
  footer: ContactSection,
};

export function SiteRenderer({ spec }: { spec: SiteSpec }) {
  const [activePath, setActivePath] = useState(spec.pages[0].path);
  const page = spec.pages.find((candidate) => candidate.path === activePath) ?? spec.pages[0];
  const previewStyle = {
    "--preview-primary": spec.theme.colors.primary,
    "--preview-bg": spec.theme.colors.background,
    "--preview-surface": spec.theme.colors.surface,
    "--preview-text": spec.theme.colors.text,
    "--preview-muted": spec.theme.colors.muted,
  } as CSSProperties;

  return (
    <section className="preview-result" aria-labelledby="preview-title">
      <div className="preview-result-heading">
        <div><span className="section-kicker">GENERATED CONCEPT</span><h2 id="preview-title">Your SiteSpec, brought to life.</h2></div>
        <span className="mock-badge"><span /> Deterministic mock</span>
      </div>
      <div className="browser-frame">
        <div className="browser-bar"><div className="browser-dots"><span /><span /><span /></div><span className="browser-address">webverse.local{page.path}</span><span className="browser-status">PREVIEW</span></div>
        <div className="generated-site" style={previewStyle}>
          <header className="preview-nav">
            <strong>{spec.project.name}</strong>
            <nav aria-label="Generated site pages">
              {spec.pages.map((item) => <button className={item.path === page.path ? "active" : ""} type="button" key={item.id} onClick={() => setActivePath(item.path)}>{item.title}</button>)}
            </nav>
          </header>
          <main>
            {page.sections.map((section) => {
              const Section = sectionRegistry[section.type];
              return <Section key={section.id} section={section} category={spec.project.category} description={spec.project.description} />;
            })}
          </main>
          <footer className="preview-footer"><strong>{spec.project.name}</strong><span>Generated safely from SiteSpec · schema {spec.schemaVersion}</span></footer>
        </div>
      </div>
    </section>
  );
}

export const SitePreview = SiteRenderer;
