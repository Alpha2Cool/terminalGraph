# terminalGraph

终端图形绘制工具，用于在终端中展示2D波形图。

## 功能特点

- 在终端中展示2D波形图
- 支持从文件读取数据并实时显示
- 使用滑动窗口显示最新的数据点（默认100个）
- 固定坐标轴，只更新波形点，减少闪烁
- 支持命令行参数控制

## 安装方法

### 前提条件
- CMake 3.10或更高版本
- C++编译器（如Visual Studio 2022）

### 构建步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/Alpha2Cool/terminalGraph.git
   cd terminalGraph
   ```

2. 构建项目
   ```bash
   mkdir build
   cd build
   cmake ..
   cmake --build . --config Debug
   ```

## 使用说明

### 命令行参数

| 参数 | 描述 |
|------|------|
| -2d | 启用2D模式 |
| -f <file> | 指定数据文件路径 |
| -w <size> | 设置窗口大小（默认：100） |
| -h | 显示帮助信息 |

### 示例用法

1. 显示帮助信息
   ```bash
   terminalGraph -h
   ```

2. 基本使用
   ```bash
   terminalGraph -2d -f testData.txt
   ```

3. 自定义窗口大小
   ```bash
   terminalGraph -2d -f testData.txt -w 200
   ```

## 数据文件格式

数据文件应包含每行一个数值，例如：

```
0.5
1.2
-0.3
2.1
-1.5
```

## 项目结构

```
terminalGraph/
├── CMakeLists.txt     # CMake构建配置
├── terminalGraph.cpp  # C++实现
├── terminalGraph.py   # Python实现
├── testData.txt       # 测试数据文件
├── testWaveform.py    # 波形测试脚本
└── README.md          # 项目说明
```

## 技术实现

- 使用C++标准库进行文件I/O和数据处理
- 使用ANSI转义序列进行终端光标定位，减少闪烁
- 实现滑动窗口数据结构，只显示最新的数据点
- 数据归一化处理，适应不同范围的数据

## 许可证

本项目采用MIT许可证。