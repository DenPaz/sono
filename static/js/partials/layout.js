class LayoutCustomizer {
  constructor() {
    this.storageKey = "__SONO_CONFIG__";
    this.defaultConfig = {
      theme: "material",
    };
    const cached = localStorage.getItem(this.storageKey);
    this.config = cached ? JSON.parse(cached) : { ...this.defaultConfig };
    this.html = document.documentElement;
  }

  updateTheme = () => {
    localStorage.setItem(this.storageKey, JSON.stringify(this.config));
    this.html.setAttribute("data-theme", this.config.theme);
  };

  initEventListeners = () => {
    document.querySelectorAll("[data-theme-control]").forEach((control) => {
      control.addEventListener("click", () => {
        const value = control.getAttribute("data-theme-control");
        if (value === "toggle") {
          this.config.theme =
            this.config.theme === "material-dark"
              ? "material"
              : "material-dark";
        } else {
          this.config.theme = value;
        }
        this.updateTheme();
      });
    });
  };

  init = () => {
    this.updateTheme();
    window.addEventListener("DOMContentLoaded", this.initEventListeners);
  };
}

new LayoutCustomizer().init();
