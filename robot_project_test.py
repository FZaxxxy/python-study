# -*- coding: utf-8 -*-
"""
第一阶段仿真：六关节机械臂协调动作演示 (纯 Python)
=====================================================
对应项目一第一阶段目标:
  - 六台大扭矩高功率舵机(6 个旋转关节)的多自由度协调运行
  - 完成初始指定动作: 抓取 -> 旋转 -> 放置
  - 双 PCA9685 级联的"角度 -> PWM"桥接(仅 Python 换算, 非 STM32 代码)

说明:
  本程序为纯 Python 仿真。其中 angle_to_pulse_ms() 等函数只负责把
  仿真算出的关节角换算成舵机脉宽, 便于日后移植到 STM32 HAL 驱动,
  并不包含任何 STM32 底层代码。

运行:
  venv\\Scripts\\python robot_project_test.py                          # 动作演示 + 3D 动画
  venv\\Scripts\\python robot_project_test.py --no-anim                # 仅打印控制指令(无 GUI)
  venv\\Scripts\\python robot_project_test.py --ik 0.4 0.1 0.3         # 给定位置反解关节角
  venv\\Scripts\\python robot_project_test.py --ik 0.4 0.1 0.3 0 90 0  # 给定位姿反解关节角
"""

import argparse
import sys

import numpy as np
import matplotlib.pyplot as plt
import roboticstoolbox as rtb
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3

# 兼容 Windows GBK 终端:避免 DH 表特殊字符打印报错
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ==================== 舵机 / PCA9685 参数(桥接实机) ====================
# 具体数值以实际舵机手册为准, 此处采用常见 180 度舵机模型
SERVO_MIN_MS = 0.5          # 0 度对应脉宽
SERVO_MAX_MS = 2.5          # 180 度对应脉宽
SERVO_MID_DEG = 90.0        # 关节 0 度对应舵机 90 度(中位)
SERVO_RANGE_DEG = 180.0     # 舵机行程
PCA9685_PERIOD_MS = 20.0    # PWM 周期(50Hz)
PCA9685_RESOLUTION = 4096   # 12 位分辨率

# 双 PCA9685 级联: 板 #1 驱动关节 1~3, 板 #2 驱动关节 4~6
BOARDS = {
    1: [1, 2, 3],
    2: [4, 5, 6],
}


# ==================== 1. 机械臂建模(对应 6 台舵机) ====================
def build_robot():
    """根据标准 DH 参数构建六关节机械臂。"""
    L = [
        #            d(m)      a(m)     alpha(rad)        关节限位
        RevoluteDH(0.333, 0.0,   -np.pi / 2, qlim=np.deg2rad([-170, 170])),  # 关节1 腰
        RevoluteDH(0.0,   0.316,  0.0,        qlim=np.deg2rad([-135, 135])),  # 关节2 肩
        RevoluteDH(0.0,   0.0,    np.pi / 2,  qlim=np.deg2rad([-170, 170])),  # 关节3 肘
        RevoluteDH(0.384, 0.0,   -np.pi / 2,  qlim=np.deg2rad([-190, 190])),  # 关节4 腕1
        RevoluteDH(0.0,   0.0,    np.pi / 2,  qlim=np.deg2rad([-120, 120])),  # 关节5 腕2
        RevoluteDH(0.107, 0.0,    0.0,        qlim=np.deg2rad([-360, 360])),  # 关节6 腕3
    ]
    robot = DHRobot(L, name="6DOF-Arm")
    robot.tool = SE3.Tx(0.05)  # 末端工具偏置
    return robot


# ==================== 2. 角度 -> PWM 桥接(纯 Python 换算) ====================
def angle_to_pulse_ms(theta_deg):
    """关节角(度) -> 舵机脉宽(ms)。

    舵机角度 = 中位 90 度 + 关节角, 线性映射到 0.5~2.5 ms。
    """
    servo_deg = SERVO_MID_DEG + theta_deg
    pulse = SERVO_MIN_MS + servo_deg / SERVO_RANGE_DEG * (SERVO_MAX_MS - SERVO_MIN_MS)
    return float(np.clip(pulse, SERVO_MIN_MS, SERVO_MAX_MS))


def angle_to_pca_count(theta_deg):
    """关节角(度) -> PCA9685 12 位计数值(0~4095)。"""
    return int(round(angle_to_pulse_ms(theta_deg) / PCA9685_PERIOD_MS * PCA9685_RESOLUTION))


# ==================== 3. 动作库(示教关节角, 单位: 度) ====================
# grip=True 表示"夹爪开合"动作: 关节不运动, 仅末端夹爪状态变化
ACTIONS = [
    dict(name="HOME",        q=[0,   0,   0,  0,  0,  0],  note="初始位姿"),
    dict(name="PICK_UP",     q=[30, -30,  40, 0, 30,  0],  note="移动到抓取点上方"),
    dict(name="PICK_DOWN",   q=[30, -45,  55, 0, 20,  0],  note="下降到抓取目标"),
    dict(name="GRASP",       q=[30, -45,  55, 0, 20,  0],  note="夹爪闭合(抓取)", grip=True),
    dict(name="LIFT",        q=[25, -25,  35, 0, 15,  0],  note="抓起后抬起"),
    dict(name="ROTATE",      q=[70, -25,  35, 0, 15, 60],  note="旋转(关节1转向+关节6腕转)"),
    dict(name="PLACE_UP",    q=[70, -30,  40, 0, 30, 60],  note="移动到放置点上方"),
    dict(name="PLACE_DOWN",  q=[70, -45,  55, 0, 20, 60],  note="下降到放置点"),
    dict(name="RELEASE",     q=[70, -45,  55, 0, 20, 60],  note="夹爪张开(放置)", grip=True),
    dict(name="PLACE_RETURN", q=[70, -30, 40, 0, 30, 60],  note="放置后抬起"),
    dict(name="HOME",        q=[0,   0,   0,  0,  0,  0],  note="回到初始位姿"),
]

# 每段轨迹插值步数
STEPS_PER_SEGMENT = 25


# ==================== 4. 打印 PWM 控制指令(按双板分组) ====================
def print_servo_command(robot, action):
    """打印一个动作对应的 6 路舵机 PWM 指令(模拟下发到双 PCA9685)。"""
    q_deg = np.array(action["q"])
    q_rad = np.deg2rad(q_deg)
    pos = robot.fkine(q_rad).t

    print(f"\n  ▶ [{action['name']}] {action['note']}")
    print(f"    末端位置: x={pos[0]:.3f}  y={pos[1]:.3f}  z={pos[2]:.3f} m")
    for board, joints in BOARDS.items():
        print(f"    PCA9685 #{board} 级联板:")
        for j in joints:
            idx = j - 1
            pulse = angle_to_pulse_ms(q_deg[idx])
            count = angle_to_pca_count(q_deg[idx])
            print(f"      关节{j}: {q_deg[idx]:>7.1f}°  ->  脉宽 {pulse:.3f} ms  "
                  f"(计数值 {count:4d})")
    if action.get("grip"):
        state = "闭合" if action["name"] == "GRASP" else "张开"
        print(f"    [末端夹爪] {state}")


# ==================== 5. 轨迹规划(多自由度协调运行) ====================
def plan_action_trajectory(robot, anim=True):
    """按动作库依次执行, 返回完整关节轨迹; 同时打印每步控制指令。"""
    print("\n" + "=" * 62)
    print("第一阶段仿真: 抓取 -> 旋转 -> 放置 协调动作演示")
    print("=" * 62)

    q_current = np.zeros(6)          # 当前关节角(弧度)
    traj_all = [q_current.copy()]    # 完整轨迹

    for action in ACTIONS:
        print_servo_command(robot, action)

        if action.get("grip"):
            # 夹爪开合动作: 关节不运动, 轨迹上重复当前点
            traj_all.append(q_current.copy())
            continue

        q_target = np.deg2rad(action["q"])
        seg = rtb.jtraj(q_current, q_target, STEPS_PER_SEGMENT)
        # 去掉首点(与上一段末点重复)
        traj_all.extend(seg.q[1:])
        q_current = q_target

    q_traj = np.array(traj_all)
    print("\n" + "-" * 62)
    print(f"完整轨迹共 {q_traj.shape[0]} 个路径点, "
          f"6 个关节(舵机)全程同步协调运动")
    return q_traj


# ==================== 6. 3D 动画 ====================
def animate(robot, q_traj):
    """matplotlib 3D 动画展示整个动作流程。"""
    print("正在播放 3D 动画 (关闭窗口后结束)...")
    robot.plot(q_traj, backend="pyplot", block=True, dt=0.04)
    plt.close("all")


# ==================== 7. 逆运动学: 给定末端位姿 -> 关节角 ====================
def solve_inverse_kinematics(robot, target):
    """给定末端位置/位姿, 反解 6 个关节角(逆运动学)。

    参数:
        target: 长度 3 的 [x, y, z](单位 m), 只约束位置;
                长度 6 的 [x, y, z, roll, pitch, yaw](位置 m, 姿态 度),
                约束完整位姿。
    返回:
        (q_deg, desc) 成功时返回关节角(度)与描述; 失败返回 (None, desc)。
    """
    if len(target) == 3:
        T_target = SE3(target[0], target[1], target[2])
        mask = [1, 1, 1, 0, 0, 0]  # 只约束位置, 不约束姿态
        desc = f"末端位置 ({target[0]:.3f}, {target[1]:.3f}, {target[2]:.3f}) m"
    elif len(target) == 6:
        T_target = SE3(target[0], target[1], target[2]) * SE3.RPY(
            np.deg2rad(target[3:]), order="zyx")
        mask = None  # 约束完整位姿
        desc = (f"末端位姿 pos=({target[0]:.3f}, {target[1]:.3f}, {target[2]:.3f}) m, "
                f"rpy=({target[3]:.1f}, {target[4]:.1f}, {target[5]:.1f}) deg")
    else:
        raise ValueError("target 必须是 3 个数(位置)或 6 个数(位置+姿态)")

    print(f"\n  目标: {desc}")
    sol = robot.ikine_LM(T_target, q0=np.zeros(6), joint_limits=True, mask=mask)
    if not sol.success:
        print("  ✗ 逆运动学求解失败:", sol.reason)
        return None, desc

    q_deg = np.rad2deg(sol.q)
    # 用正向运动学验证解算精度
    T_check = robot.fkine(sol.q)
    err_pos = np.linalg.norm(T_target.t - T_check.t)
    print(f"  ✓ 求解成功, 关节角(度): {np.round(q_deg, 2)}")
    print(f"  末端位置误差: {err_pos:.2e} m")
    return q_deg, desc


def demo_ik(robot, target, anim=True):
    """逆运动学演示: 解算目标关节角, 打印 PWM 指令, 并动画走到目标。"""
    q_deg, _ = solve_inverse_kinematics(robot, target)
    if q_deg is None:
        return

    print_servo_command(robot, dict(name="IK_TARGET", q=q_deg.tolist(),
                                    note="逆运动学解算出的目标关节角"))

    if anim:
        # 从零位平滑运动到目标关节角
        q_traj = rtb.jtraj(np.zeros(6), np.deg2rad(q_deg), 50).q
        animate(robot, q_traj)


# ==================== 主函数 ====================
def main():
    parser = argparse.ArgumentParser(description="第一阶段六关节机械臂协调动作仿真")
    parser.add_argument("--no-anim", dest="anim", action="store_false",
                        help="关闭 3D 动画, 仅打印控制指令")
    parser.add_argument("--ik", nargs="+", type=float, metavar="VAL",
                        help="逆运动学模式: 给定末端位置/位姿反解关节角。"
                             "3 个数 = x y z (m, 只解位置); "
                             "6 个数 = x y z roll pitch yaw (m, 度, 解完整位姿)")
    parser.set_defaults(anim=True)
    args = parser.parse_args()

    robot = build_robot()
    print(robot)

    if args.ik:
        # ---- 逆运动学模式 ----
        print("\n" + "=" * 62)
        print("逆运动学: 给定末端位姿 -> 求解关节角")
        print("=" * 62)
        demo_ik(robot, args.ik, anim=args.anim)
    else:
        # ---- 第一阶段动作演示模式 ----
        q_traj = plan_action_trajectory(robot)
        if args.anim:
            animate(robot, q_traj)

    print("\n仿真完成。")


if __name__ == "__main__":
    main()