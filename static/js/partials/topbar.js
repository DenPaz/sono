document.addEventListener('alpine:init', () => {
  Alpine.data('topbarData', () => {
    const el = document.getElementById('layout-topbar');

    return {
      get greeting() {
        const hour = new Date().getHours();
        if (hour < 12) return el.dataset.greetingMorning;
        if (hour < 18) return el.dataset.greetingAfternoon;
        return el.dataset.greetingEvening;
      },
    };
  });
});
