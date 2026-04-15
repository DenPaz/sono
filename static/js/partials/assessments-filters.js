function serializeFormAsQueryString(form) {
  const payload = new FormData(form);
  const search = new URLSearchParams();

  payload.forEach((value, key) => {
    if (value === null || value === undefined || value === '') return;
    search.append(key, value.toString());
  });

  return search.toString();
}

document.addEventListener('change', (event) => {
  const form = event.target.closest('form[data-assessments-filters="true"]');
  if (!form || !window.htmx) return;

  const query = serializeFormAsQueryString(form);
  const targetUrl = form.getAttribute('hx-get');
  if (!targetUrl) return;

  const mergedUrl = query ? `${targetUrl}?${query}` : targetUrl;
  window.htmx.ajax('GET', mergedUrl, {
    target: form.getAttribute('hx-target'),
  });
});
