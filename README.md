# ai-visibility-site

Static HTML rebuild of **ai-visibility.com.au**, Reviewly's research site on how AI systems (ChatGPT, Perplexity, Google AI Overviews) decide which Australian businesses to name. It runs on a Cloudflare Worker with static assets.

> **Placeholder README (8 Nov 2026).** The full README is written with Tanya. Until then, see "Questions to answer" below.

## Status (8 Nov 2026)
- **Live domain:** ai-visibility.com.au is **still served by the older Manus build**, not by this repo. Nothing here reaches visitors until the domain is attached to this Worker (Tanya's OK needed).
- **This repo:** deploys to the Worker's own address, https://ai-visibility-com-au.tanya-fc9.workers.dev, on every push to `main`. Last deploy: 8 Jul 2026.
- **Open pull request:** `brand-v7-1-and-switch-prep` retires 7 pages that overlap reviewly.com.au (301 redirects), brings wording into line with Brand Bible V7.1, and adds pull request previews.

## How it fits with other systems
- Supports **reviewly.com.au**: pages that overlapped Reviewly's own pages now redirect there, and kept pages link to the matching Reviewly page.
- Sister Authority Hub site: **geooptimisation.com.au** (repo `geooptimisation-site`).
- Analytics: Google Analytics 4 tag on every page.

## How to run and publish
- **Preview locally:** `npx wrangler dev` from this folder, then open the address it prints.
- **Preview a change:** open a pull request to `main`. The "Preview pull request" workflow uploads a Worker version without deploying it and posts a link like `https://pr-<number>-ai-visibility-com-au.tanya-fc9.workers.dev/` on the pull request.
- **Publish:** merging to `main` deploys to the Worker (workflow "Deploy to Cloudflare Workers"). The live domain only follows once it's attached to the Worker in Cloudflare.
- Redirects live in `_redirects`. `*.md`, `.github` and `node_modules` aren't uploaded (see `.assetsignore`).
- **Claims check:** `check_claims.py` runs before every deploy and every preview. It blocks banned claims (exclusivity, guarantees, results within days, Reviewly called software or an SEO agency), the ® mark, em dashes, retired names and any percentage figure. If it fails, nothing is uploaded. Run it by hand with `python check_claims.py`.
- Before publishing: wording checked against Brand Bible V7.1, and every number on a page has an approved Proof Register entry.

## Required settings (names only)
GitHub Actions secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.

**This repository is public.** Never add notes, client details, keys or tokens here.

## Questions to answer (with Tanya)
1. Who is this site for, and what should a visitor do next?
2. How does it make money or save time for Reviewly (leads, authority for reviewly.com.au, both)?
3. Who owns its content and checks it each month?
4. Should the 2026 report bring back its figures once they're on the Proof Register?

## History
| Date | Change |
| --- | --- |
| 8 Jul 2026 | Static rebuild deployed to the Cloudflare Worker |
| 1–2 Nov 2026 | Overlapping pages retired with 301s; unverified research claims removed (branch `fix/reviewly-overlap`) |
| 8 Nov 2026 | Brand Bible V7.1 wording pass, figures without Proof Register entries removed, 404 page status fixed, pull request previews and claims check added |
