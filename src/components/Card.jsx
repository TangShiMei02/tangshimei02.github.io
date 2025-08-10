import React from 'react';

function Card({ icon, title, href, children }) {
  return (
    <article className="bg-card rounded-2xl p-4 shadow-lg transition-transform hover:-translate-y-1">
      <div className="text-5xl">{icon}</div>
      <h3 className="text-xl font-bold">{title}</h3>
      <p>{children}</p>
      {href && (
        <a href={href} className="inline-block bg-secondary text-white px-4 py-2 rounded-full">
          了解更多
        </a>
      )}
    </article>
  );
}

export default Card;