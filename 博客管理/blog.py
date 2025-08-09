import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import re
import webbrowser
from datetime import datetime
import subprocess
import tempfile
import threading
import time

class BlogManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("博客管理系统")
        self.geometry("1000x700")
        
        # 基础设置
        self.blog_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_preview_dir = os.path.join(tempfile.gettempdir(), "blog_preview")
        os.makedirs(self.temp_preview_dir, exist_ok=True)
        
        # 初始化文件夹
        self.posts_dir = os.path.join(self.blog_dir, "posts")
        self.img_dir = os.path.join(self.blog_dir, "img")
        for dir_path in [self.posts_dir, self.img_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self)
        self.tab_post = ttk.Frame(self.tab_control)  # 发布文章
        self.tab_deploy = ttk.Frame(self.tab_control)  # 一键部署
        self.tab_control.add(self.tab_post, text="发布文章")
        self.tab_control.add(self.tab_deploy, text="一键部署")
        self.tab_control.pack(expand=1, fill="both")
        
        # 初始化页面
        self.init_post_tab()
        self.init_deploy_tab()
        
        # 部署状态
        self.deploying = False

    # ----------------------
    # 发布文章功能
    # ----------------------
    def init_post_tab(self):
        frame = ttk.Frame(self.tab_post, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(frame, text="文章标题：").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=80)
        self.title_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 日期
        ttk.Label(frame, text="发布日期：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(frame, width=30)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 封面图
        img_frame = ttk.Frame(frame)
        img_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(img_frame, text="封面图片：").pack(side=tk.LEFT)
        self.img_entry = ttk.Entry(img_frame, width=60)
        self.img_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(img_frame, text="选择图片", command=self.choose_image).pack(side=tk.LEFT)
        
        # 文章内容
        ttk.Label(frame, text="文章内容：").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.content_text = scrolledtext.ScrolledText(frame, width=80, height=20)
        self.content_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        ttk.Button(frame, text="发布文章", command=self.create_post).grid(row=4, column=1, sticky=tk.W, pady=10)
        self.result_label = ttk.Label(frame, text="", foreground="green")
        self.result_label.grid(row=5, column=0, columnspan=2, pady=5)

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片", "*.jpg;*.png")])
        if file_path:
            try:
                import shutil
                file_name = os.path.basename(file_path)
                shutil.copy2(file_path, os.path.join(self.img_dir, file_name))
                self.img_entry.delete(0, tk.END)
                self.img_entry.insert(0, file_name)
                self.result_label.config(text=f"图片已添加：{file_name}")
            except Exception as e:
                self.result_label.config(text=f"图片错误：{str(e)}", foreground="red")

    def create_post(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        img_name = self.img_entry.get().strip() or "default.jpg"
        
        if not title or not date or not content:
            self.result_label.config(text="标题、日期、内容不能为空！", foreground="red")
            return
        
        # 生成文章文件
        try:
            filename = title.lower().replace(" ", "-") + ".html"
            file_path = os.path.join(self.posts_dir, filename)
            
            # 文章内容格式化
            formatted_content = ""
            for para in content.split("\n"):
                if para.startswith("# "):
                    formatted_content += f"    <h2>{para[2:]}</h2>\n\n"
                else:
                    formatted_content += f"    <p>{para}</p>\n\n"
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <h1>{title}</h1>
  <p>发布于 {date}</p>
  <img src="../img/{img_name}" alt="{title}">
  <div class="content">
{formatted_content}
  </div>
</body>
</html>""")
            
            self.result_label.config(text=f"发布成功！文件：{filename}")
            # 清空输入
            self.title_entry.delete(0, tk.END)
            self.content_text.delete(1.0, tk.END)
        except Exception as e:
            self.result_label.config(text=f"发布失败：{str(e)}", foreground="red")

    # ----------------------
    # 一键部署功能
    # ----------------------
    def init_deploy_tab(self):
        frame = ttk.Frame(self.tab_deploy, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 仓库路径
        ttk.Label(frame, text="博客文件夹：").pack(anchor=tk.W, pady=5)
        self.repo_path = ttk.Entry(frame, width=80)
        self.repo_path.insert(0, self.blog_dir)
        self.repo_path.pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="选择文件夹", command=self.choose_repo).pack(anchor=tk.W, pady=5)
        
        # 更新说明
        ttk.Label(frame, text="更新说明：").pack(anchor=tk.W, pady=5)
        self.deploy_msg = ttk.Entry(frame, width=80)
        self.deploy_msg.insert(0, f"更新于 {datetime.today().strftime('%Y-%m-%d')}")
        self.deploy_msg.pack(fill=tk.X, pady=5)
        
        # 部署按钮
        ttk.Button(frame, text="开始部署", command=self.start_deploy).pack(pady=10)
        
        # 部署日志
        ttk.Label(frame, text="部署日志：").pack(anchor=tk.W, pady=5)
        self.deploy_log = scrolledtext.ScrolledText(frame, height=15)
        self.deploy_log.pack(fill=tk.BOTH, expand=True)
        self.deploy_log.config(state=tk.DISABLED)

    def choose_repo(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path.delete(0, tk.END)
            self.repo_path.insert(0, path)

    def start_deploy(self):
        if self.deploying:
            messagebox.showinfo("提示", "正在部署中，请稍等...")
            return
        
        self.deploying = True
        self.update_log("开始部署...")
        threading.Thread(target=self.run_deploy, daemon=True).start()

    def run_deploy(self):
        msg = self.deploy_msg.get().strip() or "更新"
        repo_path = self.repo_path.get()
        
        try:
            # 执行部署命令（和你的bat脚本功能一样）
            commands = [
                f'git -C "{repo_path}" add .',
                f'git -C "{repo_path}" commit -m "{msg}"',
                f'git -C "{repo_path}" push'
            ]
            
            for cmd in commands:
                self.update_log(f"执行：{cmd}")
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
                )
                if result.stdout:
                    self.update_log(result.stdout)
                if result.stderr:
                    self.update_log(f"错误：{result.stderr}")
                if result.returncode != 0:
                    raise Exception(f"命令执行失败")
            
            self.update_log("部署完成！30秒后刷新网页可见")
        except Exception as e:
            self.update_log(f"部署失败：{str(e)}")
        finally:
            self.deploying = False

    def update_log(self, text):
        self.deploy_log.config(state=tk.NORMAL)
        self.deploy_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {text}\n")
        self.deploy_log.see(tk.END)
        self.deploy_log.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        app = BlogManager()
        app.mainloop()
    except Exception as e:
        # 显示错误信息（防止闪退看不到问题）
        error_win = tk.Tk()
        error_win.title("出错了")
        tk.Label(error_win, text=f"错误：{str(e)}").pack(padx=20, pady=20)
        tk.Button(error_win, text="关闭", command=error_win.destroy).pack(pady=10)
        error_win.mainloop()
