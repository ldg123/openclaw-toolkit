# 贡献指南

感谢您对 OpenClaw Toolkit 的兴趣! 我们欢迎任何形式的贡献,包括但不限于:

- 🐛 报告 bug
- 💡 提出新功能建议
- 📝 完善文档
- 💻 提交代码改进
- 🌐 翻译文档

## 开发环境设置

1. Fork 本仓库
2. 克隆您的 Fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/openclaw-toolkit.git
   cd openclaw-toolkit
   ```

3. 创建虚拟环境:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```

4. 安装开发依赖:
   ```bash
   pip install -e ".[dev]"
   ```

5. 运行测试:
   ```bash
   pytest
   ```

## 代码规范

- 使用 [Black](https://github.com/psf/black) 格式化代码
- 使用 [MyPy](https://github.com/python/mypy) 进行类型检查
- 编写单元测试覆盖新功能
- 更新文档说明任何 API 更改

## 提交 Pull Request

1. 创建特性分支:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. 提交更改:
   ```bash
   git commit -m 'Add amazing feature'
   ```

3. 推送到您的 Fork:
   ```bash
   git push origin feature/amazing-feature
   ```

4. 在 GitHub 上创建 Pull Request

## 问题反馈

如果您发现 bug 或有新功能建议,请在 [Issue Tracker](https://github.com/openclaw/openclaw-toolkit/issues) 中创建问题。

## 行为准则

请阅读并遵守我们的 [行为准则](CODE_OF_CONDUCT.md),保持友好和包容的社区环境。

---

感谢您的贡献! 🎉
