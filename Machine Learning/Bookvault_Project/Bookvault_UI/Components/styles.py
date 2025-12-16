"""
Modern dark theme with cyan/teal accents for BookVault
Latest trendy color scheme
"""

def get_global_styles() -> str:
    """Get global CSS styles for the application"""
    return """
<style>
    /* Global Styles - Dark Theme with Cyan/Teal */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #0d1b2a 50%, #1b263b 100%);
        color: #e8eaed;
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    }

    /* Hero Section - Cyan/Teal Gradient */
    .hero-section {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 50%, #0e7490 100%);
        padding: 40px 30px;
        text-align: center;
        margin: 16px 16px 20px 16px;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(6, 182, 212, 0.4);
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: pulse 20s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.5; }
        50% { transform: scale(1.1) rotate(180deg); opacity: 0.8; }
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        margin-bottom: 12px;
        position: relative;
        z-index: 1;
        letter-spacing: 1px;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 12px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }

    .hero-description {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.9);
        position: relative;
        z-index: 1;
        font-weight: 400;
    }

    /* Search Bar - Cyan Theme */
    /* Remove default container borders and backgrounds */
    .stTextInput > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stTextInput > div > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(6, 182, 212, 0.4) !important;
        color: #e8eaed !important;
        border-radius: 14px !important;
        padding: 16px 24px !important;
        font-size: 1.05rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #06b6d4 !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2) !important;
        background: rgba(15, 23, 42, 0.95) !important;
        outline: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
    }

    /* Selectbox (Genre Dropdown) - Cyan Theme */
    .stSelectbox > div > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(6, 182, 212, 0.4) !important;
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        cursor: pointer !important;
    }

    .stSelectbox > div > div > div {
        color: #e8eaed !important;
        font-weight: 500;
        cursor: pointer !important;
    }

    .stSelectbox > div > div:hover {
        border-color: #06b6d4 !important;
    }

    /* Make selectbox input non-editable and clickable */
    .stSelectbox input {
        cursor: pointer !important;
        caret-color: transparent !important;
        user-select: none !important;
        pointer-events: none !important;
    }

    .stSelectbox [data-baseweb="select"] {
        cursor: pointer !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        cursor: pointer !important;
    }

    /* Section Headers - Cyan Theme */
    .section-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #22d3ee;
        margin: 24px 0 16px 0;
        padding-left: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: 0.5px;
        position: relative;
    }

    .section-header::before {
        content: '';
        width: 6px;
        height: 36px;
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(6, 182, 212, 0.5);
    }

    /* Book Grid - 6 columns, 2 rows */
    .book-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 16px;
        padding: 0 16px 24px 16px;
        max-width: 1600px;
        margin: 0 auto;
    }

    @media (max-width: 1400px) {
        .book-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }

    @media (max-width: 900px) {
        .book-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 600px) {
        .book-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    /* Detail Page - Cyan Theme */
    .detail-container {
        padding: 20px 24px;
        max-width: 1400px;
        margin: -8px auto 0 auto;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(6, 182, 212, 0.2);
    }

    .detail-header {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 40px;
        margin-bottom: 48px;
    }

    .detail-cover {
        width: 100%;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .detail-info {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .detail-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e8eaed;
        line-height: 1.2;
    }

    .detail-rating {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.1rem;
        color: #fbbf24;
    }

    .detail-metadata {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        font-size: 0.95rem;
        color: #9ca3af;
    }

    .detail-metadata-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .detail-genres {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }

    .genre-tag {
        background: rgba(6, 182, 212, 0.2);
        color: #67e8f9;
        padding: 8px 16px;
        border-radius: 24px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 2px solid rgba(6, 182, 212, 0.3);
        transition: all 0.3s ease;
    }

    .genre-tag:hover {
        background: rgba(6, 182, 212, 0.3);
        border-color: #06b6d4;
        transform: translateY(-2px);
    }

    .detail-description {
        font-size: 1rem;
        line-height: 1.7;
        color: #d1d5db;
        margin-top: 16px;
    }

    /* Back Button - Cyan Theme */
    .back-button {
        background: rgba(15, 23, 42, 0.8);
        color: #22d3ee;
        border: 2px solid rgba(6, 182, 212, 0.4);
        padding: 12px 24px;
        border-radius: 12px;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .back-button:hover {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        border-color: #06b6d4;
        transform: translateX(-5px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
    }

    /* Buttons - Cyan Theme */
    /* Primary buttons (all functional buttons) */
    .stButton > button[kind="primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(8, 145, 178, 0.6) !important;
    }

    .stButton > button[kind="primary"]:active,
    button[kind="primary"]:active {
        transform: translateY(0px) !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.5) !important;
    }

    /* Default button styling (fallback) */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(8, 145, 178, 0.6) !important;
    }

    /* Image Upload Button - Cyan Theme */
    .upload-button {
        background: rgba(15, 23, 42, 0.6);
        border: 2px dashed rgba(6, 182, 212, 0.4);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 20px;
    }

    .upload-button:hover {
        border-color: #06b6d4;
        background: rgba(6, 182, 212, 0.1);
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
    }

    /* Scrollbar - Cyan Theme */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    ::-webkit-scrollbar-track {
        background: #0d1b2a;
    }

    ::-webkit-scrollbar-thumb {
        background: #06b6d4;
        border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #0891b2;
    }

    /* Loading Spinner - Cyan Theme */
    .stSpinner > div {
        border-color: #06b6d4 !important;
    }

    /* Info/Warning/Success boxes - Cyan Theme */
    .stAlert {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 2px solid rgba(6, 182, 212, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        color: #e8eaed !important;
    }

    /* Hide Streamlit Branding and Remove Default Padding */
    .css-1v0mbdj { display: none; }
    .css-18e3th9 { padding-top: 0 !important; }

    /* Reduce Streamlit default padding */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Secondary buttons styling (for chat close button, etc.) */
    button[kind="secondary"] {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        color: white !important;
        border: 2px solid rgba(220, 38, 38, 0.8) !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
    }

    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(220, 38, 38, 0.5) !important;
    }

    /* File Uploader - Cyan Theme */
    .stFileUploader {
        background: rgba(15, 23, 42, 0.6);
        border: 2px dashed rgba(6, 182, 212, 0.4);
        border-radius: 12px;
        padding: 20px;
    }

    .stFileUploader:hover {
        border-color: #06b6d4;
        background: rgba(6, 182, 212, 0.1);
    }
    
</style>
"""
