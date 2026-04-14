class PasswordMeter {
  constructor(target) {
    this.input =
      typeof target === 'string' ? document.querySelector(target) : target;
    this.rules = [
      (v) => v.length >= 8, // r1: minimum length
      (v) => /[^0-9]/.test(v), // r2: not entirely numeric
      (v) => /[A-Z]/.test(v), // r3: uppercase
      (v) => /[a-z]/.test(v), // r4: lowercase
      (v) => /\W/.test(v), // r5: symbol
    ];
    this.update = this.update.bind(this);
    this.input?.addEventListener('input', this.update);
  }

  update() {
    if (!this.input) return;
    const val = this.input.value;
    let passed = 0;
    this.rules.forEach((rule, i) => {
      const attr = `data-pass-r${i + 1}`;
      if (rule(val)) {
        this.input.setAttribute(attr, '');
        passed++;
      } else {
        this.input.removeAttribute(attr);
      }
    });
    for (let i = 1; i <= this.rules.length; i++) {
      const attr = `data-pass-p${i * 20}`;
      if (i <= passed) {
        this.input.setAttribute(attr, '');
      } else {
        this.input.removeAttribute(attr);
      }
    }
  }

  destroy() {
    if (!this.input) return;
    this.input.removeEventListener('input', this.update);
    for (let i = 1; i <= this.rules.length; i++) {
      this.input.removeAttribute(`data-pass-r${i}`);
      this.input.removeAttribute(`data-pass-p${i * 20}`);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.querySelector('[data-password-meter]');
  if (input) new PasswordMeter(input);
});
