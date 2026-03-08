# 📋 Java 异常机制与IO - 常用API与使用场景速查

> 日常开发常用异常处理、IO/NIO操作与代码模板，配合《学习笔记.md》系统学习使用。

---

## ⚠️ 异常处理速查

### 常用异常类

| 异常类 | 类型 | 场景 |
|--------|------|------|
| `NullPointerException` | 运行时 | 空指针访问 |
| `IllegalArgumentException` | 运行时 | 非法参数 |
| `IllegalStateException` | 运行时 | 非法状态 |
| `IndexOutOfBoundsException` | 运行时 | 索引越界 |
| `ArrayIndexOutOfBoundsException` | 运行时 | 数组越界 |
| `StringIndexOutOfBoundsException` | 运行时 | 字符串索引越界 |
| `NumberFormatException` | 运行时 | 数字格式错误 |
| `ClassCastException` | 运行时 | 类型转换错误 |
| `ArithmeticException` | 运行时 | 算术错误（如除零）|
| `UnsupportedOperationException` | 运行时 | 不支持的操作 |
| `IOException` | 受检 | IO操作失败 |
| `FileNotFoundException` | 受检 | 文件不存在 |
| `SocketException` | 受检 | 网络异常 |
| `SQLException` | 受检 | 数据库异常 |
| `ClassNotFoundException` | 受检 | 类找不到 |
| `NoSuchMethodException` | 受检 | 方法不存在 |
| `InterruptedException` | 受检 | 线程被中断 |
| `OutOfMemoryError` | 错误 | 内存溢出 |
| `StackOverflowError` | 错误 | 栈溢出 |

### try-catch-finally 模板

```java
// 基本结构
try {
    // 可能抛出异常的代码
} catch (SpecificException e) {
    // 处理特定异常
} catch (AnotherException e) {
    // 处理其他异常
} finally {
    // 始终执行的清理代码
}

// 多异常合并（JDK 7+）
try {
    // 可能抛出异常的代码
} catch (IOException | SQLException e) {
    // 统一处理多种异常
    log.error("IO or SQL error", e);
}

// 捕获后重新抛出
try {
    riskyOperation();
} catch (IOException e) {
    log.error("Operation failed", e);
    throw new BusinessException("业务操作失败", e);  // 包装后抛出
}
```

### try-with-resources（自动关闭资源）

```java
// JDK 7+ 自动关闭实现AutoCloseable的资源
// 资源会在try结束时自动关闭，即使发生异常

try (FileInputStream fis = new FileInputStream("file.txt");
     BufferedReader br = new BufferedReader(new InputStreamReader(fis))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
} catch (IOException e) {
    log.error("读取文件失败", e);
}

// 多个资源用分号分隔
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql);
     ResultSet rs = ps.executeQuery()) {
    while (rs.next()) {
        // 处理结果
    }
} catch (SQLException e) {
    log.error("数据库查询失败", e);
}

// 自定义AutoCloseable
public class MyResource implements AutoCloseable {
    public void doSomething() {
        System.out.println("Doing something");
    }
    
    @Override
    public void close() {
        System.out.println("MyResource closed");
    }
}

try (MyResource resource = new MyResource()) {
    resource.doSomething();
}  // 自动调用close()
```

### 异常处理最佳实践

```java
// 1. 不要捕获Throwable或Exception（太宽泛）
// ✗ 不好
try {
    // ...
} catch (Exception e) {  // 捕获范围太大
    // ...
}

// ✓ 好
try {
    // ...
} catch (SpecificException e) {  // 捕获具体异常
    // ...
}

// 2. 不要忽略异常
// ✗ 不好
try {
    // ...
} catch (IOException e) {
    // 空处理，异常信息丢失！
}

// ✓ 好
try {
    // ...
} catch (IOException e) {
    log.error("操作失败", e);
    // 或重新抛出
    throw new RuntimeException("操作失败", e);
}

// 3. 不要只打印异常，要包含上下文
try {
    processUser(userId);
} catch (UserNotFoundException e) {
    // ✗ 不好
    log.error("用户不存在");
    
    // ✓ 好
    log.error("用户不存在, userId={}", userId, e);
}

// 4. 异常转换时保留原始异常
try {
    // ...
} catch (SQLException e) {
    // ✓ 保留原始异常
    throw new DataAccessException("数据库访问失败", e);
}

// 5. 优先使用标准异常
// ✓ 好
if (obj == null) {
    throw new IllegalArgumentException("参数不能为空");
}

// 6. 自定义异常
public class BusinessException extends RuntimeException {
    private final String errorCode;
    
    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
    
    public BusinessException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }
    
    public String getErrorCode() {
        return errorCode;
    }
}

// 7. 使用Optional避免空指针
// ✗ 不好
String value = getString();
if (value != null) {
    return value.toUpperCase();
}
return null;

// ✓ 好
return Optional.ofNullable(getString())
    .map(String::toUpperCase)
    .orElse(null);
```

---

## 📁 文件IO操作

### 文件路径操作（NIO.2）

```java
import java.nio.file.*;

// 创建Path
Path path1 = Paths.get("/home/user/file.txt");
Path path2 = Path.of("/home/user/file.txt");  // JDK 11+
Path path3 = Paths.get("home", "user", "file.txt");

// 路径操作
Path absolute = path1.toAbsolutePath();
Path normalized = path1.normalize();           // 去除冗余部分如 . 和 ..
Path parent = path1.getParent();               // /home/user
Path fileName = path1.getFileName();           // file.txt
int nameCount = path1.getNameCount();          // 路径组成部分数量
Path subPath = path1.subpath(0, 2);            // home/user
boolean isAbsolute = path1.isAbsolute();

// 路径拼接
Path resolved = path1.resolve("subdir/file.txt");  // /home/user/subdir/file.txt
Path resolved2 = path1.resolveSibling("other.txt"); // /home/user/other.txt
Path relativized = path1.relativize(path2);     // 计算相对路径

// 文件属性
boolean exists = Files.exists(path1);
boolean isFile = Files.isRegularFile(path1);
boolean isDir = Files.isDirectory(path1);
boolean isReadable = Files.isReadable(path1);
boolean isWritable = Files.isWritable(path1);
boolean isExecutable = Files.isExecutable(path1);
boolean isHidden = Files.isHidden(path1);
long size = Files.size(path1);
FileTime lastModified = Files.getLastModifiedTime(path1);

// 获取所有属性（批量）
BasicFileAttributes attrs = Files.readAttributes(path1, BasicFileAttributes.class);
attrs.creationTime();
attrs.lastAccessTime();
attrs.lastModifiedTime();
attrs.isRegularFile();
attrs.isDirectory();
attrs.size();
```

### 文件读写操作

```java
// 读取所有字节
byte[] bytes = Files.readAllBytes(path);

// 读取所有行
List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);

// 读取为字符串
String content = Files.readString(path, StandardCharsets.UTF_8);  // JDK 11+

// 写入字节
Files.write(path, bytes);

// 写入多行
Files.write(path, lines, StandardCharsets.UTF_8);

// 写入字符串
Files.writeString(path, "Hello World", StandardCharsets.UTF_8);  // JDK 11+

// 追加模式
Files.write(path, lines, StandardCharsets.UTF_8, 
    StandardOpenOption.APPEND, StandardOpenOption.CREATE);

// 使用BufferedReader逐行读取（大文件推荐）
try (BufferedReader reader = Files.newBufferedReader(path)) {
    String line;
    while ((line = reader.readLine()) != null) {
        // 处理每一行
    }
}

// 使用BufferedWriter写入
try (BufferedWriter writer = Files.newBufferedWriter(path)) {
    writer.write("Hello");
    writer.newLine();
    writer.write("World");
}

// 使用InputStream/OutputStream
try (InputStream is = Files.newInputStream(path);
     OutputStream os = Files.newOutputStream(targetPath)) {
    byte[] buffer = new byte[8192];
    int len;
    while ((len = is.read(buffer)) > 0) {
        os.write(buffer, 0, len);
    }
}
```

### 文件与目录操作

```java
// 创建文件
Files.createFile(path);                        // 创建空文件（已存在会报错）
Files.createDirectories(path.getParent());     // 创建父目录（如果不存在）

// 创建目录
Files.createDirectory(path);                   // 创建单级目录
Files.createDirectories(path);                 // 创建多级目录

// 复制文件
Files.copy(source, target);                    // 目标存在会报错
Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING);
Files.copy(source, target, 
    StandardCopyOption.COPY_ATTRIBUTES,
    StandardCopyOption.REPLACE_EXISTING);

// 移动/重命名文件
Files.move(source, target);
Files.move(source, target, StandardCopyOption.REPLACE_EXISTING);
Files.move(source, target, StandardCopyOption.ATOMIC_MOVE);

// 删除文件
Files.delete(path);                            // 不存在会抛异常
Files.deleteIfExists(path);                    // 不存在不抛异常

// 遍历目录
try (Stream<Path> stream = Files.list(dir)) {  // 只遍历一级
    stream.forEach(System.out::println);
}

// 递归遍历
try (Stream<Path> stream = Files.walk(dir)) {  // 遍历所有子目录
    stream.filter(Files::isRegularFile)
          .forEach(System.out::println);
}

// 递归遍历（限制深度）
try (Stream<Path> stream = Files.walk(dir, 3)) {  // 最多3层
    // ...
}

// 查找文件
try (Stream<Path> stream = Files.find(dir, 10, 
    (path, attrs) -> path.toString().endsWith(".txt"))) {
    // ...
}

// 使用DirectoryStream（更高效，适合大目录）
try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
    for (Path entry : stream) {
        System.out.println(entry.getFileName());
    }
}

// 带过滤器的DirectoryStream
try (DirectoryStream<Path> stream = 
    Files.newDirectoryStream(dir, "*.txt")) {
    // 只匹配.txt文件
}

// 创建临时文件/目录
Path tempFile = Files.createTempFile("prefix", ".tmp");
Path tempDir = Files.createTempDirectory("prefix");

// 创建符号链接和硬链接
Files.createSymbolicLink(link, target);
Files.createLink(hardLink, target);

// 读取符号链接指向的真实路径
Path realPath = Files.readSymbolicLink(link);
```

### 文件监听（WatchService）

```java
// 监视目录变化
WatchService watchService = FileSystems.getDefault().newWatchService();
Path dir = Paths.get("/home/user/watch");

// 注册监听事件
dir.register(watchService,
    StandardWatchEventKinds.ENTRY_CREATE,    // 文件创建
    StandardWatchEventKinds.ENTRY_DELETE,    // 文件删除
    StandardWatchEventKinds.ENTRY_MODIFY,    // 文件修改
    StandardWatchEventKinds.OVERFLOW         // 事件丢失
);

// 监听循环
while (true) {
    WatchKey key = watchService.take();       // 阻塞等待事件
    
    for (WatchEvent<?> event : key.pollEvents()) {
        WatchEvent.Kind<?> kind = event.kind();
        Path fileName = (Path) event.context();
        
        System.out.println(kind.name() + ": " + fileName);
        
        if (kind == StandardWatchEventKinds.ENTRY_CREATE) {
            // 处理创建事件
        }
    }
    
    boolean valid = key.reset();              // 重置key以继续监听
    if (!valid) {
        break;                                // 目录不可访问，退出
    }
}
```

---

## 🌊 传统IO（字节流/字符流）

### 字节流

```java
// FileInputStream / FileOutputStream
try (FileInputStream fis = new FileInputStream("input.txt");
     FileOutputStream fos = new FileOutputStream("output.txt")) {
    
    byte[] buffer = new byte[1024];
    int len;
    while ((len = fis.read(buffer)) != -1) {
        fos.write(buffer, 0, len);
    }
}

// BufferedInputStream / BufferedOutputStream（带缓冲，性能更好）
try (BufferedInputStream bis = new BufferedInputStream(
        new FileInputStream("input.txt"));
     BufferedOutputStream bos = new BufferedOutputStream(
        new FileOutputStream("output.txt"))) {
    
    byte[] buffer = new byte[8192];
    int len;
    while ((len = bis.read(buffer)) != -1) {
        bos.write(buffer, 0, len);
    }
}

// DataInputStream / DataOutputStream（读写基本数据类型）
try (DataOutputStream dos = new DataOutputStream(
        new FileOutputStream("data.bin"))) {
    dos.writeInt(100);
    dos.writeDouble(3.14);
    dos.writeUTF("Hello");
}

try (DataInputStream dis = new DataInputStream(
        new FileInputStream("data.bin"))) {
    int i = dis.readInt();
    double d = dis.readDouble();
    String s = dis.readUTF();
}

// ObjectInputStream / ObjectOutputStream（对象序列化）
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("object.dat"))) {
    oos.writeObject(new User("张三", 20));
}

try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("object.dat"))) {
    User user = (User) ois.readObject();
}

// ByteArrayInputStream / ByteArrayOutputStream（内存操作）
ByteArrayOutputStream baos = new ByteArrayOutputStream();
baos.write("Hello".getBytes());
byte[] data = baos.toByteArray();

ByteArrayInputStream bais = new ByteArrayInputStream(data);
```

### 字符流

```java
// FileReader / FileWriter（默认编码）
try (FileReader fr = new FileReader("input.txt");
     FileWriter fw = new FileWriter("output.txt")) {
    char[] buffer = new char[1024];
    int len;
    while ((len = fr.read(buffer)) != -1) {
        fw.write(buffer, 0, len);
    }
}

// 指定编码（推荐）
try (InputStreamReader isr = new InputStreamReader(
        new FileInputStream("input.txt"), StandardCharsets.UTF_8);
     OutputStreamWriter osw = new OutputStreamWriter(
        new FileOutputStream("output.txt"), StandardCharsets.UTF_8)) {
    char[] buffer = new char[1024];
    int len;
    while ((len = isr.read(buffer)) != -1) {
        osw.write(buffer, 0, len);
    }
}

// BufferedReader / BufferedWriter（带缓冲）
try (BufferedReader br = new BufferedReader(
        new FileReader("input.txt"));
     BufferedWriter bw = new BufferedWriter(
        new FileWriter("output.txt"))) {
    
    String line;
    while ((line = br.readLine()) != null) {
        bw.write(line);
        bw.newLine();
    }
}

// PrintWriter（方便输出）
try (PrintWriter pw = new PrintWriter("output.txt")) {
    pw.println("Hello");
    pw.printf("Name: %s, Age: %d%n", "张三", 20);
}

// StringReader / StringWriter（内存操作）
StringReader sr = new StringReader("Hello World");
StringWriter sw = new StringWriter();
char[] buffer = new char[1024];
int len;
while ((len = sr.read(buffer)) != -1) {
    sw.write(buffer, 0, len);
}
String result = sw.toString();
```

---

## ⚡ NIO（New IO）

### Buffer操作

```java
// ByteBuffer（最常用的Buffer）
// 创建Buffer
ByteBuffer buffer = ByteBuffer.allocate(1024);     // 堆内存
ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);  // 直接内存

// 写入数据（put）
buffer.put((byte) 10);
buffer.put("Hello".getBytes());

// 切换到读模式
buffer.flip();

// 读取数据（get）
while (buffer.hasRemaining()) {
    byte b = buffer.get();
    System.out.print((char) b);
}

// 清空Buffer（准备再次写入）
buffer.clear();  // 位置设为0，limit设为capacity，数据不清除

// 或压缩Buffer（保留未读数据）
buffer.compact();  // 将未读数据移到开头，位置设在未读数据之后

// 其他类型Buffer
CharBuffer charBuffer = CharBuffer.allocate(1024);
IntBuffer intBuffer = IntBuffer.allocate(1024);
LongBuffer longBuffer = LongBuffer.allocate(1024);
FloatBuffer floatBuffer = FloatBuffer.allocate(1024);
DoubleBuffer doubleBuffer = DoubleBuffer.allocate(1024);

// Buffer属性
int capacity = buffer.capacity();   // 容量
int position = buffer.position();   // 当前位置
int limit = buffer.limit();         // 限制
boolean hasRemaining = buffer.hasRemaining();  // 是否还有剩余
int remaining = buffer.remaining(); // 剩余数量
```

### Channel操作

```java
// FileChannel（文件通道）
try (RandomAccessFile file = new RandomAccessFile("data.txt", "rw");
     FileChannel channel = file.getChannel()) {
    
    // 读取
    ByteBuffer buffer = ByteBuffer.allocate(1024);
    int bytesRead = channel.read(buffer);
    
    // 写入
    buffer.clear();
    buffer.put("Hello".getBytes());
    buffer.flip();
    channel.write(buffer);
    
    // 文件位置
    long position = channel.position();
    channel.position(0);  // 设置位置
    
    // 文件大小
    long size = channel.size();
    
    // 截断文件
    channel.truncate(1024);
    
    // 强制写入磁盘
    channel.force(true);
    
    // 内存映射文件（大文件高效操作）
    MappedByteBuffer mappedBuffer = channel.map(
        FileChannel.MapMode.READ_WRITE, 0, channel.size());
}

// 使用FileChannel复制文件（零拷贝）
try (FileChannel source = new FileInputStream("source.txt").getChannel();
     FileChannel dest = new FileOutputStream("dest.txt").getChannel()) {
    
    // 方式1：transferFrom
    dest.transferFrom(source, 0, source.size());
    
    // 方式2：transferTo
    source.transferTo(0, source.size(), dest);
}

// SocketChannel（网络通道）
try (SocketChannel socketChannel = SocketChannel.open()) {
    socketChannel.connect(new InetSocketAddress("localhost", 8080));
    
    ByteBuffer buffer = ByteBuffer.allocate(1024);
    buffer.put("Hello Server".getBytes());
    buffer.flip();
    socketChannel.write(buffer);
    
    buffer.clear();
    socketChannel.read(buffer);
}

// ServerSocketChannel
try (ServerSocketChannel serverChannel = ServerSocketChannel.open()) {
    serverChannel.bind(new InetSocketAddress(8080));
    serverChannel.configureBlocking(false);  // 非阻塞模式
    
    while (true) {
        SocketChannel clientChannel = serverChannel.accept();
        if (clientChannel != null) {
            // 处理客户端连接
        }
    }
}
```

### Selector（多路复用）

```java
// NIO多路复用服务器示例
Selector selector = Selector.open();

ServerSocketChannel serverChannel = ServerSocketChannel.open();
serverChannel.bind(new InetSocketAddress(8080));
serverChannel.configureBlocking(false);
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    int readyChannels = selector.select();  // 阻塞等待就绪通道
    if (readyChannels == 0) continue;
    
    Set<SelectionKey> selectedKeys = selector.selectedKeys();
    Iterator<SelectionKey> keyIterator = selectedKeys.iterator();
    
    while (keyIterator.hasNext()) {
        SelectionKey key = keyIterator.next();
        
        if (key.isAcceptable()) {
            // 接受新连接
            ServerSocketChannel server = (ServerSocketChannel) key.channel();
            SocketChannel client = server.accept();
            client.configureBlocking(false);
            client.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // 读取数据
            SocketChannel client = (SocketChannel) key.channel();
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            int bytesRead = client.read(buffer);
            
            if (bytesRead == -1) {
                key.cancel();
                client.close();
            } else {
                // 处理数据
            }
        } else if (key.isWritable()) {
            // 写入数据
        }
        
        keyIterator.remove();
    }
}
```

---

## 🎯 常用代码场景

### 1. 文件复制工具

```java
public class FileCopyUtil {
    // NIO方式（推荐，使用零拷贝）
    public static void copyFileNIO(Path source, Path target) throws IOException {
        try (FileChannel sourceChannel = FileChannel.open(source, StandardOpenOption.READ);
             FileChannel targetChannel = FileChannel.open(target, 
                 StandardOpenOption.WRITE, StandardOpenOption.CREATE)) {
            
            sourceChannel.transferTo(0, sourceChannel.size(), targetChannel);
        }
    }
    
    // 传统IO方式
    public static void copyFileIO(File source, File target) throws IOException {
        try (InputStream is = new FileInputStream(source);
             OutputStream os = new FileOutputStream(target)) {
            
            byte[] buffer = new byte[8192];
            int len;
            while ((len = is.read(buffer)) > 0) {
                os.write(buffer, 0, len);
            }
        }
    }
    
    // Java 8+ 简单方式
    public static void copyFileSimple(Path source, Path target) throws IOException {
        Files.copy(source, target, StandardCopyOption.REPLACE_EXISTING);
    }
}
```

### 2. 大文件分块读取

```java
public void readLargeFile(Path path) throws IOException {
    try (BufferedReader reader = Files.newBufferedReader(path)) {
        String line;
        int lineCount = 0;
        while ((line = reader.readLine()) != null) {
            // 处理每一行
            processLine(line);
            
            // 每1000行输出进度
            if (++lineCount % 1000 == 0) {
                System.out.println("Processed " + lineCount + " lines");
            }
        }
    }
}

// 使用Stream API（JDK 8+）
public void readWithStream(Path path) throws IOException {
    try (Stream<String> lines = Files.lines(path)) {
        lines.forEach(this::processLine);
    }
}

// 并行处理（适合CPU密集型处理）
public void readParallel(Path path) throws IOException {
    try (Stream<String> lines = Files.lines(path)) {
        lines.parallel().forEach(this::processLine);
    }
}
```

### 3. 配置文件的读写

```java
public class ConfigUtil {
    // 读取properties
    public static Properties loadProperties(Path path) throws IOException {
        Properties props = new Properties();
        try (InputStream is = Files.newInputStream(path)) {
            props.load(is);
        }
        return props;
    }
    
    // 保存properties
    public static void saveProperties(Path path, Properties props, String comments) 
            throws IOException {
        try (OutputStream os = Files.newOutputStream(path)) {
            props.store(os, comments);
        }
    }
    
    // 读取JSON（使用Jackson或Gson）
    public static <T> T loadJson(Path path, Class<T> clazz) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(path.toFile(), clazz);
    }
    
    // 保存JSON
    public static void saveJson(Path path, Object obj) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        mapper.writerWithDefaultPrettyPrinter()
              .writeValue(path.toFile(), obj);
    }
}
```

### 4. 序列化与反序列化

```java
public class SerializationUtil {
    // Java原生序列化
    public static void serialize(Object obj, Path path) throws IOException {
        try (ObjectOutputStream oos = new ObjectOutputStream(
                Files.newOutputStream(path))) {
            oos.writeObject(obj);
        }
    }
    
    @SuppressWarnings("unchecked")
    public static <T> T deserialize(Path path) throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(
                Files.newInputStream(path))) {
            return (T) ois.readObject();
        }
    }
    
    // 需要序列化的类
    public static class User implements Serializable {
        private static final long serialVersionUID = 1L;
        private String name;
        private transient String password;  // transient字段不序列化
        
        // 自定义序列化
        private void writeObject(ObjectOutputStream out) throws IOException {
            out.defaultWriteObject();
            // 可以加密后再写入
            out.writeObject(encrypt(password));
        }
        
        private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
            in.defaultReadObject();
            // 解密
            password = decrypt((String) in.readObject());
        }
    }
}
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| 未关闭流 | 导致资源泄漏 | 用try-with-resources |
| 忽略编码 | 中文乱码 | 显式指定UTF-8 |
| 大文件readAllBytes | 内存溢出 | 用BufferedReader逐行读取 |
| 删除操作不判断 | 误删重要文件 | 先判断exists，或移动到回收站 |
| 路径拼接用字符串 | 跨平台问题 | 用Paths.get()或Path.resolve() |
| 遍历目录不处理异常 | 某些文件无权限会中断 | 用try-catch包裹处理逻辑 |
| 序列化不设置serialVersionUID | 版本不兼容 | 显式定义serialVersionUID |
| NIO Buffer模式混淆 | flip/clear用错 | 写前flip，写后clear |
| 捕获异常后吞掉 | 问题难以排查 | 至少记录日志 |

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
