import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import datetime
import shutil
import subprocess
import threading

class BlogManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("简易博客发布工具")
        self.geometry("900x600")
        
        # 确保中文显示正常
        self.option_add("*Font", "SimHei 10")
        
        # 基础设置
        self.blog_dir = os.path.dirname(os.path.abspath(__file__))
        
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
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)
        
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
        self.title_entry = ttk.Entry(frame, width=60)
        self.title_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 日期
        ttk.Label(frame, text="发布日期：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(frame, width=20)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 封面图
        img_frame = ttk.Frame(frame)
        img_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(img_frame, text="封面图片：").pack(side=tk.LEFT)
        self.img_entry = ttk.Entry(img_frame, width=50)
        self.img_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(img_frame, text="选择图片", command=self.choose_image).pack(side=tk.LEFT, padx=5)
        
        # 文章内容
        ttk.Label(frame, text="文章内容：").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.content_text = scrolledtext.ScrolledText(frame, width=60, height=15)
        self.content_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.content_text.insert(tk.END, "在这里输入你的内容，每行将自动分段...")
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=1, sticky=tk.W, pady=10)
        ttk.Button(btn_frame, text="发布文章", command=self.create_post).pack(side=tk.LEFT, padx=5)
        
        # 结果提示
        self.result_label = ttk.Label(frame, text="", foreground="green")
        self.result_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.jpg;*.png")],
            title="选择封面图片"
        )
        if file_path:
            try:
                # 复制图片到项目目录
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(self.img_dir, file_name)
                shutil.copy2(file_path, dest_path)
                
                # 更新输入框
                self.img_entry.delete(0, tk.END)
                self.img_entry.insert(0, file_name)
                self.result_label.config(text=f"图片已添加：{file_name}", foreground="green")
            except Exception as e:
                self.result_label.config(text=f"图片添加失败：{str(e)}", foreground="red")

    def create_post(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        img_name = self.img_entry.get().strip()
        
        # 验证输入
        if not title:
            self.result_label.config(text="请输入文章标题！", foreground="red")
            return
        if not date:
            self.result_label.config(text="请输入发布日期！", foreground="red")
            return
        if not content:
            self.result_label.config(text="请输入文章内容！", foreground="red")
            return
        
        # 生成文章文件
        try:
            # 生成安全的文件名
            filename = "".join([c if c.isalnum() else "-" for c in title.lower()]) + ".html"
            file_path = os.path.join(self.posts_dir, filename)
            
            # 处理内容 - 简单分段
            formatted_content = ""
            for para in content.split("\n"):
                if para.strip():  # 跳过空行
                    formatted_content += f"    <p>{para.strip()}</p>\n\n"
            
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
  {f'<img src="../img/{img_name}" alt="{title}">' if img_name else ''}
  <div class="content">
{formatted_content}
  </div>
</body>
</html>""")
            
            self.result_label.config(text=f"发布成功！文件：{filename}", foreground="green")
            
            # 清空输入
            self.title_entry.delete(0, tk.END)
            self.content_text.delete(1.0, tk.END)
            self.img_entry.delete(0, tk.END)
            
        except Exception as e:
            self.result_label.config(text=f"发布失败：{str(e)}", foreground="red")

    # ----------------------
    # 一键部署功能
    # ----------------------
    def init_deploy_tab(self):
        frame = ttk.Frame(self.tab_deploy, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 仓库路径
        ttk.Label(frame, text="博客文件夹：").pack(anchor=tk.W, pady=5)
        self.repo_path = ttk.Entry(frame, width=60)
        self.repo_path.insert(0, self.blog_dir)
        self.repo_path.pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="选择文件夹", command=self.choose_repo).pack(anchor=tk.W, pady=5)
        
        # 更新说明
        ttk.Label(frame, text="更新说明：").pack(anchor=tk.W, pady=5)
        self.deploy_msg = ttk.Entry(frame, width=60)
        self.deploy_msg.insert(0, f"更新于 {datetime.today().strftime('%Y-%m-%d')}")
        self.deploy_msg.pack(fill=tk.X, pady=5)
        
        # 部署按钮
        ttk.Button(frame, text="开始部署", command=self.start_deploy).pack(pady=10)
        
        # 部署日志
        ttk.Label(frame, text="部署日志：").pack(anchor=tk.W, pady=5)
        self.deploy_log = scrolledtext.ScrolledText(frame, height=10)
        self.deploy_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self.deploy_log.config(state=tk.DISABLED)

    def choose_repo(self):
        path = filedialog.askdirectory(title="选择博客文件夹")
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
            # 执行部署命令
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
            
            self.update_log("部署完成！")
        except Exception as e:
            self.update_log(f"部署失败：{str(e)}")
        finally:
            self.deploying = False

    def update_log(self, text):
        self.deploy_log.config(state=tk.NORMAL)
        self.deploy_log.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {text}\n")
        self.deploy_log.see(tk.END)
        self.deploy_log.config(state=tk.DISABLED)

# 确保程序出错时不会闪退，而是显示错误信息
try:
    app = BlogManager()
    app.mainloop()
except Exception as e:
    # 创建错误提示窗口
    error_window = tk.Tk()
    error_window.title("程序错误")
    error_window.geometry("400x300")
    error_window.option_add("*Font", "SimHei 10")
    
    tk.Label(error_window, text="程序运行时出现错误：", fg="red").pack(pady=10)
    error_text = scrolledtext.ScrolledText(error_window, wrap=tk.WORD)
    error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    error_text.insert(tk.END, str(e))
    error_text.config(state=tk.DISABLED)
    
    tk.Button(error_window, text="关闭", command=error_window.destroy).pack(pady=10)
    error_window.mainloop()
