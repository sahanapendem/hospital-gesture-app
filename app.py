import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import cv2
import mediapipe as mp
import av
import queue

# --- INITIALIZE SESSION STATE VARIABLES ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "show_help" not in st.session_state:
    st.session_state.show_help = False

# --- APP CONFIGURATION ---
st.set_page_config(page_title="SGEC System", page_icon="🏥", layout="wide")

# --- CENTRALIZED STYLING ARCHITECTURE ---
st.markdown("""
    <style>
    /* Reset layout framework wrapper containers */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Immersive space environment theme background */
    .stApp {
        background: radial-gradient(circle at center, #0c081d 0%, #040209 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #ffffff;
    }
    
    /* Minimal landing hero matrix card panel */
    .neon-hero-card {
        background-color: rgba(13, 8, 28, 0.85);
        border: 2px solid rgba(161, 36, 245, 0.4);
        border-radius: 24px;
        box-shadow: 0 0 50px rgba(161, 36, 245, 0.3);
        padding: 40px;
        width: 100%;
        box-sizing: border-box;
    }
    
    .card-flex-layout {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 40px;
        width: 100%;
    }
    
    .card-text-panel { flex: 1.3; text-align: left; }
    .card-graphic-panel { flex: 0.7; display: flex; justify-content: center; align-items: center; }

    /* Glowing hand vector asset wrapper */
    .hologram-hand-wrapper {
        width: 200px;
        height: 280px;
        border: 1px dashed rgba(0, 242, 254, 0.4);
        border-radius: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle, rgba(161, 36, 245, 0.15) 0%, transparent 75%);
        box-shadow: inset 0 0 30px rgba(0, 242, 254, 0.1);
    }

    .hand-vector-icon {
        font-size: 7.5rem;
        filter: drop-shadow(0 0 20px #a124f5) drop-shadow(0 0 40px #00f2fe);
    }
    
    /* Typography style rulesets */
    .main-project-title {
        font-size: 4.2rem;
        font-weight: 900;
        margin: 0 0 5px 0;
        letter-spacing: 4px;
        text-shadow: 0 0 30px rgba(161, 36, 245, 0.7);
    }
    
    .main-project-subtitle {
        color: #ca92ff;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(161, 36, 245, 0.2);
        padding-bottom: 10px;
    }
    
    .main-project-description { font-size: 1rem; line-height: 1.7; color: #94a3b8; }
    .highlight-text { color: #ffffff; font-weight: 600; }
    
    /* Main Centered Navigation Action Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #7c3aed 0%, #a124f5 100%) !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px;
        padding: 14px 50px !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 0 30px rgba(161, 36, 245, 0.5) !important;
        width: auto !important;
        display: block;
        margin: 0 auto !important; 
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 45px rgba(161, 36, 245, 0.8) !important;
    }
    
    /* Utility Action Navigation Triggers inside Active Hub */
    .back-btn-container div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(161, 36, 245, 0.3) !important;
        font-size: 0.85rem !important;
        padding: 8px 20px !important;
        color: #ca92ff !important;
        border-radius: 6px !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    
    .help-btn-container div.stButton > button {
        background: rgba(161, 36, 245, 0.12) !important;
        border: 1px solid rgba(161, 36, 245, 0.5) !important;
        font-size: 0.85rem !important;
        padding: 8px 22px !important;
        color: #e2cbff !important;
        border-radius: 6px !important;
        box-shadow: 0 0 15px rgba(161, 36, 245, 0.2) !important;
        margin: 0 0 0 auto !important;
    }
    .help-btn-container div.stButton > button:hover {
        background: rgba(161, 36, 245, 0.3) !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(161, 36, 245, 0.6) !important;
    }

    /* SOLID EMBEDDED MODAL CONTENT BOX SYSTEM */
    .embedded-modal-card {
        background: #0d0724;
        border: 2px solid #a124f5;
        box-shadow: 0 0 45px rgba(161, 36, 245, 0.4);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    .close-guide-btn-container div.stButton > button {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #f87171 !important;
        font-size: 0.9rem !important;
        padding: 10px 30px !important;
        border-radius: 8px !important;
        margin: 15px auto 0 auto !important;
        box-shadow: none !important;
    }
    .close-guide-btn-container div.stButton > button:hover {
        background: rgba(239, 68, 68, 0.25) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.4) !important;
    }

    /* Active Workspace interface dashboard frame cards */
    .workspace-container { padding: 10px 20px; width: 100%; }
    .workspace-card {
        background: rgba(13, 7, 36, 0.6);
        border: 1px solid rgba(161, 36, 245, 0.2);
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    
    .action-banner {
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.65rem;
        font-weight: 700;
        margin-top: 10px;
    }
    .status-active { background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }
    .status-inactive { background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
    .status-neutral { background: rgba(148, 163, 184, 0.08); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.18); }
    
    .gesture-table { width: 100%; border-collapse: collapse; }
    .gesture-table th { background-color: rgba(139, 92, 246, 0.15); color: #ca92ff; text-align: left; padding: 12px; border-bottom: 2px solid rgba(161, 36, 245, 0.25); }
    .gesture-table td { padding: 11px 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); color: #cbd5e1; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# SCREEN 1: HOMEPAGE (Completely minimal, no grids, tables, or buttons)
# ==============================================================================
if st.session_state.page == "landing":
    
    # Margin buffers pushing elements down safely
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    
    left_gap, center_content, right_gap = st.columns([0.05, 0.9, 0.05])
    
    with center_content:
        st.markdown("""
            <div class="neon-hero-card">
                <div class="card-flex-layout">
                    <div class="card-text-panel">
                        <h1 class="main-project-title">SGEC</h1>
                        <div class="main-project-subtitle">Sterile Gesture Environment Control System</div>
                        <div class="main-project-description">
                            Pathogen-free environment control utilizing AI-driven hand gesture recognition for modern surgical theaters.
                            <br><br>
                            <span class="highlight-text">REDUCE CONTAMINATION RISK & MAINTAIN STERILITY EFFORTLESSLY.</span>
                            <br><br>
                            INTUITIVE. TOUCHLESS. RELIABLE.
                        </div>
                    </div>
                    <div class="card-graphic-panel">
                        <div class="hologram-hand-wrapper">
                            <span class="hand-vector-icon">✋</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        if st.button("ENTER SYSTEM →"):
            st.session_state.page = "app"
            st.rerun()


# ==============================================================================
# SCREEN 2: OPERATION WORKSPACE TERMINAL (With Top-Right Help Trigger Toggle)
# ==============================================================================
elif st.session_state.page == "app":
    
    st.markdown('<div class="workspace-container">', unsafe_allow_html=True)
    
    # Header navigation split row
    header_col_left, header_col_right = st.columns([0.5, 0.5])
    
    with header_col_left:
        st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
        if st.button("← DISCONNECT TERMINAL", key="back_btn"):
            st.session_state.page = "landing"
            st.session_state.show_help = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with header_col_right:
        st.markdown('<div class="help-btn-container">', unsafe_allow_html=True)
        if st.button("❔ GESTURE GUIDE", key="help_icon_trigger"):
            st.session_state.show_help = not st.session_state.show_help
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TOGGLEABLE MODAL OVERLAY IN WORKSPACE ---
    if st.session_state.show_help:
        st.markdown('<div class="embedded-modal-card">', unsafe_allow_html=True)
        st.markdown("""
            <h3 style="margin-top:0; color:#fff; font-size:1.4rem; letter-spacing:1px; border-bottom:1px solid rgba(161, 36, 245, 0.3); padding-bottom:10px; margin-bottom:15px;">📋 Real-time Control Reference Guide</h3>
            <table class="gesture-table">
                <thead>
                    <tr><th>Spatial Gesture</th><th>Target System Action</th></tr>
                </thead>
                <tbody>
                    <tr><td>✋ OPEN PALM</td><td><span style="color:#34d399;">Light ON</span></td></tr>
                    <tr><td>✊ FIST</td><td><span style="color:#f87171;">Light OFF</span></td></tr>
                    <tr><td>👍 THUMBS UP</td><td><span style="color:#34d399;">Fan ON</span></td></tr>
                    <tr><td>👎 THUMBS DOWN</td><td><span style="color:#f87171;">Fan OFF</span></td></tr>
                    <tr><td>✌️ TWO FINGERS</td><td><span style="color:#ca92ff;">Brightness UP</span></td></tr>
                    <tr><td>☝️ ONE FINGER</td><td><span style="color:#ca92ff;">Brightness DOWN</span></td></tr>
                    <tr><td>🤙 THREE FINGERS</td><td><span style="color:#34d399;">AC ON</span></td></tr>
                </tbody>
            </table>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="close-guide-btn-container">', unsafe_allow_html=True)
        if st.button("CLOSE GUIDE", key="close_modal_embedded"):
            st.session_state.show_help = False
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<h1 style="font-size:2.5rem; text-align:left; margin:0; color:#fff; font-weight:800; line-height:1;">SGEC Operating Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8b5cf6; letter-spacing:1px; margin-bottom:25px; margin-top:5px;">LIVE WORKSPACE ENVIRONMENT MATRIX</p>', unsafe_allow_html=True)

    # Clean UI Layout columns split for video and live command status card output
    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown('<div class="workspace-card"><h3 style="color:#fff; margin-top:0;">📷 Video Capture Frame Array</h3></div>', unsafe_allow_html=True)
        
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        result_queue = queue.Queue()
        RTC_CONFIGURATION = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )

        def recognize_gesture(hand_landmarks):
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            index_tip = hand_landmarks.landmark[8]
            index_pip = hand_landmarks.landmark[6]
            middle_tip = hand_landmarks.landmark[12]
            middle_pip = hand_landmarks.landmark[10]
            ring_tip = hand_landmarks.landmark[16]
            ring_pip = hand_landmarks.landmark[14]
            pinky_tip = hand_landmarks.landmark[20]
            pinky_pip = hand_landmarks.landmark[18]
            wrist = hand_landmarks.landmark[0]

            index_open = index_tip.y < index_pip.y
            middle_open = middle_tip.y < middle_pip.y
            ring_open = ring_tip.y < ring_pip.y
            pinky_open = pinky_tip.y < pinky_pip.y
            thumb_open = abs(thumb_tip.x - wrist.x) > abs(thumb_ip.x - wrist.x)
            fingers_count = sum([index_open, middle_open, ring_open, pinky_open])

            if not index_open and not middle_open and not ring_open and not pinky_open and thumb_tip.y > index_pip.y:
                return "✊ FIST → Light OFF"
            if index_open and middle_open and ring_open and pinky_open and thumb_open:
                return "✋ OPEN PALM → Light ON"
            if thumb_tip.y < index_pip.y and thumb_tip.y < thumb_ip.y and fingers_count == 0:
                return "👍 THUMBS UP → Fan ON"
            if thumb_tip.y > wrist.y and fingers_count == 0:
                return "👎 THUMBS DOWN → Fan OFF"
            if index_open and middle_open and not ring_open and not pinky_open:
                return "✌️ TWO FINGERS → Brightness UP"
            if index_open and not middle_open and not ring_open and not pinky_open:
                return "☝️ ONE FINGER → Brightness DOWN"
            if index_open and middle_open and ring_open and not pinky_open:
                return "🤙 THREE FINGERS → AC ON"
            return "❌ INVALID GESTURE"

        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_img)
            
            detected_gesture = "❌ NO GESTURE"
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(161, 36, 245), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)
                    )
                    detected_gesture = recognize_gesture(hand_landmarks)
            
            result_queue.put(detected_gesture)
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        ctx = webrtc_streamer(
            key="sgec-clean-neon-run",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

    with col2:
        st.markdown('<div class="workspace-card"><h3 style="color:#fff; margin-top:0;">🎮 Connected Command Relay</h3></div>', unsafe_allow_html=True)
        
        status_placeholder = st.empty()
        status_placeholder.markdown('<div class="action-banner status-neutral">SYSTEM IDLE<br><span style="font-size:0.85rem; font-weight:normal; color:#64748b;">Awaiting active input tracking frames...</span></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # --- CORE STREAMS DATA DESERIALIZATION PROCESSING MATRIX ---
    while ctx.state.playing:
        try:
            gesture_output = result_queue.get(timeout=1.0)
            
            if "OFF" in gesture_output or "DOWN" in gesture_output or "❌" in gesture_output:
                status_style = "status-inactive"
            elif "NO GESTURE" in gesture_output:
                status_style = "status-neutral"
            else:
                status_style = "status-active"
                
            status_placeholder.markdown(
                f'<div class="action-banner {status_style}">{gesture_output}</div>', 
                unsafe_allow_html=True
            )
        except queue.Empty:
            pass