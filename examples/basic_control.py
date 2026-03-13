"""
基础控制示例
"""

from claw import ClawController, scan_ports


def main():
    """基础控制示例"""
    print("OpenClaw Toolkit - 基础控制示例")
    print("=" * 40)
    
    # 扫描串口
    ports = scan_ports()
    if not ports:
        print("未找到可用串口!")
        return
        
    print(f"可用串口: {ports}")
    
    # 选择第一个串口
    port = ports[0]
    print(f"使用串口: {port}")
    
    # 创建控制器
    controller = ClawController(port)
    
    # 连接
    if not controller.connect():
        print(f"连接失败: {controller.current_status.error}")
        return
        
    print("连接成功!")
    
    # 操作示例
    print("\n执行操作...")
    
    # 全开
    print("1. 完全打开 (180°)")
    controller.full_open()
    
    # 等待
    import time
    time.sleep(1)
    
    # 抓握
    print("2. 抓握位置 (45°)")
    controller.grip()
    
    time.sleep(1)
    
    # 全闭
    print("3. 完全关闭 (0°)")
    controller.full_close()
    
    time.sleep(1)
    
    # 复位
    print("4. 复位 (90°)")
    controller.reset()
    
    # 获取状态
    status = controller.status()
    print(f"\n最终状态:")
    print(f"  角度: {status.angle}°")
    print(f"  爪状态: {'打开' if status.gripper_open else '关闭'}")
    
    # 断开连接
    controller.disconnect()
    print("\n操作完成!")


if __name__ == "__main__":
    main()
