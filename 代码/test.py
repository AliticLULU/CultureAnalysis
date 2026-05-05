import matplotlib.pyplot as plt

# 设置全局字体为 SimHei (黑体) 或其他中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或 ['Microsoft YaHei'] 微软雅黑 等
plt.rcParams['axes.unicode_minus'] = False   # 解决负号 '-' 显示为方块的问题

# 示例代码
x = [1, 2, 3, 4, 5]
y = [2, 4, 1, 3, 5]

plt.plot(x, y)
plt.title('折线图示例 - 中文标题')
plt.xlabel('X 轴 - 横轴')
plt.ylabel('Y 轴 - 纵轴')
plt.legend(['数据系列 - 中文图例'])
plt.show()