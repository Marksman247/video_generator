# Built by MAX — Pro V6 Clean Fixed Data Race Video Generator
# Secure, reviewed, no extra left space, centered title and subtitle properly placed

# ===== Imports =====
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np
import io
import os

# ===== Global Style =====
plt.rcParams.update({
    'axes.facecolor': 'black',
    'figure.facecolor': 'black',
    'axes.edgecolor': 'black',
    'axes.grid': False
})

# ===== Streamlit Config =====
st.set_page_config(
    page_title="Data Race Video Generator by MAX",
    layout="wide",
    page_icon="📊"
)

# ===== Title & Info =====
st.markdown("<h1 style='text-align: center; color: white;'>📊 Data Race Video Generator</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Built by MAX</h4>", unsafe_allow_html=True)
st.markdown("---")

# ===== Frame Generator =====
def generate_frames(df_pivot, top_n, font_size, resolution, video_title, subtitle, color_palette):
    frames = []
    years = df_pivot.index.tolist()
    dpi, figsize = (128, (16, 9)) if resolution == "720p" else (192, (19.2, 10.8))

    cmap = plt.get_cmap(color_palette)
    colors = cmap.colors if hasattr(cmap, 'colors') else [cmap(i) for i in np.linspace(0, 1, 20)]
    item_colors = {name: colors[i % len(colors)] for i, name in enumerate(df_pivot.columns)}

    for idx, year in enumerate(years):
        data = df_pivot.loc[year].sort_values(ascending=False).head(top_n)
        max_value = data.max()

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        data.plot(kind='barh', ax=ax, color=[item_colors.get(i, 'skyblue') for i in data.index])

        for i, (value, name) in enumerate(zip(data.values, data.index)):
            ax.text(value * 0.98, i, f"{value:,.0f}", ha='right', va='center',
                    fontsize=font_size, color='white', fontweight='bold')

        # Centered video title above chart
        ax.text(max_value * 0.5, top_n + 0.3, f"{video_title}",
                fontsize=font_size + 10, color='white', ha='center', va='bottom', fontweight='bold')

        # Subtitle centered below chart
        ax.text(max_value * 0.5, -0.9, f"{subtitle}",
                fontsize=font_size, color='gray', ha='center', va='bottom')

        # Year label
        ax.text(max_value * 1.05, -0.5, f"{int(year)}",
                fontsize=font_size + 12, color='white', ha='right', va='center', fontweight='bold')

        # Clean axes styling
        ax.set_xlim(0, max_value * 1.12)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])
        ax.set_yticklabels(data.index, fontsize=font_size, color='white')
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(False)

        # Adjust margins: minimal left space, enough top/bottom for labels
        plt.subplots_adjust(left=0.18, top=0.88, bottom=0.13)

        # Save frame to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi, facecolor=fig.get_facecolor())
        buf.seek(0)
        frames.append(buf)
        plt.close()

    return frames

# ===== Save Video =====
def save_video(frames, output_path, fps):
    image_arrays = [np.array(Image.open(f)) for f in frames]
    final_clip = ImageSequenceClip(image_arrays, fps=fps)
    final_clip.write_videofile(output_path, codec="libx264")

# ===== Video Generator from CSV =====
def generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps,
                   video_title, subtitle, color_palette, n_frames_per_year):
    try:
        csv_file.seek(0)
        df = pd.read_csv(csv_file, skip_blank_lines=True)
        if df.empty or df.shape[1] < 2:
            st.error("❌ CSV appears empty or has no columns.")
            return None

        df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[year_col, value_col], inplace=True)

        df_pivot = df.pivot(index=year_col, columns=name_col, values=value_col).fillna(0)
        if df_pivot.empty:
            st.error("❌ CSV contains no usable data.")
            return None

        years = df_pivot.index.tolist()
        new_years = []
        for i in range(len(years) - 1):
            start_year, end_year = years[i], years[i + 1]
            step = (end_year - start_year) / n_frames_per_year
            for j in range(n_frames_per_year):
                new_years.append(start_year + j * step)
        new_years.append(years[-1])

        df_pivot_interp = df_pivot.reindex(df_pivot.index.union(new_years))
        df_pivot_interp = df_pivot_interp.interpolate(method='linear').sort_index()

        st.write(f"📊 Total frames: {len(df_pivot_interp.index)}")

        frames = generate_frames(df_pivot_interp, top_n, font_size, resolution, video_title, subtitle, color_palette)
        video_path = 'output_video.mp4'
        save_video(frames, video_path, fps)

        return video_path

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# ===== Sidebar Config =====
with st.sidebar:
    st.header("⚙️ Config")
    csv_file = st.file_uploader("📁 Upload CSV", type=["csv"])

    if csv_file:
        df = pd.read_csv(csv_file, skip_blank_lines=True)
        columns = df.columns.tolist()
        year_col = st.selectbox("📅 Year Column", columns)
        name_col = st.selectbox("🏷️ Name Column", columns)
        value_col = st.selectbox("💲 Value Column", columns)

        top_n = st.slider("🔢 Bars", 2, 20, 5)
        font_size = st.slider("🔠 Font Size", 12, 36, 16)
        fps = st.slider("🎞️ FPS", 1, 30, 5)
        n_frames_per_year = st.slider("🕰️ Frames Per Year", 5, 50, 10)
        resolution = st.radio("🖥️ Resolution", ["720p", "1080p"], index=0)
        video_title = st.text_input("🎬 Title", "Data Race Video by MAX")
        subtitle = st.text_input("📝 Subtitle", "Generated via Streamlit")
        color_palette = st.selectbox("🎨 Palette", ['tab20', 'Set3', 'plasma', 'inferno', 'magma', 'cividis'], index=0)

        generate = st.button("🎥 Generate Video")

# ===== Run Generation =====
if csv_file and generate:
    st.info("🚀 Generating video...")
    video_path = generate_video(csv_file, year_col, name_col, value_col, top_n, font_size, resolution, fps,
                                video_title, subtitle, color_palette, n_frames_per_year)

    if video_path and os.path.exists(video_path):
        st.success("✅ Video ready!")
        st.video(video_path)
    else:
        st.error("❌ Failed to generate video.")
