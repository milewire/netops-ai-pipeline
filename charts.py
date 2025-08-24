import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd


def save_kpi_chart(df: pd.DataFrame, out_path: str):
    plt.figure(figsize=(12, 8))

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("KPI Anomaly Detection Results", fontsize=16)

    colors = ["red" if x == -1 else "blue" for x in df.get("anomaly", [1] * len(df))]

    axes[0, 0].scatter(df.index, df["PRB_Util"], c=colors, alpha=0.6)
    axes[0, 0].set_title("PRB Utilization (%)")
    axes[0, 0].set_ylabel("PRB_Util")

    axes[0, 1].scatter(df.index, df["RRC_Conn"], c=colors, alpha=0.6)
    axes[0, 1].set_title("RRC Connections")
    axes[0, 1].set_ylabel("RRC_Conn")

    axes[1, 0].scatter(df.index, df["Throughput_Mbps"], c=colors, alpha=0.6)
    axes[1, 0].set_title("Throughput (Mbps)")
    axes[1, 0].set_ylabel("Throughput_Mbps")
    axes[1, 0].set_xlabel("Sample Index")

    axes[1, 1].scatter(df.index, df["BLER"], c=colors, alpha=0.6)
    axes[1, 1].set_title("Block Error Rate")
    axes[1, 1].set_ylabel("BLER")
    axes[1, 1].set_xlabel("Sample Index")

    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="blue", label="Normal"),
        Patch(facecolor="red", label="Anomaly"),
    ]
    fig.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
