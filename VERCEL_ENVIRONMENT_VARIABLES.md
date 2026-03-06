# Vercel Environment Variables (summary)

This file summarizes Vercel environment variable practices relevant to this
project.

Key points
- Environment variables are key=value pairs configured outside source code.
- Values can be sensitive (tokens) and are encrypted at rest in Vercel.
- Changes apply to new deployments only; they do not retroactively change
  prior deployments.

Size limits
- Total per-deployment environment variables: 64 KB (all runtimes listed).
- Edge Functions / Middleware: limit of 5 KB per environment variable.

Environments
- Production: applied on next Production Deployment (push to main or `vercel --prod`).
- Preview: applied to Preview Deployments (branches other than Production).
- Development: used by `vercel dev` or local runs; `vercel env pull` downloads them.

Local development
- Define local variables in a `.env.local` file at the project root as `KEY=VALUE`.
- Or run:

```powershell
vercel env pull
```

  This creates a `.env` file populated from the Vercel project's Development
  environment.

Best practices for this repo
- Keep secrets only in Vercel/project environment settings (do not commit
  secrets to the repo).
- Use descriptive variable names and document them in `DEVELOPMENT.md` or
  `README.md` so teammates know required keys.
- For deterministic builds, avoid putting mutable runtime state into env vars
  that are expected to remain stable across deployments unless versioned.

Commands
- Pull development env vars locally:

```powershell
vercel env pull
```

- Add a production env var via CLI (example):

```powershell
vercel env add MY_KEY production
```

See Vercel docs for full details: https://vercel.com/docs/concepts/projects/environment-variables
