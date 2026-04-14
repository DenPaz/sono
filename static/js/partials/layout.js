class LayoutCustomizer {
  constructor() {
    this.storageKey = '__SONO_CONFIG__';

    this.themes = {
      light: 'material',
      dark: 'material-dark',
    };

    this.darkThemes = ['dark', 'dim', 'material-dark'];

    this.fontUrls = {
      default:
        'https://fonts.googleapis.com/css2?family=Inclusive+Sans:wght@400;500;600;700;800;900;1000&display=swap',
      inclusive:
        'https://fonts.googleapis.com/css2?family=Inclusive+Sans:wght@400;500;600;700;800;900;1000&display=swap',
      'dm-sans':
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@100;200;300;400;500;600;700;800;900;950;1000&display=swap',
      wix: 'https://fonts.googleapis.com/css2?family=Wix+Madefor+Text:wght@400;500;600;700;800;1000&display=swap',
      'ar-one':
        'https://fonts.googleapis.com/css2?family=AR+One+Sans:wght@400;500;600;700;800;1000&display=swap',
    };

    const cached = localStorage.getItem(this.storageKey);
    const parsed = cached ? JSON.parse(cached) : null;
    const mode = parsed?.mode === 'dark' ? 'dark' : 'light';

    this.config = {
      mode,
      theme: this.themes[mode],
      fontFamily: parsed?.fontFamily ?? 'default',
    };

    this.html = document.documentElement;
  }

  updateTheme = () => {
    localStorage.setItem(this.storageKey, JSON.stringify(this.config));
    this.html.setAttribute('data-theme', this.config.theme);
  };

  updateFont = () => {
    this.html.setAttribute('data-font-family', this.config.fontFamily);

    const url =
      this.fontUrls[this.config.fontFamily] ?? this.fontUrls['default'];
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
  };

  initEventListeners = () => {
    document.querySelectorAll('[data-theme-control]').forEach((control) => {
      control.addEventListener('click', () => {
        const value = control.getAttribute('data-theme-control');
        if (value === 'toggle') {
          this.config.mode = this.config.mode === 'dark' ? 'light' : 'dark';
        } else {
          this.config.mode = this.darkThemes.includes(value) ? 'dark' : 'light';
        }
        this.config.theme = this.themes[this.config.mode];
        this.updateTheme();
      });
    });

    document.querySelectorAll('[data-font-control]').forEach((control) => {
      control.addEventListener('click', () => {
        this.config.fontFamily = control.getAttribute('data-font-control');
        this.updateFont();
        localStorage.setItem(this.storageKey, JSON.stringify(this.config));
      });
    });
  };

  init = () => {
    this.updateTheme();
    this.updateFont();
    window.addEventListener('DOMContentLoaded', this.initEventListeners);
  };
}

new LayoutCustomizer().init();
