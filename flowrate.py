import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob
from statsmodels.tsa.arima.model import ARIMA

# 📌 1. 设置 Matplotlib 英文字体
plt.rcParams["font.sans-serif"] = ["Arial"]
plt.rcParams["axes.unicode_minus"] = False

# 📌 2. 读取并合并文件夹内的所有数据文件
data_folder = "data_visitors_flowrate"  # 🚨 请替换为你的文件夹路径
file_paths = glob(os.path.join(data_folder, "*.csv"))  # 获取所有 CSV 文件

dfs = []

for file_path in file_paths:
    try:
        df = pd.read_csv(file_path, encoding="GB18030")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="GBK")  # 备用编码
    dfs.append(df)

# 合并所有数据
df = pd.concat(dfs, ignore_index=True)

# 统一列名
df.columns = ["id", "location", "visitors", "comfort_level", "datetime"]

# 📌 3. 处理时间格式
def fix_datetime_format(x):
    if len(x) == 10:  # 例如 "2018/7/31"
        return x + " 00:00"
    return x

df["datetime"] = df["datetime"].astype(str).apply(fix_datetime_format)
df["datetime"] = pd.to_datetime(df["datetime"], format="%Y/%m/%d %H:%M", errors="coerce")

# 过滤掉无法解析的时间
df = df.dropna(subset=["datetime"])

# 设置时间索引
df = df.set_index("datetime")

# 📌 4. 按景点分组预测
unique_spots = df["location"].unique()

# 创建存储结果的文件夹
output_dir = "visitors_flowrate_pred_arima"
csv_output_dir = os.path.join(output_dir, "csv_predictions")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(csv_output_dir, exist_ok=True)

for spot_name in unique_spots:
    df_spot = df[df["location"] == spot_name].copy()

    if len(df_spot) < 200:  # 数据太少的景点跳过
        print(f"⚠️ {spot_name} has insufficient data, skipping prediction.")
        continue

    print(f"📊 Predicting visitor flow for {spot_name} using ARIMA...")

    # 📌 5. 训练 ARIMA 模型
    try:
        model = ARIMA(df_spot["visitors"], order=(5,1,0))  # (p,d,q) 设为 (5,1,0)
        arima_result = model.fit()
    except Exception as e:
        print(f"❌ ARIMA model training failed for {spot_name}: {e}")
        continue

    # 📌 6. 生成未来 7 天的小时级数据
    future_hours = 24 * 7  # 未来 7 天
    future_dates = pd.date_range(start=df_spot.index[-1], periods=future_hours+1, freq="H")[1:]

    predicted_visitors = arima_result.forecast(steps=future_hours)
    future_df = pd.DataFrame({
        "datetime": future_dates,
        "predicted_visitors": np.maximum(predicted_visitors, 0)  # 预测值不能小于0
    })

    # 📌 7. 保存预测数据到 CSV
    csv_file_path = os.path.join(csv_output_dir, f"{spot_name}_arima_prediction.csv")
    future_df.to_csv(csv_file_path, encoding="utf-8-sig", index=False)
    print(f"📄 Prediction data for {spot_name} has been saved to CSV: {csv_file_path}")

    # 📌 8. 可视化
    plt.figure(figsize=(12, 5))
    plt.plot(df_spot.index, df_spot["visitors"], label="Historical Visitor Flow", linestyle="--", color="gray")
    plt.plot(future_df["datetime"], future_df["predicted_visitors"], label="Predicted Visitor Flow", color="blue")

    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Visitor Flow", fontsize=12)
    plt.title(f"{spot_name} - ARIMA Visitor Flow Prediction for Next 7 Days", fontsize=14)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # 📌 9. 保存图像
    plt.savefig(f"{output_dir}/{spot_name}_arima_prediction.png", dpi=300)
    plt.close()

    print(f"✅ {spot_name} prediction completed, chart saved!")

print("🎯 All visitor flow predictions using ARIMA completed!")
