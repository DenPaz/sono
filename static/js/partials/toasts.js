const TOAST_DELAY = 2500;

function getOrCreateToastsContainer() {
  let container = document.getElementById('toasts-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toasts-container';
    container.className = 'toast toast-end toast-top z-50';
    document.body.appendChild(container);
  }
  return container;
}

function initToastTimer(toast) {
  const controller = new AbortController();
  const { signal } = controller;
  let timeoutId = null;
  let remaining = TOAST_DELAY;
  let startedAt = null;

  function dismiss() {
    controller.abort();
    clearTimeout(timeoutId);
    const data = Alpine.$data(toast);
    if (data) data.show = false;
    toast.addEventListener('transitionend', () => toast.remove(), {
      once: true,
    });
  }

  function start() {
    startedAt = Date.now();
    timeoutId = setTimeout(dismiss, remaining);
  }

  function pause() {
    clearTimeout(timeoutId);
    remaining -= Date.now() - startedAt;
  }

  toast.querySelector('button').addEventListener('click', dismiss, { signal });
  toast.addEventListener('mouseenter', pause, { signal });
  toast.addEventListener('mouseleave', start, { signal });

  start();
}

function createToast({ message, tags }) {
  const template = document.getElementById('toast-template');
  const toast = template.content.cloneNode(true).firstElementChild;

  toast.classList.add(`alert-${tags}`);
  toast.querySelector('[data-toast-message]').textContent = message;
  toast
    .querySelector('button')
    .classList.add(
      `hover:text-${tags}`,
      `hover:border-${tags}`,
      'hover:bg-transparent',
    );

  Alpine.initTree(toast);
  initToastTimer(toast);
  return toast;
}

window.showToasts = (messages) => {
  const container = getOrCreateToastsContainer();
  messages.forEach((msg) => container.appendChild(createToast(msg)));
};

document.addEventListener('messages', (event) => {
  window.showToasts(event.detail?.value ?? []);
});
