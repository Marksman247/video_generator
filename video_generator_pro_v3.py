# Built by MAX — Pro V3 MP4 Data Race Video Generator (Secure & Reviewed)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from PIL import Image
import numpy as np
import io
import os

# Matplotlib styling config
plt.rcParams.update({
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'axes.edgecolor': 'white',
    'axes.grid': False
})

st.title("📊 Pro V3 Data Race Video Generator by MAX")

# Function to generate chart frames for the video
def generate_frames(df_pivot, top_n, font_size, resolution, video_title, subtitle):
    frames = []
    years = df_pivot.index.tolist()
    dpi, figsize = (128, (16, 9)) if resolution == "720p" else (192, (19.2, 10.8))

    # Assign colors to items consistently
    colors = plt.cm.tab20.colors
    item_colors = {name: colors[i % len(colors)] for i, name in enumerate(df_pivot.columns)}

    for year in years:
        data = df_pivot.loc[year].sort_values(ascending=False).head(top_n)
        max_value = data.max()

        fig, ax = plt.subplots(figsize=figsize)

        # Horizontal bar chart
        data.plot(kind='barh', ax=ax, color=[item_colors.get(i, 'skyblue') for i in data.index])

        # Value labels on bars
        for i, (value, name) in enumerate(zip(data.values, data.index)):
            ax.text(value * 0.98, i, f"{value:,.0f}", ha='right', va='center',
                    fontsize=font_size-2, color='white')

        # Title and subtitle
        ax.set_title(f"{video_title}", fontsize=font_size+10, weight='bold')
        ax.text(0, top_n + 0.5, f"{subtitle}", fontsize=font_size, color='gray', ha='left')

        # Year label (no decimals)
        ax.text(max_value * 0.95, top_n - 0.5, f"{int(year)}", fontsize=font_size+10,
                color='gray', ha='right')

        # Chart styling
        ax.set_xlim(0, max_value * 1.05)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_yticklabels(data.index, fontsize=font_size)
        ax.set_xticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        plt.tight_layout()

        # Save frame to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi)
        buf.seek(0)
        frames.append(buf)
        plt.close()

    return frames

# Function to save frames into a video file
def save_video(frames, output_path, fps):
    image_arrays = []
    for f in frames:
        img = Image.open(f)
        img_array = np.array(img)
        image_arrays.append(img_array)

    final_clip = ImageSequenceClip(image_arrays, fps=fps)
    final_clip.write_videofile(output_path, codec="libx264")

# Core video generation logic
def generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps, video_title, subtitle):
    try:
        csv_file.seek(0)  # ⬅️ Key fix: reset file cursor
        df = pd.read_csv(csv_file)

        # Ensure numeric columns
        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[year_col, value_col], inplace=True)

        df_pivot = df.pivot(index=year_col, columns=name_col, values=value_col).fillna(0)

        if df_pivot.empty:
            st.error("CSV contains no usable data.")
            return None

        # Interpolation: insert in-between years for smoothness
        n_frames_per_year = 10
        years = df_pivot.index.tolist()
        new_years = []
        for i in range(len(years) - 1):
            start_year, end_year = years[i], years[i+1]
            step = (end_year - start_year) / n_frames_per_year
            for j in range(n_frames_per_year):
                new_years.append(start_year + j * step)
        new_years.append(years[-1])

        df_pivot_interp = df_pivot.reindex(df_pivot.index.union(new_years))
        df_pivot_interp = df_pivot_interp.interpolate(method='linear').sort_index()

        st.write(f"📊 Total frames after interpolation: {len(df_pivot_interp.index)}")

        frames = generate_frames(df_pivot_interp, top_n, font_size, resolution, video_title, subtitle)
        video_path = 'output_video.mp4'
        save_video(frames, video_path, fps)

        return video_path

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Streamlit frontend: controls and inputs
csv_file = st.file_uploader("📁 Upload CSV Dataset", type=["csv"])

if csv_file:
    st.success("✅ CSV uploaded successfully!")

    csv_file.seek(0)  # ⬅️ Reset before reading again
    df = pd.read_csv(csv_file)
    columns = df.columns.tolist()

    # Select columns
    year_col = st.selectbox("📅 Select Year Column", columns)
    name_col = st.selectbox("🏷️ Select Item Name Column", columns)
    value_col = st.selectbox("💲 Select Value Column", columns)

    # User customization controls
    top_n = st.slider("🔢 Number of Bars to Display", 2, 20, 5)
    font_size = st.slider("🔠 Font Size", 12, 36, 16)
    fps = st.slider("🎞️ Frames Per Second", 1, 30, 5)
    resolution = st.radio("🖥️ Video Resolution", ["720p", "1080p"], index=0)
    video_title = st.text_input("🎬 Video Title", "Data Race Video by MAX")
    subtitle = st.text_input("📝 Video Subtitle", "Generated via Streamlit & Python")

    # Generate video on click
    if st.button("🎥 Generate MP4 Video"):
        st.info("🚀 Starting video generation...")
        video_path = generate_video(csv_file, year_col, name_col, value_col,
                                    top_n, font_size, resolution, fps,
                                    video_title, subtitle)

        if video_path and os.path.exists(video_path):
            st.success("✅ MP4 Video generated successfully!")
            st.video(video_path)
        else:
            st.error("❌ Failed to generate video.")
else:
    st.info("📁 Please upload a CSV file to begin.")

