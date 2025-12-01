import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from datetime import datetime

# 博客根目录（自动获取当前文件所在文件夹）
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
# 文章模板
POST_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - TangShiMei</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
  <header style="position: relative;">
    <h1 class="site-title">{title}</h1>
    <button id="theme-toggle" class="theme-btn" title="切换夜间模式">🌙</button>
  </header>

  <main class="post-content">
    <img src="img/{img_name}" alt="{title}" class="post-banner" />
    <p class="post-date">发布于 {date}</p>
    
{content}
  </main>

  <footer style="margin-top: 60px;">
    <a href="posts.html" class="btn">← 返回文章列表</a>
    <br><br>
    <small>© 2025 TangShiMei</small>
  </footer>

    <script src="../js/main.js"></script>
</body>
</html>
"""

# 文章列表页更新模板（添加新文章卡片）
POST_LIST_ITEM = """
    <!-- 新增文章 -->
    <article class="card">
      <img src="img/{img_name}" alt="{title}" class="post-img" />
      <h2>{title}</h2>
      <p class="post-date">{date}</p>
      <p>{summary}</p>
      <a href="posts/{filename}" class="btn">阅读全文</a>
    </article>
"""

def create_post():
    """生成文章文件并更新列表页"""
    title = title_entry.get()
    date = date_entry.get()
    summary = summary_entry.get()
    content = content_text.get("1.0", tk.END).strip()
    img_name = img_entry.get() or "default.jpg"  # 默认图片
    
    # 检查必填项
    if not title or not date or not content:
        result_label.config(text="标题、日期、内容不能为空！", foreground="red")
        return
    
    # 生成文件名（英文/数字，比如 "how-to-draw.html"）
    filename = title.lower().replace(" ", "-").replace("？", "").replace("！", "") + ".html"
    filename = os.path.join(BLOG_DIR, "posts", filename)
    
    # 替换文章模板内容（处理换行）
    formatted_content = ""
    for para in content.split("\n"):
        if para.startswith("# "):
            formatted_content += f"    <h2>{para[2:]}</h2>\n\n"
        else:
            formatted_content += f"    <p>{para}</p>\n\n"
    
    # 写入文章文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(POST_TEMPLATE.format(
            title=title,
            date=date,
            content=formatted_content,
            img_name=img_name
        ))
    
    # 更新文章列表页 posts.html
    posts_path = os.path.join(BLOG_DIR, "posts.html")
    if os.path.exists(posts_path):
        with open(posts_path, "r", encoding="utf-8") as f:
            html = f.read()
        
        # 在 </main> 标签前插入新文章卡片
        new_html = html.replace(
            "</main>",
            POST_LIST_ITEM.format(
                title=title,
                date=date,
                summary=summary,
                filename=os.path.basename(filename),
                img_name=img_name
            ) + "\n</main>"
        )
        
        with open(posts_path, "w", encoding="utf-8") as f:
            f.write(new_html)
    
    result_label.config(text=f"文章生成成功！文件：{filename}", foreground="green")

# 创建图形界面
root = tk.Tk()
root.title("博客文章生成工具")
root.geometry("600x600")

# 标题输入
ttk.Label(root, text="文章标题：").pack(anchor="w", padx=20, pady=5)
title_entry = ttk.Entry(root, width=70)
title_entry.pack(anchor="w", padx=20)

# 日期输入（默认今天）
ttk.Label(root, text="发布日期（例如 2025-08-09）：").pack(anchor="w", padx=20, pady=5)
date_entry = ttk.Entry(root, width=30)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
date_entry.pack(anchor="w", padx=20)

# 封面图片名
ttk.Label(root, text="封面图片名（放在 img 文件夹，例如 post3.jpg）：").pack(anchor="w", padx=20, pady=5)
img_entry = ttk.Entry(root, width=50)
img_entry.pack(anchor="w", padx=20)

# 摘要
ttk.Label(root, text="文章摘要（列表页显示）：").pack(anchor="w", padx=20, pady=5)
summary_entry = ttk.Entry(root, width=70)
summary_entry.pack(anchor="w", padx=20)

# 内容输入（支持换行，# 开头会变成标题）
ttk.Label(root, text="文章内容（每行一段，# 开头的行会变成标题）：").pack(anchor="w", padx=20, pady=5)
content_text = scrolledtext.ScrolledText(root, width=70, height=15)
content_text.pack(anchor="w", padx=20, pady=5)

# 生成按钮
generate_btn = ttk.Button(root, text="生成文章", command=create_post)
generate_btn.pack(pady=10)

# 结果提示
result_label = ttk.Label(root, text="")
result_label.pack(pady=10)

root.mainloop()