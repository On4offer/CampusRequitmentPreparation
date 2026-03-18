# venv 已激活但提示 `No module named pytest`

日期：2026-03-18  
项目：个性化情感陪伴智能体（Windows + PowerShell）

---

## 1. 现象（Symptoms）

在项目根目录执行：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

报错：

```text
...\.venv\Scripts\python.exe: No module named pytest
```

终端提示符可能同时出现：
- `(.venv)`（已激活虚拟环境）
- `(base)`（conda base 仍处于激活状态）

---

## 2. 根因（Root Cause）

`pytest` **没有安装到当前正在使用的解释器环境**（即项目的 `.venv`）中，而是安装到了其他 Python 环境里（常见：conda base、系统 Python、用户目录 site-packages）。

因此：
- `python -m pytest` 使用的是 `.venv\Scripts\python.exe`
- 但该环境内并不存在 `pytest` 模块

---

## 3. 复现步骤（Repro）

1. 在 conda/base 或系统 Python 环境中安装过 pytest
2. 在项目中创建并激活 `.venv`
3. 直接运行 `python -m pytest -q`
4. 由于 `.venv` 内缺少 pytest，触发 `No module named pytest`

---

## 4. 解决方案（Fix）

### 4.1 临时解决方案（一行命令应急）

如果你的提示符里还带着 `(base)`（conda base 处于激活状态），先执行这行把它退掉：

```powershell
conda deactivate
```

然后在**已激活 `.venv`** 的前提下，直接执行下面这一行把 pytest 装进当前环境：

```powershell
python -m pip install -r requirements.txt
```

然后再跑：

```powershell
python -m pytest -q
```

> 说明：用 `python -m pip ...` 是为了保证安装发生在“当前 python（即 `.venv`）”里，避免装到 conda/base 或系统 Python。

### 4.2 标准解决方案（推荐）

在项目根目录执行（推荐做法：始终用 `python -m ...`）：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

预期输出：
- `pytest` 安装成功（安装位置属于 `.venv`）
- `3 passed`（或你的测试用例数量）

可选：关闭 conda base 自动激活（从根上减少干扰）：

```powershell
conda config --set auto_activate_base false
```

然后关闭终端重开。

---

## 5. 验证（Verify）

### 5.1 验证 pytest 已装入 `.venv`

```powershell
python -c "import sys; import pytest; print(sys.executable); print(pytest.__version__)"
```

预期：
- `sys.executable` 指向 `<项目>\\.venv\\Scripts\\python.exe`
- 打印出 pytest 版本号

### 5.2 运行测试

```powershell
python -m pytest -q
```

预期：测试通过。

---

## 6. 预防（Prevention）

最小规则（强烈推荐）：
- **永远不用裸 `pip/pytest/uvicorn`**
- 永远使用：
  - `python -m pip ...`
  - `python -m pytest ...`
  - `python -m uvicorn ...`

原因：
- 这样永远与当前解释器绑定，避免“装在 A 环境、跑在 B 环境”的经典坑。

