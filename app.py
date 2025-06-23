# Built by MAX — Smart MP4 Race Video Generator with Interpolation (Pro Stable Version)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from PIL import Image
import numpy as np
import io
import os

st.title("📊 Custom Data Race Video Generator by MAX")

def deduplicate_columns(columns):
    seen = {}
    result = []
    for col in columns:
        if col not in seen:
            seen[col] = 0
            result.append(col)
        else:
            seen[col] += 1
            new_col = f"{col}.{seen[col]}"
            result.append(new_col)
    return result

def generate_frames(df_pivot, top_n, font_size, resolution):
    frames = []
    years = df_pivot.index.tolist()
    dpi, figsize = (128, (16, 9)) if resolution == "720p" else (192, (19.2, 10.8))

    for year in years:
        data = df_pivot.loc[year].sort_values(ascending=False).head(top_n)

        fig, ax = plt.subplots(figsize=figsize)
        data.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_title(f"Top {top_n} - {year:.2f}", fontsize=font_size+4)
        ax.set_xlabel('Value', fontsize=font_size)
        ax.set_ylabel('Item', fontsize=font_size)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi)
        buf.seek(0)
        frames.append(buf)
        plt.close()

    return frames

def save_video(frames, output_path, fps):
    image_arrays = []
    for f in frames:
        img = Image.open(f)
        img_array = np.array(img)
        image_arrays.append(img_array)

    final_clip = ImageSequenceClip(image_arrays, fps=fps)
    final_clip.write_videofile(output_path, codec="libx264")

def generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps):
    try:
        csv_file.seek(0)
        df = pd.read_csv(csv_file)

        # Deduplicate columns
        df.columns = deduplicate_columns(df.columns)

        if year_col not in df.columns or name_col not in df.columns or value_col not in df.columns:
            st.error("❌ Selected columns do not exist in the uploaded CSV.")
            return None

        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[year_col, value_col], inplace=True)

        df_pivot = df.pivot(index=year_col, columns=name_col, values=value_col).fillna(0)

        if df_pivot.empty:
            st.error("CSV contains no usable data.")
            return None

        n_frames_per_year = 10
        years = df_pivot.index.tolist()
        new_years = []

        for i in range(len(years) - 1):
            start_year = years[i]
            end_year = years[i + 1]
            step = (end_year - start_year) / n_frames_per_year
            for j in range(n_frames_per_year):
                new_years.append(start_year + j * step)
        new_years.append(years[-1])

        df_pivot_interp = df_pivot.reindex(df_pivot.index.union(new_years))
        df_pivot_interp = df_pivot_interp.interpolate(method='linear').sort_index()

        st.write(f"📊 Total frames after interpolation: {len(df_pivot_interp.index)}")

        frames = generate_frames(df_pivot_interp, top_n, font_size, resolution)
        video_path = 'output_video.mp4'
        save_video(frames, video_path, fps)

        return video_path

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# UI Inputs
csv_file = st.file_uploader("📁 Upload CSV Dataset", type=["csv"])

if csv_file:
    st.success("✅ CSV uploaded successfully!")

    csv_file.seek(0)
    df = pd.read_csv(csv_file)
    df.columns = deduplicate_columns(df.columns)
    columns = df.columns.tolist()

    year_col = st.selectbox("📅 Select Year Column", columns)
    name_col = st.selectbox("🏷️ Select Item Name Column", columns)
    value_col = st.selectbox("💲 Select Value Column", columns)

    top_n = st.slider("🔢 Number of Bars to Display", 2, 20, 5)
    font_size = st.slider("🔠 Font Size", 12, 36, 16)
    fps = st.slider("🎞️ Frames Per Second", 1, 30, 5)
    resolution = st.radio("🖥️ Video Resolution", ["720p", "1080p"], index=0)

    if st.button("🎥 Generate MP4 Video"):
        st.info("🚀 Starting video generation...")
        video_path = generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps)

        if video_path and os.path.exists(video_path):
            st.success("✅ MP4 Video generated successfully!")
            st.video(video_path)
        else:
            st.error("❌ Failed to generate video.")
else:
    st.info("📁 Please upload a CSV file to begin.")
