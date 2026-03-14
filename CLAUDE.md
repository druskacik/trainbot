# TrainBot — AI design context

## Design Context

### Users
- **Who:** Travelers planning European train trips, especially those looking for sleeper and couchette options (European Sleeper, Nightjet, etc.).
- **Context:** They want to find the lowest fares between two stations, optionally for return trips, with control over seat type (any vs couchettes only).
- **Job to be done:** Choose departure and destination, set journey type and preferences, run a search, and get actionable results (price, dates, leg breakdown) with a direct link to book.

### Brand Personality

**Story:** TrainBot sits at the intersection of *ecology* and *technology*: travel by train instead of plane, with AI used to find the best way to get there. The brand should feel like that — thoughtful about the planet and smart about the route.

- **Three words:** *Calm, precise, grounded.*
- **Voice:** Quietly confident. No hype, no greenwashing. The product does the work; the interface gets out of the way. Copy is short, direct, and human.
- **Emotional goal:** Users should feel *oriented* — "I know what to do" — and *reassured* — "this is the smarter way to travel." Not flashy or playful; more like a reliable tool that respects their time and the planet.
- **What we're not:** Preachy, corporate-green, or tech-bro. No fake warmth, no gradients-for-the-sake-of-it. Minimalism and clarity over decoration.

### Aesthetic Direction
- **Driven by the brand:** Restrained, legible, plenty of space. Visual language should feel *grounded* (earth, rail, journey) and *precise* (data, clarity, one clear path). Prefer a single accent or a very small palette so the UI feels calm and intentional.
- **Minimalism:** Every element should earn its place. No decorative flourishes, no “AI slop” (gradient text, cyan+indigo, glass for glass's sake). Typography and spacing do the work; color supports hierarchy and actions.
- **Theme:** Light or dark (or both via system preference) is fine; the brand is not tied to dark mode. Choose contrast and readability over trend.
- **Anti-references:** Generic SaaS dashboards, crypto/AI landing pages, sustainability clichés (leaf logos, green overload). Avoid looking like “AI made this.”

### Design Principles
1. **One accent, clear hierarchy** — Use a single accent (or very small palette) for key actions and focus. Spacing and typography carry the rest; no competing colors.
2. **Token-first** — CSS custom properties for spacing, radius, colors, focus ring, shadows. Keeps the UI maintainable and themable without hardcoding.
3. **Accessible by default** — Visible focus (`:focus-visible`), sufficient contrast, touch targets ≥44px, `aria-live`/`aria-busy` for dynamic content, and respect `prefers-reduced-motion`.
4. **Calm and scannable** — The flow “From/To → options → Search → results” should be obvious. Whitespace and structure over visual noise; empty and error states guide, not distract.
5. **Resilient and honest** — In-page errors and validation (no `alert()`), safe external links (`rel="noopener noreferrer"`), loading states that are clear and announced to assistive tech.

---

*This design context is the source of truth for all design decisions. The brand personality was created from scratch (ecology + technology, minimalism + clarity) and is independent of the current UI.*
