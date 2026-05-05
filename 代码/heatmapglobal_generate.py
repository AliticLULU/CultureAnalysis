import plotly.graph_objects as go
import pandas as pd

# 定义地区和对应的得分数据
regions = ['简体(其他)', '繁体', '英文', '韩语', '日语', '越南语', '俄语', '西语', '法语']
scores = [337203.04, 291719.76, 572073.10, 365764.71, 520714.65, 354258.23, 617089.19, 496443.64, 418546.41]

# 为每个地区分配代表性国家的ISO代码
region_iso_mapping = {
    '简体(其他)': ['SGP', 'MYS'],  # 新加坡、马来西亚
    '繁体': ['TWN', 'HKG'],       # 台湾、香港
    '英文': ['USA', 'GBR','AUS','CAN'],       # 美国、英国、澳大利亚、加拿大
    '韩语': ['KOR'],              # 韩国
    '日语': ['JPN'],              # 日本
    '越南语': ['VNM'],            # 越南
    '俄语': ['RUS'],              # 俄罗斯
    '西语': ['ESP', 'MEX'],       # 西班牙、墨西哥
    '法语': ['FRA']               # 法国
}

# 创建数据框
data_list = []
for i, region in enumerate(regions):
    score = scores[i]
    countries = region_iso_mapping[region]
    for country in countries:
        data_list.append({'iso_alpha_3': country, 'score': score, 'region': region})

df = pd.DataFrame(data_list)

# 从浅红到深红的渐变
red_colors = [
    [0, '#ffe6e6'],      # 非常浅的粉红
    [0.15, '#ffcccc'],   # 很浅的红
    [0.3, '#ffb3b3'],    # 浅红
    [0.45, '#ff9999'],   # 柔和的红
    [0.6, '#ff8080'],    # 中等红
    [0.75, '#ff6666'],   # 深红
    [0.9, '#ff4d4d'],    # 深红色
    [1, '#cc0000']       # 深红宝石色
]

fig = go.Figure(data=go.Choropleth(
    locations=df['iso_alpha_3'],
    z=df['score'],
    locationmode='ISO-3',
    colorscale=red_colors,
    zmin=min(scores),
    zmax=max(scores),
    colorbar=dict(title="传播影响力得分", tickformat=".0f"),
    hovertemplate='<b>%{location}</b><br>' +
                  '语言区域: %{customdata}<br>' +
                  '得分: %{z:,.2f}<extra></extra>',
    customdata=[row['region'] for idx, row in df.iterrows()],
    name=''
))

# 更新布局，去除南极洲
fig.update_layout(
    title_text='全球各语言区域传播影响力热力图<br><sub>(浅红→深红，层次分明)</sub>',
    title_x=0.5,
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        projection_scale=1.2,  # 稍微放大地图
        center=dict(lat=15, lon=0),  # 将中心稍微向上移动
        lataxis_range=[-60, 80]  # 设置纬度范围，排除南极洲(-90到-60度)
    ),
    height=700,
    width=1200
)

fig.show()
fig.write_html("language_regions_heatmap_reds.html")

print("热力图已生成并保存为 language_regions_heatmap_reds.html")
print("\n各地区得分详情 (按得分排序):")
sorted_data = sorted(zip(regions, scores), key=lambda x: x[1], reverse=True)
for region, score in sorted_data:
    print(f"{region}: {score:,.2f}")