`fork()` 是 Unix/Linux 系统中用于**创建子进程**的系统调用，几乎是多进程编程的“起点”。它会让当前进程**复制出一个几乎完全一样的新进程**，也就是“子进程”。

------

## 一、`fork()` 的基本原理

当一个进程调用 `fork()` 时：

- 系统会创建一个**新的子进程**，这个子进程是父进程的“克隆体”。
- 子进程会从 `fork()` 的那一行开始执行。
- `fork()` **返回两次**：
  - 在 **父进程** 中返回**子进程的 PID**；
  - 在 **子进程** 中返回**0**；
  - 如果出错，则返回 -1。

------

## 二、简单代码示例（Python）

```python
import os

pid = os.fork()

if pid == 0:
    print("我是子进程，PID =", os.getpid())
else:
    print("我是父进程，PID =", os.getpid(), "子进程 PID =", pid)
```

**输出可能是：**

```
我是父进程，PID = 1234 子进程 PID = 1235
我是子进程，PID = 1235
```

------

## 三、内存开销：复制还是共享？

- `fork()` 并**不会完全复制父进程的内存**，而是使用**写时复制（copy-on-write）**机制：
  - 初始时父子进程共享内存；
  - 只有当父或子修改内存数据时，系统才真正复制数据。

------

## 四、常见用途

- 创建子进程处理任务（如：Web服务器中多进程并发处理）
- 与 `exec()` 系列函数配合实现新程序运行
- 后台守护进程（daemon）启动流程的一部分

------

## 五、常见问题：

### 1. 如何避免**僵尸进程**？

- 父进程必须使用 `os.wait()` 或 `os.waitpid()` 等待子进程结束。

### 2. Windows 中有 `fork()` 吗？

- 没有，`fork()` 是 Unix/Linux 系统特有的。
- Windows 下使用 `multiprocessing` 模块实现跨平台多进程。

------

## 六、Python `fork()` 与多进程模块

虽然 `os.fork()` 很强大，但写多进程程序更推荐使用 `multiprocessing` 模块（封装更好，跨平台）：

```python
from multiprocessing import Process

def task():
    print("我是子进程")

p = Process(target=task)
p.start()
p.join()
```

------

如果你需要我讲讲 `fork` 后配合 `exec` 的用法，或者如何写一个守护进程（daemon）创建流程，也可以继续说，我来帮你写。