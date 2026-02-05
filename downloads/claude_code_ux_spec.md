# Claude Code UX Specification

> **Purpose**: This document describes the user interface (UX) specification for the Claude Code session selector UI, intended for replication in UI mockups or implementation by bots and developers.

---

## 🌍 Overview

This UX describes a split-pane interface used to navigate and launch code sessions within a local or cloud Git directory.

---

## 🔢 Layout

### ➞ Left Panel (Navigation Drawer)

- **Header Title**: `Claude Code` (white serif font)
- **Subtitle Tag**: `Research preview` (gray label badge)
- **Command Bar**:
  - Placeholder: `dir this directory`
  - Orange upload button with an arrow icon (⇧)
- **Path Display**:
  - Folder Path: `deiasolutions/deia` (button-style element)
  - Context Selector: `Default` (dropdown)
- **Sessions Section**:
  - Header: `Sessions`
  - If empty: `No sessions`
  - Filter control (dropdown, right-aligned): `Active ▼`

### ➞ Right Panel (Main Display)

- **Centered Pixel Art Icon**: Small orange 8-bit creature
- **Undertext**: `let's git together and code`
  - Styled with monospace font, `git` in bold

---

## 🎨 Visual Design

- **Theme**: Dark mode interface
  - Left Panel: Black or near-black solid fill
  - Right Panel: Dark gray dotted grid
- **Typography**:
  - Command text: Monospace
  - UI/Label text: Sans-serif or semi-serif
- **Buttons and Inputs**:
  - Rounded edges
  - Hover/active highlights
  - Upload button: orange color (for visibility)

---

## ⚙️ Functional Specs

- **Search/Command Bar**:
  - Accepts `dir`, `cd`, and other terminal-style commands
  - Triggers directory scan or file listing

- **Session Panel**:
  - Lists past or active sessions
  - Filters: Active, Archived, All (dropdown selector)

- **Welcome Panel**:
  - Only shows default screen if no session is active
  - Disappears when a session is opened

---

## 🖊️ Replication Prompt (Example)

```prompt
Replicate the Claude Code session selector UI:

1. Left panel with:
   - Title "Claude Code" and subtitle "Research preview"
   - Search input: "dir this directory" + upload icon
   - Path button: "deiasolutions/deia"
   - Dropdown: "Default"
   - Sessions list: empty + "Active" dropdown

2. Right panel:
   - Centered orange pixel character
   - Below text: `let's git together and code` ("git" in bold, monospace)

3. Style:
   - Dark theme
   - Dotted grid background
   - Monospace + sans-serif
   - Rounded buttons, orange accents
```

---

## 🎓 Authors
- Drafted by: ChatGPT-4o, based on screenshot provided by @daaaave-atx
- Date: 2025-10-25

---

## 🔧 Export Options
- [X] Markdown (.md)
- [ ] SVG wireframe (see below)

