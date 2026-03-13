"""
OpenClaw Toolkit 安装配置
"""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """读取文件内容"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


setup(
    name="openclaw-toolkit",
    version="1.0.0",
    author="OpenClaw Team",
    author_email="team@openclaw.ai",
    description="开源机械爪 & 舵机控制工具箱",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/openclaw-toolkit",
    project_urls={
        "Bug Tracker": "https://github.com/openclaw/openclaw-toolkit/issues",
        "Documentation": "https://github.com/openclaw/openclaw-toolkit#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "pyserial>=3.5",
        "PyYAML>=6.0",
        "click>=8.0",
    ],
    extras_require={
        "gui": [
            "PyQt6>=6.4",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-qt>=4.0",
            "black>=23.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openclaw-toolkit=openclaw_toolkit:main",
            "openclaw-gui=gui.window:main",
            "openclaw-cli=cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
