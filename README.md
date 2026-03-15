# Matthew Davis Personal Website

Personal website for Matthew Davis, built as a static site with vanilla HTML, CSS, and JavaScript and deployed with GitHub Pages.

Live site: https://matthewwdavis.github.io/

## Features

- Responsive one-page layout with sections for About, Recent Publications, Projects, CV, and Contact
- Manual theme toggle with `Auto`, `Dark`, and `Light` modes
- Recent publications loaded from `data/publications.json`
- Automated weekly refresh of publication data from Google Scholar
- GitHub Pages deployment through GitHub Actions
- Clickable project cards linking to external repositories

## Project Structure

```text
Website/
├── .github/
│   └── workflows/
│       ├── deploy-pages.yml
│       └── update-publications.yml
├── css/
│   └── style.css
├── data/
│   └── publications.json
├── js/
│   └── main.js
├── scripts/
│   └── fetch_scholar_publications.py
├── index.html
├── Matthew_Davis_CV_2025-11-12_site.pdf
└── README.md
```

## Local Preview

Because this is a static site, there is no build step. To preview locally:

```bash
cd /Users/davismw/Documents/Website
python3 -m http.server 8000
```

Then open: http://localhost:8000

This is preferred over opening `index.html` directly because the publications section loads JSON with `fetch()`, which is blocked in many browsers for local `file://` pages.

## Updating the Site

Most content changes live in `index.html`.

- Edit section content, links, and project cards in `index.html`
- Edit colors, spacing, layout, and responsive behavior in `css/style.css`
- Edit interactivity, theme logic, and publication rendering in `js/main.js`
- Replace or add site images in the repository root and update file paths in HTML or CSS

## Publications Workflow

The Recent Publications section is populated from `data/publications.json`.

### Automatic updates

GitHub Actions runs `.github/workflows/update-publications.yml` every Monday and can also be triggered manually from the Actions tab.

The workflow:

1. Sets up Python 3.11
2. Installs `requests` and `beautifulsoup4`
3. Runs `scripts/fetch_scholar_publications.py`
4. Commits and pushes `data/publications.json` if publication data changed

### Manual update

To refresh publications locally:

```bash
cd /Users/davismw/Documents/Website
python3 -m pip install requests beautifulsoup4
python3 scripts/fetch_scholar_publications.py
```

## Deployment

This site deploys with GitHub Actions using `.github/workflows/deploy-pages.yml`.

Any push to `main` triggers a new deployment to GitHub Pages.

Typical update flow:

```bash
cd /Users/davismw/Documents/Website
git add .
git commit -m "Update site"
git push
```

## Notes

- The CV link in the navigation currently points to `Matthew_Davis_CV_2025-11-12_site.pdf`
- The publication source is the Google Scholar profile for user `NVSRY8kAAAAJ`
- Font Awesome icons are loaded from a CDN in `index.html`
