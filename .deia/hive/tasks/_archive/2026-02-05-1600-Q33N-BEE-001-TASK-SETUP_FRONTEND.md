# Task: Setup Next.js Frontend

**ID:** TASK-SETUP_FRONTEND
**Assigned To:** BEE-001
**Issued By:** Q33N
**Date:** 2026-02-05

---

## 1. Objective

Your primary objective is to correctly scaffold and initialize the Next.js project for the Human Dashboard in the `frontend` directory.

## 2. Context

Previous attempts to scaffold the project have been blocked by two recurring errors:
1.  An interactive prompt from `npx create-next-app` that requires user confirmation.
2.  A subsequent `pnpm install` failure (`Cannot create process, error code: 267`), likely due to an incomplete or corrupted initial scaffolding.

Your task is to execute this setup process robustly.

## 3. Action Plan

Execute the following steps precisely from the project root (`C:\Users\davee\OneDrive\Documents\GitHub\simdecisions`).

### 3.1. Ensure a Clean State

First, ensure the `frontend` directory is completely removed to prevent any state conflicts from previous failed attempts.

```bash
Remove-Item -Path "C:\Users\davee\OneDrive\Documents\GitHub\simdecisions\frontend" -Recurse -Force -ErrorAction SilentlyContinue
```

### 3.2. Scaffold the Next.js Project

Execute the `npx create-next-app` command. The `--yes` flag should handle the initial prompt, but you must ensure it completes successfully without interactive blocking.

```bash
npx create-next-app "C:\Users\davee\OneDrive\Documents\GitHub\simdecisions\frontend" --use-pnpm --ts --eslint --app --tailwind --src-dir --import-alias "@/*" --yes
```

### 3.3. Install Dependencies

Once the project is scaffolded, navigate into the new directory and install the dependencies using `pnpm`.

```bash
cd "C:\Users\davee\OneDrive\Documents\GitHub\simdecisions\frontend"
pnpm install
```

## 4. Success Criteria

The task is considered complete when:
1.  The `pnpm install` command finishes without any errors.
2.  You can successfully run `pnpm dev` from within the `frontend` directory, and the Next.js development server starts.

## 5. Reporting

Upon completion, create a response file in `.deia/hive/responses/` named `YYYY-MM-DD-HHMM-BEE-001-Q33N-RESPONSE-SETUP_FRONTEND.md` confirming successful setup and termination of the `pnpm dev` server.
