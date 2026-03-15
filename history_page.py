import streamlit as st
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image

# Import the separate database module
from detection_database import save_detection, get_all_detections, get_detection_count, clear_all_detections, get_disease_stats

def history_page():
    """History page that displays all detections from separate database"""
    load_css()
    navigation_sidebar()
    
    # Check if we need to save a new detection
    # EVERY detection is saved - no duplicate checking
    if st.session_state.get('save_to_history', False) and st.session_state.get('cls_name'):
        
        # Get image from session state
        image = st.session_state.get('uploaded_image', None)
        disease = st.session_state.cls_name
        confidence = st.session_state.display_conf
        
        # Save EVERY detection to database - returns unique ID
        detection_id = save_detection(
            disease=disease,
            confidence=confidence,
            image=image,
            metadata={
                'source': 'user_upload',
                'session_id': str(datetime.now().timestamp())
            }
        )
        
        if detection_id > 0:
            st.success(f"✅ Detection #{detection_id} saved to database!")
        else:
            st.error("❌ Failed to save detection")
        
        # Reset the flag
        st.session_state.save_to_history = False
    
    # Page styling with no-drag CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    
    /* Prevent dragging on all interactive elements */
    .stButton > button, 
    .stSidebar button,
    .stSidebar [data-testid="stSidebarNav"] li,
    .stSidebar a,
    .stSidebar [role="button"],
    nav, 
    .nav-item,
    .sidebar-content *,
    .history-item,
    .history-img {
        user-drag: none !important;
        -webkit-user-drag: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    
    /* Prevent image dragging */
    img {
        user-drag: none !important;
        -webkit-user-drag: none !important;
    }
    
    .history-title {
        font-family: 'Playfair Display', serif;
        font-size: 48px;
        text-align: center;
        color: #ff1493;
        margin: 30px 0 20px 0;
        text-shadow: 
            0 0 20px rgba(255, 20, 147, 0.8),
            0 0 40px rgba(255, 20, 147, 0.6),
            0 0 60px rgba(255, 20, 147, 0.4);
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { 
            text-shadow: 0 0 20px rgba(255, 20, 147, 0.8), 0 0 40px rgba(255, 20, 147, 0.6);
        }
        to { 
            text-shadow: 0 0 30px rgba(255, 20, 147, 1), 0 0 60px rgba(255, 20, 147, 0.8), 0 0 90px rgba(255, 105, 180, 0.6);
        }
    }
    
    .history-subtitle {
        text-align: center;
        color: #db7093;
        font-size: 16px;
        margin-bottom: 40px;
        font-style: italic;
    }
    
    /* Stats Container */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.9) 0%, rgba(255, 228, 235, 0.9) 100%);
        border-radius: 15px;
        padding: 15px 25px;
        border: 2px solid rgba(255, 182, 193, 0.5);
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.15);
        text-align: center;
        min-width: 120px;
    }
    
    .stat-number {
        font-size: 28px;
        font-weight: 700;
        color: #ff1493;
        margin: 0;
    }
    
    .stat-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    
    /* History Card Container */
    .history-item {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.95) 100%);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 2px solid rgba(255, 182, 193, 0.5);
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .history-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 20, 147, 0.25);
        border-color: #ff1493;
    }
    
    .history-content {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .history-img {
        width: 80px;
        height: 80px;
        min-width: 80px;
        border-radius: 12px;
        object-fit: cover;
        border: 2px solid rgba(255, 182, 193, 0.6);
        box-shadow: 0 4px 10px rgba(255, 105, 180, 0.2);
        display: block !important;
    }
    
    .history-img-placeholder {
        width: 80px;
        height: 80px;
        min-width: 80px;
        border-radius: 12px;
        background: linear-gradient(135deg, #ffe4e1, #ffb6c1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        border: 2px solid rgba(255, 182, 193, 0.6);
    }
    
    .history-details {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .history-id {
        font-size: 10px;
        color: #aaa;
        font-weight: 600;
    }
    
    .history-disease-label {
        font-size: 11px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .history-disease-name {
        font-size: 18px;
        color: #ff1493;
        font-weight: 700;
        text-transform: capitalize;
        margin: 2px 0;
    }
    
    .history-meta {
        display: flex;
        gap: 15px;
        align-items: center;
        margin-top: 5px;
        flex-wrap: wrap;
    }
    
    .history-confidence {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(255, 20, 147, 0.3);
    }
    
    .history-datetime {
        font-size: 12px;
        color: #999;
        font-weight: 500;
    }
    
    .empty-history {
        text-align: center;
        padding: 60px 20px;
        background: rgba(255, 240, 245, 0.5);
        border-radius: 20px;
        border: 2px dashed rgba(255, 182, 193, 0.6);
    }
    
    .empty-icon {
        font-size: 60px;
        margin-bottom: 20px;
        opacity: 0.5;
        animation: floatEmpty 3s ease-in-out infinite;
    }
    
    @keyframes floatEmpty {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .empty-text {
        color: #db7093;
        font-size: 16px;
        margin-bottom: 10px;
    }
    
    .empty-subtext {
        color: #999;
        font-size: 13px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a6f) !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 25px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(238, 90, 111, 0.3) !important;
        transition: all 0.3s ease !important;
        user-drag: none !important;
        -webkit-user-drag: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(238, 90, 111, 0.4) !important;
    }
    </style>
    
    <div class="history-title">📜 Detection History</div>
    <div class="history-subtitle">Track all your flower disease detections</div>
    """, unsafe_allow_html=True)
    
    # Get statistics
    total_count = get_detection_count()
    disease_stats = get_disease_stats()
    
    # Display statistics
    if total_count > 0:
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">{total_count}</div>
                <div class="stat-label">Total Detections</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(disease_stats)}</div>
                <div class="stat-label">Diseases Found</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Get all detections from database
    detections = get_all_detections()
    
    if detections:
        # Display history cards (newest first) with images
        for detection in detections:
            detection_id = detection.get('detection_id', 0)
            
            # Image handling
            if detection.get('image_base64') and detection['image_base64'].startswith('data:image'):
                img_html = f'<img src="{detection["image_base64"]}" class="history-img" alt="Detection" draggable="false">'
            else:
                img_html = '<div class="history-img-placeholder">🌸</div>'
            
            # Format confidence
            confidence_val = detection.get('confidence', 0)
            if isinstance(confidence_val, (int, float)):
                confidence_str = f"{confidence_val:.1%}"
            else:
                confidence_str = str(confidence_val)
            
            st.markdown(f"""
            <div class="history-item">
                <div class="history-content">
                    {img_html}
                    <div class="history-details">
                        <div class="history-id">Detection #{detection_id}</div>
                        <div class="history-disease-label">DETECTED DISEASE</div>
                        <div class="history-disease-name">🦠 {detection['disease'].replace("-", " ").title()}</div>
                        <div class="history-meta">
                            <span class="history-confidence">Confidence: {confidence_str}</span>
                            <span class="history-datetime">📅 {detection.get('date', 'N/A')} | 🕐 {detection.get('time', 'N/A')}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear History Button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("🗑️ Clear All History", key="clear_history", use_container_width=True):
                if clear_all_detections():
                    st.success("✅ All history cleared!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear history")
        
        # Export button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("📥 Export to JSON", key="export_json", use_container_width=True):
                from detection_database import db
                if db.export_to_json():
                    st.success("✅ Exported to detections_export.json")
                else:
                    st.error("❌ Export failed")
        
    else:
        # Empty state
        st.markdown("""
        <div class="empty-history">
            <div class="empty-icon">🌸</div>
            <div class="empty-text">No detection history yet</div>
            <div class="empty-subtext">Go to the Detect page to start analyzing your flowers!</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Go to detect button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔍 Start Detecting", key="goto_detect"):
                st.session_state.page = "detection"
                st.rerun()