import roboticstoolbox as rtb
import numpy as np

robot = rtb.models.DH.Puma560()
q_zero = np.zeros(6)

print("正在打开浏览器 3D 可视化...")
print("如果浏览器没有自动打开，请手动访问 http://127.0.0.1:8080")
robot.teach(q_zero)