"""
OpenClaw Toolkit CLI 主程序
"""

import click
import sys
from typing import Optional

from claw import ClawController, scan_ports, get_port_info, __version__
from claw.core import ClawStatus


@click.group()
@click.version_option(version=__version__)
def cli():
    """OpenClaw Toolkit - 开源机械爪 & 舵机控制工具箱"""
    pass


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='显示详细信息')
def scan(verbose):
    """扫描可用串口"""
    click.echo("正在扫描串口...")
    
    ports = scan_ports()
    
    if not ports:
        click.echo(click.style("未找到可用串口", fg='red'))
        return
        
    click.echo(f"\n找到 {len(ports)} 个可用串口:\n")
    
    if verbose:
        port_info = get_port_info()
        for info in port_info:
            click.echo(f"  设备: {info['device']}")
            if info['description']:
                click.echo(f"    描述: {info['description']}")
            if info['manufacturer']:
                click.echo(f"    制造商: {info['manufacturer']}")
            if info['serial_number']:
                click.echo(f"    序列号: {info['serial_number']}")
            click.echo("")
    else:
        for port in ports:
            click.echo(f"  - {port}")


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
@click.option('--timeout', '-t', default=1.0, help='超时时间(秒)')
def connect(port, baudrate, timeout):
    """连接机械爪"""
    click.echo(f"正在连接 {port} @ {baudrate}bps...")
    
    controller = ClawController(port, baudrate, timeout)
    
    if controller.connect():
        click.echo(click.style("连接成功!", fg='green'))
        
        status = controller.status()
        click.echo(f"\n状态:")
        click.echo(f"  角度: {status.angle}°")
        click.echo(f"  爪状态: {'打开' if status.gripper_open else '关闭'}")
        
        controller.disconnect()
    else:
        click.echo(click.style(f"连接失败: {status.error}", fg='red'))
        sys.exit(1)


@cli.command()
@click.argument('port')
@click.argument('angle', type=int)
@click.option('--baudrate', '-b', default=115200, help='波特率')
def move(port, angle, baudrate):
    """移动舵机到指定角度"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.move_angle(angle):
        click.echo(click.style(f"已移动到 {angle}°", fg='green'))
    else:
        click.echo(click.style(f"移动失败: {controller.current_status.error}", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def open_gripper(port, baudrate):
    """打开爪"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.open_gripper():
        click.echo(click.style("爪已打开", fg='green'))
    else:
        click.echo(click.style("操作失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def close_gripper(port, baudrate):
    """关闭爪"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.close_gripper():
        click.echo(click.style("爪已关闭", fg='green'))
    else:
        click.echo(click.style("操作失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def status(port, baudrate):
    """查看机械爪状态"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    status = controller.status()
    
    click.echo("\n=== 机械爪状态 ===")
    click.echo(f"  串口: {status.port}")
    click.echo(f"  波特率: {status.baudrate}")
    click.echo(f"  当前角度: {status.angle}°")
    click.echo(f"  爪状态: {'打开' if status.gripper_open else '关闭'}")
    click.echo(f"  连接: {click.style('已连接', fg='green')}")
    
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def full_open(port, baudrate):
    """完全打开爪"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.full_open():
        click.echo(click.style("爪已完全打开 (180°)", fg='green'))
    else:
        click.echo(click.style("操作失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def full_close(port, baudrate):
    """完全关闭爪"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.full_close():
        click.echo(click.style("爪已完全关闭 (0°)", fg='green'))
    else:
        click.echo(click.style("操作失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def grip(port, baudrate):
    """抓握位置 (45°)"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.grip():
        click.echo(click.style("已设置抓握位置 (45°)", fg='green'))
    else:
        click.echo(click.style("操作失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


@cli.command()
@click.argument('port')
@click.option('--baudrate', '-b', default=115200, help='波特率')
def reset(port, baudrate):
    """复位机械爪"""
    controller = ClawController(port, baudrate)
    
    if not controller.connect():
        click.echo(click.style(f"连接失败!", fg='red'))
        sys.exit(1)
        
    if controller.reset():
        click.echo(click.style("已复位 (90°)", fg='green'))
    else:
        click.echo(click.style("复位失败", fg='red'))
        sys.exit(1)
        
    controller.disconnect()


def main():
    """CLI 入口"""
    cli()


if __name__ == '__main__':
    main()
