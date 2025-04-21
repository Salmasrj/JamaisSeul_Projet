import streamlit as st
import base64
from pathlib import Path
import pandas as pd
import time
import os

# Page configuration
st.set_page_config(
    page_title="Les Saisons des Anciens | Course Jamais Seul",
    page_icon="assets/images/logo-icone.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = "accueil"

# Custom CSS with the correct colors and fonts
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
<style>
    
    /* Import custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    @font-face {
        font-family: 'Bogart';
        src: url('https://your-hosting-location.com/bogart-regular.woff2') format('woff2');
        /* You'll need to host the Bogart font files or use a service that provides them */
        font-weight: normal;
        font-style: normal;
    }
    /* Base styles */
    /* Apply Anton font to all headings */
    h1, h2, h3, h4, h5, h6, .section-title {
        font-family: 'Anton', sans-serif !important;
        letter-spacing: 1px;
    }
    /* Apply Bogart to all body text */
    body, p, div, span, .stMarkdown, .stText {
        font-family: 'Bogart', 'Montserrat', sans-serif !important;
    }

    /* Fix for specific Streamlit elements that might not inherit properly */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        font-family: 'Bogart', 'Montserrat', sans-serif !important;
    }
    body {
        font-family: 'Montserrat', sans-serif;
        color: #2b545f;
        background-color: #f0f5f9; /* New background color - light blue-gray */
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .main > .block-container {
        padding-top: 1rem !important;
        max-width: 1200px;
        background-color: #2b545f;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 20px;
        margin: 60px auto 20px auto;
    }
    
    h1, h2, h3, h4, h5 {
        color: #34a0a2;
        font-weight: 600;
    }
    
    /* Navigation */
    .nav-container {
        background-color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    
    .logo-title {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-title h1 {
        margin: 0;
        font-size: 24px;
    }
    
    .nav-links {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .nav-link {
        color: #2b545f;
        padding: 8px 15px;
        margin: 0 5px;
        text-decoration: none;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        background-color: #e7f4e7;
        color: #34a0a2;
    }
    
    .nav-link.active {
        background-color: #34a0a2;
        color: white;
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #34a0a2 0%, #2b545f 100%);
        color: white;
        padding: 60px 40px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 40px;
    }
    
    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    
    .hero p {
        font-size: 1.2rem;
        max-width: 700px;
        margin: 0 auto 30px auto;
        opacity: 0.9;
    }
    
    /* Content Sections */
    .section {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .section-title {
        color: #34a0a2;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e7f4e7;
    }
    
    /* Buttons */
    .cta-button {
        background-color: #ffd600;
        color: #2b545f;
        padding: 12px 30px;
        border-radius: 50px;
        font-weight: 600;
        display: inline-block;
        text-decoration: none;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .cta-button:hover {
        background-color: #e6c200;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Cards */
    .card {
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .card-content {
        padding: 20px;
    }
    
    .card h3 {
        margin-top: 0;
    }
    
    /* Stats */
    .stat-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-between;
        margin-bottom: 30px;
    }
    
    .stat-item {
        background-color: #34a0a2;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        flex: 1;
        min-width: 200px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Quote */
    .quote {
        font-style: italic;
        padding: 30px;
        text-align: center;
        font-size: 1.3rem;
        color: #2b545f;
        position: relative;
    }
    
    .quote::before, .quote::after {
        content: '"';
        font-size: 3rem;
        position: absolute;
        color: #e7f4e7;
    }
    
    .quote::before {
        top: 0;
        left: 10px;
    }
    
    .quote::after {
        bottom: -30px;
        right: 10px;
    }
    
    /* Events */
    .event-card {
        display: flex;
        margin-bottom: 15px;
        background-color: #f9f9f9;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .event-date {
        background-color: #34a0a2;
        color: white;
        padding: 15px;
        text-align: center;
        min-width: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .event-content {
        padding: 15px;
        flex-grow: 1;
    }
    
    /* Testimonials */
    .testimonial {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .testimonial p {
        font-style: italic;
    }
    
    .testimonial-author {
        font-weight: 600;
        color: #34a0a2;
        margin-top: 10px;
    }
    
    /* Newsletter */
    .newsletter {
        background: linear-gradient(135deg, #34a0a2 0%, #2b545f 100%);
        padding: 40px;
        border-radius: 10px;
        color: white;
        margin: 40px 0;
    }
    
    /* Footer */
    .footer {
        background-color: #2b545f;
        color: white;
        padding: 40px 0 20px 0;
        margin-top: 60px;
        border-radius: 10px;
    }
    
    .footer-section {
        margin-bottom: 20px;
    }
    
    .footer-title {
        color: white;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .footer-link {
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
    
    .footer-link:hover {
        color: white;
    }
    
    .social-links {
        display: flex;
        margin-top: 15px;
        gap: 10px;
    }
    
    .social-link {
        width: 36px;
        height: 36px;
        background-color: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-decoration: none;
        font-size: 18px;
    }
    
    .social-link:hover {
        background-color: #ffd600;
        color: #2b545f;
    }
    
    .copyright {
        text-align: center;
        padding-top: 20px;
        margin-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.2);
        color: rgba(255,255,255,0.6);
    }
    
    /* Contact form styling */
    .contact-form input, 
    .contact-form textarea {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    
    .contact-form textarea {
        min-height: 120px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .nav-container {
            flex-direction: column;
            align-items: center;
        }
        
        .nav-links {
            margin-top: 15px;
            justify-content: center;
        }
        
        .hero {
            padding: 40px 20px;
        }
        
        .hero h1 {
            font-size: 2rem;
        }
    }
    .partners-container {
        overflow-x: auto;
        white-space: nowrap;
        padding: 20px 0;
        scrollbar-width: thin;
        scrollbar-color: #34a0a2 #e7f4e7;
    }
    .partners-container::-webkit-scrollbar {
        height: 8px;
    }
    .partners-container::-webkit-scrollbar-track {
        background: #e7f4e7;
        border-radius: 10px;
    }
    .partners-container::-webkit-scrollbar-thumb {
        background-color: #34a0a2;
        border-radius: 10px;
    }
    .partner-logo {
        display: inline-block;
        margin: 0 15px;
        transition: transform 0.3s ease;
    }
    .partner-logo:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Function to convert image to base64
def get_img_as_base64(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: Image not found at {file_path}")
        return None
    
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


# Navigation bar
logo_base64 = get_img_as_base64("assets/images/logo.png")
st.markdown(f"""
<div class="nav-container">
    <div class="logo-title">
        <img src="data:image/png;base64,{logo_base64 or ''}" alt="Logo Les Saisons des Anciens" width="60">
        <h1>Les Saisons des Anciens</h1>
    </div>
    <div class="nav-links">
        <a href="#" class="nav-link active">Accueil</a>
        <a href="#" class="nav-link">Nous rejoindre</a>
        <a href="#" class="nav-link">Qui sommes-nous ?</a>
        <a href="#" class="nav-link">La course Jamais Seul</a>
        <a href="#" class="nav-link">Rejoignez-nous</a>
        <a href="#" class="nav-link">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">
    <h1>Courir ensemble, à tout âge</h1>
    <p>Bienvenue sur le site de l'association "Les Saisons des Anciens". Notre événement phare, la course Jamais Seul, permet aux personnes âgées de participer à une expérience sportive adaptée et conviviale.</p>
    <a href="#" class="cta-button">Découvrir la course</a>
</div>
""", unsafe_allow_html=True)

# Stats section
st.markdown("""
<div class="section">
    <h2 class="section-title">Notre impact</h2>
    <div class="stat-container">
        <div class="stat-item">
            <div class="stat-number">300+</div>
            <div class="stat-label">Participants seniors</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">150</div>
            <div class="stat-label">Bénévoles engagés</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">15</div>
            <div class="stat-label">Années d'expérience</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">20+</div>
            <div class="stat-label">Partenaires</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Qui sommes-nous (formerly Notre mission)
st.markdown("""
<div class="section">
    <h2 class="section-title" id="about">Qui sommes-nous ?</h2>
    <div class="row">
        <p>L'association "Les Saisons des Anciens" a été fondée en 2010 par un groupe de professionnels de la santé et d'amateurs de course à pied, avec une vision commune : créer des opportunités sportives et sociales pour les personnes âgées.</p>
        <p>Notre équipe est composée de bénévoles passionnés, de kinésithérapeutes, de médecins et de professionnels du sport adaptés aux seniors. Ensemble, nous travaillons pour proposer des activités qui maintiennent la forme physique et créent du lien social.</p>
        <p>Notre course annuelle "Jamais Seul" est conçue pour permettre aux seniors de pratiquer une activité physique adaptée tout en créant des liens intergénérationnels. Nous croyons fermement que l'âge ne devrait jamais être un obstacle à la pratique sportive et au maintien d'une vie sociale épanouissante.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Activities section with cards
col1, col2, col3 = st.columns(3)

with col1:
    img_path_course = "assets/images/course.png"
    img_base64_course = get_img_as_base64(img_path_course)
    if img_base64_course:
        st.markdown(f"""
        <div class="card">
            <img src="data:image/png;base64,{img_base64_course}" width="100%">
            <div class="card-content">
                <h3>La course Jamais Seul</h3>
                <p>Notre événement phare annuel qui permet aux seniors de participer à une course adaptée avec le soutien de bénévoles.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <img src="https://via.placeholder.com/400x200?text=Course+Jamais+Seul" width="100%">
            <div class="card-content">
                <h3>La course Jamais Seul</h3>
                <p>Notre événement phare annuel qui permet aux seniors de participer à une course adaptée avec le soutien de bénévoles.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    img_path_ateliers = "assets/images/ateliers.png"
    img_base64_ateliers = get_img_as_base64(img_path_ateliers)
    if img_base64_ateliers:
        st.markdown(f"""
        <div class="card">
            <img src="data:image/png;base64,{img_base64_ateliers}" width="100%">
            <div class="card-content">
                <h3>Ateliers bien-être</h3>
                <p>Des séances hebdomadaires de gymnastique douce, yoga et relaxation spécialement conçues pour les seniors.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <img src="https://via.placeholder.com/400x200?text=Ateliers+Bien-être" width="100%">
            <div class="card-content">
                <h3>Ateliers bien-être</h3>
                <p>Des séances hebdomadaires de gymnastique douce, yoga et relaxation spécialement conçues pour les seniors.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col3:
    img_path_rencontres = "assets/images/rencontres.png"
    img_base64_rencontres = get_img_as_base64(img_path_rencontres)
    if img_base64_rencontres:
        st.markdown(f"""
        <div class="card">
            <img src="data:image/png;base64,{img_base64_rencontres}" width="100%">
            <div class="card-content">
                <h3>Rencontres intergénérationnelles</h3>
                <p>Des événements qui favorisent les échanges et le partage d'expériences entre générations.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <img src="https://via.placeholder.com/400x200?text=Rencontres+Intergénérationnelles" width="100%">
            <div class="card-content">
                <h3>Rencontres intergénérationnelles</h3>
                <p>Des événements qui favorisent les échanges et le partage d'expériences entre générations.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Quote
st.markdown("""
<div style="margin-top: 50px;"></div>
<div class="section">
    <div class="quote">
        L'âge n'est qu'un chiffre. Ce qui compte vraiment, c'est de rester actif, entouré et jamais seul dans sa passion pour la vie.
    </div>
</div>
""", unsafe_allow_html=True)

# Upcoming events
st.markdown("""
<div class="section">
    <h2 class="section-title">Événements à venir</h2>
    <div class="event-card">
        <div class="event-date">
            <div style="font-weight: bold; font-size: 1.5rem;">15</div>
            <div>JUIN</div>
        </div>
        <div class="event-content">
            <h3 style="margin-top: 0;">Course Jamais Seul 2025</h3>
            <p>Notre événement annuel revient pour sa 15ème édition au Parc Municipal. Inscriptions ouvertes!</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">S'inscrire</a>
        </div>
    </div>
    <div class="event-card">
        <div class="event-date">
            <div style="font-weight: bold; font-size: 1.5rem;">28</div>
            <div>MAI</div>
        </div>
        <div class="event-content">
            <h3 style="margin-top: 0;">Atelier préparation physique</h3>
            <p>Séance spéciale pour préparer la course avec nos coaches spécialisés en activité physique adaptée.</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">En savoir plus</a>
        </div>
    </div>
    <div class="event-card">
        <div class="event-date">
            <div style="font-weight: bold; font-size: 1.5rem;">10</div>
            <div>MAI</div>
        </div>
        <div class="event-content">
            <h3 style="margin-top: 0;">Conférence bien-vieillir</h3>
            <p>Intervention de spécialistes sur les bienfaits de l'activité physique chez les seniors.</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">En savoir plus</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Testimonials
st.markdown("<h2 class='section-title'>Témoignages</h2>", unsafe_allow_html=True)

testimonial_cols = st.columns(2)
with testimonial_cols[0]:
    st.markdown("""
    <div class="testimonial">
        <p>"Grâce à la course Jamais Seul, j'ai retrouvé le goût de l'activité physique à 78 ans. Les bénévoles sont extraordinaires et l'ambiance est tellement chaleureuse !"</p>
        <div class="testimonial-author">Jeanne, 78 ans</div>
    </div>
    """, unsafe_allow_html=True)

with testimonial_cols[1]:
    st.markdown("""
    <div class="testimonial">
        <p>"Accompagner les seniors pendant cette course est une expérience humaine incroyable. On donne beaucoup, mais on reçoit encore plus en retour."</p>
        <div class="testimonial-author">Marc, bénévole depuis 5 ans</div>
    </div>
    """, unsafe_allow_html=True)

# NEW: Rejoignez-nous section
st.markdown("""
<div class="section" id="join-us">
    <h2 class="section-title">Rejoignez-nous</h2>
    <p>L'association Les Saisons des Anciens est toujours à la recherche de nouvelles personnes souhaitant s'impliquer, que ce soit comme :</p>
    <div style="display: flex; flex-wrap: wrap; margin-top: 20px; gap: 20px;">
        <div style="flex: 1; min-width: 250px; background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
            <h3 style="color: #34a0a2;">Participant</h3>
            <p>Vous avez plus de 60 ans et souhaitez participer à nos activités ? Rejoignez nos séances hebdomadaires ou inscrivez-vous à nos événements spéciaux.</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">Devenir participant</a>
        </div>
        <div style="flex: 1; min-width: 250px; background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
            <h3 style="color: #34a0a2;">Bénévole</h3>
            <p>Envie de donner de votre temps pour une cause qui a du sens ? Nos bénévoles sont essentiels au bon déroulement de toutes nos activités.</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">Devenir bénévole</a>
        </div>
        <div style="flex: 1; min-width: 250px; background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
            <h3 style="color: #34a0a2;">Partenaire</h3>
            <p>Vous représentez une entreprise et souhaitez soutenir notre cause ? Découvrez nos différentes formules de partenariat.</p>
            <a href="#" class="cta-button" style="padding: 8px 20px; font-size: 0.9rem;">Devenir partenaire</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# NEW: Contact section
st.markdown("""
<div class="section" id="contact">
    <h2 class="section-title">Contact</h2>
    <div style="display: flex; flex-wrap: wrap; gap: 40px;">
        <div style="flex: 1; min-width: 300px;">
            <h3>Nos coordonnées</h3>
            <p><strong>Adresse :</strong> 15 rue des Saisons, 75000 Paris</p>
            <p><strong>Téléphone :</strong> 01 23 45 67 89</p>
            <p><strong>Email :</strong> contact@saisons-anciens.fr</p>
            <p><strong>Horaires d'ouverture :</strong><br>
            Lundi au vendredi : 9h00 - 18h00<br>
            Samedi : 10h00 - 16h00</p>
        </div>
        <div style="flex: 1; min-width: 300px;">
            <h3>Formulaire de contact</h3>
            <div class="contact-form">
                <input type="text" placeholder="Nom" />
                <input type="email" placeholder="Email" />
                <input type="text" placeholder="Sujet" />
                <textarea placeholder="Votre message"></textarea>
                <button class="cta-button" style="width: 100%;">Envoyer</button>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Newsletter
st.markdown("""
<div class="newsletter">
    <h2>Restez informé</h2>
    <p>Inscrivez-vous à notre newsletter pour recevoir les dernières actualités de l'association et les informations sur nos prochains événements.</p>
    <div style="display: flex; max-width: 500px; margin-top: 20px;">
        <input type="email" placeholder="Votre adresse email" style="flex-grow: 1; padding: 12px; border: none; border-radius: 50px 0 0 50px; outline: none;">
        <button class="cta-button" style="border-radius: 0 50px 50px 0; margin: 0;">S'abonner</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Partners - Modified for 6 partners with horizontal scrolling
img_base64_AXA = get_img_as_base64("assets/images/AXA_Logo.png")
img_base64_vallee = get_img_as_base64("assets/images/Logo-bureau-vallee-2021.png")
img_base64_cave = get_img_as_base64("assets/images/logo-cave.jpg")
img_base64_joseph = get_img_as_base64("assets/images/logo-joseph.png")
img_base64_leclerc = get_img_as_base64("assets/images/logo-Leclerc.jpg")
img_base64_sodebo = get_img_as_base64("assets/images/Logo-Sodebo.png")
st.markdown(f"""
<h2 class='section-title'>Nos partenaires</h2>
<div class="partners-container">
    <div class="partner-logo">
        <img src="data:image/png;base64,{img_base64_AXA or ''}" width="150" alt="AXA">
    </div>
    <div class="partner-logo">
        <img src="data:image/png;base64,{img_base64_vallee or ''}" width="150" alt="Bureau Vallée">
    </div>
    <div class="partner-logo">
        <img src="data:image/jpg;base64,{img_base64_cave or ''}" width="150" alt="La Cave">
    </div>
    <div class="partner-logo">
        <img src="data:image/png;base64,{img_base64_joseph or ''}" width="150" alt="Joseph">
    </div>
    <div class="partner-logo">
        <img src="data:image/jpg;base64,{img_base64_leclerc or ''}" width="150" alt="Leclerc">
    </div>
    <div class="partner-logo">
        <img src="data:image/png;base64,{img_base64_sodebo or ''}" width="150" alt="Sodebo">
    </div>
</div>
""", unsafe_allow_html=True)

# Footer with fixed social icons using emoji for reliability
st.markdown("""
<div class="footer">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
            <div class="footer-section" style="flex: 1; min-width: 200px; margin-right: 20px;">
                <h3 class="footer-title">Les Saisons des Anciens</h3>
                <p>Association dédiée au bien-être et à l'inclusion des seniors à travers des activités sportives et sociales adaptées.</p>
                <div class="social-links">
                    <a href="#" class="social-link">📘</a>
                    <a href="#" class="social-link">🔗</a>
                    <a href="#" class="social-link">🐦</a>
                    <a href="#" class="social-link">📷</a>
                </div>
            </div>
            <div class="footer-section" style="flex: 1; min-width: 200px; margin-right: 20px;">
                <h3 class="footer-title">Navigation</h3>
                <a href="#" class="footer-link">Accueil</a>
                <a href="#" class="footer-link">Nous rejoindre</a>
                <a href="#" class="footer-link">Qui sommes-nous ?</a>
                <a href="#" class="footer-link">La course Jamais Seul</a>
                <a href="#" class="footer-link">Rejoignez-nous</a>
                <a href="#" class="footer-link">Contact</a>
            </div>
            <div class="footer-section" style="flex: 1; min-width: 200px;">
                <h3 class="footer-title">Contact</h3>
                <p>15 rue des Saisons<br>75000 Paris</p>
                <p>Tél: 01 23 45 67 89<br>Email: contact@saisons-anciens.fr</p>
            </div>
        </div>
        <div class="copyright">
            © 2025 Les Saisons des Anciens - Tous droits réservés - Images générées par l'IA
            <div style="margin-top: 10px;">
                <a href="#" style="color: rgba(255,255,255,0.6); margin-right: 20px; text-decoration: none;">Mentions légales</a>
                <a href="#" style="color: rgba(255,255,255,0.6); text-decoration: none;">Politique de confidentialité</a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)