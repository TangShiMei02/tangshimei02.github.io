import os
import subprocess
import time
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class DeployHelper:
    def __init__(self, parent):
        self.parent = parent
        self.repo_path = os.getcwd()  # 默认当前目录
        self.remote_repo = ""
        self.branch = "main"
        
    def set_repo_info(self, repo_path, remote_repo, branch):
        """设置仓库信息"""
        self.repo_path = repo_path
        self.remote_repo = remote_repo
        self.branch = branch or "main"
    
    def run_deploy(self):
        """执行部署流程"""
        # 获取更新说明
        msg = simpledialog.askstring(
            "更新说明", 
            "请输入更新说明：",
            parent=self.parent,
            initialvalue=f"update: {time.strftime('%Y-%m-%d %H:%M')}"
        )
        
        if msg is None:  # 用户取消
            return False
            
        if not msg.strip():
            msg = f"update: {time.strftime('%Y-%m-%d')}"
        
        # 显示部署进度窗口
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("正在部署")
        progress_window.geometry("500x300")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        # 进度条
        ttk.Label(progress_window, text="部署进度：").pack(pady=10, anchor=tk.W, padx=20)
        progress = ttk.Progressbar(progress_window, length=450, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        # 日志区域
        ttk.Label(progress_window, text="部署日志：").pack(pady=10, anchor=tk.W, padx=20)
        log_text = tk.Text(progress_window, height=8, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        log_scroll = ttk.Scrollbar(log_text, command=log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=log_scroll.set, state=tk.DISABLED)
        
        # 更新日志的函数
        def update_log(message):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)
            progress_window.update_idletasks()
        
        # 在新线程中执行部署命令
        result = [False]  # 用列表存储结果，以便在内部函数中修改
        
        def deploy_thread():
            try:
                # 检查是否是Git仓库
                if not os.path.exists(os.path.join(self.repo_path, ".git")):
                    update_log("未发现Git仓库，正在初始化...")
                    self.run_command("git init", update_log)
                
                # 检查远程仓库配置
                if self.remote_repo:
                    remotes = self.run_command("git remote", update_log, capture_output=True)
                    if "origin" not in remotes:
                        update_log(f"添加远程仓库: {self.remote_repo}")
                        self.run_command(f"git remote add origin {self.remote_repo}", update_log)
                    else:
                        # 检查远程仓库是否匹配
                        current_remote = self.run_command("git remote get-url origin", update_log, capture_output=True)
                        if current_remote.strip() != self.remote_repo.strip():
                            update_log(f"更新远程仓库地址为: {self.remote_repo}")
                            self.run_command(f"git remote set-url origin {self.remote_repo}", update_log)
                
                # 检查分支
                branches = self.run_command("git branch --list", update_log, capture_output=True)
                if f"*{self.branch}" not in branches and self.branch not in branches:
                    update_log(f"创建并切换到 {self.branch} 分支")
                    self.run_command(f"git checkout -b {self.branch}", update_log)
                else:
                    update_log(f"切换到 {self.branch} 分支")
                    self.run_command(f"git checkout {self.branch}", update_log)
                
                # 拉取最新代码
                update_log("拉取远程最新代码...")
                self.run_command(f"git pull origin {self.branch}", update_log, allow_failure=True)
                
                # 添加文件
                update_log("添加文件到暂存区...")
                self.run_command("git add .", update_log)
                
                # 提交更改
                update_log(f"提交更改: {msg}")
                self.run_command(f'git commit -m "{msg}"', update_log, allow_failure=True)
                
                # 推送更改
                update_log("推送更改到远程仓库...")
                self.run_command(f"git push origin {self.branch}", update_log)
                
                update_log("部署完成！")
                result[0] = True
                
            except Exception as e:
                update_log(f"部署失败: {str(e)}")
            finally:
                progress.stop()
                ttk.Button(progress_window, text="关闭", command=progress_window.destroy).pack(pady=10)
        
        # 启动部署线程
        import threading
        threading.Thread(target=deploy_thread, daemon=True).start()
        
        progress_window.wait_window()  # 等待窗口关闭
        return result[0]
    
    def run_command(self, command, log_callback, capture_output=False, allow_failure=False):
        """执行命令并处理输出"""
        try:
            # 执行命令
            process = subprocess.Popen(
                command,
                cwd=self.repo_path,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace"  # 处理编码错误
            )
            
            # 实时输出日志
            output = []
            for line in process.stdout:
                stripped_line = line.strip()
                if stripped_line:
                    log_callback(stripped_line)
                    output.append(stripped_line)
            
            process.wait()
            
            # 检查返回代码
            if process.returncode != 0 and not allow_failure:
                raise Exception(f"命令执行失败: {command} (返回代码: {process.returncode})")
                
            return "\n".join(output) if capture_output else None
            
        except Exception as e:
            log_callback(f"命令执行错误: {str(e)}")
            if not allow_failure:
                raise
            return None

# 单独运行时的测试代码
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    deployer = DeployHelper(root)
    
    # 获取仓库路径
    repo_path = simpledialog.askstring(
        "仓库路径", 
        "请输入博客仓库路径：",
        initialvalue=os.getcwd()
    )
    
    if repo_path and os.path.exists(repo_path):
        deployer.set_repo_info(
            repo_path,
            simpledialog.askstring("远程仓库", "请输入远程仓库地址："),
            simpledialog.askstring("分支", "请输入分支名称：", initialvalue="main")
        )
        
        success = deployer.run_deploy()
        if success:
            messagebox.showinfo("成功", "部署完成！几分钟后刷新网页即可看到更新。")
        else:
            messagebox.showerror("失败", "部署过程中出现错误，请查看日志。")
    else:
        messagebox.showerror("错误", "无效的仓库路径")
    
    root.destroy()
