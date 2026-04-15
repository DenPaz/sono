document.addEventListener('alpine:init', () => {
  Alpine.data('assessmentsWizard', ({ initialStep = 0 } = {}) => ({
    currentStep: initialStep,
    isSubmitting: false,
    hasUnsavedProgress: false,

    init() {
      document.body.addEventListener('htmx:beforeRequest', (event) => {
        const form = event.target;
        if (
          form &&
          form.matches(
            'form[hx-post*="/operacional/questionario/partials/passo/"]',
          )
        ) {
          this.isSubmitting = true;
          this.hasUnsavedProgress = true;
        }
      });

      document.body.addEventListener('htmx:afterSwap', (event) => {
        if (event.target?.id !== 'questionnaire-step-target') return;
        this.isSubmitting = false;

        const step = Number(event.target.dataset.currentStep);
        if (!Number.isNaN(step)) {
          this.currentStep = step;
        }

        if (event.target.dataset.status === 'completed') {
          this.hasUnsavedProgress = false;
        }
      });
    },

    warnOnUnsaved(event) {
      if (!this.hasUnsavedProgress || this.isSubmitting) return;
      event.preventDefault();
      event.returnValue = '';
    },
  }));
});
