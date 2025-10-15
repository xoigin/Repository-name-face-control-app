import streamlit as st
from PIL import Image, ImageEnhance
import random, time, io

st.set_page_config(page_title="動態人臉控制展示", layout="wide", page_icon="🧠")

# --- CSS to size main display 80% and controls 20% ---
st.markdown(
    """
    <style>
    .main > div.block-container{padding-top:1rem;}
    .stApp { background-color: #0f0f0f; color: white; }
    .display-area { height: 80vh; display:flex; align-items:center; justify-content:center; background:#000; }
    .controls-area { height: 20vh; display:flex; align-items:center; justify-content:center; gap:18px; background:#111; }
    .control-btn { width:104px; height:72px; border-radius:10px; font-size:20px; }
    </style>
    """, unsafe_allow_html=True
)

st.title("🧠 動態人臉控制展示")

# Upload area (limit 6)
uploaded = st.file_uploader("上傳最多6張同一人的正面照片（jpg/png）", type=['jpg','jpeg','png'], accept_multiple_files=True)
if 'images' not in st.session_state:
    st.session_state['images'] = []
if uploaded:
    files = uploaded[:6]
    st.session_state['images'] = []
    for f in files:
        try:
            img = Image.open(f).convert("RGB")
            st.session_state['images'].append(img)
        except Exception as e:
            st.warning(f"載入失敗: {f.name}")

if len(st.session_state['images'])==0:
    st.info("尚未上傳照片，請上方上傳至少一張照片以開始。")
    # show placeholder big box
    st.markdown('<div class="display-area"><h2 style="color:#888">等待上傳的照片...</h2></div>', unsafe_allow_html=True)
else:
    # Layout: display area (80%) then controls (20%)
    cols = st.columns([1])
    with cols[0]:
        st.markdown('<div class="display-area">', unsafe_allow_html=True)
        # Display the current image (use index 0 by default)
        index = st.session_state.get('current_index', 0)
        img = st.session_state['images'][index]
        # Show as large in center
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        st.image(buf.getvalue(), use_column_width=False, output_format='JPEG', clamp=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Controls area
    st.markdown('<div class="controls-area">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("1", key="btn1", help="向左（45°）", on_click=None):
            # Simulate left turn by using flip + mild transform via resize crop
            img = st.session_state['images'][0]
            turned = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(0, expand=False)
            st.session_state['last_display'] = turned
            st.experimental_rerun()
    with c2:
        if st.button("2", key="btn2", help="正面自然律動(眨眼)", on_click=None):
            # Show a simple blink simulation: darken a horizontal strip briefly
            base = st.session_state['images'][0].copy()
            w,h = base.size
            # create 'blink' frames (3 frames)
            frames = []
            for i in range(3):
                f = base.copy()
                if i==1:
                    # draw a dark band over eyes
                    band_h = int(h*0.12)
                    from PIL import ImageDraw
                    d = ImageDraw.Draw(f)
                    y = int(h*0.35)
                    d.rectangle([0,y, w, y+band_h], fill=(10,10,10))
                frames.append(f)
            # display frames sequentially
            for fr in frames:
                buf = io.BytesIO(); fr.save(buf, format='JPEG')
                st.image(buf.getvalue(), use_column_width=False)
                time.sleep(random.uniform(0.4,1.0))
            st.experimental_rerun()
    with c3:
        if st.button("3", key="btn3", help="微笑 (不露齒)", on_click=None):
            # Simulate smile by slightly increasing brightness and contrast
            base = st.session_state['images'][0].copy()
            enhancer = ImageEnhance.Brightness(base)
            b = enhancer.enhance(1.08)
            enhancer2 = ImageEnhance.Contrast(b)
            cimg = enhancer2.enhance(1.06)
            buf = io.BytesIO(); cimg.save(buf, format='JPEG')
            st.image(buf.getvalue(), use_column_width=False)
            st.experimental_rerun()
    with c4:
        if st.button("4", key="btn4", help="向右（45°）", on_click=None):
            img = st.session_state['images'][0]
            # rotate slightly to simulate turn
            turned = img.rotate(-10, resample=Image.BICUBIC, expand=False)
            buf = io.BytesIO(); turned.save(buf, format='JPEG')
            st.image(buf.getvalue(), use_column_width=False)
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Footer: small gallery + reset
st.markdown("---")
cols = st.columns([1,1,1,1,1,1])
for i in range(6):
    with cols[i%6]:
        if i < len(st.session_state['images']):
            img = st.session_state['images'][i]
            buf = io.BytesIO(); img.thumbnail((120,120)); img.save(buf, format='JPEG')
            if st.button(f"選擇{i}", key=f"sel{i}"):
                st.session_state['current_index'] = i
                st.experimental_rerun()
            st.image(buf.getvalue())
        else:
            st.write("")

if st.button("重置上傳"):
    st.session_state.clear()
    st.experimental_rerun()
