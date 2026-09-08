/* Layered concept artwork: CSS perspective + projected signal particles.
   An illustrative research vision, not a simulation of a completed robot system. */
(() => {
  'use strict';
  const hero = document.querySelector('.hero-interface');
  if (!hero) return;
  const stage = hero.querySelector('.hero-stage');
  const scene = hero.querySelector('.hero-scene');
  const canvas = hero.querySelector('.hero-signals');
  const ctx = canvas.getContext('2d');
  const motion = hero.querySelector('.hero-motion');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(pointer: fine)');
  const modes = [...hero.querySelectorAll('.hero-mode')];
  const colors = [[40,125,149], [121,103,159], [151,116,55]];
  let selected = 0, paused = reduced.matches, visible = false, frame = 0;
  let width = 0, height = 0, elapsed = 0, last = 0, x = 0, y = 0, tx = 0, ty = 0;
  function labels() {
    const ko = document.documentElement.lang === 'ko';
    motion.querySelector('.hero-motion-label').textContent = paused ? (ko ? '모션 켜기' : 'Enable motion') : (ko ? '모션 멈춤' : 'Pause motion');
    motion.querySelector('.hero-motion-icon').textContent = paused ? '▷' : 'Ⅱ';
    const teamPhoto=document.querySelector('.welcome-photo img');
    if(teamPhoto)teamPhoto.alt=ko?'식사를 함께하는 PPEL 연구팀':'PPEL research team sharing a meal';
    const fields=document.querySelector('.welcome-fields');
    if(fields)fields.setAttribute('aria-label',ko?'연구 관심 분야':'Research interests');
    hero.querySelectorAll('.hero-art').forEach(art => { art.alt = ko ? '사람의 손과 로봇의 손이 유연한 인쇄전자막을 사이에 두고 마주하는 이미지. AI 생성 연구 콘셉트이며 실험 사진이 아닙니다.' : 'Human and robotic hands meeting across a flexible printed electronic film. AI-generated research concept, not an experimental photograph.'; });
  }
  function paint() {
    if (!ctx || !width || !height) return;
    ctx.clearRect(0, 0, width, height);
    const c = colors[selected];
    // Small depth-projected signals remain close to the painted interface.
    for (let i = 0; i < 42; i++) {
      const u = (i / 42 + elapsed * 0.000038) % 1;
      const lane = i % 3 - 1;
      const theta = u * Math.PI * 2 + lane * 1.15;
      const z = Math.cos(theta) * 24;
      const depth = 700 / (700 - z);
      const px = (.5 + (u - .5) * .45 * depth) * width;
      const py = (.468 + Math.sin(theta) * .038 * depth + lane * .014) * height;
      const alpha = .18 + (z + 24) / 48 * .4;
      ctx.beginPath(); ctx.arc(px, py, (i % 4 === 0 ? 1.9 : 1.15) * depth, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${c.join(',')},${alpha})`; ctx.fill();
    }
  }
  function draw(now) {
    frame = 0;
    if (paused || !visible || document.hidden) return;
    elapsed += last ? Math.min(now - last, 50) : 0; last = now;
    x += (tx - x) * .045; y += (ty - y) * .045;
    const drift = Math.sin(elapsed * .00036);
    scene.style.transform = `rotateX(${y * -2 + drift * .45}deg) rotateY(${x * 3 + Math.cos(elapsed * .00031) * .8}deg) translateY(${drift * 2}px)`;
    paint(); frame = requestAnimationFrame(draw);
  }
  function sync() {
    cancelAnimationFrame(frame); frame = 0; last = 0;
    hero.dataset.motion = paused ? 'paused' : 'running';
    if (paused) { x = y = tx = ty = 0; scene.style.transform = 'none'; paint(); }
    if (!paused && visible && !document.hidden) frame = requestAnimationFrame(draw);
    labels();
  }
  function resize() {
    const r = stage.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 1.75);
    width = r.width; height = r.height;
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    paint();
  }
  modes.forEach((button, index) => button.addEventListener('click', () => {
    selected = index;
    modes.forEach((item, i) => item.setAttribute('aria-pressed', String(i === index)));
    hero.querySelectorAll('.hero-panel').forEach((panel, i) => { panel.hidden = i !== index; });
    hero.style.setProperty('--signal-rgb', colors[index].join(','));
    paint();
  }));
  stage.addEventListener('pointermove', event => {
    if (paused || !fine.matches || event.pointerType === 'touch') return;
    const r = stage.getBoundingClientRect();
    tx = (event.clientX - r.left) / r.width - .5;
    ty = (event.clientY - r.top) / r.height - .5;
  }, {passive:true});
  stage.addEventListener('pointerleave', () => { tx = ty = 0; });
  motion.addEventListener('click', () => { paused = !paused; sync(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; sync(); });
  document.addEventListener('visibilitychange', sync);
  document.addEventListener('ppel:language', labels);
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }, {threshold:.05}).observe(stage);
  new ResizeObserver(resize).observe(stage);
  motion.hidden = false; resize(); sync();
})();
