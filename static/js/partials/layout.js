// Config
const STORAGE_KEY = '__SONO_CONFIG__';

const THEMES = {
  light: 'material',
  dark: 'material-dark',
};

const DEFAULT_FONT = 'default';

const FONT_URLS = {
  default:
    'https://fonts.googleapis.com/css2?family=Inclusive+Sans:wght@400;500;600;700;800;900;1000&display=swap',
  'dm-sans':
    'https://fonts.googleapis.com/css2?family=DM+Sans:wght@100;200;300;400;500;600;700;800;900;950;1000&display=swap',
  wix: 'https://fonts.googleapis.com/css2?family=Wix+Madefor+Text:wght@400;500;600;700;800;1000&display=swap',
  'ar-one':
    'https://fonts.googleapis.com/css2?family=AR+One+Sans:wght@400;500;600;700;800;1000&display=swap',
};

// State
function loadConfig() {
  try {
    const cached = localStorage.getItem(STORAGE_KEY);
    const parsed = cached ? JSON.parse(cached) : null;
    const mode = parsed?.mode === 'dark' ? 'dark' : 'light';
    return {
      mode,
      theme: THEMES[mode],
      fontFamily: parsed?.fontFamily ?? DEFAULT_FONT,
    };
  } catch {
    return { mode: 'light', theme: THEMES.light, fontFamily: DEFAULT_FONT };
  }
}

function saveConfig(config) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

// DOM Updates
function applyTheme(config) {
  document.documentElement.setAttribute('data-theme', config.theme);
  document.documentElement.setAttribute('data-mode', config.mode);
  saveConfig(config);
}

function applyFont(config) {
  const url = FONT_URLS[config.fontFamily] ?? FONT_URLS.default;

  document.documentElement.setAttribute('data-font-family', config.fontFamily);

  const linkId = 'google-font';
  let link = document.getElementById(linkId);

  if (!link) {
    link = document.createElement('link');
    link.id = linkId;
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }

  if (link.href !== url) {
    link.href = url;
  }

  saveConfig(config);
}

// Event Listeners
function initThemeControls(config) {
  document.querySelectorAll('[data-theme-control]').forEach((control) => {
    control.addEventListener('click', () => {
      const value = control.getAttribute('data-theme-control');
      if (value === 'toggle') {
        config.mode = config.mode === 'dark' ? 'light' : 'dark';
      } else if (value === 'light' || value === 'dark') {
        config.mode = value;
      }
      config.theme = THEMES[config.mode];
      applyTheme(config);
    });
  });
}

function initFontControls(config) {
  document.querySelectorAll('[data-font-control]').forEach((control) => {
    control.addEventListener('click', () => {
      config.fontFamily = control.getAttribute('data-font-control');
      applyFont(config);
    });
  });
}

// Initialization
const config = loadConfig();

applyTheme(config);
applyFont(config);

window.addEventListener('DOMContentLoaded', () => {
  initThemeControls(config);
  initFontControls(config);
});
