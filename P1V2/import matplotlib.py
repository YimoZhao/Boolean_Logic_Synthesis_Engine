import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_simple_and_gate():
    fig, ax = plt.subplots()

    # 绘制AND门
    rect = patches.Rectangle((0.2, 0.2), 0.6, 0.6, linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(rect)

    # 绘制圆圈，表示AND门的特有形状
    circle = patches.Circle((0.8, 0.5), 0.1, linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(circle)

    # 添加输入输出标签
    ax.text(0.1, 0.7, 'A', fontsize=12, ha='center', va='center')
    ax.text(0.1, 0.3, 'B', fontsize=12, ha='center', va='center')
    ax.text(0.95, 0.5, 'Q', fontsize=12, ha='center', va='center')

    # 设置坐标轴的范围和隐藏坐标轴
    ax.set_xlim(0, 1.2)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 显示图形
    plt.show()

draw_simple_and_gate()
