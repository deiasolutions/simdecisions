# ADR-007: Choose MkDocs for Project Documentation Stack

**Status:** PROPOSED
**Date:** 2026-02-05
**Author:** Gemini
**Reviewers:** [Pending]

---

## Summary

This ADR proposes the adoption of **MkDocs with the MkDocs-Material theme** as the primary documentation stack for the `simdecisions` project. This solution will provide user-friendly, online-accessible, and AI-parsable documentation, which can be easily maintained and deployed.

---

## Context

### Problem

The `simdecisions` project requires a robust yet user-friendly documentation system to serve both human users (e.g., package downloaders) and AI agents. Currently, documentation is ad-hoc (e.g., individual ADRs), lacking a centralized, navigable, and easily accessible online presence.

### Requirements

1.  **Online Accessibility:** Documentation must be deployable online for public consumption.
2.  **Human-Readable:** Content should be well-formatted, easy to navigate, searchable, and aesthetically pleasing.
3.  **AI-Readable:** The underlying format must be structured and easily parsable by AI agents for understanding and processing.
4.  **Maintainability:** The system should be easy for developers to write and update documentation using a simple, widely adopted syntax.
5.  **Integration:** Ideally, the solution should integrate well with the existing project's likely Python ecosystem.
6.  **Scalability:** The stack should be able to accommodate growing documentation over time (e.g., user guides, API references, architectural decisions).

---

## Decision

Adopt **MkDocs** (a Python-based static site generator) utilizing the **MkDocs-Material theme** as the documentation stack for the `simdecisions` project.

---

## Architecture/Design

The documentation stack will operate as follows:

1.  **Source Files:** Documentation content will be written in Markdown (`.md`) files and organized within a dedicated `docs/` subdirectory in the `simdecisions` project root.
2.  **Configuration:** A `mkdocs.yml` file will be created in the project root to configure the site title, navigation structure, theme, and other settings.
3.  **Static Site Generation:** MkDocs will process the Markdown files and `mkdocs.yml` to generate a complete static HTML website into a `site/` directory.
4.  **Deployment:** The contents of the `site/` directory can then be hosted on any static site hosting service (e.g., GitHub Pages, Netlify, Vercel), making it accessible online.

```
simdecisions/
├── mkdocs.yml
├── docs/
│   ├── index.md        (Homepage)
│   ├── how-to-use.md
│   ├── installation.md
│   ├── specs/
│   │   ├── ADR-006-Hive-Control-Plane.md
│   │   └── ADR-007-Documentation-Stack.md
│   └── ...
├── src/                (Project source code)
└── ...
```

---

## Pros

*   **Markdown Simplicity:** Uses standard Markdown for content, making it highly accessible for writing and easily parsable by AI.
*   **User-Friendly:** The MkDocs-Material theme provides a modern, responsive, and searchable UI out-of-the-box, enhancing the human reading experience.
*   **Python Ecosystem Alignment:** Being Python-based, it integrates naturally with Python-heavy projects like `simdecisions`.
*   **Easy Deployment:** Generates a static site, which is simple and cost-effective to host (e.g., GitHub Pages).
*   **Low Maintenance Overhead:** The build process is straightforward, and there are no server-side components to manage.
*   **Extensible:** Supports plugins for additional functionality (e.g., diagrams, mathjax).

---

## Cons

*   **Static Nature:** As a static site generator, it is not suitable for dynamic content or interactive applications within the documentation itself.
*   **Python Dependency:** Requires a Python environment to build the documentation, which might be an extra dependency if the project wasn't already Python-based.

---

## Alternatives Considered

*   **Sphinx:** A powerful Python documentation generator, widely used, especially for API reference. However, it has a steeper learning curve, often uses reStructuredText (less common than Markdown), and can be overkill for general-purpose, user-friendly documentation.
*   **Docusaurus:** A modern documentation framework built on React. Offers excellent features and themes. However, it introduces a JavaScript/Node.js dependency, which might be an unnecessary additional tech stack for a primarily Python project.

---

## Implications

*   A new `docs/` directory will be created within the `simdecisions` project.
*   A `mkdocs.yml` configuration file will be added to the project root.
*   The project's development environment will need Python and `pip` to install MkDocs and its theme.
*   Deployment will require a static site hosting solution (e.g., configuring GitHub Pages for the repository).

---

## Implementation Phases

1.  **Phase 1: Initial Setup:** Install MkDocs and MkDocs-Material. Initialize the documentation project (`mkdocs new .`).
2.  **Phase 2: Basic Configuration:** Configure `mkdocs.yml` with basic project info and navigation.
3.  **Phase 3: Content Migration:** Migrate existing ADRs and feedback documents into Markdown pages within `docs/specs/`.
4.  **Phase 4: Initial Content Creation:** Create an `index.md` homepage and placeholder pages for key user documentation.
5.  **Phase 5: Local Preview:** Verify the documentation renders correctly using `mkdocs serve`.
6.  **Phase 6: Deployment:** Set up GitHub Pages or a similar service to host the generated site.

---

## References

*   [MkDocs Official Website](https://www.mkdocs.org/)
*   [MkDocs-Material Theme](https://squidfunk.github.io/mkdocs-material/)
