document.querySelectorAll('[data-target]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(`.${link.dataset.target}`);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
