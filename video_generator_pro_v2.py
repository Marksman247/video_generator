# Built by MAX — Pro V2 MP4 Data Race Video Generator (Clean, Secure & Reviewed)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from PIL import Image
import numpy as np
import io
import os

# 📊 Matplotlib Styling for clean, bright charts
plt.rcParams.update({
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'axes.edgecolor': 'white',
    'axes.grid': False
})

st.title("📊 Pro V2 Data Race Video Generator by MAX")

def generate_frames(df_pivot, top_n, font_size, resolution):
    """Generate chart frames for each time step"""
    frames = []
    years = df_pivot.index.tolist()
    dpi, figsize = (128, (16, 9)) if resolution == "720p" else (192, (19.2, 10.8))

    # Assign consistent colors to each item
    colors = plt.cm.tab20.colors
    item_colors = {name: colors[i % len(colors)] for i, name in enumerate(df_pivot.columns)}

    for year in years:
        data = df_pivot.loc[year].sort_values(ascending=False).head(top_n)
        max_value = data.max()

        fig, ax = plt.subplots(figsize=figsize)

        # Plot horizontal bars with assigned colors
        data.plot(kind='barh', ax=ax, color=[item_colors.get(i, 'skyblue') for i in data.index])

        # Value labels on bars
        for i, (value, name) in enumerate(zip(data.values, data.index)):
            ax.text(value * 0.98, i, f"{value:,.0f}",
                    ha='right', va='center', fontsize=font_size-2, color='white', fontweight='bold')

        # Year label inside chart
        ax.text(max_value * 0.95, top_n - 0.5, f"{year:.1f}",
                fontsize=font_size+8, color='gray', ha='right', va='center')

        ax.set_xlim(0, max_value * 1.05)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_yticklabels(data.index, fontsize=font_size)
        ax.set_xticks([])

        # Clean up chart spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()

        # Save chart as image in memory
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi)
        buf.seek(0)
        frames.append(buf)
        plt.close()

    return frames

def save_video(frames, output_path, fps):
    """Assemble image frames into MP4 video"""
    image_arrays = [np.array(Image.open(f)) for f in frames]
    final_clip = ImageSequenceClip(image_arrays, fps=fps)
    final_clip.write_videofile(output_path, codec="libx264")

def generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps):
    """Main video generation logic: data loading, interpolation, frame creation, video assembly"""
    try:
        # Reset file pointer before reading (important for file uploader)
        csv_file.seek(0)
        df = pd.read_csv(csv_file)

        # Validate required columns exist
        for col in [year_col, name_col, value_col]:
            if col not in df.columns:
                st.error(f"Missing column: {col} in uploaded file.")
                return None

        # Convert year and value to numeric, drop invalid rows
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[year_col, value_col], inplace=True)

        if df.empty:
            st.error("CSV has no valid data after cleaning.")
            return None

        # Pivot table: rows = Year, columns = Item Name, values = Value
        df_pivot = df.pivot(index=year_col, columns=name_col, values=value_col).fillna(0)

        if df_pivot.empty:
            st.error("CSV contains no usable data for plotting.")
            return None

        # Interpolation for smoother animation between years
        n_frames_per_year = 10
        years = df_pivot.index.tolist()
        new_years = []

        for i in range(len(years) - 1):
            start_year, end_year = years[i], years[i + 1]
            step = (end_year - start_year) / n_frames_per_year
            new_years.extend([start_year + j * step for j in range(n_frames_per_year)])

        new_years.append(years[-1])  # Include final year

        # Interpolate missing values for new years
        df_pivot_interp = df_pivot.reindex(df_pivot.index.union(new_years))
        df_pivot_interp = df_pivot_interp.interpolate(method='linear').sort_index()

        st.write(f"📊 Total frames after interpolation: {len(df_pivot_interp.index)}")

        # Generate chart images
        frames = generate_frames(df_pivot_interp, top_n, font_size, resolution)

        # Save video
        video_path = 'output_video.mp4'
        save_video(frames, video_path, fps)

        return video_path

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# 🖥️ Streamlit UI Controls
csv_file = st.file_uploader("📁 Upload CSV Dataset", type=["csv"])

if csv_file:
    st.success("✅ CSV uploaded successfully!")
    csv_file.seek(0)  # Reset again for UI preview
    df_preview = pd.read_csv(csv_file)
    st.dataframe(df_preview.head())

    columns = df_preview.columns.tolist()

    year_col = st.selectbox("📅 Select Year Column", columns)
    name_col = st.selectbox("🏷️ Select Item Name Column", columns)
    value_col = st.selectbox("💲 Select Value Column", columns)

    top_n = st.slider("🔢 Number of Bars to Display", 2, 20, 5)
    font_size = st.slider("🔠 Font Size", 12, 36, 16)
    fps = st.slider("🎞️ Frames Per Second", 1, 30, 5)
    resolution = st.radio("🖥️ Video Resolution", ["720p", "1080p"], index=0)

    if st.button("🎥 Generate MP4 Video"):
        st.info("🚀 Starting video generation...")
        video_path = generate_video(csv_file, year_col, name_col, value_col,
                                    top_n, font_size, resolution, fps)

        if video_path and os.path.exists(video_path):
            st.success("✅ MP4 Video generated successfully!")
            st.video(video_path)
        else:
            st.error("❌ Failed to generate video.")
else:
    st.info("📁 Please upload a CSV file to begin.")
