// 夜间模式
const toggleBtn = document.getElementById('theme-toggle');
const body = document.body;

if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark');
  toggleBtn.textContent = '☀️';
}

toggleBtn.addEventListener('click', () => {
  body.classList.toggle('dark');
  const isDark = body.classList.contains('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  toggleBtn.textContent = isDark ? '☀️' : '🌙';
});

// 时间
function updateTime() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false });
  const weekStr = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()];
  const elem = document.getElementById('time-display');
  if (elem) elem.textContent = `${timeStr} ${weekStr}`;
}
updateTime();
setInterval(updateTime, 1000);

// 一言
function loadHitokoto() {
  const h = document.getElementById('hitokoto');
  const f = document.getElementById('hitokoto-from');
  if (h) h.classList.add('hitokoto-fade');
  if (f) f.classList.add('hitokoto-fade');

  setTimeout(() => {
    fetch('https://v1.hitokoto.cn/?max_length=40')
      .then(res => res.json())
      .then(data => {
        if (h) {
          h.textContent = data.hitokoto;
          h.classList.remove('hitokoto-fade');
        }
        if (f) {
          f.textContent = data.from ? `—— ${data.from}` : '';
          f.classList.remove('hitokoto-fade');
        }
      })
      .catch(() => {
        if (h) {
          h.textContent = '今天也要加油呀~';
          h.classList.remove('hitokoto-fade');
        }
        if (f) f.classList.remove('hitokoto-fade');
      });
  }, 500);
}
loadHitokoto();
setInterval(loadHitokoto, 15000);

// 背景图（每10分钟换一次）
function changeBackground() {
  const url = 'https://source.unsplash.com/random/1920x1080/?nature,light';
  document.body.style.backgroundImage = `url('${url}')`;
}
setInterval(changeBackground, 600000); // 10分钟