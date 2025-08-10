import React from 'react';
import './components/Navbar';
import './components/Card';

function App() {
  return (
  <div className="App">
    <Navbar />
    <div className="container mx-auto px-4">
      <Card icon="📝" title="关于我" href="about.html">关于我</Card>
      <Card icon="🔖" title="最新随笔" href="blog.html">最新随笔</Card>
    </div>
  </div>
);