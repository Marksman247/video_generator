📊 Pro V4 Data Race Video Generator by MAX
A professional-grade Python + Streamlit app for creating beautiful, interpolated MP4 Data Race Bar Chart Videos from CSV datasets.
Customize titles, subtitles, frame rates, fonts, resolution, and number of bars — with automatic color palettes and smooth animations.

📦 Features
✅ Upload any properly formatted CSV file
✅ Choose Year, Item Name, and Value columns
✅ Customize:

Number of bars to display

Font size

Frames per second

Video resolution (720p or 1080p)

Video title and subtitle

✅ Clean, modern visuals with consistent color palettes
✅ Interpolates smooth intermediate frames between years
✅ Outputs high-quality MP4 video
✅ Securely handles data parsing and errors
✅ Built with Streamlit, Matplotlib, MoviePy, Pandas, and PIL

📁 Sample CSV Format
Year	Item Name	Value
2000	Toyota	90000
2000	Honda	87000
2001	Toyota	93000
2001	Honda	91000

Notes:

No duplicate headers.

No missing year, value, or name entries.

Save as .csv (comma-separated) — UTF-8 encoding.

🚀 How to Run
1️⃣ Install required packages:

bash
Copy
Edit
pip install streamlit pandas matplotlib moviepy pillow numpy
2️⃣ Run the Streamlit app:

bash
Copy
Edit
streamlit run video_generator_pro_v4.py
📽️ Output Example
MP4 video generated in your project directory as output_video.mp4

Smooth, clean animated race bar chart

Titles, subtitles, year labels, and interpolated frames

📌 Project Structure
video_generator/
├── __pycache__/
├── flagged/
├── venv/
├── app.py
├── video_generator_pro.py
├── video_generator_pro_v2.py
├── video_generator_pro_v3.py
├── video_generator_pro_v4.py
├── README.md
├── requirements.txt
├── matplotlibrc.txt  (if needed)
└── sample_dataset.csv

🛡️ Built and secured by MAX
Custom-crafted with care and stability in mind.