const TOAST_DELAY = 2500;

function getOrCreateToastsContainer() {
  let container = document.getElementById("toasts-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toasts-container";
    container.className = "toast toast-end toast-top z-50";
    document.body.appendChild(container);
  }
  return container;
}

function initToastTimer(toast) {
  const controller = new AbortController();
  const { signal } = controller;
  let timeoutId = null;

  function dismiss() {
    controller.abort();
    clearTimeout(timeoutId);
    const data = Alpine.$data(toast);
    if (data) data.show = false;
    toast.addEventListener("transitionend", () => toast.remove(), {
      once: true,
    });
  }

  function start() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(dismiss, TOAST_DELAY);
  }

  function pause() {
    clearTimeout(timeoutId);
  }

  toast.querySelector("button").addEventListener("click", dismiss, { signal });
  toast.addEventListener("mouseenter", pause, { signal });
  toast.addEventListener("mouseleave", start, { signal });

  start();
}

function createToast({ message, tags }) {
  const template = document.getElementById("toast-template");
  const toast = template.content.cloneNode(true).firstElementChild;

  toast.classList.add(`alert-${tags}`);
  toast.querySelector("[data-toast-message]").textContent = message;
  toast
    .querySelector("button")
    .classList.add(
      `hover:text-${tags}`,
      `hover:border-${tags}`,
      "hover:bg-transparent",
    );

  Alpine.initTree(toast);
  initToastTimer(toast);
  return toast;
}

window.showToasts = (messages) => {
  const container = getOrCreateToastsContainer();
  messages.forEach((msg) => container.appendChild(createToast(msg)));
};

document.addEventListener("messages", (event) => {
  window.showToasts(event.detail?.value ?? []);
});
