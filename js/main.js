/* 夜间模式切换 + 记忆 */
const toggleBtn = document.getElementById('theme-toggle');
const body = document.body;

// 页面加载时读取本地存储
if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark');
  toggleBtn.textContent = '☀️'; // 白天图标
}

// 点击按钮切换
toggleBtn.addEventListener('click', () => {
  body.classList.toggle('dark');
  const isDark = body.classList.contains('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  toggleBtn.textContent = isDark ? '☀️' : '🌙';
});