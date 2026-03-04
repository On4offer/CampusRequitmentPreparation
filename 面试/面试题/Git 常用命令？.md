好，这道题我继续帮你整理成标准的面试八股文模板 👇

------

# 面试题：Git 常用命令有哪些？

### 1. 概念解释

Git 是一个分布式版本控制系统，日常开发中需要频繁使用命令来 **管理代码版本、分支、远程仓库**。掌握常用命令能提高协作效率。

------

### 2. 常用命令分类与说明

#### （1）仓库操作

- `git init`：初始化本地仓库。
- `git clone <url>`：克隆远程仓库。
- `git config --global user.name "xxx"`：配置用户名。
- `git config --global user.email "xxx"`：配置邮箱。

#### （2）暂存区与版本管理

- `git status`：查看文件状态。
- `git add <file>`：将文件添加到暂存区。
- `git commit -m "message"`：提交代码到本地仓库。
- `git log`：查看提交历史。
- `git diff`：查看文件差异。
- `git reset --hard <commitId>`：回退到指定版本。

#### （3）分支管理

- `git branch`：查看分支。
- `git branch <name>`：新建分支。
- `git checkout <name>`：切换分支。
- `git merge <branch>`：合并分支。
- `git rebase <branch>`：变基操作。
- `git branch -d <name>`：删除分支。

#### （4）远程协作

- `git remote -v`：查看远程仓库。
- `git pull`：拉取远程最新代码并合并。
- `git push origin <branch>`：推送本地分支到远程仓库。
- `git fetch`：获取远程更新，但不合并。

#### （5）冲突解决与其他

- `git stash`：临时保存当前修改。
- `git stash pop`：恢复暂存的修改。
- `git cherry-pick <commitId>`：拣选某次提交到当前分支。
- `git tag <name>`：打标签（版本号）。

------

### 3. 案例说明（结合项目）

在 **黑马点评项目**：

- 开发一个新功能时，我会：

  ```bash
  git checkout -b feature/shop-cache   # 新建并切换分支
  git add .                            # 暂存所有修改
  git commit -m "新增店铺缓存逻辑"      # 提交
  git push origin feature/shop-cache   # 推送到远程
  ```

- 提交 PR 后合并到主分支，保证功能上线。

在 **苍穹外卖项目**：

- 修复线上 bug 时会：

  ```bash
  git checkout -b hotfix/order-bug
  # 修复完成后提交
  git cherry-pick 提交ID   # 如果其他分支也需要修复
  git push origin hotfix/order-bug
  ```

------

### 4. 使用场景

- **日常开发**：commit、branch、checkout、merge。
- **团队协作**：push、pull、fetch。
- **问题排查/回滚**：log、reset、revert。
- **上线发布**：tag、cherry-pick、hotfix 分支。

------

### 5. 面试标准回答模板

> Git 常用命令主要包括几类：
>  1）版本管理：`git add`、`git commit`、`git log`；
>  2）分支操作：`git branch`、`git checkout`、`git merge`、`git rebase`；
>  3）远程协作：`git push`、`git pull`、`git fetch`；
>  4）其他工具：`git stash`、`git cherry-pick`、`git tag`。
>  在我的项目中，比如黑马点评，我经常用 `git checkout -b` 新建分支开发功能，然后通过 `git push` 推送到远程，提交 PR 后合并进主分支，保证开发流程规范。

------

### 6. 扩展追问

- `git pull` 和 `git fetch` 的区别？
- `git reset` 和 `git revert` 的区别？
- `git stash` 在多人协作中有什么用？
- 如何删除远程分支？
- 你在项目中最常用的 Git 命令组合是什么？

------

要不要我接着帮你整理 **“Git pull 和 fetch 的区别？”** 这种常见追问题？