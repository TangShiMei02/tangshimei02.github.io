import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
import os
import re
import webbrowser
from datetime import datetime
import subprocess
import tempfile
import threading
import time
from tkinter import font

class BlogManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("博客管理系统")
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        # 设置主题颜色
        self.colors = {
            "primary": "#3b82f6",
            "secondary": "#64748b",
            "success": "#10b981",
            "danger": "#ef4444",
            "warning": "#f59e0b",
            "light": "#f1f5f9",
            "dark": "#1e293b",
            "background": "#ffffff",
            "card": "#f8fafc"
        }
        
        # 配置样式
        self.style = ttk.Style()
        self.setup_styles()
        
        # 设置中文字体支持
        self.font_config()
        
        # 博客根目录（默认为当前程序所在目录）
        self.blog_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_preview_dir = os.path.join(tempfile.gettempdir(), "blog_preview")
        os.makedirs(self.temp_preview_dir, exist_ok=True)
        
        # 初始化文件路径
        self.initialize_paths()
        
        # 创建界面
        self.create_widgets()
        
        # 加载文件列表
        self.load_file_lists()
        
        # 绑定动画事件
        self.bind_animations()
        
        # 部署状态
        self.deploying = False
        
        # 草稿保存定时器
        self.draft_timer = None
    
    def setup_styles(self):
        """设置自定义样式"""
        self.style.configure("TNotebook", background=self.colors["background"])
        self.style.configure("TNotebook.Tab", 
                            background=self.colors["light"], 
                            foreground=self.colors["dark"],
                            padding=[15, 5])
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.colors["primary"])],
                      foreground=[("selected", "white")])
        
        self.style.configure("TButton", 
                            background=self.colors["primary"],
                            foreground="white",
                            padding=[10, 5])
        self.style.map("TButton",
                      background=[("active", "#2563eb")])
        
        self.style.configure("Card.TFrame",
                            background=self.colors["card"],
                            relief="solid",
                            borderwidth=1)
        
        self.style.configure("Header.TLabel",
                            font=("SimHei", 12, "bold"),
                            foreground=self.colors["dark"],
                            padding=[5, 10])
    
    def font_config(self):
        """配置字体以支持中文显示"""
        default_font = ('SimHei', 10)
        self.option_add("*Font", default_font)
    
    def initialize_paths(self):
        """初始化各文件路径"""
        self.html_files = {
            "首页": os.path.join(self.blog_dir, "index.html"),
            "旧首页": os.path.join(self.blog_dir, "old-index.html"),
            "文章列表": os.path.join(self.blog_dir, "posts.html"),
            "关于我": os.path.join(self.blog_dir, "about.html"),
            "留言板": os.path.join(self.blog_dir, "guestbook.html")
        }
        
        self.css_file = os.path.join(self.blog_dir, "style.css")
        self.js_dir = os.path.join(self.blog_dir, "js")
        self.posts_dir = os.path.join(self.blog_dir, "posts")
        self.img_dir = os.path.join(self.blog_dir, "img")
        self.drafts_dir = os.path.join(self.blog_dir, "drafts")
        
        # 确保必要目录存在
        for dir_path in [self.js_dir, self.posts_dir, self.img_dir, self.drafts_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # 文章模板
        self.post_template = """<!DOCTYPE html>
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
    <div class="post-tags">{tags}</div>
    
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
        
        # 文章列表项模板
        self.post_list_item = """
    <!-- 新增文章 -->
    <article class="card">
      <img src="img/{img_name}" alt="{title}" class="post-img" />
      <h2>{title}</h2>
      <p class="post-date">{date}</p>
      <div class="post-tags">{tags}</div>
      <p>{summary}</p>
      <a href="posts/{filename}" class="btn">阅读全文</a>
    </article>
"""
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主标签页，重点突出发布文章和部署标签页
        self.tab_control = ttk.Notebook(self)
        
        # 文章发布标签页（放在最前面）
        self.tab_post = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_post, text="发布文章")
        
        # 文章管理标签页
        self.tab_manage = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_manage, text="文章管理")
        
        # 部署标签页（放在前面）
        self.tab_deploy = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_deploy, text="一键部署")
        
        # 其他标签页
        self.tab_pages = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_pages, text="页面编辑")
        
        self.tab_css = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_css, text="样式管理")
        
        self.tab_js = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_js, text="脚本管理")
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
        # 初始化各个标签页
        self.init_post_tab()  # 重点优化
        self.init_manage_tab()
        self.init_deploy_tab()  # 重点优化
        self.init_pages_tab()
        self.init_css_tab()
        self.init_js_tab()
        
        # 状态栏
        self.status_bar = ttk.Label(self, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def init_post_tab(self):
        """初始化发布文章标签页（重点优化）"""
        # 使用卡片式布局
        main_frame = ttk.Frame(self.tab_post, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题卡片
        title_card = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        title_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_card, text="文章标题：", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(title_card, font=("SimHei", 12))
        self.title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        title_card.columnconfigure(1, weight=1)
        
        # 基本信息卡片
        info_card = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        info_card.pack(fill=tk.X, pady=(0, 10))
        
        # 日期和标签
        ttk.Label(info_card, text="发布日期：").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 20))
        self.date_entry = ttk.Entry(info_card, width=20)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_card, text="文章标签：").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 20))
        self.tags_entry = ttk.Entry(info_card, width=30)
        self.tags_entry.insert(0, "技术,博客")  # 默认标签
        self.tags_entry.grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 封面图片
        img_frame = ttk.Frame(info_card)
        img_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        ttk.Label(img_frame, text="封面图片：").pack(side=tk.LEFT, padx=(0, 10))
        self.img_entry = ttk.Entry(img_frame, width=60)
        self.img_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.img_button = ttk.Button(img_frame, text="选择图片", command=self.choose_image)
        self.img_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_img_button = ttk.Button(img_frame, text="预览图片", command=self.preview_selected_image)
        self.preview_img_button.pack(side=tk.LEFT)
        
        # 摘要卡片
        summary_card = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        summary_card.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(summary_card, text="文章摘要：", style="Header.TLabel").pack(anchor=tk.W)
        self.summary_entry = scrolledtext.ScrolledText(summary_card, height=3)
        self.summary_entry.pack(fill=tk.X, pady=5)
        
        # 内容编辑卡片（主要区域）
        content_card = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 简易工具栏
        toolbar = ttk.Frame(content_card)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="粗体 (Ctrl+B)", command=lambda: self.format_text("**", "**")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="标题", command=lambda: self.format_text("# ", "")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="链接", command=lambda: self.format_text("[链接文本](url)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="列表", command=lambda: self.format_text("- ", "")).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(content_card, text="文章内容：\n(# 开头会变成标题，**文本**会变成粗体)", style="Header.TLabel").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(content_card, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 绑定快捷键
        self.content_text.bind("<Control-b>", lambda e: self.format_text("**", "**"))
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_draft_btn = ttk.Button(btn_frame, text="保存草稿", command=self.save_draft)
        self.save_draft_btn.pack(side=tk.LEFT, padx=10)
        
        self.load_draft_btn = ttk.Button(btn_frame, text="加载草稿", command=self.load_draft)
        self.load_draft_btn.pack(side=tk.LEFT, padx=10)
        
        self.preview_btn = ttk.Button(btn_frame, text="预览文章", command=self.preview_post)
        self.preview_btn.pack(side=tk.LEFT, padx=10)
        
        self.generate_btn = ttk.Button(btn_frame, text="发布文章", command=self.create_post, style="Accent.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=10)
        
        # 结果提示
        self.result_label = ttk.Label(main_frame, text="", foreground=self.colors["success"])
        self.result_label.pack(fill=tk.X, pady=5)
        
        # 自动保存提示
        self.auto_save_label = ttk.Label(main_frame, text="", font=("SimHei", 9), foreground=self.colors["secondary"])
        self.auto_save_label.pack(anchor=tk.E)
        
        # 设置自动保存
        self.setup_auto_save()
    
    def setup_auto_save(self):
        """设置自动保存草稿功能"""
        def auto_save():
            if self.title_entry.get().strip() or self.content_text.get("1.0", tk.END).strip():
                self.save_draft(silent=True)
            self.draft_timer = self.after(60000, auto_save)  # 每60秒自动保存一次
        
        auto_save()
    
    def format_text(self, prefix, suffix=""):
        """格式化选中的文本"""
        try:
            # 获取选中的文本
            selected_text = self.content_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            # 删除选中的文本
            self.content_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            # 插入格式化后的文本
            self.content_text.insert(tk.INSERT, f"{prefix}{selected_text}{suffix}")
        except tk.TclError:
            # 如果没有选中文本，只插入前缀和后缀
            self.content_text.insert(tk.INSERT, f"{prefix}{suffix}")
            # 将光标移动到中间
            position = self.content_text.index(tk.INSERT)
            line, col = map(int, position.split('.'))
            self.content_text.mark_set(tk.INSERT, f"{line}.{col - len(suffix)}")
    
    def preview_selected_image(self):
        """预览选中的图片"""
        img_name = self.img_entry.get().strip()
        if not img_name:
            self.result_label.config(text="请先选择图片", foreground=self.colors["warning"])
            return
            
        img_path = os.path.join(self.img_dir, img_name)
        if os.path.exists(img_path):
            try:
                webbrowser.open(f"file:///{img_path}")
            except Exception as e:
                self.result_label.config(text=f"预览失败：{str(e)}", foreground=self.colors["danger"])
        else:
            self.result_label.config(text="图片不存在", foreground=self.colors["danger"])
    
    def save_draft(self, silent=False):
        """保存草稿"""
        title = self.title_entry.get().strip() or "未命名草稿"
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not content:
            if not silent:
                self.result_label.config(text="内容为空，不保存草稿", foreground=self.colors["warning"])
            return
        
        # 生成草稿文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title[:20].lower().replace(' ', '-')}_{timestamp}.txt"
        draft_path = os.path.join(self.drafts_dir, filename)
        
        try:
            # 保存草稿内容
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(f"标题：{title}\n")
                f.write(f"日期：{self.date_entry.get()}\n")
                f.write(f"标签：{self.tags_entry.get()}\n")
                f.write(f"图片：{self.img_entry.get()}\n")
                f.write(f"摘要：{self.summary_entry.get('1.0', tk.END)}\n")
                f.write("---\n")  # 分隔符
                f.write(content)
            
            if not silent:
                self.animate_result(f"草稿已保存：{filename}", "success")
            else:
                self.auto_save_label.config(text=f"自动保存于 {datetime.now().strftime('%H:%M')}")
            
        except Exception as e:
            self.result_label.config(text=f"保存草稿失败：{str(e)}", foreground=self.colors["danger"])
    
    def load_draft(self):
        """加载草稿"""
        # 获取草稿列表
        drafts = []
        if os.path.exists(self.drafts_dir):
            for filename in os.listdir(self.drafts_dir):
                if filename.endswith(".txt"):
                    drafts.append((filename, os.path.join(self.drafts_dir, filename)))
        
        if not drafts:
            messagebox.showinfo("提示", "没有找到草稿")
            return
        
        # 创建草稿选择对话框
        draft_window = tk.Toplevel(self)
        draft_window.title("选择草稿")
        draft_window.geometry("400x300")
        draft_window.transient(self)
        draft_window.grab_set()
        
        ttk.Label(draft_window, text="选择要加载的草稿：").pack(pady=10)
        
        draft_listbox = tk.Listbox(draft_window)
        draft_listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        
        scrollbar = ttk.Scrollbar(draft_listbox, orient=tk.VERTICAL, command=draft_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        draft_listbox.config(yscrollcommand=scrollbar.set)
        
        for draft in drafts:
            draft_listbox.insert(tk.END, draft[0])
        
        def load_selected_draft():
            selection = draft_listbox.curselection()
            if not selection:
                return
                
            index = selection[0]
            draft_path = drafts[index][1]
            
            try:
                with open(draft_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # 解析草稿内容
                title = ""
                date = ""
                tags = ""
                img = ""
                summary = ""
                content = []
                section = "header"
                
                for line in lines:
                    line = line.rstrip("\n")
                    if line == "---":
                        section = "content"
                        continue
                        
                    if section == "header":
                        if line.startswith("标题："):
                            title = line[3:]
                        elif line.startswith("日期："):
                            date = line[3:]
                        elif line.startswith("标签："):
                            tags = line[3:]
                        elif line.startswith("图片："):
                            img = line[3:]
                        elif line.startswith("摘要："):
                            summary = line[3:]
                    else:
                        content.append(line)
                
                # 填充到表单
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, title)
                
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date or datetime.today().strftime("%Y-%m-%d"))
                
                self.tags_entry.delete(0, tk.END)
                self.tags_entry.insert(0, tags)
                
                self.img_entry.delete(0, tk.END)
                self.img_entry.insert(0, img)
                
                self.summary_entry.delete(1.0, tk.END)
                self.summary_entry.insert(tk.END, summary)
                
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, "\n".join(content))
                
                self.animate_result(f"已加载草稿：{drafts[index][0]}", "success")
                draft_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"加载草稿失败：{str(e)}")
        
        ttk.Button(draft_window, text="加载选中的草稿", command=load_selected_draft).pack(pady=10)
        ttk.Button(draft_window, text="取消", command=draft_window.destroy).pack(pady=5)
    
    def init_deploy_tab(self):
        """初始化部署标签页（重点优化）"""
        frame = ttk.Frame(self.tab_deploy, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 部署设置卡片
        settings_card = ttk.Frame(frame, style="Card.TFrame", padding=15)
        settings_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(settings_card, text="部署设置", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # 仓库路径设置
        path_frame = ttk.Frame(settings_card)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="博客目录：", width=12).pack(side=tk.LEFT)
        self.repo_path_var = tk.StringVar(value=self.blog_dir)
        ttk.Entry(path_frame, textvariable=self.repo_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(path_frame, text="浏览", command=self.browse_repo_path).pack(side=tk.LEFT, padx=5)
        
        # 远程仓库设置
        remote_frame = ttk.Frame(settings_card)
        remote_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(remote_frame, text="远程仓库：", width=12).pack(side=tk.LEFT)
        self.remote_repo_var = tk.StringVar()
        ttk.Entry(remote_frame, textvariable=self.remote_repo_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(remote_frame, text="检测", command=self.detect_remote_repo).pack(side=tk.LEFT, padx=5)
        
        # 分支设置
        branch_frame = ttk.Frame(settings_card)
        branch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(branch_frame, text="部署分支：", width=12).pack(side=tk.LEFT)
        self.branch_var = tk.StringVar(value="main")
        ttk.Entry(branch_frame, textvariable=self.branch_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 保存设置按钮
        ttk.Button(settings_card, text="保存设置", command=self.save_deploy_settings).pack(anchor=tk.E, pady=10)
        
        # 部署操作区域
        deploy_ops_card = ttk.Frame(frame, style="Card.TFrame", padding=15)
        deploy_ops_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(deploy_ops_card, text="部署操作", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # 更新说明
        ttk.Label(deploy_ops_card, text="更新说明：").pack(anchor=tk.W)
        self.deploy_msg = ttk.Entry(deploy_ops_card)
        self.deploy_msg.insert(0, f"更新于 {datetime.today().strftime('%Y-%m-%d')}")
        self.deploy_msg.pack(fill=tk.X, pady=5)
        
        # 部署按钮区域
        btn_frame = ttk.Frame(deploy_ops_card)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.check_status_btn = ttk.Button(btn_frame, text="检查状态", command=self.check_repo_status)
        self.check_status_btn.pack(side=tk.LEFT, padx=10)
        
        self.pull_btn = ttk.Button(btn_frame, text="拉取更新", command=self.pull_from_remote)
        self.pull_btn.pack(side=tk.LEFT, padx=10)
        
        self.deploy_btn = ttk.Button(btn_frame, text="开始部署", command=self.start_deploy, style="Accent.TButton")
        self.deploy_btn.pack(side=tk.LEFT, padx=10)
        
        # 部署状态指示器
        self.deploy_status_frame = ttk.Frame(deploy_ops_card, height=20)
        self.deploy_status_frame.pack(fill=tk.X, pady=5)
        self.deploy_status_var = tk.StringVar(value="就绪")
        self.deploy_status_label = ttk.Label(
            self.deploy_status_frame, 
            textvariable=self.deploy_status_var, 
            foreground=self.colors["secondary"]
        )
        self.deploy_status_label.pack(anchor=tk.W)
        
        # 部署日志
        log_card = ttk.Frame(frame, style="Card.TFrame", padding=15)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_card, text="部署日志", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        self.deploy_log = scrolledtext.ScrolledText(log_card, height=12, wrap=tk.WORD)
        self.deploy_log.pack(fill=tk.BOTH, expand=True)
        self.deploy_log.config(state=tk.DISABLED)
        
        # 加载保存的部署设置
        self.load_deploy_settings()
    
    def browse_repo_path(self):
        """浏览选择仓库路径"""
        path = filedialog.askdirectory(title="选择博客仓库目录")
        if path:
            self.repo_path_var.set(path)
            self.blog_dir = path
            self.initialize_paths()  # 重新初始化路径
    
    def detect_remote_repo(self):
        """检测当前远程仓库"""
        repo_path = self.repo_path_var.get()
        if not os.path.exists(os.path.join(repo_path, ".git")):
            self.update_deploy_log("错误：所选目录不是Git仓库")
            return
            
        try:
            # 执行git remote命令
            process = subprocess.Popen(
                "git remote get-url origin",
                cwd=repo_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            
            output, _ = process.communicate()
            if process.returncode == 0 and output.strip():
                self.remote_repo_var.set(output.strip())
                self.update_deploy_log(f"已检测到远程仓库：{output.strip()}")
            else:
                self.update_deploy_log("未设置远程仓库，请手动输入")
                
        except Exception as e:
            self.update_deploy_log(f"检测失败：{str(e)}")
    
    def check_repo_status(self):
        """检查仓库状态"""
        self.update_deploy_log("检查仓库状态...")
        threading.Thread(target=self._check_repo_status_thread, daemon=True).start()
    
    def _check_repo_status_thread(self):
        """检查仓库状态的线程"""
        repo_path = self.repo_path_var.get()
        if not os.path.exists(os.path.join(repo_path, ".git")):
            self.update_deploy_log("错误：所选目录不是Git仓库")
            return
            
        try:
            # 执行git status命令
            process = subprocess.Popen(
                "git status",
                cwd=repo_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            
            for line in process.stdout:
                self.update_deploy_log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                self.update_deploy_log(f"命令执行失败，返回代码：{process.returncode}")
                
        except Exception as e:
            self.update_deploy_log(f"检查失败：{str(e)}")
    
    def pull_from_remote(self):
        """从远程仓库拉取更新"""
        if self.deploying:
            messagebox.showinfo("提示", "正在执行部署操作，请稍后再试")
            return
            
        self.update_deploy_log("开始从远程拉取更新...")
        self.deploying = True
        self.update_deploy_button_state()
        threading.Thread(target=self._pull_thread, daemon=True).start()
    
    def _pull_thread(self):
        """拉取更新的线程"""
        repo_path = self.repo_path_var.get()
        branch = self.branch_var.get() or "main"
        
        try:
            # 执行git pull命令
            process = subprocess.Popen(
                f"git pull origin {branch}",
                cwd=repo_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            
            for line in process.stdout:
                self.update_deploy_log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.update_deploy_log("拉取更新成功")
                self.animate_deploy_status("拉取更新成功", "success")
            else:
                self.update_deploy_log(f"拉取更新失败，返回代码：{process.returncode}")
                self.animate_deploy_status("拉取更新失败", "danger")
                
        except Exception as e:
            self.update_deploy_log(f"拉取失败：{str(e)}")
            self.animate_deploy_status("拉取更新失败", "danger")
        finally:
            self.deploying = False
            self.update_deploy_button_state()
    
    def start_deploy(self):
        """开始部署（在新线程中执行）"""
        if self.deploying:
            messagebox.showinfo("提示", "正在执行部署操作，请稍后再试")
            return
            
        # 保存部署设置
        self.save_deploy_settings()
        
        # 检查必要信息
        if not self.remote_repo_var.get().strip():
            messagebox.showwarning("警告", "请设置远程仓库地址")
            return
            
        # 获取更新说明
        msg = self.deploy_msg.get().strip() or f"更新于 {datetime.today().strftime('%Y-%m-%d')}"
        
        self.update_deploy_log("开始部署...")
        self.deploying = True
        self.update_deploy_button_state()
        self.animate_deploy_status("正在部署...", "warning")
        
        # 在新线程中执行部署，避免界面冻结
        threading.Thread(target=self._deploy_thread, args=(msg,), daemon=True).start()
    
    def _deploy_thread(self, msg):
        """部署的线程函数"""
        repo_path = self.repo_path_var.get()
        branch = self.branch_var.get() or "main"
        
        try:
            # 检查是否是Git仓库
            if not os.path.exists(os.path.join(repo_path, ".git")):
                self.update_deploy_log("错误：所选目录不是Git仓库，正在初始化...")
                self.run_git_command(f"git init", "初始化Git仓库...")
            
            # 检查是否有远程仓库配置
            process = subprocess.Popen(
                "git remote",
                cwd=repo_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            output, _ = process.communicate()
            
            if "origin" not in output:
                self.update_deploy_log("添加远程仓库...")
                self.run_git_command(
                    f"git remote add origin {self.remote_repo_var.get()}", 
                    "添加远程仓库..."
                )
            
            # 检查分支是否存在，不存在则创建
            self.run_git_command(f"git checkout {branch}", f"切换到{branch}分支...", allow_failure=True)
            
            # 添加所有文件
            self.run_git_command(f"git add .", "添加文件...")
            
            # 提交更改
            self.run_git_command(f'git commit -m "{msg}"', "提交更改...", allow_failure=True)
            
            # 推送到远程仓库
            self.run_git_command(f"git push origin {branch}", "推送更改...")
            
            self.update_deploy_log("部署完成！几分钟后刷新网页即可看到更新。")
            self.animate_deploy_status("部署成功", "success")
            
        except Exception as e:
            self.update_deploy_log(f"部署失败：{str(e)}")
            self.animate_deploy_status("部署失败", "danger")
        finally:
            self.deploying = False
            self.update_deploy_button_state()
    
    def update_deploy_button_state(self):
        """更新部署按钮状态"""
        state = "disabled" if self.deploying else "normal"
        self.deploy_btn.config(state=state)
        self.check_status_btn.config(state=state)
        self.pull_btn.config(state=state)
    
    def save_deploy_settings(self):
        """保存部署设置"""
        settings = {
            "repo_path": self.repo_path_var.get(),
            "remote_repo": self.remote_repo_var.get(),
            "branch": self.branch_var.get()
        }
        
        try:
            with open(os.path.join(self.blog_dir, ".blog_config"), "w", encoding="utf-8") as f:
                for key, value in settings.items():
                    f.write(f"{key}={value}\n")
            
            self.update_deploy_log("部署设置已保存")
        except Exception as e:
            self.update_deploy_log(f"保存设置失败：{str(e)}")
    
    def load_deploy_settings(self):
        """加载部署设置"""
        config_path = os.path.join(self.blog_dir, ".blog_config")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line:
                            key, value = line.split("=", 1)
                            if key == "repo_path" and value:
                                self.repo_path_var.set(value)
                            elif key == "remote_repo" and value:
                                self.remote_repo_var.set(value)
                            elif key == "branch" and value:
                                self.branch_var.set(value)
                
                self.update_deploy_log("已加载部署设置")
            except Exception as e:
                self.update_deploy_log(f"加载设置失败：{str(e)}")
    
    def run_git_command(self, command, message, allow_failure=False):
        """运行Git命令"""
        self.update_deploy_log(message)
        
        process = subprocess.Popen(
            command,
            cwd=self.repo_path_var.get(),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8"
        )
        
        # 实时输出日志
        for line in process.stdout:
            self.update_deploy_log(line.strip())
        
        process.wait()
        
        if process.returncode != 0 and not allow_failure:
            raise Exception(f"命令执行失败：{command}，返回代码：{process.returncode}")
    
    def update_deploy_log(self, message):
        """更新部署日志"""
        self.deploy_log.config(state=tk.NORMAL)
        self.deploy_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.deploy_log.see(tk.END)
        self.deploy_log.config(state=tk.DISABLED)
        self.update_idletasks()
    
    def init_manage_tab(self):
        """初始化文章管理标签页"""
        frame = ttk.Frame(self.tab_manage, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧文章列表
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        ttk.Label(left_frame, text="已发布文章：", style="Header.TLabel").pack(anchor=tk.W, pady=5)
        
        self.posts_listbox = tk.Listbox(left_frame, width=30, height=25)
        self.posts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.posts_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.posts_listbox.config(yscrollcommand=scrollbar.set)
        
        # 绑定列表点击事件
        self.posts_listbox.bind('<<ListboxSelect>>', self.on_post_select)
        
        # 右侧编辑区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.post_edit_title = ttk.Entry(right_frame, font=("SimHei", 12))
        self.post_edit_title.pack(fill=tk.X, pady=5)
        
        # 简易工具栏
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="粗体 (Ctrl+B)", command=lambda: self.format_edit_text("**", "**")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="标题", command=lambda: self.format_edit_text("# ", "")).pack(side=tk.LEFT, padx=2)
        
        self.post_edit_content = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.post_edit_content.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 绑定快捷键
        self.post_edit_content.bind("<Control-b>", lambda e: self.format_edit_text("**", "**"))
        
        # 按钮区域
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_edit_btn = ttk.Button(btn_frame, text="保存修改", command=self.save_post_edit)
        self.save_edit_btn.pack(side=tk.LEFT, padx=10)
        
        self.delete_post_btn = ttk.Button(btn_frame, text="删除文章", command=self.delete_post)
        self.delete_post_btn.pack(side=tk.LEFT, padx=10)
        
        self.preview_edit_btn = ttk.Button(btn_frame, text="预览文章", command=self.preview_edited_post)
        self.preview_edit_btn.pack(side=tk.LEFT, padx=10)
        
        self.edit_result_label = ttk.Label(right_frame, text="", foreground=self.colors["success"])
        self.edit_result_label.pack(fill=tk.X, pady=5)
    
    def format_edit_text(self, prefix, suffix=""):
        """格式化编辑中的文章文本"""
        try:
            # 获取选中的文本
            selected_text = self.post_edit_content.get(tk.SEL_FIRST, tk.SEL_LAST)
            # 删除选中的文本
            self.post_edit_content.delete(tk.SEL_FIRST, tk.SEL_LAST)
            # 插入格式化后的文本
            self.post_edit_content.insert(tk.INSERT, f"{prefix}{selected_text}{suffix}")
        except tk.TclError:
            # 如果没有选中文本，只插入前缀和后缀
            self.post_edit_content.insert(tk.INSERT, f"{prefix}{suffix}")
            # 将光标移动到中间
            position = self.post_edit_content.index(tk.INSERT)
            line, col = map(int, position.split('.'))
            self.post_edit_content.mark_set(tk.INSERT, f"{line}.{col - len(suffix)}")
    
    def init_pages_tab(self):
        """初始化页面编辑标签页"""
        frame = ttk.Frame(self.tab_pages, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧页面列表
        left_frame = ttk.Frame(frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_frame, text="页面列表：", style="Header.TLabel").pack(anchor=tk.W, pady=5)
        
        self.page_listbox = tk.Listbox(left_frame, width=25, height=25)
        self.page_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 绑定列表点击事件
        self.page_listbox.bind('<<ListboxSelect>>', self.on_page_select)
        
        # 右侧编辑区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.page_editor = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.page_editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_page_btn = ttk.Button(btn_frame, text="保存页面", command=self.save_page)
        self.save_page_btn.pack(side=tk.LEFT, padx=10)
        
        self.preview_page_btn = ttk.Button(btn_frame, text="预览页面", command=self.preview_page)
        self.preview_page_btn.pack(side=tk.LEFT, padx=10)
        
        self.page_result_label = ttk.Label(right_frame, text="", foreground=self.colors["success"])
        self.page_result_label.pack(fill=tk.X, pady=5)
    
    def init_css_tab(self):
        """初始化样式管理标签页"""
        frame = ttk.Frame(self.tab_css, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="CSS 样式编辑：", style="Header.TLabel").pack(anchor=tk.W, pady=5)
        
        self.css_editor = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.css_editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_css_btn = ttk.Button(btn_frame, text="保存样式", command=self.save_css)
        self.save_css_btn.pack(side=tk.LEFT, padx=10)
        
        self.preview_css_btn = ttk.Button(btn_frame, text="预览效果", command=self.preview_css)
        self.preview_css_btn.pack(side=tk.LEFT, padx=10)
        
        self.css_result_label = ttk.Label(frame, text="", foreground=self.colors["success"])
        self.css_result_label.pack(fill=tk.X, pady=5)
        
        # 加载CSS内容
        self.load_css_content()
    
    def init_js_tab(self):
        """初始化脚本管理标签页"""
        frame = ttk.Frame(self.tab_js, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧JS文件列表
        left_frame = ttk.Frame(frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_frame, text="JS 文件列表：", style="Header.TLabel").pack(anchor=tk.WORD, pady=5)
        
        self.js_listbox = tk.Listbox(left_frame, width=25, height=25)
        self.js_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 绑定列表点击事件
        self.js_listbox.bind('<<ListboxSelect>>', self.on_js_select)
        
        # 添加JS文件按钮
        self.add_js_btn = ttk.Button(left_frame, text="添加JS文件", command=self.add_js_file)
        self.add_js_btn.pack(fill=tk.X, pady=5)
        
        # 右侧编辑区域
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.js_editor = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.js_editor.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.save_js_btn = ttk.Button(btn_frame, text="保存脚本", command=self.save_js)
        self.save_js_btn.pack(side=tk.LEFT, padx=10)
        
        self.delete_js_btn = ttk.Button(btn_frame, text="删除文件", command=self.delete_js_file)
        self.delete_js_btn.pack(side=tk.LEFT, padx=10)
        
        self.js_result_label = ttk.Label(right_frame, text="", foreground=self.colors["success"])
        self.js_result_label.pack(fill=tk.X, pady=5)
    
    def load_file_lists(self):
        """加载各种文件列表"""
        # 加载页面列表
        self.page_listbox.delete(0, tk.END)
        for page_name in self.html_files.keys():
            self.page_listbox.insert(tk.END, page_name)
        
        # 加载文章列表
        self.load_posts_list()
        
        # 加载JS文件列表
        self.load_js_files()
    
    def load_posts_list(self):
        """加载文章列表"""
        self.posts_listbox.delete(0, tk.END)
        self.posts_files = []
        
        if os.path.exists(self.posts_dir):
            for filename in os.listdir(self.posts_dir):
                if filename.endswith(".html"):
                    self.posts_listbox.insert(tk.END, filename)
                    self.posts_files.append(os.path.join(self.posts_dir, filename))
    
    def load_js_files(self):
        """加载JS文件列表"""
        self.js_listbox.delete(0, tk.END)
        self.js_files = []
        
        if os.path.exists(self.js_dir):
            for filename in os.listdir(self.js_dir):
                if filename.endswith(".js"):
                    self.js_listbox.insert(tk.END, filename)
                    self.js_files.append(os.path.join(self.js_dir, filename))
    
    def load_css_content(self):
        """加载CSS内容，尝试多种编码格式"""
        if os.path.exists(self.css_file):
            # 尝试多种编码格式
            encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(self.css_file, "r", encoding=encoding) as f:
                        content = f.read()
                        self.css_editor.delete(1.0, tk.END)
                        self.css_editor.insert(tk.END, content)
                    return  # 成功读取则退出
                except UnicodeDecodeError:
                    continue  # 尝试下一种编码
            # 如果所有编码都失败
            self.css_result_label.config(text=f"无法解码CSS文件，请检查文件编码", foreground=self.colors["danger"])
    
    def on_post_select(self, event):
        """处理文章选择事件"""
        selection = self.posts_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < 0 or index >= len(self.posts_files):
            return
            
        post_file = self.posts_files[index]
        self.current_post_file = post_file
        
        # 解析HTML文件获取标题和内容
        try:
            # 尝试多种编码读取
            encodings = ['utf-8', 'gbk', 'gb2312']
            content = None
            
            for encoding in encodings:
                try:
                    with open(post_file, "r", encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise Exception("无法解码文章文件，请检查文件编码")
                
            # 提取标题
            title_match = re.search(r'<h1 class="site-title">(.*?)</h1>', content)
            if title_match:
                title = title_match.group(1)
                self.post_edit_title.delete(0, tk.END)
                self.post_edit_title.insert(0, title)
            
            # 提取正文内容
            content_match = re.search(r'<main class="post-content">(.*?)</main>', content, re.DOTALL)
            if content_match:
                main_content = content_match.group(1)
                # 转换HTML内容为编辑格式
                edit_content = self.html_to_edit_format(main_content)
                self.post_edit_content.delete(1.0, tk.END)
                self.post_edit_content.insert(tk.END, edit_content)
            
            self.animate_result(f"已加载：{os.path.basename(post_file)}", "success")
        except Exception as e:
            self.animate_result(f"加载失败：{str(e)}", "danger")
    
    def html_to_edit_format(self, html_content):
        """将HTML内容转换为编辑格式"""
        # 移除图片和日期行
        content = re.sub(r'<img.*?>', '', html_content, flags=re.DOTALL)
        content = re.sub(r'<p class="post-date">.*?</p>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="post-tags">.*?</div>', '', content, flags=re.DOTALL)
        
        # 转换h2标签为# 格式
        content = re.sub(r'<h2>(.*?)</h2>', r'# \1', content, flags=re.DOTALL)
        
        # 转换p标签为普通文本
        content = re.sub(r'<p>(.*?)</p>', r'\1', content, flags=re.DOTALL)
        
        # 去除多余空行和空格
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def on_page_select(self, event):
        """处理页面选择事件"""
        selection = self.page_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        page_names = list(self.html_files.keys())
        if index < 0 or index >= len(page_names):
            return
            
        page_name = page_names[index]
        page_path = self.html_files[page_name]
        self.current_page_path = page_path
        
        # 加载页面内容
        try:
            if os.path.exists(page_path):
                # 尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(page_path, "r", encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise Exception("无法解码页面文件，请检查文件编码")
                    
                self.page_editor.delete(1.0, tk.END)
                self.page_editor.insert(tk.END, content)
                self.animate_page_result(f"已加载：{page_name}", "success")
            else:
                self.animate_page_result(f"文件不存在：{page_name}", "warning")
        except Exception as e:
            self.animate_page_result(f"加载失败：{str(e)}", "danger")
    
    def on_js_select(self, event):
        """处理JS文件选择事件"""
        selection = self.js_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < 0 or index >= len(self.js_files):
            return
            
        js_file = self.js_files[index]
        self.current_js_file = js_file
        
        # 加载JS内容
        try:
            with open(js_file, "r", encoding="utf-8") as f:
                self.js_editor.delete(1.0, tk.END)
                self.js_editor.insert(tk.END, f.read())
            self.animate_js_result(f"已加载：{os.path.basename(js_file)}", "success")
        except Exception as e:
            self.animate_js_result(f"加载失败：{str(e)}", "danger")
    
    def choose_image(self):
        """选择图片并复制到img目录"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.gif;*.ico")]
        )
        
        if file_path:
            # 确保img目录存在
            if not os.path.exists(self.img_dir):
                os.makedirs(self.img_dir)
            
            # 复制文件到img目录（使用二进制模式）
            try:
                import shutil
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(self.img_dir, file_name)
                
                # 二进制模式复制图片
                with open(file_path, 'rb') as fsrc, open(dest_path, 'wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
                
                self.img_entry.delete(0, tk.END)
                self.img_entry.insert(0, file_name)
                self.animate_result(f"图片已复制：{file_name}", "success")
            except Exception as e:
                self.animate_result(f"图片处理失败：{str(e)}", "danger")
    
    def create_post(self):
        """创建新文章"""
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        tags = self.tags_entry.get().strip()
        summary = self.summary_entry.get("1.0", tk.END).strip()
        content = self.content_text.get("1.0", tk.END).strip()
        img_name = self.img_entry.get().strip() or "default.jpg"
        
        # 检查必填项
        if not title or not date or not content:
            self.animate_result("标题、日期、内容不能为空！", "warning")
            return
        
        # 生成文件名（处理特殊字符）
        filename = re.sub(r'[^\w\-]', '', title.lower().replace(" ", "-")) + ".html"
        if not filename or filename == ".html":  # 处理可能的空文件名
            filename = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        
        filename = os.path.join(self.posts_dir, filename)
        
        # 处理标签
        formatted_tags = ""
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            formatted_tags = "<div class='tags'>" + " ".join([f"<span class='tag'>{tag}</span>" for tag in tag_list]) + "</div>"
        
        # 替换文章模板内容（处理换行）
        formatted_content = ""
        for para in content.split("\n"):
            para = para.strip()
            if not para:
                continue
            if para.startswith("# "):
                formatted_content += f"    <h2>{para[2:]}</h2>\n\n"
            else:
                formatted_content += f"    <p>{para}</p>\n\n"
        
        # 写入文章文件
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.post_template.format(
                    title=title,
                    date=date,
                    tags=formatted_tags,
                    content=formatted_content,
                    img_name=img_name
                ))
            
            # 更新文章列表页 posts.html
            posts_path = self.html_files["文章列表"]
            # 确保文章列表文件存在
            if not os.path.exists(posts_path):
                self.create_default_posts_page()
            
            with open(posts_path, "r", encoding="utf-8") as f:
                html = f.read()
            
            # 在 </main> 标签前插入新文章卡片
            new_html = html.replace(
                "</main>",
                self.post_list_item.format(
                    title=title,
                    date=date,
                    tags=formatted_tags,
                    summary=summary,
                    filename=os.path.basename(filename),
                    img_name=img_name
                ) + "\n</main>"
            )
            
            with open(posts_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            
            # 刷新文章列表
            self.load_posts_list()
            
            self.animate_result(f"文章发布成功！文件：{os.path.basename(filename)}", "success")
            
            # 提供选项：继续编辑或新建
            def on_continue():
                dialog.destroy()
            
            def on_new():
                # 清空输入框
                self.title_entry.delete(0, tk.END)
                self.summary_entry.delete(1.0, tk.END)
                self.content_text.delete(1.0, tk.END)
                self.tags_entry.delete(0, tk.END)
                self.tags_entry.insert(0, "技术,博客")
                dialog.destroy()
            
            dialog = tk.Toplevel(self)
            dialog.title("发布成功")
            dialog.geometry("300x120")
            dialog.transient(self)
            dialog.grab_set()
            
            ttk.Label(dialog, text=f"文章《{title}》已成功发布！").pack(pady=15)
            
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Button(btn_frame, text="继续编辑", command=on_continue).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="新建文章", command=on_new).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            self.animate_result(f"发布失败：{str(e)}", "danger")
    
    def create_default_posts_page(self):
        """创建默认的文章列表页"""
        posts_page_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>文章列表 - TangShiMei</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1 class="site-title">文章列表</h1>
    <button id="theme-toggle" class="theme-btn" title="切换夜间模式">🌙</button>
  </header>

  <main class="posts-container">
  </main>

  <footer>
    <a href="index.html" class="btn">← 返回首页</a>
    <br><br>
    <small>© 2025 TangShiMei</small>
  </footer>

  <script src="js/main.js"></script>
</body>
</html>"""
        
        with open(self.html_files["文章列表"], "w", encoding="utf-8") as f:
            f.write(posts_page_content)
    
    def save_post_edit(self):
        """保存文章编辑"""
        if not hasattr(self, 'current_post_file') or not self.current_post_file:
            self.animate_result("请先选择一篇文章", "warning")
            return
            
        try:
            title = self.post_edit_title.get().strip()
            content = self.post_edit_content.get("1.0", tk.END).strip()
            
            if not title or not content:
                self.animate_result("标题和内容不能为空", "warning")
                return
            
            # 读取原文件内容
            with open(self.current_post_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # 更新标题
            new_html = re.sub(
                r'<h1 class="site-title">.*?</h1>',
                f'<h1 class="site-title">{title}</h1>',
                html_content
            )
            
            new_html = re.sub(
                r'<title>.*? - TangShiMei</title>',
                f'<title>{title} - TangShiMei</title>',
                new_html
            )
            
            # 处理内容
            formatted_content = ""
            for para in content.split("\n"):
                para = para.strip()
                if not para:
                    continue
                if para.startswith("# "):
                    formatted_content += f"    <h2>{para[2:]}</h2>\n\n"
                else:
                    formatted_content += f"    <p>{para}</p>\n\n"
            
            # 更新正文内容（保留图片和日期）
            # 首先提取图片和日期部分
            match = re.search(r'(?s)<main class="post-content">(.*?)<p class="post-date">.*?</p>(.*?)</main>', html_content)
            if match:
                img_part = match.group(1)
                # 构建新的main内容
                new_main_content = f"{img_part}<p class='post-date'>{match.group(2).split('</p>')[0]}</p>\n{formatted_content}"
                
                # 更新正文内容
                new_html = re.sub(
                    r'(?s)<main class="post-content">.*?</main>',
                    f'<main class="post-content">{new_main_content}</main>',
                    new_html,
                    count=1
                )
            else:
                # 如果没有找到匹配的结构，直接替换
                new_html = re.sub(
                    r'(?s)<main class="post-content">.*?</main>',
                    f'<main class="post-content">\n{formatted_content}\n</main>',
                    new_html,
                    count=1
                )
            
            # 写入更新后的内容
            with open(self.current_post_file, "w", encoding="utf-8") as f:
                f.write(new_html)
            
            self.animate_result("文章更新成功", "success")
            
        except Exception as e:
            self.animate_result(f"保存失败：{str(e)}", "danger")
    
    def delete_post(self):
        """删除文章"""
        if not hasattr(self, 'current_post_file') or not self.current_post_file:
            self.animate_result("请先选择一篇文章", "warning")
            return
            
        filename = os.path.basename(self.current_post_file)
        
        if messagebox.askyesno("确认删除", f"确定要删除文章 '{filename}' 吗？此操作不可恢复。"):
            try:
                # 从文章列表中移除
                posts_path = self.html_files["文章列表"]
                if os.path.exists(posts_path):
                    with open(posts_path, "r", encoding="utf-8") as f:
                        html = f.read()
                
                    # 找到并移除文章卡片
                    pattern = re.compile(
                        rf'(?s)<!-- 新增文章 -->\s*<article class="card">.*?href="posts/{re.escape(filename)}".*?</article>',
                        re.IGNORECASE
                    )
                    new_html = pattern.sub('', html)
                    
                    with open(posts_path, "w", encoding="utf-8") as f:
                        f.write(new_html)
                
                # 删除文章文件
                os.remove(self.current_post_file)
                
                # 刷新文章列表
                self.load_posts_list()
                
                # 清空编辑区域
                self.post_edit_title.delete(0, tk.END)
                self.post_edit_content.delete(1.0, tk.END)
                
                self.animate_result(f"文章 '{filename}' 已删除", "success")
                
            except Exception as e:
                self.animate_result(f"删除失败：{str(e)}", "danger")
    
    def save_page(self):
        """保存页面编辑"""
        if not hasattr(self, 'current_page_path') or not self.current_page_path:
            self.animate_page_result("请先选择一个页面", "warning")
            return
            
        try:
            content = self.page_editor.get("1.0", tk.END)
            
            with open(self.current_page_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.animate_page_result("页面保存成功", "success")
            
        except Exception as e:
            self.animate_page_result(f"保存失败：{str(e)}", "danger")
    
    def save_css(self):
        """保存CSS样式"""
        try:
            content = self.css_editor.get("1.0", tk.END)
            
            with open(self.css_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.animate_css_result("样式保存成功", "success")
            
        except Exception as e:
            self.animate_css_result(f"保存失败：{str(e)}", "danger")
    
    def add_js_file(self):
        """添加新的JS文件"""
        filename = simpledialog.askstring("新建JS文件", "请输入文件名（带.js扩展名）：")
        
        if not filename:
            return
            
        if not filename.endswith(".js"):
            filename += ".js"
            
        file_path = os.path.join(self.js_dir, filename)
        
        if os.path.exists(file_path):
            self.animate_js_result(f"文件已存在：{filename}", "warning")
            return
            
        try:
            # 创建空文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("// 新增JS文件\n")
            
            # 刷新JS文件列表
            self.load_js_files()
            
            self.animate_js_result(f"已创建文件：{filename}", "success")
            
        except Exception as e:
            self.animate_js_result(f"创建失败：{str(e)}", "danger")
    
    def save_js(self):
        """保存JS文件"""
        if not hasattr(self, 'current_js_file') or not self.current_js_file:
            self.animate_js_result("请先选择一个JS文件", "warning")
            return
            
        try:
            content = self.js_editor.get("1.0", tk.END)
            
            with open(self.current_js_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.animate_js_result("脚本保存成功", "success")
            
        except Exception as e:
            self.animate_js_result(f"保存失败：{str(e)}", "danger")
    
    def delete_js_file(self):
        """删除JS文件"""
        if not hasattr(self, 'current_js_file') or not self.current_js_file:
            self.animate_js_result("请先选择一个JS文件", "warning")
            return
            
        filename = os.path.basename(self.current_js_file)
        
        if messagebox.askyesno("确认删除", f"确定要删除JS文件 '{filename}' 吗？此操作不可恢复。"):
            try:
                os.remove(self.current_js_file)
                
                # 刷新JS文件列表
                self.load_js_files()
                
                # 清空编辑区域
                self.js_editor.delete(1.0, tk.END)
                
                self.animate_js_result(f"JS文件 '{filename}' 已删除", "success")
                
            except Exception as e:
                self.animate_js_result(f"删除失败：{str(e)}", "danger")
    
    def preview_post(self):
        """预览文章（未发布状态）"""
        title = self.title_entry.get().strip() or "预览文章"
        date = self.date_entry.get().strip() or datetime.today().strftime("%Y-%m-%d")
        tags = self.tags_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        img_name = self.img_entry.get().strip() or "default.jpg"
        
        # 处理标签
        formatted_tags = ""
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            formatted_tags = "<div class='tags'>" + " ".join([f"<span class='tag'>{tag}</span>" for tag in tag_list]) + "</div>"
        
        # 处理内容
        formatted_content = ""
        for para in content.split("\n"):
            para = para.strip()
            if not para:
                continue
            if para.startswith("# "):
                formatted_content += f"    <h2>{para[2:]}</h2>\n\n"
            else:
                formatted_content += f"    <p>{para}</p>\n\n"
        
        # 创建临时预览文件
        try:
            temp_file = os.path.join(self.temp_preview_dir, "preview_post.html")
            
            # 复制CSS文件到临时目录
            if os.path.exists(self.css_file):
                import shutil
                shutil.copy2(self.css_file, self.temp_preview_dir)
            
            # 创建临时js目录并复制文件
            temp_js_dir = os.path.join(self.temp_preview_dir, "js")
            os.makedirs(temp_js_dir, exist_ok=True)
            if os.path.exists(self.js_dir):
                for js_file in os.listdir(self.js_dir):
                    if js_file.endswith(".js"):
                        shutil.copy2(os.path.join(self.js_dir, js_file), temp_js_dir)
            
            # 创建临时img目录并复制需要的图片（使用二进制模式）
            temp_img_dir = os.path.join(self.temp_preview_dir, "img")
            os.makedirs(temp_img_dir, exist_ok=True)
            if img_name and os.path.exists(os.path.join(self.img_dir, img_name)):
                src_path = os.path.join(self.img_dir, img_name)
                dest_path = os.path.join(temp_img_dir, img_name)
                with open(src_path, 'rb') as fsrc, open(dest_path, 'wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
            # 复制默认图片
            if not img_name or not os.path.exists(os.path.join(self.img_dir, img_name)):
                default_img = os.path.join(self.img_dir, "default.jpg")
                if os.path.exists(default_img):
                    dest_path = os.path.join(temp_img_dir, "default.jpg")
                    with open(default_img, 'rb') as fsrc, open(dest_path, 'wb') as fdst:
                        shutil.copyfileobj(fsrc, fdst)
            
            # 写入预览内容
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(self.post_template.format(
                    title=title,
                    date=date,
                    tags=formatted_tags,
                    content=formatted_content,
                    img_name=img_name
                ))
            
            # 在浏览器中打开预览
            webbrowser.open(f"file:///{temp_file}")
            self.animate_result("预览已在浏览器中打开", "success")
            
        except Exception as e:
            self.animate_result(f"预览失败：{str(e)}", "danger")
    
    def preview_edited_post(self):
        """预览编辑中的文章"""
        if not hasattr(self, 'current_post_file') or not self.current_post_file:
            self.animate_result("请先选择一篇文章", "warning")
            return
            
        try:
            # 创建临时预览文件
            temp_file = os.path.join(self.temp_preview_dir, "preview_edited_post.html")
            
            # 复制文件到临时目录
            import shutil
            shutil.copy2(self.current_post_file, temp_file)
            
            # 复制CSS文件
            if os.path.exists(self.css_file):
                shutil.copy2(self.css_file, self.temp_preview_dir)
            
            # 复制JS文件
            temp_js_dir = os.path.join(self.temp_preview_dir, "js")
            os.makedirs(temp_js_dir, exist_ok=True)
            if os.path.exists(self.js_dir):
                for js_file in os.listdir(self.js_dir):
                    if js_file.endswith(".js"):
                        shutil.copy2(os.path.join(self.js_dir, js_file), temp_js_dir)
            
            # 复制图片目录
            temp_img_dir = os.path.join(self.temp_preview_dir, "img")
            if os.path.exists(self.img_dir):
                if os.path.exists(temp_img_dir):
                    shutil.rmtree(temp_img_dir)
                shutil.copytree(self.img_dir, temp_img_dir)
            
            # 在浏览器中打开预览
            webbrowser.open(f"file:///{temp_file}")
            self.animate_result("预览已在浏览器中打开", "success")
            
        except Exception as e:
            self.animate_result(f"预览失败：{str(e)}", "danger")
    
    def preview_page(self):
        """预览页面"""
        if not hasattr(self, 'current_page_path') or not self.current_page_path:
            self.animate_page_result("请先选择一个页面", "warning")
            return
            
        try:
            # 创建临时目录结构
            temp_page_dir = os.path.join(self.temp_preview_dir, "preview_page")
            os.makedirs(temp_page_dir, exist_ok=True)
            
            # 复制当前页面
            page_filename = os.path.basename(self.current_page_path)
            temp_page_path = os.path.join(temp_page_dir, page_filename)
            
            # 保存当前编辑的内容到临时文件
            content = self.page_editor.get("1.0", tk.END)
            with open(temp_page_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 复制CSS文件
            if os.path.exists(self.css_file):
                shutil.copy2(self.css_file, temp_page_dir)
            
            # 复制JS目录
            temp_js_dir = os.path.join(temp_page_dir, "js")
            os.makedirs(temp_js_dir, exist_ok=True)
            if os.path.exists(self.js_dir):
                for js_file in os.listdir(self.js_dir):
                    if js_file.endswith(".js"):
                        shutil.copy2(os.path.join(self.js_dir, js_file), temp_js_dir)
            
            # 复制图片目录
            temp_img_dir = os.path.join(temp_page_dir, "img")
            if os.path.exists(self.img_dir):
                if os.path.exists(temp_img_dir):
                    shutil.rmtree(temp_img_dir)
                shutil.copytree(self.img_dir, temp_img_dir)
            
            # 复制posts目录（如果是文章列表页）
            if page_filename == "posts.html" and os.path.exists(self.posts_dir):
                temp_posts_dir = os.path.join(temp_page_dir, "posts")
                os.makedirs(temp_posts_dir, exist_ok=True)
                for post_file in os.listdir(self.posts_dir):
                    if post_file.endswith(".html"):
                        shutil.copy2(os.path.join(self.posts_dir, post_file), temp_posts_dir)
            
            # 在浏览器中打开预览
            webbrowser.open(f"file:///{temp_page_path}")
            self.animate_page_result("预览已在浏览器中打开", "success")
            
        except Exception as e:
            self.animate_page_result(f"预览失败：{str(e)}", "danger")
    
    def preview_css(self):
        """预览CSS效果（通过首页预览）"""
        try:
            # 创建临时目录
            temp_css_dir = os.path.join(self.temp_preview_dir, "preview_css")
            os.makedirs(temp_css_dir, exist_ok=True)
            
            # 复制首页文件
            if "首页" in self.html_files and os.path.exists(self.html_files["首页"]):
                index_filename = os.path.basename(self.html_files["首页"])
                temp_index_path = os.path.join(temp_css_dir, index_filename)
                shutil.copy2(self.html_files["首页"], temp_index_path)
            else:
                # 如果首页不存在，创建一个简单的首页用于预览
                temp_index_path = os.path.join(temp_css_dir, "index.html")
                with open(temp_index_path, "w", encoding="utf-8") as f:
                    f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>预览CSS效果</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header><h1>CSS预览</h1></header>
  <main>
    <p>这是一个CSS预览页面</p>
    <div class="card">卡片样式预览</div>
    <button class="btn">按钮样式</button>
  </main>
</body>
</html>""")
            
            # 保存当前编辑的CSS内容
            css_content = self.css_editor.get("1.0", tk.END)
            temp_css_path = os.path.join(temp_css_dir, "style.css")
            with open(temp_css_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            
            # 复制JS目录
            temp_js_dir = os.path.join(temp_css_dir, "js")
            os.makedirs(temp_js_dir, exist_ok=True)
            if os.path.exists(self.js_dir):
                for js_file in os.listdir(self.js_dir):
                    if js_file.endswith(".js"):
                        shutil.copy2(os.path.join(self.js_dir, js_file), temp_js_dir)
            
            # 复制图片目录
            temp_img_dir = os.path.join(temp_css_dir, "img")
            if os.path.exists(self.img_dir):
                if os.path.exists(temp_img_dir):
                    shutil.rmtree(temp_img_dir)
                shutil.copytree(self.img_dir, temp_img_dir)
            
            # 在浏览器中打开预览
            webbrowser.open(f"file:///{temp_index_path}")
            self.animate_css_result("CSS效果预览已在浏览器中打开", "success")
            
        except Exception as e:
            self.animate_css_result(f"预览失败：{str(e)}", "danger")
    
    def bind_animations(self):
        """绑定动画效果"""
        # 为按钮添加悬停效果
        self.style.configure("Accent.TButton", 
                            background="#1e40af",
                            foreground="white")
        
        # 为标签页添加切换动画（通过绑定事件实现）
        self.tab_control.bind("<<NotebookTabChanged>>", self.animate_tab_change)
    
    def animate_tab_change(self, event):
        """标签页切换动画"""
        current_tab = self.tab_control.select()
        frame = self.nametowidget(current_tab)
        
        # 淡入效果
        for i in range(0, 11):
            frame.configure(alpha=i/10)
            self.update_idletasks()
            time.sleep(0.02)
    
    def animate_result(self, text, status):
        """结果提示动画"""
        colors = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "warning": self.colors["warning"]
        }
        
        self.result_label.config(text=text, foreground=colors.get(status, self.colors["secondary"]))
        
        # 闪烁动画
        for i in range(2):
            self.result_label.config(foreground=colors.get(status, self.colors["secondary"]))
            self.update_idletasks()
            time.sleep(0.2)
            self.result_label.config(foreground=self.colors["background"])
            self.update_idletasks()
            time.sleep(0.2)
        
        self.result_label.config(foreground=colors.get(status, self.colors["secondary"]))
    
    def animate_page_result(self, text, status):
        """页面编辑结果提示动画"""
        colors = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "warning": self.colors["warning"]
        }
        
        self.page_result_label.config(text=text, foreground=colors.get(status, self.colors["secondary"]))
    
    def animate_css_result(self, text, status):
        """CSS编辑结果提示动画"""
        colors = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "warning": self.colors["warning"]
        }
        
        self.css_result_label.config(text=text, foreground=colors.get(status, self.colors["secondary"]))
    
    def animate_js_result(self, text, status):
        """JS编辑结果提示动画"""
        colors = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "warning": self.colors["warning"]
        }
        
        self.js_result_label.config(text=text, foreground=colors.get(status, self.colors["secondary"]))
    
    def animate_deploy_status(self, text, status):
        """部署状态动画"""
        colors = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "warning": self.colors["warning"],
            "info": self.colors["primary"]
        }
        
        self.deploy_status_var.set(text)
        self.deploy_status_label.config(foreground=colors.get(status, self.colors["secondary"]))
        
        # 状态变化动画
        for i in range(3):
            self.deploy_status_label.config(font=("SimHei", 10, "bold" if i%2 else "normal"))
            self.update_idletasks()
            time.sleep(0.2)
        
        self.deploy_status_label.config(font=("SimHei", 10))

if __name__ == "__main__":
    try:
        app = BlogManager()
        app.mainloop()
    except Exception as e:
        # 创建一个简单的错误提示窗口
        error_window = tk.Tk()
        error_window.title("运行错误")
        error_window.geometry("400x300")
        
        tk.Label(error_window, text="程序运行时出现错误：", font=('SimHei', 12)).pack(pady=10)
        error_text = scrolledtext.ScrolledText(error_window, wrap=tk.WORD)
        error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        error_text.insert(tk.END, str(e))
        error_text.config(state=tk.DISABLED)
        
        tk.Button(error_window, text="关闭", command=error_window.destroy).pack(pady=10)
        error_window.mainloop()
