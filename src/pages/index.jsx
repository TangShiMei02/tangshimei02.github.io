import React from 'react';
export default function Home() {
  return (
    <div className="min-h-screen bg-[rgb(var(--color-bg))] text-gray-900 dark:text-gray-100 transition-colors">
      {/* 导航 */}
      <nav className="flex justify-between items-center p-4">
        <h1 className="text-3xl font-handwritten text-primary">TangShiMei</h1>
        <button className="text-2xl">🌙</button>
      </nav>

      {/* 英雄区 */}
      <section className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-pink-200 via-purple-200 to-indigo-200 dark:from-gray-800 dark:via-gray-900 dark:to-black">
        <h2 className="text-5xl font-bold mb-4 animate-fade-in">欢迎来到主页</h2>
        <p className="text-xl mb-8">这里是我的个人空间，分享创作与思考</p>
        <a href="/blog" className="bg-secondary px-6 py-3 rounded-full text-white hover:scale-105 transition-transform">
          进入博客
        </a>
      </section>

      {/* 卡片网格 */}
      <section className="py-20 container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { icon: '👤', title: '关于我', href: '/about' },
            { icon: '📝', title: '我的博客', href: '/blog' },
            { icon: '💬', title: '留言板', href: '/guestbook' },
            { icon: '🎨', title: '作品展示', href: '/portfolio' },
          ].map(({ icon, title, href }) => (
            <article key={title} className="bg-[rgb(var(--color-card))] rounded-2xl p-6 shadow-lg hover:scale-105 transition-transform">
              <div className="text-4xl mb-4">{icon}</div>
              <h3 className="text-xl font-bold mb-2">{title}</h3>
              <a href={href} className="text-primary hover:underline">查看详情</a>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}