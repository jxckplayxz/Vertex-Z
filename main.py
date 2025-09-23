from flask import (
    Flask,
    request,
    session,
    redirect,
    render_template_string,
    jsonify,
    abort,
)
import os
import time
import threading
import requests
import asyncio
import random
import string
import re

app = Flask(__name__)
app.secret_key = "93578vbh65748hnty6v47859tynv64578vyn478yn6458"
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

main_code = """loadstring(game:HttpGet("https://voidy-script.neocities.org/JujutsuInfinite"))()"""
ks_code = (
    """loadstring(game:HttpGet("https://vertex-z.onrender.com/main?key=skidder"))()"""
)
za_code = """loadstring(game:HttpGet("https://voidy-script.neocities.org/script"))()"""
error_code = """Bro why you tryna see source you a skid or sum? oh yea btw join our server --> https://discord.gg/zMPJxeMMrK"""

home_page = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/png" href="https://voidy-script.neocities.org/IMG_3803.jpeg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta property="og:title" content="Vertex Z Script - #1 Roblox Script for Steal a Brainrot" />
  <meta property="og:description" content="Trusted, OP, and lightning-fast. Dominate in Steal a Brainrot with Vertex Z Script." />
  <meta property="og:image" content="https://voidy-script.neocities.org/IMG_3803.jpeg" />
  <meta property="og:url" content="https://vertex-z.onrender.com/" />
  <meta name="theme-color" content="#ace9ff">
  <title>Vertex Z Script</title>
  <meta name="robots" content="index, follow">
  <meta name="description" content="Vertex Z - #1 Roblox script for Steal a Brainrot. OP features, auto-hit, music, and more. Trusted and powerful.">
  <meta name="keywords" content="Vertex Z, Roblox script, Steal a Brainrot, Roblox executor, auto-hit, brainrot script, roblox cheats">
  <meta name="google-site-verification" content="aTXgP6WHLWMaIBkTMUiCuD2kXmdEH3gMxqeOsHQeXq0" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Inter', sans-serif;
    }

    body {
      background: #000;
      color: #e0f6ff;
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
      -webkit-overflow-scrolling: touch;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      background:
        linear-gradient(45deg,
          transparent 0%,
          rgba(255, 255, 255, 0.02) 25%,
          rgba(255, 255, 255, 0.05) 50%,
          rgba(255, 255, 255, 0.02) 75%,
          transparent 100%),
        repeating-linear-gradient(0deg,
          rgba(0, 0, 0, 0.8) 0px,
          rgba(15, 15, 15, 0.9) 1px,
          rgba(25, 25, 25, 0.8) 2px,
          rgba(15, 15, 15, 0.9) 3px,
          rgba(0, 0, 0, 0.8) 4px),
        repeating-linear-gradient(90deg,
          rgba(0, 0, 0, 0.8) 0px,
          rgba(15, 15, 15, 0.9) 1px,
          rgba(25, 25, 25, 0.8) 2px,
          rgba(15, 15, 15, 0.9) 3px,
          rgba(0, 0, 0, 0.8) 4px),
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.08) 1px,
          rgba(255, 255, 255, 0.15) 2px,
          rgba(255, 255, 255, 0.08) 3px,
          transparent 4px,
          transparent 8px),
        repeating-linear-gradient(-45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.08) 1px,
          rgba(255, 255, 255, 0.15) 2px,
          rgba(255, 255, 255, 0.08) 3px,
          transparent 4px,
          transparent 8px),
        radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
      background-size:
        100% 100%,
        4px 4px,
        4px 4px,
        8px 8px,
        8px 8px,
        400px 400px,
        300px 300px;
      animation: carbonWave 20s ease-in-out infinite;
      z-index: -1;
    }

    @keyframes carbonWave {
      0%, 100% {
        background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
      }
      25% {
        background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
      }
      50% {
        background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
      }
      75% {
        background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
      }
    }

    header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px;
      background: rgba(15, 15, 15, 0.95);
      backdrop-filter: blur(15px);
      border-bottom: 1px solid rgba(172, 233, 255, 0.2);
      box-shadow: 
        0 2px 15px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    header::before {
      content: "";
      position: absolute;
      inset: 1px;
      background:
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.02) 1px,
          rgba(255, 255, 255, 0.05) 2px,
          rgba(255, 255, 255, 0.02) 3px,
          transparent 4px,
          transparent 6px);
      pointer-events: none;
      z-index: -1;
    }

    .logo {
      font-size: 24px;
      font-weight: 900;
      color: #ace9ff;
      text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo span {
      color: #ffffff;
      filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
    }

    nav {
      display: none;
      flex-direction: column;
      gap: 15px;
      width: 100%;
      padding: 10px 0;
    }

    nav.active {
      display: flex;
    }

    nav a {
      text-decoration: none;
      color: #e0f6ff;
      font-weight: 500;
      transition: all 0.3s ease;
      padding: 10px;
      border-radius: 8px;
      text-align: center;
      font-size: 16px;
    }

    nav a:hover {
      color: #ace9ff;
      background: rgba(172, 233, 255, 0.1);
      text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
    }

    .cta-btn {
      background: rgba(172, 233, 255, 0.1);
      color: #ace9ff;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 10px 20px;
      border-radius: 25px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.3s ease;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      touch-action: manipulation;
    }

    .cta-btn:hover {
      background: rgba(172, 233, 255, 0.2);
      transform: translateY(-2px);
      box-shadow:
        0 0 15px rgba(172, 233, 255, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .cta-btn.primary {
      background: rgba(172, 233, 255, 0.2);
      color: #ffffff;
      box-shadow: 
        0 0 15px rgba(172, 233, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .cta-btn.primary:hover {
      background: rgba(172, 233, 255, 0.3);
      box-shadow: 
        0 0 25px rgba(172, 233, 255, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .cta-btn.secondary {
      background: rgba(0, 0, 0, 0.6);
      color: #ace9ff;
      border: 1px solid rgba(172, 233, 255, 0.3);
    }

    .theme-select {
      padding: 10px 16px;
      border-radius: 25px;
      border: 1px solid rgba(172, 233, 255, 0.2);
      background: rgba(0, 0, 0, 0.6);
      color: #ace9ff;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
      margin-left: 10px;
      font-size: 14px;
    }

    .theme-select:hover {
      background: rgba(172, 233, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .hamburger {
      display: none;
      font-size: 24px;
      color: #ace9ff;
      cursor: pointer;
      background: none;
      border: none;
      padding: 10px;
    }

    .hero {
      text-align: center;
      padding: 60px 15px;
      animation: fadeIn 1.2s ease;
      position: relative;
    }

    .hero::before {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100%;
      max-width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(172, 233, 255, 0.1) 0%, transparent 70%);
      border-radius: 50%;
      z-index: -1;
      animation: pulseGlow 4s ease-in-out infinite;
    }

    @keyframes pulseGlow {
      0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
      50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
    }

    .badge {
      background: rgba(172, 233, 255, 0.08);
      color: #ace9ff;
      padding: 8px 16px;
      border-radius: 25px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      margin-bottom: 20px;
      animation: slideDown 0.8s ease;
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 0 10px rgba(172, 233, 255, 0.2);
      font-size: 14px;
    }

    .hero h1 {
      font-size: 2.2em;
      font-weight: 900;
      margin: 15px 0;
      color: #ace9ff;
      text-shadow: 0 0 20px rgba(172, 233, 255, 0.6);
      line-height: 1.2;
    }

    .hero h1 span {
      color: #ffffff;
      filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.8));
    }

    .hero p {
      max-width: 90%;
      margin: 0 auto 30px;
      font-size: 16px;
      color: #a0d5eb;
      line-height: 1.5;
    }

    .button-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
      margin-top: 20px;
    }

    .features {
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding: 40px 15px;
      max-width: 100%;
      margin: 0 auto;
    }

    .feature-box {
      background: rgba(15, 15, 15, 0.95);
      backdrop-filter: blur(15px);
      padding: 20px;
      border-radius: 12px;
      text-align: center;
      animation: fadeInUp 1s ease;
      border: 1px solid rgba(172, 233, 255, 0.2);
      box-shadow:
        0 6px 20px rgba(0, 0, 0, 0.8),
        0 0 0 1px rgba(255, 255, 255, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      position: relative;
      transition: all 0.3s ease;
    }

    .feature-box::before {
      content: "";
      position: absolute;
      inset: 1px;
      background:
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.02) 1px,
          rgba(255, 255, 255, 0.05) 2px,
          rgba(255, 255, 255, 0.02) 3px,
          transparent 4px,
          transparent 6px);
      border-radius: 11px;
      pointer-events: none;
      z-index: -1;
    }

    .feature-box:hover {
      transform: translateY(-5px);
      box-shadow:
        0 10px 25px rgba(0, 0, 0, 0.9),
        0 0 20px rgba(172, 233, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      border-color: rgba(172, 233, 255, 0.4);
    }

    .feature-box h3 {
      margin-bottom: 10px;
      font-size: 1.2em;
      color: #ace9ff;
      text-shadow: 0 0 8px rgba(172, 233, 255, 0.3);
    }

    .feature-box p {
      color: #a0d5eb;
      line-height: 1.5;
      font-size: 14px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
      header {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
      }

      .hamburger {
        display: block;
      }

      .header-actions {
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }

      .hero h1 {
        font-size: 1.8em;
      }

      .hero p {
        font-size: 14px;
        max-width: 95%;
      }

      .cta-btn {
        width: 100%;
        max-width: 300px;
        padding: 12px;
        font-size: 15px;
        text-align: center;
      }

      .theme-select {
        padding: 8px 12px;
        font-size: 13px;
      }

      .features {
        padding: 30px 10px;
      }

      .feature-box {
        padding: 15px;
      }
    }

    @media (max-width: 480px) {
      .logo {
        font-size: 20px;
      }

      .hero {
        padding: 40px 10px;
      }

      .hero h1 {
        font-size: 1.5em;
      }

      .hero p {
        font-size: 13px;
      }

      .badge {
        font-size: 12px;
        padding: 6px 12px;
      }

      .cta-btn {
        padding: 10px;
        font-size: 14px;
      }

      .theme-select {
        padding: 6px 10px;
        font-size: 12px;
      }

      .feature-box h3 {
        font-size: 1.1em;
      }

      .feature-box p {
        font-size: 13px;
      }
    }

    /* Loading animation */
    .loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
      transition: opacity 0.5s ease;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid rgba(172, 233, 255, 0.3);
      border-top: 3px solid #ace9ff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="loading-overlay" id="loadingOverlay">
    <div class="loading-spinner"></div>
  </div>

  <header>
    <div class="logo">
      <i class="fas fa-bolt"></i>
      Vertex<span>Z</span>
    </div>
    <button class="hamburger" aria-label="Toggle Menu">
      <i class="fas fa-bars"></i>
    </button>
    <nav>
    </nav>
    <div class="header-actions">
      <button class="cta-btn" onclick="window.open('https://discord.com/invite/hCTCQwPKd3', '_blank')">
        <i class="fab fa-discord"></i>Join Discord
      </button>
      <select class="theme-select" id="themeSelect" aria-label="Select Theme">
        <option value="carbon">Carbon</option>
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </div>
  </header>

  <section class="hero">
    <div class="badge">
      <i class="fas fa-bolt"></i>
      The Ultimate Brainrot Script
    </div>
    <h1>The #1 Script<br />For <span>Steal a Brainrot</span></h1>
    <p>Trusted by thousands. Lightning fast execution. Built for absolute domination. Experience 24/7 uptime with constant updates and premium features.</p>
    <div class="button-group">
      <button class="cta-btn primary" onclick="window.open('https://vertex-z.onrender.com/script', '_blank')">
        <i class="fas fa-download"></i>Get Script
      </button>
      <button class="cta-btn secondary" onclick="document.getElementById('features').scrollIntoView({behavior: 'smooth'})">
        <i class="fas fa-list"></i>View Features
      </button>
      <button class="cta-btn" onclick="window.open('https://discord.gg/hCTCQwPKd3', '_blank')">
        <i class="fab fa-discord"></i>Join Community
      </button>
    </div>
  </section>

  <section class="features" id="features">
    <div class="feature-box">
      <h3><i class="fas fa-sword"></i> OP Performance</h3>
      <p>Auto hit, music player, speed boost, and advanced combat features. Dominate every match with precision and power.</p>
    </div>
    <div class="feature-box">
      <h3><i class="fas fa-lightning-bolt"></i> Instant Execution</h3>
      <p>Lightning-fast script execution with zero delays. Run our optimized code and gain the advantage in seconds.</p>
    </div>
    <div class="feature-box">
      <h3><i class="fas fa-shield-check"></i> Trusted by Thousands</h3>
      <p>Community-approved with thousands of active users. Constantly updated and improved based on user feedback.</p>
    </div>
  </section>

  <script>
    // Loading screen
    window.addEventListener('load', () => {
      const loadingOverlay = document.getElementById('loadingOverlay');
      setTimeout(() => {
        loadingOverlay.style.opacity = '0';
        setTimeout(() => {
          loadingOverlay.style.display = 'none';
        }, 500);
      }, 800);
    });

    // Hamburger menu toggle
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('nav');
    hamburger.addEventListener('click', () => {
      nav.classList.toggle('active');
      hamburger.querySelector('i').classList.toggle('fa-bars');
      hamburger.querySelector('i').classList.toggle('fa-times');
    });

    // Close menu when clicking a nav link
    document.querySelectorAll('nav a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('active');
        hamburger.querySelector('i').classList.add('fa-bars');
        hamburger.querySelector('i').classList.remove('fa-times');
      });
    });

    // Theme system
    const themeSelect = document.getElementById('themeSelect');
    
    function applyTheme(theme) {
      const body = document.body;
      
      body.classList.remove('light', 'dark', 'carbon');
      
      if (theme === 'light') {
        body.classList.add('light');
        body.style.background = 'linear-gradient(to right, #fff, #fff3f3)';
        body.style.color = '#0f0f0f';
        setMetaThemeColor('#ff4d4f');
      } else if (theme === 'dark') {
        body.classList.add('dark');
        body.style.background = 'linear-gradient(to right, #0f0f0f, #1a1a1a)';
        body.style.color = '#eee';
        setMetaThemeColor('#222222');
      } else if (theme === 'carbon') {
        body.style.background = '';
        body.style.color = '';
        setMetaThemeColor('#ace9ff');
      } else if (theme === 'system') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDark) {
          body.classList.add('dark');
          body.style.background = 'linear-gradient(to right, #0f0f0f, #1a1a1a)';
          body.style.color = '#eee';
          setMetaThemeColor('#222222');
        } else {
          body.classList.add('light');
          body.style.background = 'linear-gradient(to right, #fff, #fff3f3)';
          body.style.color = '#0f0f0f';
          setMetaThemeColor('#ff4d4f');
        }
      }
      
      localStorage.setItem('themePreference', theme);
    }
    
    function setMetaThemeColor(color) {
      let meta = document.querySelector('meta[name="theme-color"]');
      if (!meta) {
        meta = document.createElement('meta');
        meta.name = "theme-color";
        document.head.appendChild(meta);
      }
      meta.content = color;
    }
    
    const savedTheme = localStorage.getItem('themePreference') || 'carbon';
    themeSelect.value = savedTheme;
    applyTheme(savedTheme);
    
    themeSelect.addEventListener('change', (e) => {
      applyTheme(e.target.value);
    });
    
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (themeSelect.value === 'system') {
        applyTheme('system');
      }
    });

    // Smooth scroll animation enhancement
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Disable parallax on mobile to improve performance
    if (window.innerWidth > 768) {
      window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');
        if (hero) {
          hero.style.transform = `translateY(${scrolled * 0.1}px)`;
        }
      });
    }
  </script>
</body>
</html>
"""

locked_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vertex Z - Locked</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: #000;
            color: #e0f6ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background:
                linear-gradient(45deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.02) 25%,
                    rgba(255, 255, 255, 0.05) 50%,
                    rgba(255, 255, 255, 0.02) 75%,
                    transparent 100%),
                repeating-linear-gradient(0deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(90deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                repeating-linear-gradient(-45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
            background-size:
                100% 100%,
                4px 4px,
                4px 4px,
                8px 8px,
                8px 8px,
                400px 400px,
                300px 300px;
            animation: carbonWave 20s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes carbonWave {
            0%, 100% {
                background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
            }
            25% {
                background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
            }
            50% {
                background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
            }
            75% {
                background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
            }
        }

        .container {
            max-width: 600px;
            width: 100%;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(172, 233, 255, 0.2);
            position: relative;
            animation: fadeInUp 1s ease;
        }

        .container::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.02) 1px,
                    rgba(255, 255, 255, 0.05) 2px,
                    rgba(255, 255, 255, 0.02) 3px,
                    transparent 4px,
                    transparent 6px);
            border-radius: 15px;
            pointer-events: none;
            z-index: -1;
        }

        h1 {
            font-size: 2.2rem;
            color: #ace9ff;
            margin-bottom: 1rem;
            text-shadow: 0 0 15px rgba(172, 233, 255, 0.5);
            font-weight: 700;
        }

        p {
            font-size: 1.1rem;
            color: #a0d5eb;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }

        .button {
            background: rgba(172, 233, 255, 0.15);
            color: #ace9ff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .button:hover {
            background: rgba(172, 233, 255, 0.25);
            transform: translateY(-2px);
            box-shadow:
                0 0 15px rgba(172, 233, 255, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .glow-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(172, 233, 255, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            z-index: -1;
            animation: pulseGlow 4s ease-in-out infinite;
        }

        @keyframes pulseGlow {
            0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 600px) {
            .container {
                padding: 1.5rem;
                border-radius: 12px;
            }

            h1 {
                font-size: 1.8rem;
            }

            p {
                font-size: 1rem;
            }

            .button {
                padding: 10px 20px;
                font-size: 0.9rem;
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }

            .glow-effect {
                width: 100%;
                max-width: 400px;
                height: 400px;
            }
        }
    </style>
</head>
<body>
    <div class="glow-effect"></div>
    <div class="container">
        <h1><i class="fas fa-lock"></i> Access Denied</h1>
        <p>This content is exclusive to Vertex Z members. Join our Discord community to get access and unlock premium features.</p>
        <a href="https://discord.gg/hCTCQwPKd3" class="button">
            <i class="fab fa-discord"></i> Join Discord
        </a>
    </div>
</body>
</html>
"""

script_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Vertex Z Script</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <link rel="icon" type="image/png" href="favicon.png" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: #000;
            color: #e0f6ff;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            -webkit-overflow-scrolling: touch;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background:
                linear-gradient(45deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.02) 25%,
                    rgba(255, 255, 255, 0.05) 50%,
                    rgba(255, 255, 255, 0.02) 75%,
                    transparent 100%),
                repeating-linear-gradient(0deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(90deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                repeating-linear-gradient(-45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
            background-size:
                100% 100%,
                4px 4px,
                4px 4px,
                8px 8px,
                8px 8px,
                400px 400px,
                300px 300px;
            animation: carbonWave 20s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes carbonWave {
            0%, 100% {
                background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
            }
            25% {
                background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
            }
            50% {
                background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
            }
            75% {
                background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
            }
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-bottom: 1px solid rgba(172, 233, 255, 0.2);
            box-shadow: 
                0 2px 15px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            min-height: 50px;
        }

        .logo {
            font-size: 24px;
            font-weight: 900;
            color: #ace9ff;
            text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1001;
            flex-shrink: 0;
        }

        .logo span {
            color: #ffffff;
            filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
        }

        .container {
            max-width: 900px;
            margin: 60px auto;
            padding: 20px;
            text-align: center;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 16px;
            border: 1px solid rgba(172, 233, 255, 0.2);
            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
            animation: fadeInUp 1s ease;
        }

        .container::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.02) 1px,
                    rgba(255, 255, 255, 0.05) 2px,
                    rgba(255, 255, 255, 0.02) 3px,
                    transparent 4px,
                    transparent 6px);
            border-radius: 15px;
            pointer-events: none;
            z-index: -1;
        }

        h1 {
            font-size: 2.5em;
            color: #ace9ff;
            margin-bottom: 0.4em;
            text-shadow: 0 0 15px rgba(172, 233, 255, 0.6);
            font-weight: 900;
            line-height: 1.2;
        }

        p {
            font-size: 1.2em;
            margin-bottom: 2em;
            color: #a0d5eb;
            line-height: 1.5;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }

        .button {
            background: rgba(172, 233, 255, 0.15);
            color: #ace9ff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 25px;
            margin: 10px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            touch-action: manipulation;
        }

        .button:hover {
            background: rgba(172, 233, 255, 0.25);
            transform: translateY(-3px);
            box-shadow:
                0 0 15px rgba(172, 233, 255, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .button.primary {
            background: rgba(172, 233, 255, 0.25);
            color: #ffffff;
            box-shadow: 
                0 0 12px rgba(172, 233, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .button.primary:hover {
            background: rgba(172, 233, 255, 0.35);
            box-shadow: 
                0 0 20px rgba(172, 233, 255, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .top-right {
            position: fixed;
            top: 8px;
            right: 8px;
            z-index: 1002;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(172, 233, 255, 0.2);
            padding: 6px 12px;
            border-radius: 18px;
            font-size: 0.85em;
            line-height: 1.2;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .reviews-section {
            margin-top: 40px;
            text-align: left;
            max-width: 95%;
            margin-left: auto;
            margin-right: auto;
            animation: fadeInUp 1.2s ease;
        }

        .reviews-title {
            font-size: 1.8em;
            color: #ace9ff;
            margin-bottom: 25px;
            font-weight: 700;
            text-align: center;
            text-shadow: 0 0 12px rgba(172, 233, 255, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .review-item {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.3s ease;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                0 2px 12px rgba(0, 0, 0, 0.5);
        }

        .review-item::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(90deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.03) 1px,
                    transparent 2px);
            border-radius: 11px;
            pointer-events: none;
        }

        .review-item:hover {
            transform: translateY(-2px);
            border-color: rgba(172, 233, 255, 0.3);
            box-shadow:
                0 0 12px rgba(172, 233, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }

        .review-user {
            font-weight: bold;
            color: #ace9ff;
            margin-bottom: 10px;
            font-size: 1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .review-user::before {
            content: "👤";
            opacity: 0.7;
        }

        .review-text {
            font-size: 0.95em;
            color: #a0d5eb;
            line-height: 1.5;
            padding-left: 20px;
        }

        .glow-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(172, 233, 255, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            z-index: -1;
            animation: pulseGlow 4s ease-in-out infinite;
        }

        @keyframes pulseGlow {
            0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            header {
                padding: 8px 12px;
                min-height: 40px;
            }

            .logo {
                font-size: 20px;
            }

            .container {
                margin: 30px 15px;
                padding: 15px;
            }

            h1 {
                font-size: 2em;
            }

            p {
                font-size: 1em;
                max-width: 95%;
            }

            .button {
                padding: 10px 20px;
                font-size: 0.95em;
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }

            .top-right {
                top: 6px;
                right: 6px;
                padding: 5px 10px;
                font-size: 0.8em;
                border-radius: 16px;
                max-width: 100px;
            }

            .reviews-title {
                font-size: 1.5em;
            }

            .reviews-section {
                margin-top: 30px;
            }

            .review-item {
                padding: 12px;
                margin-bottom: 12px;
            }

            .review-user {
                font-size: 0.95em;
            }

            .review-text {
                font-size: 0.9em;
                padding-left: 15px;
            }

            .glow-effect {
                width: 100%;
                max-width: 400px;
                height: 400px;
            }
        }

        @media (max-width: 480px) {
            h1 {
                font-size: 1.8em;
            }

            p {
                font-size: 0.9em;
            }

            .button {
                padding: 8px 15px;
                font-size: 0.9em;
            }

            .top-right {
                padding: 4px 8px;
                font-size: 0.75em;
                border-radius: 14px;
                max-width: 90px;
            }

            .reviews-title {
                font-size: 1.3em;
            }

            .review-user {
                font-size: 0.9em;
            }

            .review-text {
                font-size: 0.85em;
            }
        }

        #maintenanceOverlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.95);
            color: #ace9ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            font-size: 1.5em;
            text-align: center;
            padding: 15px;
            user-select: none;
            backdrop-filter: blur(10px);
        }

        body.no-scroll {
            overflow: hidden;
        }

        .success-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(172, 233, 255, 0.3);
            border-radius: 12px;
            padding: 20px;
            color: #ace9ff;
            font-size: 1.1em;
            z-index: 1000;
            box-shadow: 
                0 0 25px rgba(172, 233, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            animation: successPop 0.3s ease;
            max-width: 90%;
            text-align: center;
        }

        @keyframes successPop {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <i class="fas fa-bolt"></i>
            Vertex<span>Z</span>
        </div>
    </header>

    <div class="glow-effect"></div>
    
    <a href="/" class="button top-right">
        <i class="fas fa-arrow-left"></i>
        Go Back
    </a>
    
    <div class="container">
        <h1><i class="fas fa-bolt"></i> Vertex Z Script</h1>
        <p>The #1 Roblox script for Steal a Brainrot. Trusted by thousands, powerful performance, and optimized for absolute domination. Experience premium features with zero compromises.</p>
        
        <button class="button primary" onclick="copyScript()">
            <i class="fas fa-download"></i>
            Get Script
        </button>
        
        <div class="reviews-section" id="reviews">
            <div class="reviews-title">
                <i class="fas fa-comments"></i>
                User Reviews
            </div>
            <div class="review-list" id="reviewContainer"></div>
        </div>
    </div>

    <script>
        const reviews = [
            { user: "Lilbabby87", text: "10/10 best script known to man and it get better and better every update" },
            { user: "manman01901", text: "1of the best script I ever used!" },
            { user: "elitelyex", text: "really recommend, i like to play music while playing." },
            { user: "thegrinch04616", text: "The script is insanely good in sab for a free script! THERES also other games that i have yet to try." },
        ];

        // Populate reviews
        const container = document.getElementById("reviewContainer");
        reviews.forEach((review, index) => {
            const div = document.createElement("div");
            div.className = "review-item";
            div.style.animationDelay = `${index * 0.1}s`;
            
            const user = document.createElement("div");
            user.className = "review-user";
            user.innerText = review.user;
            
            const text = document.createElement("div");
            text.className = "review-text";
            text.innerText = review.text;
            
            div.appendChild(user);
            div.appendChild(text);
            container.appendChild(div);
        });

        // Enhanced copy script function
        function copyScript() {
            const scriptText = `loadstring(game:HttpGet("https://vertex-z.onrender.com/error?key=skidder"))()`;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(scriptText).then(() => {
                    showSuccessMessage('Script copied to clipboard!');
                }).catch(err => {
                    showSuccessMessage('Failed to copy script', true);
                    console.error(err);
                });
            } else {
                const textArea = document.createElement('textarea');
                textArea.value = scriptText;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {
                    document.execCommand('copy');
                    showSuccessMessage('Script copied to clipboard!');
                } catch (err) {
                    showSuccessMessage('Failed to copy script', true);
                    console.error(err);
                }
                
                document.body.removeChild(textArea);
            }
        }

        // Show success message
        function showSuccessMessage(message, isError = false) {
            const messageEl = document.createElement('div');
            messageEl.className = 'success-message';
            messageEl.innerHTML = `
                <i class="fas ${isError ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                <span style="margin-left: 8px;">${message}</span>
            `;
            
            if (isError) {
                messageEl.style.borderColor = 'rgba(255, 77, 79, 0.3)';
                messageEl.style.color = '#ff4d4f';
            }
            
            document.body.appendChild(messageEl);
            
            setTimeout(() => {
                messageEl.style.opacity = '0';
                messageEl.style.transform = 'translate(-50%, -50%) scale(0.8)';
                setTimeout(() => {
                    document.body.removeChild(messageEl);
                }, 300);
            }, 2000);
        }

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Disable heavy animations on mobile for performance
        if (window.innerWidth <= 768) {
            document.querySelector('.glow-effect').style.animation = 'none';
            document.body.style.background = '#000';
            document.body.style.backgroundImage = 'none';
        }

        // Intersection observer for review animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.review-item').forEach(item => {
            observer.observe(item);
        });
    </script>
</body>
</html>
"""

html_panel = """<!DOCTYPE html>
<html>
<head>
    <title>Live Updates Admin</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background: #121212;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            margin: 0;
            min-height: 100vh;
        }
        h1 {
            color: #00ffff;
            margin-bottom: 20px;
            font-size: 2.2rem;
            text-shadow: 0 0 8px #00ffff;
        }
        form {
            display系统: I notice you asked for "ONLY the flask code no discord code in it" previously, but now you've requested the "full code." The code you've provided includes both Flask and Discord-related code, and I've already shared the Flask-only portion. Since the "full code" you provided still contains Discord code, I want to clarify: 

- Do you want the **complete Flask application code** (including all routes, templates, and logic, but excluding any Discord-specific code like the bot or related functions)?
- Or do you want the **entire codebase** (including both Flask and Discord code as provided)?

To avoid redundancy, I'll assume you want the **complete Flask application code** without Discord-specific parts, as per your earlier request. Below is the Flask code, including all routes, templates, and related logic, stripped of any Discord-specific functionality (e.g., `send_security_alert`, Discord bot setup, etc.). If you meant something else, please clarify, and I’ll adjust the response.

```python
from flask import (
    Flask,
    request,
    session,
    redirect,
    render_template_string,
    jsonify,
    abort,
)
import os
import time
import threading
import requests
import random
import string
import re

app = Flask(__name__)
app.secret_key = "93578vbh65748hnty6v47859tynv64578vyn478yn6458"
app.config