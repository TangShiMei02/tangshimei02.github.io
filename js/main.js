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


// 显示当前时间
function updateTime() {
  const now = new Date();
  // 格式化时间为 时:分:秒 星期几
  const timeStr = now.toLocaleTimeString();
  const weekStr = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()];
  document.getElementById('time-display').textContent = `${timeStr} ${weekStr}`;
}
// 每秒更新一次时间
updateTime();
setInterval(updateTime, 1000);

// 显示天气（替换成你的和风天气KEY）
const WEATHER_KEY = '你的和风天气KEY'; // 这里粘贴刚才复制的KEY
// 获取当前城市（自动定位，也可以手动改城市名，比如 '北京'）
function getWeather() {
  // 先获取IP定位（免费接口）
  fetch('https://ipapi.co/json/')
    .then(response => response.json())
    .then(location => {
      const city = location.city; // 自动获取城市名
      // 调用和风天气API
      fetch(`https://devapi.qweather.com/v7/weather/now?location=${city}&key=${WEATHER_KEY}`)
        .then(response => response.json())
        .then(weather => {
          if (weather.code === '200') {
            const now = weather.now;
            document.getElementById('weather-display').textContent = 
              `${city} ${now.text} ${now.temp}°C\n体感${now.feelsLike}°C`;
          } else {
            document.getElementById('weather-display').textContent = '天气获取失败';
          }
        });
    });
}
getWeather(); // 页面加载时获取天气


// 定时更换背景图（每5分钟换一次）
function changeBackground() {
  // 随机获取自然风景类图片（light参数确保背景偏亮，不影响文字阅读）
  const bgUrl = 'https://source.unsplash.com/random/1920x1080/?nature,light';
  document.body.style.backgroundImage = `url('${bgUrl}')`;
}
// 每300000毫秒（5分钟）换一次背景
setInterval(changeBackground, 300000);