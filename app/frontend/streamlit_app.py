"""
DocPilot — Streamlit Frontend

A premium web interface for uploading PDF documents and asking questions
about their content. Gets answers with citations and page numbers.

Run with:
    streamlit run app/frontend/streamlit_app.py --server.port 8501
"""

import os

import requests
import streamlit as st
import streamlit.components.v1 as components

# ==================================================
# Configuration — reads BACKEND_URL from env for Docker compatibility
# ==================================================
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="DocPilot — AI Document Assistant",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ==================================================
# Interactive Constellation Network Canvas Background
# ==================================================
components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    let canvas = parentDoc.getElementById('constellation-bg-canvas');
    if (!canvas) {
        canvas = parentDoc.createElement('canvas');
        canvas.id = 'constellation-bg-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '1';
        canvas.style.pointerEvents = 'none'; // let mouse clicks pass to Streamlit
        parentDoc.body.prepend(canvas);

        const ctx = canvas.getContext('2d');
        let width = canvas.width = parentDoc.documentElement.clientWidth || window.parent.innerWidth;
        let height = canvas.height = parentDoc.documentElement.clientHeight || window.parent.innerHeight;

        window.parent.addEventListener('resize', () => {
            width = canvas.width = parentDoc.documentElement.clientWidth || window.parent.innerWidth;
            height = canvas.height = parentDoc.documentElement.clientHeight || window.parent.innerHeight;
        });

        // Mouse tracking across the entire parent window
        let mouse = { x: -1000, y: -1000, active: false };
        window.parent.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
            mouse.active = true;
        });
        window.parent.addEventListener('mouseleave', () => {
            mouse.active = false;
        });

        // Particle constellation network
        const numParticles = Math.min(85, Math.floor((width * height) / 13000));
        const particles = [];
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.85,
                vy: (Math.random() - 0.5) * 0.85,
                radius: Math.random() * 2 + 1.8,
                color: Math.random() > 0.35 ? 'rgba(99, 102, 241, 0.45)' : 'rgba(14, 165, 233, 0.45)'
            });
        }

        function animate() {
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];

                // Move
                p.x += p.vx;
                p.y += p.vy;

                // Bounce at screen boundaries
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;

                // Mouse interaction — attract toward cursor when close
                if (mouse.active) {
                    let dx = mouse.x - p.x;
                    let dy = mouse.y - p.y;
                    let dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 180 && dist > 5) {
                        p.vx += (dx / dist) * 0.045;
                        p.vy += (dy / dist) * 0.045;

                        // Draw connecting line directly to mouse cursor
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.strokeStyle = `rgba(99, 102, 241, ${(1 - dist / 180) * 0.38})`;
                        ctx.lineWidth = 1.3;
                        ctx.stroke();
                    }
                }

                // Speed cap
                let speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
                if (speed > 2.3) {
                    p.vx = (p.vx / speed) * 2.3;
                    p.vy = (p.vy / speed) * 2.3;
                }

                // Draw point
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();

                // Connect to other nearby points
                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    let dx2 = p.x - p2.x;
                    let dy2 = p.y - p2.y;
                    let dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
                    if (dist2 < 140) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(99, 102, 241, ${(1 - dist2 / 140) * 0.24})`;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    }
    </script>
    """,
    height=0,
    width=0,
)

# ==================================================
# Premium Glassmorphism Theme — v2.0
# ==================================================
st.markdown(
    """
    <style>
    /* ── Google Fonts ─────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap');

    /* ── Root Design Tokens ──────────────────────── */
    :root {
        /* Backgrounds */
        --bg-primary: #f8fafc;
        --bg-secondary: #f1f5f9;
        --bg-elevated: #ffffff;

        /* Glass layers */
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-bg-elevated: rgba(255, 255, 255, 0.9);
        --glass-border: rgba(203, 213, 225, 0.7);
        --glass-border-hover: rgba(99, 102, 241, 0.5);
        --glass-hover: rgba(255, 255, 255, 0.98);
        --glass-inner-glow: inset 0 1px 0 rgba(255, 255, 255, 1);

        /* Accent palette */
        --accent-primary: #6366f1;
        --accent-secondary: #4f46e5;
        --accent-tertiary: #0ea5e9;
        --accent-warm: #ea580c;
        --accent-glow: rgba(99, 102, 241, 0.25);
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #0ea5e9 100%);
        --accent-gradient-warm: linear-gradient(135deg, #6366f1, #ea580c);
        --neon-glow: 0 0 20px rgba(99, 102, 241, 0.12), 0 0 40px rgba(99, 102, 241, 0.05);

        /* Text - Ultra Readable Dark Slate/Navy */
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;

        /* Status */
        --success: #10b981;
        --success-bg: rgba(16, 185, 129, 0.08);
        --success-border: rgba(16, 185, 129, 0.25);
        --warning: #f59e0b;
        --warning-bg: rgba(245, 158, 11, 0.08);
        --warning-border: rgba(245, 158, 11, 0.25);
        --error: #ef4444;
        --error-bg: rgba(239, 68, 68, 0.08);
        --error-border: rgba(239, 68, 68, 0.25);
        --info-bg: rgba(14, 165, 233, 0.08);
        --info-border: rgba(14, 165, 233, 0.25);

        /* Radii */
        --radius-xs: 8px;
        --radius-sm: 12px;
        --radius-md: 16px;
        --radius-lg: 20px;
        --radius-full: 100px;

        /* Motion */
        --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
        --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
        --transition-fast: all 0.2s var(--ease-out-expo);
        --transition: all 0.35s var(--ease-out-expo);
        --transition-slow: all 0.5s var(--ease-out-expo);
    }

    /* ── Global Resets & Transparent Canvas Base ── */
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        background: #f8fafc !important;
        color: var(--text-primary) !important;
        scroll-behavior: smooth;
    }

    div#root, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], [data-testid="stMain"] {
        background: transparent !important;
        position: relative !important;
        z-index: 2 !important;
    }

    /* Completely remove sidebar and top header so EVERYTHING lives inside the center glass box */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"], header[data-testid="stHeader"] {
        display: none !important;
    }

    /* ── CENTRAL GLASSMORPHISM BOX (Main Shell Container) ── */
    [data-testid="stMainBlockContainer"] {
        background: rgba(255, 255, 255, 0.78) !important;
        backdrop-filter: blur(36px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(36px) saturate(180%) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
        border-radius: 32px !important;
        box-shadow: 0 24px 64px rgba(15, 23, 42, 0.08), 0 4px 16px rgba(99, 102, 241, 0.06), inset 0 1px 0 rgba(255, 255, 255, 1) !important;
        padding: 3.5rem 4rem 4rem !important;
        margin: 3.5rem auto !important;
        max-width: 820px !important;
        position: relative !important;
        z-index: 10 !important;
    }

    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            padding: 2rem 1.5rem 3rem !important;
            margin: 1.5rem auto !important;
            border-radius: 24px !important;
        }
    }

    /* Text selection */
    ::selection {
        background: rgba(99, 102, 241, 0.25);
        color: #0f172a;
    }

    /* ── Animated Background Mesh (Light Pastel Orbs) ── */
    [data-testid="stApp"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(800px circle at 20% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 60%),
            radial-gradient(600px circle at 80% 15%, rgba(14, 165, 233, 0.07) 0%, transparent 50%),
            radial-gradient(700px circle at 65% 75%, rgba(139, 92, 246, 0.06) 0%, transparent 55%),
            radial-gradient(500px circle at 10% 85%, rgba(249, 115, 22, 0.05) 0%, transparent 45%);
        pointer-events: none;
        z-index: 0;
        animation: meshFloat 25s ease-in-out infinite alternate;
    }

    /* Second floating orb layer */
    [data-testid="stApp"]::after {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(400px circle at 50% 50%, rgba(99, 102, 241, 0.04) 0%, transparent 70%),
            radial-gradient(300px circle at 30% 60%, rgba(14, 165, 233, 0.035) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
        animation: meshFloat2 30s ease-in-out infinite alternate-reverse;
    }

    /* Noise grain overlay */
    [data-testid="stMain"]::before {
        content: '';
        position: fixed;
        inset: 0;
        opacity: 0.01;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        background-repeat: repeat;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes meshFloat {
        0% {
            background-position: 0% 0%;
            opacity: 0.85;
            transform: scale(1);
        }
        33% { opacity: 1; transform: scale(1.02); }
        66% { opacity: 0.9; transform: scale(0.98); }
        100% {
            background-position: 100% 100%;
            opacity: 0.95;
            transform: scale(1.01);
        }
    }

    @keyframes meshFloat2 {
        0% { opacity: 0.6; transform: translateY(0) rotate(0deg); }
        50% { opacity: 1; transform: translateY(-20px) rotate(1deg); }
        100% { opacity: 0.7; transform: translateY(10px) rotate(-1deg); }
    }

    /* ── Header ──────────────────────────────────── */
    header[data-testid="stHeader"] {
        background: rgba(248, 250, 252, 0.6) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }

    /* ── SIDEBAR — Frosted Glass ─────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(241, 245, 249, 0.88) !important;
        backdrop-filter: blur(32px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(32px) saturate(150%) !important;
        border-right: 1px solid var(--glass-border) !important;
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.05) !important;
    }

    [data-testid="stSidebar"]::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 1px;
        height: 100%;
        background: linear-gradient(180deg, transparent 0%, rgba(99, 102, 241, 0.2) 50%, transparent 100%);
        pointer-events: none;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        color: var(--text-secondary) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--glass-border) !important;
        margin: 1rem 0 !important;
    }

    /* ── Glass Card System ───────────────────────── */
    .glass-card {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) saturate(140%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(140%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
        box-shadow: var(--glass-inner-glow), 0 4px 24px rgba(15, 23, 42, 0.05) !important;
        transition: var(--transition) !important;
    }

    .glass-card:hover {
        background: var(--glass-bg-elevated) !important;
        border-color: var(--glass-border-hover) !important;
        box-shadow: var(--glass-inner-glow), var(--neon-glow), 0 8px 32px rgba(15, 23, 42, 0.08) !important;
        transform: translateY(-2px) !important;
    }

    .glass-card:active {
        transform: translateY(0) scale(0.985) !important;
        transition: var(--transition-fast) !important;
    }

    .glass-card-elevated {
        background: var(--glass-bg-elevated) !important;
        backdrop-filter: blur(24px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
        border: 1px solid rgba(203, 213, 225, 0.8) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
        box-shadow: var(--glass-inner-glow), 0 8px 32px rgba(15, 23, 42, 0.06) !important;
        transition: var(--transition) !important;
    }

    /* ── HERO SECTION — Premium ──────────────────── */
    .hero-container {
        text-align: center;
        padding: 2.5rem 0 1.5rem;
        position: relative;
        animation: heroFadeIn 0.8s var(--ease-out-expo) forwards;
    }

    @keyframes heroFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(124,108,240,0.12), rgba(168,160,255,0.06));
        border: 1px solid rgba(124, 108, 240, 0.2);
        border-radius: var(--radius-full);
        padding: 7px 20px;
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--accent-secondary);
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
        animation: badgePulse 3s ease-in-out infinite, heroFadeIn 0.6s var(--ease-out-expo) 0.1s both;
        position: relative;
        overflow: hidden;
    }

    .hero-badge::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(90deg, transparent 0%, rgba(168,160,255,0.1) 50%, transparent 100%);
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes badgePulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(124,108,240,0); }
        50% { box-shadow: 0 0 0 6px rgba(124,108,240,0.06); }
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .hero-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #7c6cf0 0%, #a8a0ff 30%, #74b9ff 60%, #a8a0ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.6rem;
        line-height: 1.1;
        letter-spacing: -1.5px;
        animation: gradientShift 6s ease-in-out infinite, heroFadeIn 0.8s var(--ease-out-expo) 0.2s both;
        text-shadow: none;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0 auto;
        max-width: 480px;
        line-height: 1.7;
        animation: heroFadeIn 0.8s var(--ease-out-expo) 0.35s both;
    }

    /* Floating particles around hero */
    .hero-container::before,
    .hero-container::after {
        content: '';
        position: absolute;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-secondary);
        opacity: 0.15;
        animation: particleFloat 8s ease-in-out infinite;
    }

    .hero-container::before {
        top: 15%;
        left: 8%;
        animation-delay: 0s;
    }

    .hero-container::after {
        bottom: 20%;
        right: 10%;
        animation-delay: 4s;
        width: 4px;
        height: 4px;
    }

    @keyframes particleFloat {
        0%, 100% { transform: translate(0, 0); opacity: 0.15; }
        25% { transform: translate(15px, -20px); opacity: 0.3; }
        50% { transform: translate(-10px, -35px); opacity: 0.1; }
        75% { transform: translate(20px, -15px); opacity: 0.25; }
    }

    /* ── SECTION HEADERS — Interactive ───────────── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2.5rem 0 1.25rem;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid var(--glass-border);
        position: relative;
        transition: var(--transition);
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 0;
        height: 2px;
        background: var(--accent-gradient);
        border-radius: 2px;
        transition: width 0.5s var(--ease-out-expo);
    }

    .section-header:hover::after {
        width: 100%;
    }

    .section-icon {
        width: 38px;
        height: 38px;
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .section-icon::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, transparent, rgba(255,255,255,0.08));
        opacity: 0;
        transition: var(--transition);
    }

    .section-header:hover .section-icon::before {
        opacity: 1;
    }

    .section-header:hover .section-icon {
        transform: scale(1.08) rotate(-3deg);
    }

    .section-icon.upload {
        background: linear-gradient(135deg, rgba(124,108,240,0.2), rgba(168,160,255,0.08));
        box-shadow: 0 2px 12px rgba(124,108,240,0.1);
    }
    .section-icon.ask {
        background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(52,211,153,0.08));
        box-shadow: 0 2px 12px rgba(52,211,153,0.1);
    }
    .section-icon.answer {
        background: linear-gradient(135deg, rgba(251,191,36,0.2), rgba(251,191,36,0.08));
        box-shadow: 0 2px 12px rgba(251,191,36,0.1);
    }

    .section-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.3px;
    }

    .section-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin: 0;
    }

    /* ── FILE UPLOADER — Pristine Light Dropzone ─── */
    [data-testid="stFileUploader"] {
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.88) !important;
        border: 2px dashed rgba(99, 102, 241, 0.38) !important;
        border-radius: var(--radius-md) !important;
        padding: 2.5rem 1.5rem !important;
        transition: var(--transition) !important;
        box-shadow: inset 0 2px 8px rgba(15, 23, 42, 0.02) !important;
    }

    [data-testid="stFileUploadDropzone"] *,
    [data-testid="stFileUploadDropzone"] div,
    [data-testid="stFileUploadDropzone"] section,
    [data-testid="stFileUploadDropzone"] span {
        background-color: transparent !important;
    }

    [data-testid="stFileUploadDropzone"]:hover {
        background: rgba(255, 255, 255, 0.98) !important;
        border-color: var(--accent-primary) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.12), inset 0 2px 8px rgba(15, 23, 42, 0.01) !important;
        transform: translateY(-2px);
    }

    [data-testid="stFileUploadDropzone"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stFileUploadDropzone"] label,
    [data-testid="stFileUploadDropzone"] span {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploadDropzone"] small {
        color: var(--text-muted) !important;
    }

    [data-testid="stFileUploadDropzone"] button {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-xs) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25) !important;
    }

    [data-testid="stFileUploadDropzone"] button:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── BUTTONS — Ripple + Press Physics ─────────── */
    [data-testid="stButton"] > button {
        background: var(--accent-gradient) !important;
        background-size: 200% 200% !important;
        background-position: 0% 50% !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1.75rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        transition: var(--transition) !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25),
                    inset 0 1px 0 rgba(255,255,255,0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Shimmer sweep on button */
    [data-testid="stButton"] > button::before {
        content: '' !important;
        position: absolute !important;
        inset: 0 !important;
        background: linear-gradient(105deg,
            transparent 20%,
            rgba(255,255,255,0.12) 45%,
            rgba(255,255,255,0.15) 50%,
            rgba(255,255,255,0.12) 55%,
            transparent 80%) !important;
        transform: translateX(-100%) !important;
        transition: transform 0.6s var(--ease-out-expo) !important;
    }

    [data-testid="stButton"] > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.4),
                    0 2px 10px rgba(99, 102, 241, 0.2),
                    inset 0 1px 0 rgba(255,255,255,0.15) !important;
        background-position: 100% 50% !important;
    }

    [data-testid="stButton"] > button:hover::before {
        transform: translateX(100%) !important;
    }

    [data-testid="stButton"] > button:active {
        transform: translateY(0) scale(0.97) !important;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.2),
                    inset 0 1px 0 rgba(255,255,255,0.05) !important;
        transition: var(--transition-fast) !important;
    }

    /* ── TEXT INPUT — Focus Brilliance ───────────── */
    [data-testid="stTextInput"] {
        width: 100% !important;
    }

    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1.5px solid rgba(203, 213, 225, 0.8) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: inset 0 2px 6px rgba(15, 23, 42, 0.03) !important;
        transition: var(--transition) !important;
        overflow: hidden !important;
    }

    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    [data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15), inset 0 1px 4px rgba(15, 23, 42, 0.02) !important;
        background: #ffffff !important;
    }

    [data-testid="stTextInput"] input {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        padding: 0.85rem 1.25rem !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: var(--text-muted) !important;
        font-style: italic !important;
    }

    [data-testid="stTextInput"] label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }

    /* ── STATUS ALERTS ───────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--glass-border) !important;
        backdrop-filter: blur(12px) !important;
        animation: alertSlide 0.4s var(--ease-out-expo) !important;
    }

    @keyframes alertSlide {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stAlert"][data-baseweb*="positive"],
    .stSuccess, .element-container .stAlert:has(svg[data-icon="check"]) {
        background: var(--success-bg) !important;
        border-color: var(--success-border) !important;
    }

    div[data-testid="stAlert"][data-baseweb*="warning"] {
        background: var(--warning-bg) !important;
        border-color: var(--warning-border) !important;
    }

    div[data-testid="stAlert"][data-baseweb*="negative"] {
        background: var(--error-bg) !important;
        border-color: var(--error-border) !important;
    }

    div[data-testid="stAlert"][data-baseweb*="info"] {
        background: var(--info-bg) !important;
        border-color: var(--info-border) !important;
    }

    /* ── EXPANDER ────────────────────────────────── */
    [data-testid="stExpander"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-sm) !important;
        margin-bottom: 0.5rem !important;
        overflow: hidden !important;
        transition: var(--transition) !important;
        box-shadow: var(--glass-inner-glow) !important;
    }

    [data-testid="stExpander"]:hover {
        border-color: var(--glass-border-hover) !important;
        box-shadow: var(--glass-inner-glow), 0 4px 20px rgba(124,108,240,0.05) !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: var(--accent-secondary) !important;
    }

    [data-testid="stExpander"] [data-testid="stMarkdown"] {
        color: var(--text-secondary) !important;
    }

    /* ── CITATION TAGS — Chip Interactions ────────── */
    .citation-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(124,108,240,0.1), rgba(168,160,255,0.05));
        border: 1px solid rgba(124, 108, 240, 0.18);
        border-radius: var(--radius-full);
        padding: 6px 16px;
        margin: 4px 5px;
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--accent-secondary);
        transition: var(--transition);
        cursor: default;
        backdrop-filter: blur(8px);
        animation: chipSlideIn 0.4s var(--ease-out-expo) backwards;
    }

    .citation-tag:nth-child(1) { animation-delay: 0s; }
    .citation-tag:nth-child(2) { animation-delay: 0.06s; }
    .citation-tag:nth-child(3) { animation-delay: 0.12s; }
    .citation-tag:nth-child(4) { animation-delay: 0.18s; }
    .citation-tag:nth-child(5) { animation-delay: 0.24s; }
    .citation-tag:nth-child(6) { animation-delay: 0.3s; }

    @keyframes chipSlideIn {
        from { opacity: 0; transform: translateY(8px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .citation-tag:hover {
        background: linear-gradient(135deg, rgba(124,108,240,0.18), rgba(168,160,255,0.1));
        border-color: rgba(124, 108, 240, 0.35);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(124,108,240,0.12);
    }

    /* ── USER QUESTION CARD (For Cross-Questioning History) ── */
    .user-question-card {
        background: rgba(99, 102, 241, 0.08) !important;
        border: 1.5px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.25rem 1.5rem !important;
        margin: 1.75rem 0 0.75rem !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.06) !important;
    }

    /* ── ANSWER CARD — Reveal Animation & Ultra Readable Text ── */
    .answer-card {
        background: #ffffff !important;
        backdrop-filter: blur(24px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
        border: 1.5px solid rgba(203, 213, 225, 0.9) !important;
        border-radius: var(--radius-md) !important;
        padding: 2rem 2rem !important;
        margin: 0.5rem 0 1.25rem !important;
        position: relative;
        overflow: hidden;
        animation: answerReveal 0.5s var(--ease-out-expo) forwards;
        box-shadow: 0 12px 36px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255, 255, 255, 1) !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        line-height: 1.8 !important;
    }

    /* Animated gradient left border */
    .answer-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1, #4f46e5, #0ea5e9, #4f46e5, #6366f1);
        background-size: 100% 300%;
        animation: borderShimmer 4s ease-in-out infinite;
    }

    @keyframes borderShimmer {
        0% { background-position: 0% 0%; }
        50% { background-position: 0% 100%; }
        100% { background-position: 0% 0%; }
    }

    @keyframes answerReveal {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Force all text inside answer card to be crisp, bold dark navy #0f172a */
    .answer-card *, .answer-card p, .answer-card li, .answer-card span,
    .answer-card div, .answer-card h1, .answer-card h2, .answer-card h3, .answer-card h4 {
        color: #0f172a !important;
        font-weight: 500 !important;
        line-height: 1.8 !important;
    }

    .answer-card strong, .answer-card b {
        color: #4f46e5 !important;
        font-weight: 700 !important;
    }

    .answer-card code {
        background: rgba(99, 102, 241, 0.12) !important;
        color: #4f46e5 !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-size: 0.92rem !important;
    }

    /* ── STATS BAR — Dashboard Style ─────────────── */
    .stats-bar {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 1.25rem;
        animation: answerReveal 0.6s var(--ease-out-expo) 0.2s both;
    }

    .stat-item {
        flex: 1;
        min-width: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-size: 0.78rem;
        color: var(--text-muted);
        padding: 0.65rem 0.75rem;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-sm);
        transition: var(--transition);
        box-shadow: var(--glass-inner-glow);
    }

    .stat-item:hover {
        border-color: var(--glass-border-hover);
        background: var(--glass-bg-elevated);
        transform: translateY(-1px);
    }

    .stat-value {
        color: var(--accent-secondary);
        font-weight: 700;
        font-size: 0.82rem;
    }

    /* ── SIDEBAR STATUS PILL ─────────────────────── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: var(--radius-full);
        font-size: 0.8rem;
        font-weight: 500;
        backdrop-filter: blur(8px);
        transition: var(--transition);
    }

    .status-pill:hover {
        transform: translateY(-1px);
    }

    .status-pill.online {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }

    .status-pill.offline {
        background: var(--error-bg);
        color: var(--error);
        border: 1px solid var(--error-border);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        position: relative;
    }

    .status-dot::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 50%;
        animation: breathe 3s ease-in-out infinite;
    }

    .status-dot.online {
        background: var(--success);
        box-shadow: 0 0 8px var(--success);
    }

    .status-dot.online::after {
        border: 1.5px solid var(--success);
    }

    .status-dot.offline {
        background: var(--error);
        box-shadow: 0 0 8px var(--error);
    }

    .status-dot.offline::after {
        border: 1.5px solid var(--error);
    }

    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.6; }
        50% { transform: scale(1.8); opacity: 0; }
    }

    /* ── PROCESSED FILE ITEM ─────────────────────── */
    .file-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-sm);
        margin-bottom: 6px;
        font-size: 0.82rem;
        color: var(--text-secondary);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .file-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: var(--accent-gradient);
        opacity: 0.15;
        transition: width 0.4s var(--ease-out-expo);
    }

    .file-item:hover {
        background: var(--glass-bg-elevated);
        border-color: var(--glass-border-hover);
        transform: translateX(3px);
    }

    .file-item:hover::before {
        width: 3px;
    }

    /* ── FOOTER ──────────────────────────────────── */
    .footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        color: var(--text-muted);
        font-size: 0.72rem;
        letter-spacing: 0.5px;
    }

    .footer a {
        color: var(--accent-secondary);
        text-decoration: none;
        transition: var(--transition-fast);
        position: relative;
    }

    .footer a::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 0;
        height: 1px;
        background: var(--accent-secondary);
        transition: width 0.3s var(--ease-out-expo);
    }

    .footer a:hover {
        color: var(--accent-primary);
    }

    .footer a:hover::after {
        width: 100%;
    }

    /* ── DIVIDER ─────────────────────────────────── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--glass-border), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── SPINNER ─────────────────────────────────── */
    [data-testid="stSpinner"] {
        color: var(--accent-secondary) !important;
    }

    /* ── SCROLLBAR — Thin + Hover Expand ──────────── */
    ::-webkit-scrollbar {
        width: 5px;
        transition: width 0.2s;
    }

    ::-webkit-scrollbar:hover {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(124, 108, 240, 0.15);
        border-radius: 10px;
        transition: background 0.2s;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(124, 108, 240, 0.35);
    }

    /* ── FILE INFO CARD ──────────────────────────── */
    .file-info {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 1.1rem 1.35rem;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-sm);
        margin-bottom: 1rem;
        transition: var(--transition);
        box-shadow: var(--glass-inner-glow);
        animation: alertSlide 0.4s var(--ease-out-expo);
    }

    .file-info:hover {
        border-color: var(--glass-border-hover);
        background: var(--glass-bg-elevated);
    }

    .file-info-icon {
        width: 42px;
        height: 42px;
        border-radius: var(--radius-sm);
        background: linear-gradient(135deg, rgba(248,113,113,0.15), rgba(248,113,113,0.05));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
        transition: var(--transition);
    }

    .file-info:hover .file-info-icon {
        transform: rotate(-5deg) scale(1.05);
    }

    .file-info-name {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.92rem;
    }

    .file-info-size {
        color: var(--text-muted);
        font-size: 0.76rem;
        margin-top: 2px;
    }

    /* ── PROCESS RESULT CARDS ────────────────────── */
    .process-result {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 0.75rem;
    }

    .process-stat {
        flex: 1;
        min-width: 95px;
        text-align: center;
        padding: 0.85rem 0.5rem;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-sm);
        transition: var(--transition);
        box-shadow: var(--glass-inner-glow);
        animation: statReveal 0.5s var(--ease-out-expo) backwards;
    }

    .process-stat:nth-child(1) { animation-delay: 0.05s; }
    .process-stat:nth-child(2) { animation-delay: 0.1s; }
    .process-stat:nth-child(3) { animation-delay: 0.15s; }
    .process-stat:nth-child(4) { animation-delay: 0.2s; }

    @keyframes statReveal {
        from { opacity: 0; transform: translateY(12px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .process-stat:hover {
        border-color: var(--glass-border-hover);
        background: var(--glass-bg-elevated);
        transform: translateY(-3px);
        box-shadow: var(--glass-inner-glow), var(--neon-glow);
    }

    .process-stat-value {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    .process-stat-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ── SIDEBAR LOGO — Shimmer ──────────────────── */
    .sidebar-logo {
        position: relative;
        overflow: hidden;
        display: inline-block;
    }

    .sidebar-logo-text {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
    }

    .sidebar-logo::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.65), transparent);
        animation: logoShimmer 4s ease-in-out infinite;
    }

    @keyframes logoShimmer {
        0%, 100% { left: -100%; }
        50% { left: 150%; }
    }

    /* ── Focus-visible accessibility ─────────────── */
    :focus-visible {
        outline: 2px solid var(--accent-primary) !important;
        outline-offset: 2px !important;
        border-radius: var(--radius-xs) !important;
    }

    /* Hide default Streamlit decoration */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Session State
# ==================================================
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# ==================================================
# Sidebar
# ==================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0 0.5rem;">
            <div style="font-size: 2.4rem; margin-bottom: 6px;
                 filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.25));">🚀</div>
            <div class="sidebar-logo">
                <span class="sidebar-logo-text">DocPilot</span>
            </div>
            <div style="font-size: 0.68rem; color: #64748b; letter-spacing: 1.5px;
                 text-transform: uppercase; margin-top: 4px; font-weight: 600;">
                AI Document Assistant
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #334155; line-height: 1.7;">
            Upload PDF documents and ask questions.
            Get answers with <strong style="color:#4f46e5;">citations</strong>
            and <strong style="color:#4f46e5;">page numbers</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Backend health check
    st.markdown(
        '<p style="font-size:0.75rem; color:#64748b; text-transform:uppercase; '
        'letter-spacing:1px; margin-bottom:8px; font-weight:600;">System Status</p>',
        unsafe_allow_html=True,
    )

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.markdown(
                '<div class="status-pill online">'
                '<span class="status-dot online"></span>'
                f'Backend Online — v{health_data.get("version", "N/A")}'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-pill offline">'
                '<span class="status-dot offline"></span>'
                'Backend Unhealthy'
                '</div>',
                unsafe_allow_html=True,
            )
    except (requests.ConnectionError, requests.Timeout, requests.RequestException, Exception):
        st.markdown(
            '<div class="status-pill offline">'
            '<span class="status-dot offline"></span>'
            'Backend Offline / Busy'
            '</div>',
            unsafe_allow_html=True,
        )
        st.caption("If timing out, backend is restarting or busy.")

    # Processed documents
    if st.session_state.processed_files:
        st.markdown("---")
        st.markdown(
            '<p style="font-size:0.75rem; color:#64748b; text-transform:uppercase; '
            'letter-spacing:1px; margin-bottom:8px; font-weight:600;">Indexed Documents</p>',
            unsafe_allow_html=True,
        )
        for fname in st.session_state.processed_files:
            st.markdown(
                f'<div class="file-item">📄 {fname}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        '<div class="footer">'
        'Built with ❤️ using <a href="#">FastAPI</a> + '
        '<a href="#">Streamlit</a> + <a href="#">Groq</a>'
        '</div>',
        unsafe_allow_html=True,
    )

# ==================================================
# Main Content — Hero & Status Section
# ==================================================
status_badge_html = '<span style="background: rgba(16, 185, 129, 0.12); color: #059669; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.25);">🟢 Backend Online</span>'
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if response.status_code != 200:
        status_badge_html = '<span style="background: rgba(239, 68, 68, 0.12); color: #dc2626; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.25);">🔴 Backend Unhealthy</span>'
except Exception:
    status_badge_html = '<span style="background: rgba(245, 158, 11, 0.12); color: #d97706; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(245, 158, 11, 0.25);">🟡 Backend Connecting...</span>'

st.markdown(
    f"""
    <div class="hero-container" style="text-align: center; margin-bottom: 2.5rem;">
        <div style="display: flex; justify-content: center; gap: 10px; align-items: center; margin-bottom: 12px;">
            <div class="hero-badge" style="margin: 0;">✨ Powered by Groq AI</div>
            {status_badge_html}
        </div>
        <h1 class="hero-title" style="font-size: 3.5rem; margin-bottom: 8px;">DocPilot</h1>
        <p class="hero-subtitle" style="max-width: 620px; margin: 0 auto; color: #475569; font-size: 1.05rem; line-height: 1.6;">
            Upload your PDF documents and get precise, cited answers
            powered by AI. Every fact traced back to its source page.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Upload Section
# ==================================================
st.markdown(
    """
    <div class="section-header">
        <div class="section-icon upload">📄</div>
        <div>
            <p class="section-title">Upload Document</p>
            <p class="section-desc">Drag & drop or browse for a PDF file</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a PDF document to ask questions about its content.",
    label_visibility="collapsed",
)

if uploaded_file is not None:
    # File info card
    file_size_kb = uploaded_file.size / 1024
    size_str = (
        f"{file_size_kb:.1f} KB" if file_size_kb < 1024
        else f"{file_size_kb / 1024:.1f} MB"
    )
    st.markdown(
        f"""
        <div class="file-info">
            <div class="file-info-icon">📕</div>
            <div>
                <div class="file-info-name">{uploaded_file.name}</div>
                <div class="file-info-size">{size_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Upload & Process button
    if st.button("⚡ Upload & Process", type="primary", use_container_width=True):
        # Step 1: Upload
        with st.spinner("🔄 Uploading to server..."):
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                response = requests.post(
                    f"{BACKEND_URL}/upload", files=files, timeout=30
                )

                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Upload failed: {error_detail}")
                    st.stop()

                result = response.json()
                st.success(f"✅ Uploaded: **{result['filename']}**")

            except requests.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )
                st.stop()
            except Exception as e:
                st.error(f"❌ Upload error: {str(e)}")
                st.stop()

        # Step 2: Process
        with st.spinner("⚙️ Processing — parsing, chunking, embedding... This may take a moment."):
            try:
                proc_response = requests.post(
                    f"{BACKEND_URL}/process/{uploaded_file.name}",
                    timeout=120,
                )

                if proc_response.status_code == 200:
                    proc_data = proc_response.json()

                    st.success("✅ Document processed successfully!")
                    st.markdown(
                        f"""
                        <div class="process-result">
                            <div class="process-stat">
                                <div class="process-stat-value">{proc_data['total_pages']}</div>
                                <div class="process-stat-label">Pages</div>
                            </div>
                            <div class="process-stat">
                                <div class="process-stat-value">{proc_data['total_chunks']}</div>
                                <div class="process-stat-label">Chunks</div>
                            </div>
                            <div class="process-stat">
                                <div class="process-stat-value">{proc_data['embeddings_stored']}</div>
                                <div class="process-stat-label">Embeddings</div>
                            </div>
                            <div class="process-stat">
                                <div class="process-stat-value">{proc_data['processing_time_seconds']:.1f}s</div>
                                <div class="process-stat-label">Time</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Track processed files
                    if uploaded_file.name not in st.session_state.processed_files:
                        st.session_state.processed_files.append(uploaded_file.name)
                else:
                    error_detail = proc_response.json().get("detail", "Unknown error")
                    st.error(f"❌ Processing failed: {error_detail}")

            except requests.ConnectionError:
                st.error("❌ Lost connection to backend during processing.")
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")

# ==================================================
# Q&A Section
# ==================================================
st.markdown(
    """
    <div class="section-header">
        <div class="section-icon ask">💬</div>
        <div>
            <p class="section-title">Ask a Question</p>
            <p class="section-desc">Query your documents with natural language</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Document selector (multi-doc support) ────────────────────────────
if st.session_state.processed_files:
    doc_options = ["📚 All Documents"] + st.session_state.processed_files
    selected_doc_label = st.selectbox(
        "Search in",
        options=doc_options,
        help="Select a specific document to query, or search across all indexed documents.",
        label_visibility="visible",
    )
    # None means search all; otherwise extract the filename
    selected_filename: str | None = (
        None if selected_doc_label == "📚 All Documents" else selected_doc_label
    )
else:
    selected_filename = None

question = st.text_input(
    "Your question",
    placeholder="e.g. What are the key findings in this document?",
    help="Ask any question about the uploaded and processed documents.",
    label_visibility="collapsed",
)

if question:
    if st.button("🔍 Get Answer", type="primary", use_container_width=True):
        with st.spinner("🧠 Thinking — embedding → retrieving → generating..."):
            try:
                # Build conversation history from session state (newest first, already ordered)
                history_payload = [
                    {"question": h["question"], "answer": h["answer"]}
                    for h in st.session_state.qa_history
                ]

                ask_payload: dict = {
                    "question": question,
                    "filename": selected_filename,
                    "conversation_history": history_payload if history_payload else None,
                }

                ask_response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json=ask_payload,
                    timeout=60,
                )

                if ask_response.status_code == 200:
                    data = ask_response.json()
                    st.session_state.qa_history.insert(0, {
                        "question": question,
                        "answer": data["answer"],
                        "citations": data.get("citations", []),
                        "source_chunks": data.get("source_chunks", []),
                        "model": data.get("model", "grok-3-mini"),
                        "tokens_used": data.get("tokens_used", 0),
                        "processing_time_seconds": data.get("processing_time_seconds", 0.0),
                        "searched_doc": selected_filename or "All Documents",
                    })
                elif ask_response.status_code == 400:
                    error_detail = ask_response.json().get(
                        "detail", "Unknown error"
                    )
                    st.warning(f"⚠️ {error_detail}")
                else:
                    error_detail = ask_response.json().get(
                        "detail", "Unknown error"
                    )
                    st.error(f"❌ Error: {error_detail}")

            except (requests.ConnectionError, requests.Timeout, requests.RequestException, Exception) as e:
                st.error(f"❌ Could not connect or error occurred: {str(e)}")

# ==================================================
# Q&A History Display (Cross-Questioning Loop)
# ==================================================
if st.session_state.qa_history:
    st.markdown("---")
    col_hist_title, col_clear = st.columns([3, 1])
    with col_hist_title:
        st.markdown(
            '<p style="font-size:0.9rem; color:#4f46e5; text-transform:uppercase; '
            'letter-spacing:1px; font-weight:700; margin: 8px 0 0;">💬 Conversation & Cross-Questioning History</p>',
            unsafe_allow_html=True,
        )
    with col_clear:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.qa_history = []
            st.rerun()

    for idx, item in enumerate(st.session_state.qa_history, 1):
        # User Question Banner
        searched_doc = item.get("searched_doc", "All Documents")
        doc_badge = (
            f'<span style="background:rgba(99,102,241,0.1);color:#4f46e5;'
            f'padding:2px 10px;border-radius:12px;font-size:0.72rem;font-weight:600;'
            f'border:1px solid rgba(99,102,241,0.2);margin-left:8px;">📄 {searched_doc}</span>'
        )
        st.markdown(
            f"""
            <div class="user-question-card">
                <span style="font-size:1.3rem;">👤</span>
                <div>
                    <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.8px;">
                        You Asked (Q#{len(st.session_state.qa_history) - idx + 1}){doc_badge}
                    </div>
                    <div style="color:#0f172a; font-weight:600; font-size:1.08rem;">{item['question']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Answer card
        st.markdown(
            """
            <div class="section-header" style="margin-top:0.75rem;">
                <div class="section-icon answer">💡</div>
                <div>
                    <p class="section-title">DocPilot Answer</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="answer-card">{item["answer"]}</div>',
            unsafe_allow_html=True,
        )

        # Citations
        if item.get("citations"):
            st.markdown(
                '<p style="font-size:0.8rem; color:#64748b; '
                'text-transform:uppercase; letter-spacing:0.8px; '
                'font-weight:600; margin:1rem 0 0.5rem;">📖 Sources</p>',
                unsafe_allow_html=True,
            )
            citation_html = ""
            seen_pages = set()
            for cite in item["citations"]:
                for page in cite["page_numbers"]:
                    if page not in seen_pages:
                        seen_pages.add(page)
                        citation_html += (
                            f'<span class="citation-tag">'
                            f'📄 Page {page} — {cite["source_file"]}'
                            f'</span>'
                        )
            st.markdown(citation_html, unsafe_allow_html=True)

        # Source chunks inside Expander
        if item.get("source_chunks"):
            st.markdown(
                '<p style="font-size:0.8rem; color:#64748b; '
                'text-transform:uppercase; letter-spacing:0.8px; '
                'font-weight:600; margin:1.25rem 0 0.5rem;">📑 Source Chunks</p>',
                unsafe_allow_html=True,
            )
            for i, chunk in enumerate(item["source_chunks"], 1):
                pages_str = ", ".join(
                    str(p) for p in chunk["page_numbers"]
                )
                similarity = chunk["similarity_score"]
                with st.expander(
                    f"Chunk {i}  ·  Pages {pages_str}  ·  "
                    f"Match: {similarity:.0%}"
                ):
                    st.markdown(f'<div style="color:#0f172a; line-height:1.7;">{chunk["text_preview"]}</div>', unsafe_allow_html=True)
                    st.caption(
                        f"Source: {chunk['source_file']}  |  "
                        f"ID: {chunk['chunk_id']}"
                    )

        # Stats bar
        st.markdown(
            f"""
            <div class="stats-bar" style="margin-bottom: 2rem;">
                <div class="stat-item">
                    🤖 <span class="stat-value">{item['model']}</span>
                </div>
                <div class="stat-item">
                    🔤 <span class="stat-value">{item['tokens_used']}</span> tokens
                </div>
                <div class="stat-item">
                    ⚡ <span class="stat-value">{item['processing_time_seconds']:.1f}s</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
