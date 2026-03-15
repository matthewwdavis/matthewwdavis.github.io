# Personal Website

A clean, responsive personal portfolio site built with vanilla HTML, CSS, and JavaScript.

## Project Structure

```
Website/
├── index.html          # Main page
├── css/
│   └── style.css       # Styles
├── js/
│   └── main.js         # Interactivity
├── assets/
│   └── profile.jpg     # Your profile photo (add this yourself)
└── README.md
```

## Personalizing the Site

Before publishing, update the following placeholders in `index.html`:

| Placeholder | What to change it to |
|---|---|
| `Davis MW` | Your name |
| `your@email.com` | Your email address |
| `yourusername` (×3 in social links) | Your GitHub / LinkedIn / X handles |
| Project card content | Your real projects, links, and tech stacks |
| `assets/profile.jpg` | Your own photo (same filename, or update the `src`) |

---

## Publishing on GitHub Pages

### 1. Create the repository

1. Go to [github.com](https://github.com) and sign in.
2. Click **+** → **New repository**.
3. Name it exactly: `<your-github-username>.github.io`  
   *(e.g. `davismw.github.io`)*
4. Set visibility to **Public**.
5. Click **Create repository**.

### 2. Push your local files

Open a terminal in this folder and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
git push -u origin main
```

### 3. Enable GitHub Pages

1. In your repository, go to **Settings → Pages**.
2. Under **Source**, select **Deploy from a branch**.
3. Choose branch **main** / root `/`.
4. Click **Save**.

Your site will be live at `https://<your-username>.github.io` within a minute or two.

### 4. Update after making changes

```bash
git add .
git commit -m "Update site"
git push
```

GitHub Pages will automatically redeploy on every push to `main`.
