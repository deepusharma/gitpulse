# Web UI Guide

The GitPulse Web UI provides a fast, no-install experience for generating summaries from public GitHub repositories.

**Live URL:** https://gitpulse-kappa.vercel.app

## Features

1. **GitHub OAuth Integration:** Log in securely via GitHub to access your data.
2. **Dynamic Repository Selection:** Type your username, and GitPulse fetches your public repos. Use the multiselect dropdown to pick which ones to analyze.
3. **Analytics Dashboard:** Visual representation of your commit frequency and activity.
4. **Permanent History:** All generated summaries are saved to a PostgreSQL database so you can access them anytime at `/history`.

> Note: Currently supports public repositories only.
