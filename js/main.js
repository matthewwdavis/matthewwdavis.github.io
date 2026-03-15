/* ==============================================
   main.js — lightweight interactivity
   ============================================== */

// ── Navbar: shadow on scroll + hamburger toggle ──
const navbar    = document.getElementById('navbar');
const hamburger = document.getElementById('hamburger');
const navLinks  = document.querySelector('.nav-links');
const themeToggle = document.getElementById('theme-toggle');

const THEME_STORAGE_KEY = 'site-theme';
const THEME_MODES = ['auto', 'dark', 'light'];

function getStoredThemeMode() {
  const savedThemeMode = localStorage.getItem(THEME_STORAGE_KEY);

  if (THEME_MODES.includes(savedThemeMode)) {
    return savedThemeMode;
  }

  return 'auto';
}

function applyThemeMode(mode) {
  const themeMode = THEME_MODES.includes(mode) ? mode : 'auto';

  if (themeMode === 'auto') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', themeMode);
  }

  if (themeToggle) {
    const icon = themeToggle.querySelector('i');
    const labelElement = themeToggle.querySelector('.theme-label');

    if (icon) {
      if (themeMode === 'auto') {
        icon.className = 'fa-solid fa-circle-half-stroke';
      } else if (themeMode === 'dark') {
        icon.className = 'fa-solid fa-moon';
      } else {
        icon.className = 'fa-solid fa-sun';
      }
    }

    const label = themeMode[0].toUpperCase() + themeMode.slice(1);
    if (labelElement) {
      labelElement.textContent = label;
    }
    themeToggle.setAttribute('aria-label', `Theme mode: ${label}. Click to change.`);
    themeToggle.setAttribute('title', `Theme: ${label} (click to cycle)`);
  }
}

applyThemeMode(getStoredThemeMode());

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const currentMode = getStoredThemeMode();
    const currentIndex = THEME_MODES.indexOf(currentMode);
    const nextMode = THEME_MODES[(currentIndex + 1) % THEME_MODES.length];

    localStorage.setItem(THEME_STORAGE_KEY, nextMode);
    applyThemeMode(nextMode);
  });

  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
    if (getStoredThemeMode() === 'auto') {
      applyThemeMode('auto');
    }
  });
}

window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
});

hamburger.addEventListener('click', () => {
  const open = hamburger.classList.toggle('open');
  navLinks.classList.toggle('open', open);
  hamburger.setAttribute('aria-expanded', open);
});

// Close mobile menu when a link is tapped
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('open');
    navLinks.classList.remove('open');
    hamburger.setAttribute('aria-expanded', false);
  });
});

// ── Fade-in sections as they enter the viewport ──
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target); // animate once
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll('.section, .project-card').forEach(el => {
  el.classList.add('fade-in');
  observer.observe(el);
});

// ── Recent publications: render from generated Scholar JSON ──
const publicationList = document.getElementById('publication-list');
const publicationUpdated = document.getElementById('publication-updated');

function formatUpdatedAt(value) {
  if (!value) {
    return '';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return '';
  }

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

async function loadRecentPublications() {
  if (!publicationList) {
    return;
  }

  try {
    const response = await fetch('data/publications.json', { cache: 'no-store' });

    if (!response.ok) {
      throw new Error('Failed to load publication data.');
    }

    const data = await response.json();
    const publications = Array.isArray(data.publications) ? data.publications.slice(0, 5) : [];
    const updatedText = formatUpdatedAt(data.updated_at);

    if (publicationUpdated) {
      publicationUpdated.textContent = updatedText ? `Last updated ${updatedText}.` : '';
    }

    if (publications.length === 0) {
      publicationList.innerHTML = `
        <li>
          Recent publications are available on
          <a href="https://scholar.google.com/citations?user=NVSRY8kAAAAJ&hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a>.
        </li>
      `;
      return;
    }

    if (publicationUpdated) {
      publicationUpdated.textContent = '';
    }

    publicationList.innerHTML = publications.map((publication) => {
      const safeTitle = publication.title || 'Untitled publication';
      const safeUrl = publication.url || 'https://scholar.google.com/citations?user=NVSRY8kAAAAJ&hl=en';
      const authors = publication.authors ? `<span class="publication-meta">${publication.authors}</span>` : '';
      const venueParts = [publication.venue, publication.year].filter(Boolean).join(', ');
      const venue = venueParts ? `<span class="publication-meta">${venueParts}</span>` : '';

      return `
        <li>
          <a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${safeTitle}</a>
          ${authors}
          ${venue}
        </li>
      `;
    }).join('');
  } catch (error) {
    publicationList.innerHTML = `
      <li>
        Recent publications are available on
        <a href="https://scholar.google.com/citations?user=NVSRY8kAAAAJ&hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a>.
      </li>
    `;
  }
}

loadRecentPublications();
