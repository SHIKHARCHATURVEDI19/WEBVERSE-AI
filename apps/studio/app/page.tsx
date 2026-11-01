import { ArrowUpRight, Box, Layers3, WandSparkles } from "lucide-react";
import Link from "next/link";
import { CreatePanel } from "@/components/create-panel";
import { ProjectsPanel } from "@/components/projects-panel";

const examples = [
  { label: "Developer portfolio", detail: "A personal space with a living 3D centerpiece", icon: Layers3 },
  { label: "Restaurant experience", detail: "A warm digital front door for a great menu", icon: Box },
  { label: "Product showcase", detail: "Make a product the main character", icon: WandSparkles },
];

export default function HomePage() {
  return (
    <main className="studio-shell">
      <header className="topbar">
        <Link className="brand" href="/" aria-label="WebVerse home">
          <span className="brand-mark"><span /></span>
          <span>webverse<span className="brand-ai">.ai</span></span>
        </Link>
        <nav className="topnav" aria-label="Main navigation">
          <a href="#create">Create</a>
          <a href="#projects">My projects</a>
          <a href="#examples">Explore</a>
          <a href="#how-it-works">How it works</a>
        </nav>
        <button className="profile-button" type="button" aria-label="Profile menu">S</button>
      </header>

      <section className="hero" id="create">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> YOUR IDEA, IN THREE DIMENSIONS</div>
          <h1>Build a world.<br /><em>Not just</em> a website.</h1>
          <p className="hero-description">Describe the experience you imagine. WebVerse turns it into a responsive website with thoughtful design, real interactions and a little more dimension.</p>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="orbit-core"><span>W</span></div>
          <span className="orbit-label label-top">DESIGN</span>
          <span className="orbit-label label-right">MOTION</span>
          <span className="orbit-label label-bottom">DIMENSION</span>
        </div>
      </section>

      <section className="create-section" aria-labelledby="create-title">
        <div className="section-heading">
          <div><span className="section-kicker">START WITH A THOUGHT</span><h2 id="create-title">What should we create?</h2></div>
          <span className="step-label">01 <span>/</span> PROMPT</span>
        </div>
        <CreatePanel />
      </section>

      <ProjectsPanel />

      <section className="examples-section" id="examples">
        <div className="section-heading compact-heading">
          <div><span className="section-kicker">A FEW PLACES TO BEGIN</span><h2>Made for more than one kind of idea.</h2></div>
          <a className="text-link" href="#create">Start creating <ArrowUpRight size={15} /></a>
        </div>
        <div className="example-grid">
          {examples.map(({ label, detail, icon: Icon }, index) => (
            <article className={`example-card example-${index + 1}`} key={label}>
              <div className="example-icon"><Icon size={19} strokeWidth={1.6} /></div>
              <div><h3>{label}</h3><p>{detail}</p></div>
              <ArrowUpRight className="example-arrow" size={17} />
            </article>
          ))}
        </div>
      </section>

      <footer className="footer" id="how-it-works">
        <span>WEBVERSE AI <span className="footer-separator">/</span> EARLY STUDIO</span>
        <span>From a sentence to a whole experience.</span>
      </footer>
    </main>
  );
}
