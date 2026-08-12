const navLinks = new Map(
  [...document.querySelectorAll('nav a')].map((link) => [link.hash.slice(1), link]),
);

const sectionObserver = new IntersectionObserver((entries) => {
  const visible = entries
    .filter((entry) => entry.isIntersecting)
    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

  if (!visible) return;
  for (const link of navLinks.values()) link.removeAttribute('aria-current');
  navLinks.get(visible.target.id)?.setAttribute('aria-current', 'true');
}, { rootMargin: '-25% 0px -60% 0px', threshold: [0, 0.2, 0.5] });

for (const id of navLinks.keys()) {
  const section = document.getElementById(id);
  if (section) sectionObserver.observe(section);
}
