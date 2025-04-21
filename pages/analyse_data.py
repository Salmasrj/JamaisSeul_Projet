import streamlit as st

# PAGE CONFIGURATION MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Tableau de Bord | Jamais Seul",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import all other libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
import time
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards

# Définir la palette de couleurs globale au début du fichier, juste après les imports

# Palette de couleurs Jamais Seul
COLOR_PALETTE = {
    # Couleurs principales
    "vert_fonce": "#145f48",
    "vert": "#2ba149",
    "jaune": "#f7c914",
    "orange": "#f5933c",
    "rouge": "#bc2141",
    "violet": "#8e4175",
    "jaune_pale": "#e5ea98",
    
    # Phases
    "phase1": "#145f48",  # vert foncé
    "phase2": "#2ba149",  # vert
    "phase3": "#f5933c",  # orange
    "phase4": "#8e4175",  # violet
    
    # Niveaux de risque
    "mineur": "#2ba149",  # vert
    "modere": "#f7c914",  # jaune
    "majeur": "#bc2141",  # rouge
    "critique": "#bc2141", # rouge pour criticité 4
    
    # Statuts et indicateurs
    "success": "#2ba149",  # vert
    "warning": "#f7c914",  # jaune
    "danger": "#bc2141",   # rouge
    "info": "#145f48",     # vert foncé
    "neutral": "#f5933c"   # orange
}

# Initialize session state
if "dashboard_period" not in st.session_state:
    st.session_state.dashboard_period = "S9"
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# Helper functions
@st.cache_data
def load_project_data():
    """Load all project data and return as dictionary"""
    # Generate periods - S1 à S14
    periods = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14"]
    
    # Project progress data
    project_progress = {
        "S1": 7, "S2": 14, "S3": 21, "S4": 28, 
        "S5": 35, "S6": 42, "S7": 50, "S8": 60, 
        "S9": 70, "S10": 80, "S11": 86, "S12": 92,
        "S13": 96, "S14": 100
    }
    
    # Budget data with realistic scaled increases
    budget_categories_new = [
    "Logistique", "Sécurité & secours", "Communication", "Inscriptions/plateforme", 
    "Animation", "Prévention des risques", "Imprévus"
    ]   

    budget_data = {}
    # Structure: period -> {category -> [budget_initial, dernier_budget, estime, consomme]}
    fixed_budgets = {
        "Logistique": [2000, 1900, 1900],
        "Sécurité & secours": [900, 900, 900],
        "Communication": [1490, 1490, 1490],
        "Inscriptions/plateforme": [600, 600, 600],
        "Animation": [1000, 1100, 1100],
        "Prévention des risques": [1000, 1000, 1000],
        "Imprévus": [200, 200, 200]
    }

    for period in periods:
        # Calculate spending scale factor - increases with each period
        spend_factor = (periods.index(period) + 1) / len(periods)
        budget_data[period] = {}
        
        for category, values in fixed_budgets.items():
            budget_initial, budget_valide, estime = values
            
            # Calculate spending based on period progress
            # Special case for communication which might exceed budget
            if category == "Communication":
                max_spend = 2070  # Known communication overspend
                spend = min(max_spend, max_spend * spend_factor)
            else:
                # For other categories, spending increases proportionally, up to the validated budget
                spend = min(budget_valide, budget_valide * spend_factor * 1.1)  # 1.1 to allow some overspend
            
            budget_data[period][category] = [budget_initial, budget_valide, estime, spend]
    
    # Risk data with evolving profile
    # Risk data with evolving profile
    risk_levels = ["Mineur", "Modéré", "Majeur"]
    risk_trends = ["↓", "→", "↑"]
    risk_data = {}

    # Define risk evolution patterns - Replace with specific risks
    risk_patterns = {
        "R01_Désistement des bénévoles": [0, 0, 0, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0, 0],
        "R02_Risques sanitaires": [2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "R03_Nombre de participants": [0, 0, 1, 1, 2, 2, 2, 2, 1, 1, 0, 0, 0, 0],
        "R04_Conditions extremes": [0, 0, 0, 0, 1, 2, 2, 1, 1, 0, 0, 0, 0, 0]
    }
    
    for i, period in enumerate(periods):
        risk_data[period] = {}
        for risk, pattern in risk_patterns.items():
            level = risk_levels[pattern[i]]
            # Determine trend
            if i < len(periods) - 1:
                if pattern[i] < pattern[i+1]:
                    trend = risk_trends[2]  # Upward
                elif pattern[i] > pattern[i+1]:
                    trend = risk_trends[0]  # Downward
                else:
                    trend = risk_trends[1]  # Stable
            else:
                trend = risk_trends[1]  # Stable for last period
                
            impact = 9 - pattern[i] * 2 + np.random.randint(-1, 2)
            impact = max(1, min(10, impact))
            
            priority = "Urgent" if level == "Majeur" else "Élevé" if level == "Modéré" and impact > 6 else "Normal" if level == "Modéré" else "Faible"
            
            risk_data[period][risk] = {
                "niveau": level, 
                "tendance": trend, 
                "impact": impact, 
                "priorité": priority
            }
    
    # Objectives data with realistic progression
    # Objectives data with SMART objectives
    objectives_data = {}
    objectives = {
        "Participants": {"cible": 700, "max": 1000},
        "Bénévoles": {"cible": 40},
        "Partenaires": {"cible": 10},
        "Satisfaction": {"cible": 100}
    }

    # Define growth curves for 14 periods based on SMART criteria
    growth_curves = {
        # Progressive increase up to potentially 1000 participants
        "Participants": [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.20, 1.30],
        # Steady recruitment of volunteers
        "Bénévoles": [0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05],
        # 5 partners by S8 (50%), then growing to target
        "Partenaires": [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00],
        # Zero until S10, then rapid growth
        "Satisfaction": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.60, 0.70, 0.80, 0.90]
    }

    for i, period in enumerate(periods):
        objectives_data[period] = {}
        for obj, details in objectives.items():
            target = details["cible"]
            percentage = growth_curves[obj][i] * 100
            actual = int(target * growth_curves[obj][i])
            objectives_data[period][obj] = {
                "cible": target,
                "actuel": actual,
                "pourcentage": int(percentage)
            }
    
    # Team performance data (1=Formation, 2=Confrontation, 3=Normalisation, 4=Performance, 0=Absent)
    team_states = {
        "Adèle": [1, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4],     
        "Alexia": [1, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],    
        "Hoang": [1, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4],     
        "Margaux": [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4],   
        "Salma": [1, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4],     
        "Nordine": [1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4],   
        "Antoine": [1, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4],   
        "Alexandre": [1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4], 
        "Moumene": [1, 1, 0, 2, 2, 0, 3, 3, 0, 3, 0, 4, 0, 4]    
    }
    
    # Create detailed GANTT data with the exact task specifications provided
    gantt_data = []
    
    # Task definitions with start and end dates
    task_definitions = [
        # Phase 1
        {"name": "1 Conception et mise en route du projet", "start": "2025-02-24", "end": "2025-03-14", "phase": "Phase 1", "level": "Main"},
        {"name": "1.1 Identification des besoins des bénéficiaires", "start": "2025-02-24", "end": "2025-02-26", "phase": "Phase 1", "level": "Sub"},
        {"name": "1.2 Création d'un canal de communication interne", "start": "2025-02-26", "end": "2025-02-28", "phase": "Phase 1", "level": "Sub"},
        {"name": "1.3 Estimation des coûts par poste", "start": "2025-02-27", "end": "2025-03-06", "phase": "Phase 1", "level": "Sub"},
        {"name": "1.4 Rédaction de la charte du projet", "start": "2025-03-07", "end": "2025-03-10", "phase": "Phase 1", "level": "Sub"},
        {"name": "1.5 Elaboration d'un plan de contact", "start": "2025-03-07", "end": "2025-03-11", "phase": "Phase 1", "level": "Sub"},
        {"name": "1.6 Mise en route du projet", "start": "2025-03-12", "end": "2025-03-14", "phase": "Phase 1", "level": "Sub"},
        
        # Phase 2
        {"name": "2 Définition et planification du projet", "start": "2025-03-17", "end": "2025-04-04", "phase": "Phase 2", "level": "Main"},
        {"name": "2.1 Définition des critères d'éligibilité", "start": "2025-03-17", "end": "2025-03-17", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.2 Définition des indicateurs de succès", "start": "2025-03-17", "end": "2025-03-19", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.3 Mise en place d'un diagramme de GANTT", "start": "2025-03-20", "end": "2025-03-21", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.4 Attribution des rôles et des responsabilités", "start": "2025-03-21", "end": "2025-03-28", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.5 Repérage terrain", "start": "2025-03-28", "end": "2025-04-01", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.6 Préparation des dossiers de demande", "start": "2025-04-02", "end": "2025-04-04", "phase": "Phase 2", "level": "Sub"},
        {"name": "2.7 Planification des réunions régulières", "start": "2025-04-04", "end": "2025-04-04", "phase": "Phase 2", "level": "Sub"},
        
        # Phase 3
        {"name": "3 Mise en œuvre du projet", "start": "2025-04-07", "end": "2025-05-10", "phase": "Phase 3", "level": "Main"},
        {"name": "3.1 Réservation des lieux", "start": "2025-04-07", "end": "2025-04-08", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.2 Conception graphique des affiches", "start": "2025-04-08", "end": "2025-04-09", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.3 Enregistrement et appariement selon centre d'intérêt", "start": "2025-04-08", "end": "2025-04-10", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.4 Suivi des validations administratives", "start": "2025-04-09", "end": "2025-04-11", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.5 Location de matériel (barnums, barrières, etc.)", "start": "2025-04-14", "end": "2025-04-14", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.6 Réalisation de vidéos promotionnelles", "start": "2025-04-10", "end": "2025-04-15", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.7 Recrutement des bénévoles", "start": "2025-04-16", "end": "2025-04-22", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.8 Session de présentation du parcours", "start": "2025-04-23", "end": "2025-04-23", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.9 Organisation d'ateliers de préparation", "start": "2025-04-23", "end": "2025-04-23", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.10 Coordination avec les pompiers et SAMU", "start": "2025-04-23", "end": "2025-04-28", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.11 Mises en relation avant l'évènement", "start": "2025-04-30", "end": "2025-05-02", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.12 Briefing des bénévoles sur la sécurité", "start": "2025-05-05", "end": "2025-05-06", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.13 Installation technique (signalétique, barrières…)", "start": "2025-05-07", "end": "2025-05-10", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.14 Installation de stands thématiques", "start": "2025-05-09", "end": "2025-05-10", "phase": "Phase 3", "level": "Sub"},
        {"name": "3.15 Journée de l'évènement", "start": "2025-05-10", "end": "2025-05-10", "phase": "Phase 3", "level": "Sub"},
        
        # Phase 4
        {"name": "4 Performances/contrôle du projet", "start": "2025-05-12", "end": "2025-05-21", "phase": "Phase 4", "level": "Main"},
        {"name": "4.1 Création d'un questionnaire de satisfaction", "start": "2025-05-12", "end": "2025-05-13", "phase": "Phase 4", "level": "Sub"},
        {"name": "4.2 Analyse des retours", "start": "2025-05-14", "end": "2025-05-16", "phase": "Phase 4", "level": "Sub"},
        {"name": "4.3 Performances du projet", "start": "2025-05-15", "end": "2025-05-16", "phase": "Phase 4", "level": "Sub"},
        {"name": "4.4 Présentation aux parties prenantes", "start": "2025-05-19", "end": "2025-05-21", "phase": "Phase 4", "level": "Sub"},
    ]
    
    # Add tasks to gantt data
    for task in task_definitions:
        gantt_data.append({
            "Task": task["name"],
            "Start": task["start"],
            "Finish": task["end"],
            "Resource": task["phase"],
            "Level": task["level"]
        })
    # Ajouter après la section GANTT data dans la fonction load_project_data

    # Map periods to dates for GANTT chart reference
    period_dates = {
        "S1": "2025-02-24", "S2": "2025-03-03", "S3": "2025-03-10",
        "S4": "2025-03-17", "S5": "2025-03-24", "S6": "2025-03-31",
        "S7": "2025-04-07", "S8": "2025-04-14", "S9": "2025-04-21",
        "S10": "2025-04-28", "S11": "2025-05-05", "S12": "2025-05-12", 
        "S13": "2025-05-19", "S14": "2025-05-26"
    }
    
    # Satisfaction data
    satisfaction_data = {}
    for i, period in enumerate(periods):
        very_satisfied_base = 3 + i * 2
        satisfied_base = 3 - i * 0.3
        neutral_base = max(0, 1 - i * 0.1)
        unsatisfied_base = max(0, 1 - i * 0.08)
        very_unsatisfied_base = max(0, 1 - i * 0.07)
        
        # Make sure none are negative and they add up to 100
        very_unsatisfied = max(0, round(very_unsatisfied_base))
        unsatisfied = max(0, round(unsatisfied_base))
        neutral = max(0, round(neutral_base))
        satisfied = max(0, round(satisfied_base))
        very_satisfied = 100 - (satisfied + neutral + unsatisfied + very_unsatisfied)
        
        satisfaction_data[period] = {
            "Très satisfait": very_satisfied,
            "Satisfait": satisfied,
            "Neutre": neutral,
            "Insatisfait": unsatisfied,
            "Très insatisfait": very_unsatisfied
        }
    
    # Return complete dataset
    data = {
        "periods": periods,
        "project_progress": project_progress,
        "budget_data": budget_data,
        "risk_data": risk_data,
        "objectives_data": objectives_data,
        "team_states": team_states,
        "satisfaction_data": satisfaction_data,
        "gantt_data": gantt_data,
        "period_dates": period_dates
    }

    # Définition des jalons clés du projet
    milestones = [
        {"Milestone": "Validation de la charte", "Date": "2025-03-14", "Phase": "Phase 1"},
        {"Milestone": "Planification complétée", "Date": "2025-04-04", "Phase": "Phase 2"},
        {"Milestone": "Recrutement bénévoles finalisé", "Date": "2025-04-22", "Phase": "Phase 3"},
        {"Milestone": "Jour de l'événement", "Date": "2025-05-10", "Phase": "Phase 3"},
        {"Milestone": "Rapport final", "Date": "2025-05-21", "Phase": "Phase 4"}
    ]

    # Ajouter les jalons aux données
    data["milestones"] = milestones
    
    return data

def calculate_delta(current_value, previous_value):
    """Calculate difference and percentage change"""
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

# Load data
data = load_project_data()
periods = data["periods"]
selected_period = st.session_state.dashboard_period
selected_period_index = periods.index(selected_period)

# Page header
st.title("🏃‍♂️ Gestion de projet pour la course Jamais Seul 🏃‍♀️")

# Top level navigation with tabs
tab_titles = ["📊 Général", "📅 Planning", "💰 Budget", "⚠️ Risques", "👥 Équipe"]
tabs = st.tabs(tab_titles)

# Sidebar
with st.sidebar:
    st.title("Jamais Seul")
    
    # Period selector
    st.header("⚙️ Contrôles")
    period_selector = st.select_slider(
        "Période d'analyse",
        options=periods,
        value=selected_period,
        key="sidebar-period-selector"
    )
    if period_selector != selected_period:
        st.session_state.dashboard_period = period_selector
        st.rerun()
    
    # Date reference
    st.caption(f"Date de référence: {data['period_dates'][selected_period]}")
    
    # Quick filters
    st.header("Filtres rapides")
    st.checkbox("Afficher les tendances", value=True)
    
    # Download report button
    # st.button("📄 Accéder à notre Google Sheet", type="primary")
    report_url = "https://docs.google.com/spreadsheets/d/1NZX1-ZxpK5vkV1O5e1yBhYtq5k9lzWJy/edit?gid=1616606434#gid=1616606434"

    st.markdown(
        f"""
        <a href="{report_url}" target="_blank" style="
            display: inline-block;
            background-color: rgb(19, 23, 32);
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 0.5rem;
            border: none;
            cursor: pointer;
            text-align: center;
            width: 100%;
            font-weight: 500;
            line-height: 1.6;
            margin-bottom: 0.5rem;">
            📄 Accéder à notre Google Sheet
        </a>
        """, 
        unsafe_allow_html=True
    )

# Tab 1: General Overview - Keep compact to fit on one page without scrolling
with tabs[0]:
    st.header("📊 Tableau de bord")
    # Top level metrics in compact layout
    col1, col2, col3, col4 = st.columns(4)

    # Calculate current metrics and deltas
    current_progress = data["project_progress"][selected_period]
    prev_progress = data["project_progress"][periods[max(0, selected_period_index-1)]]
    progress_delta, progress_delta_percent = calculate_delta(current_progress, prev_progress)

    current_objectives = data["objectives_data"][selected_period]
    avg_objective = int(sum(obj['pourcentage'] for obj in current_objectives.values()) / len(current_objectives))
    prev_period = periods[max(0, selected_period_index-1)]
    prev_avg = int(sum(obj['pourcentage'] for obj in data['objectives_data'][prev_period].values()) / len(data['objectives_data'][prev_period]))
    objective_delta, objective_delta_percent = calculate_delta(avg_objective, prev_avg)

    current_risks = data["risk_data"][selected_period]
    high_risks = sum(1 for risk in current_risks.values() if risk["niveau"] == "Majeur")
    prev_high_risks = sum(1 for risk in data["risk_data"][periods[max(0, selected_period_index-1)]].values() if risk["niveau"] == "Majeur")
    risk_delta, risk_delta_percent = calculate_delta(high_risks, prev_high_risks)

    current_participants = current_objectives['Participants']['actuel']
    prev_participants = data['objectives_data'][periods[max(0, selected_period_index-1)]]['Participants']['actuel']
    participants_delta, participants_delta_percent = calculate_delta(current_participants, prev_participants)

    # Display metrics with customized styling
    with col1:
        st.metric("Progression", f"{current_progress}%", f"{progress_delta:+.0f}%", delta_color="normal")
        
    with col2:
        st.metric("Objectifs SMART", f"{avg_objective}%", f"{objective_delta:+.0f}%", delta_color="normal")
        
    with col3:
        st.metric("Risques majeurs", high_risks, f"{risk_delta:+.0f}", delta_color="inverse")
        
    with col4:
        st.metric("Participants", current_participants, f"{participants_delta:+.0f}", delta_color="normal")

    # Apply metric styling
    style_metric_cards(
        background_color="#FFFFFF",
        border_left_color={
            "normal": COLOR_PALETTE["vert"],
            "inverse-normal": COLOR_PALETTE["orange"],
            "up": COLOR_PALETTE["vert"],
            "down": COLOR_PALETTE["orange"],
            "off": COLOR_PALETTE["jaune"]
        },
        border_color="#FFFFFF",
        box_shadow=True
    )
    
    # Main dashboard in two columns - Top row
    col1, col2 = st.columns(2)
    
    # Modifier la section du mini GANTT dans l'onglet général

    with col1:
        # Mini GANTT chart showing main phases
        st.subheader("GANTT - Phases principales")
        st.caption("Phases principales du projet avec jalons clés")
        
        # Create GANTT data for main phases only
        main_phases = [
            {"Task": "1. Conception et mise en route", "Start": "2025-02-24", "Finish": "2025-03-14", "Phase": "Phase 1"},
            {"Task": "2. Définition et planification", "Start": "2025-03-17", "Finish": "2025-04-04", "Phase": "Phase 2"},
            {"Task": "3. Mise en œuvre", "Start": "2025-04-07", "Finish": "2025-05-10", "Phase": "Phase 3"},
            {"Task": "4. Performances/contrôle", "Start": "2025-05-12", "Finish": "2025-05-21", "Phase": "Phase 4"}
        ]
        
        mini_gantt_df = pd.DataFrame(main_phases)
        mini_gantt_df["Start"] = pd.to_datetime(mini_gantt_df["Start"])
        mini_gantt_df["Finish"] = pd.to_datetime(mini_gantt_df["Finish"])
        
        # Créer le diagramme de Gantt
        fig = px.timeline(
            mini_gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Phase",
            color_discrete_map={
                "Phase 1": COLOR_PALETTE["phase1"],
                "Phase 2": COLOR_PALETTE["phase2"],
                "Phase 3": COLOR_PALETTE["phase3"],
                "Phase 4": COLOR_PALETTE["phase4"]
            }
        )
        
        # Add vertical line for current period
        current_date = data['period_dates'][selected_period]
        fig.add_vline(x=current_date, line_width=2, line_dash="dash", line_color="#444444")
        
        # Add vertical line for race day - May 9, 2025
        race_day = "2025-05-09"
        fig.add_vline(x=race_day, line_width=3, line_color=COLOR_PALETTE["rouge"])
        
        # Add annotation for race day
        fig.add_annotation(
            x=race_day,
            y=4,
            text="Jour J",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=COLOR_PALETTE["rouge"],
            font=dict(color=COLOR_PALETTE["rouge"]),
            xanchor="left"
        )
        
        # Ajouter les jalons comme des points sur le diagramme
        for milestone in data["milestones"]:
            milestone_date = pd.to_datetime(milestone["Date"])
            for i, phase in enumerate(main_phases):
                phase_start = pd.to_datetime(phase["Start"])
                phase_end = pd.to_datetime(phase["Finish"])
                
                # Afficher le jalon sur sa phase correspondante
                if milestone["Phase"] == phase["Phase"] and phase_start <= milestone_date <= phase_end:
                    y_position = i
                    
                    # Ajouter un marqueur pour le jalon
                    fig.add_trace(go.Scatter(
                        x=[milestone_date],
                        y=[y_position],
                        mode="markers",
                        marker=dict(symbol="diamond", size=12, color=COLOR_PALETTE["jaune"]),
                        name=milestone["Milestone"],
                        showlegend=False
                    ))
                    
                    # Ajouter une annotation pour le jalon
                    fig.add_annotation(
                        x=milestone_date,
                        y=y_position - 0.3,
                        text=milestone["Milestone"],
                        showarrow=False,
                        font=dict(size=8, color=COLOR_PALETTE["jaune_pale"]),
                        bgcolor=COLOR_PALETTE["vert_fonce"],
                        bordercolor=COLOR_PALETTE["jaune"],
                        borderwidth=1,
                        borderpad=2,
                        opacity=0.8,
                        yanchor="top"
                    )
        
        fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(
                tickformat="%d %b",
                tickangle=45,
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Objectives - compact chart - RENAMED
        st.subheader("Objectifs SMART")
        st.caption("Suivi des objectifs SMART du projet")
        objectives_df = pd.DataFrame({
            'Objectif': list(current_objectives.keys()),
            'Pourcentage': [obj['pourcentage'] for obj in current_objectives.values()]
        })
        
        # Add reference lines to show targets vs actuals
        fig = px.bar(
            objectives_df, 
            y='Objectif', 
            x='Pourcentage',
            orientation='h',
            text='Pourcentage',
            color_discrete_sequence=[COLOR_PALETTE["vert"]]
        )
        
        # Add visual cues for targets
        for i, objective in enumerate(objectives_df['Objectif']):
            if objective == "Participants":
                # Add a dashed line at 100% to show target
                fig.add_shape(
                    type="line",
                    x0=100, y0=i-0.4, x1=100, y1=i+0.4,
                    line=dict(color=COLOR_PALETTE["rouge"], width=2, dash="dash"),
                    layer="above"
                )
                # Add a marker at max capacity
                fig.add_shape(
                    type="line",
                    x0=142.86, y0=i-0.4, x1=142.86, y1=i+0.4,
                    line=dict(color=COLOR_PALETTE["vert_fonce"], width=2),
                    layer="above"
                )
        
        fig.update_layout(
            height=200, 
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis=dict(range=[0, 150])  # Ensure max of 150% to show the 1000 participant max
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Main dashboard in two columns - Bottom row
    # Main dashboard in two columns - Bottom row
    bottom_col1, bottom_col2 = st.columns(2)

    # Remplacer la section "Aperçu des risques" dans bottom_col1

    with bottom_col1:
        # Risk overview - compact chart with specific risks
        st.subheader("Aperçu des risques")
        st.caption("Évaluation et suivi des risques du projet")
        risk_counts = {"Mineur": 0, "Modéré": 0, "Majeur": 0}
        
        # Evaluate specific risk conditions based on current period
        risk_warnings = []
        
        # R01: État critique si tous les bénévoles n'ont pas répondu aux relances
        benevoles_objectif = current_objectives['Bénévoles']['cible']
        benevoles_actuels = current_objectives['Bénévoles']['actuel']
        benevoles_ratio = benevoles_actuels / benevoles_objectif if benevoles_objectif > 0 else 0
        
        if benevoles_ratio < 0.75:  # Moins de 75% des bénévoles ont répondu
            risk_warnings.append({
                "Risque": "R01_Désistement des bénévoles",
                "Statut": "Critique",
                "Description": f"Seulement {benevoles_actuels}/{benevoles_objectif} bénévoles confirmés"
            })
        
        # R02: État critique si les mesures de prévention ne sont pas en place
        prevention_complete = selected_period_index >= 9  
        if not prevention_complete:
            risk_warnings.append({
                "Risque": "R02_Risques sanitaires", 
                "Statut": "Critique",
                "Description": "Mesures de prévention incomplètes" 
            })
        
        # R03: État critique si le nombre de participants est inférieur à l'objectif
        participants_objectif = current_objectives['Participants']['cible']
        participants_actuels = current_objectives['Participants']['actuel']
        participants_ratio = participants_actuels / participants_objectif if participants_objectif > 0 else 0
        
        if participants_ratio < 0.7:  
            risk_warnings.append({
                "Risque": "R03_Nombre de participants", 
                "Statut": "Critique",
                "Description": f"Seulement {participants_actuels}/{participants_objectif} participants inscrits" 
            })
        
        # R04: État critique si météo non validée en S9-S11
        meteo_validee = selected_period_index < 8 or selected_period_index > 10 
        if not meteo_validee:
            risk_warnings.append({
                "Risque": "R04_Conditions extremes", 
                "Statut": "Critique",
                "Description": "Prévisions météo non validées" 
            })
        
        # Count risk levels for the pie chart
        for risk_data in current_risks.values():
            risk_counts[risk_data["niveau"]] += 1
        
        # Create a more compact horizontal bar chart instead of a pie chart
        risk_df = pd.DataFrame({
            "Niveau": list(risk_counts.keys()),
            "Nombre": list(risk_counts.values())
        })
        
        
        # Display critical risks as alerts (pas besoin de colonnes imbriquées)
        if risk_warnings:
            for risk in risk_warnings:
                st.warning(f"⚠️ {risk['Risque']}: {risk['Description']}")
        else:
            st.success("✅ Aucun risque critique identifié")

    with bottom_col2:
    # Budget overview - compact chart
        st.subheader("Aperçu du budget")
        current_budget = data["budget_data"][selected_period]
        
        # Calculer les totaux
        total_budget = sum(item[1] for item in current_budget.values())  # Dernier budget validé
        total_depense = sum(item[3] for item in current_budget.values())  # Consommé
        
        # Créer un dataframe pour afficher la comparaison budget vs dépenses
        budget_vs_depense = pd.DataFrame({
            "Type": ["Budget validé", "Dépenses"],
            "Montant": [total_budget, total_depense]
        })
        
        # Créer le graphique en barres
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=["Budget"],
            y=[total_budget],
            name="Budget validé",
            marker_color=COLOR_PALETTE["vert_fonce"]
        ))
        fig1.add_trace(go.Bar(
            x=["Budget"],
            y=[total_depense],
            name="Dépensé",
            marker_color=COLOR_PALETTE["orange"]
        ))
        
        fig1.update_layout(
            height=200,
            margin=dict(l=5, r=5, t=5, b=5),
            barmode="group"
        )
        
        # Créer un dataframe pour les catégories de dépenses
        categories_data = []
        for category, values in current_budget.items():
            categories_data.append({
                "Catégorie": category,
                "Dépensé": values[3],
                "Pourcentage": (values[3] / total_depense) * 100 if total_depense > 0 else 0
            })
        
        categories_df = pd.DataFrame(categories_data)
        categories_df = categories_df.sort_values(by="Pourcentage", ascending=False)
        
        # Afficher les deux graphiques côte à côte
        budget_cols = st.columns([1, 1])
        
        with budget_cols[0]:
            st.caption("Budget validé vs Dépenses")
            st.plotly_chart(fig1, use_container_width=True)
            # Afficher le pourcentage d'utilisation du budget
            pourcentage = (total_depense / total_budget) * 100 if total_budget else 0
            st.caption(f"Utilisation du budget: {pourcentage:.1f}%")
            st.progress(pourcentage/100)
        
        with budget_cols[1]:
            # Créer un donut chart pour les catégories de dépenses
            st.caption("Répartition des dépenses par catégorie")
            fig2 = px.pie(
                categories_df, 
                values="Pourcentage", 
                names="Catégorie",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(
                height=200,
                margin=dict(l=5, r=5, t=5, b=5),
                showlegend=True
            )
            
            # Afficher le graphique
            st.plotly_chart(fig2, use_container_width=True)
            
            # Afficher un indicateur pour montrer si on est au-dessus ou en-dessous du budget
            if pourcentage > 100:
                st.error(f"⚠️ Dépassement: +{pourcentage - 100:.1f}%")
            else:
                st.success(f"✅ Reste: {100 - pourcentage:.1f}%")

# Tab 2: Planning with detailed GANTT chart
with tabs[1]:
    # Remplacer la section GANTT dans l'onglet Planning (Tab 2)
    # Planning du Projet
    st.header("Planning du Projet")
    
    # GANTT chart with full task structure from CSV
    st.subheader("Calendrier complet")
    st.caption("Détails des tâches et jalons clés")
    
    # Afficher les filtres pour les phases
    phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    selected_phases = st.multiselect("Filtrer par phase", phases, default=phases)
    
    # Option pour afficher tous les détails ou seulement les tâches principales
    show_details = st.checkbox("Afficher les sous-tâches", value=True)
    
    # Filtrer le DataFrame selon les options choisies
    gantt_df = pd.DataFrame(data["gantt_data"])
    
    # Filtrer par phase
    if selected_phases:
        gantt_df = gantt_df[gantt_df["Resource"].isin(selected_phases)]
    
    # Filtrer par niveau de détail
    if not show_details:
        gantt_df = gantt_df[gantt_df["Level"] == "Main"]
    
    # Convert date strings to datetime objects
    gantt_df["Start"] = pd.to_datetime(gantt_df["Start"])
    gantt_df["Finish"] = pd.to_datetime(gantt_df["Finish"])
    
    # Create Gantt chart
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        color_discrete_map={
            "Phase 1": "#3498db",
            "Phase 2": "#2ecc71",
            "Phase 3": "#f39c12",
            "Phase 4": "#9b59b6"
        }
    )
    
    # Highlight current period
    current_date = data['period_dates'][selected_period]
    fig.add_vline(x=current_date, line_width=2, line_dash="dash", line_color="#444444")
    
    # Add vertical line for race day - May 9, 2025
    race_day = "2025-05-09"
    fig.add_vline(x=race_day, line_width=3, line_color=COLOR_PALETTE["rouge"])
    
    # Add annotation for race day
    fig.add_annotation(
        x=race_day,
        y=0,
        text="Jour de la course",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=COLOR_PALETTE["rouge"],
        font=dict(color=COLOR_PALETTE["rouge"]),
        xanchor="right"
    )
    
    
    # Ajouter les jalons comme des marqueurs
    milestone_traces = []
    for milestone in data["milestones"]:
        milestone_date = pd.to_datetime(milestone["Date"])
        
        # Ajouter un marqueur pour chaque jalon
        milestone_traces.append(
            go.Scatter(
                x=[milestone_date],
                y=[milestone["Milestone"]],
                mode="markers+text",
                marker=dict(
                    symbol="diamond",
                    size=16,
                    color=COLOR_PALETTE["jaune"],
                    line=dict(color=COLOR_PALETTE["vert_fonce"], width=2)
                ),
                text=milestone["Milestone"],
                textposition="middle right",
                textfont=dict(color=COLOR_PALETTE["jaune_pale"]),
                name=milestone["Milestone"],
                hoverinfo="text",
                hovertext=f"{milestone['Milestone']} - {milestone['Date']}",
            )
        )

    # Ajouter les traces de jalons au graphique
    for trace in milestone_traces:
        fig.add_trace(trace)

    fig.update_layout(
        height=600 if show_details else 300,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Task progress
    st.subheader("Avancement des phases")
    
    # Create realistic task progress data
    phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    progress_data = {
        "Phase 1": 100 if selected_period_index >= 3 else min(100, (selected_period_index + 1) * 33.33),
        "Phase 2": 0 if selected_period_index < 3 else (
                   100 if selected_period_index >= 6 else min(100, (selected_period_index - 2) * 33.33)),
        "Phase 3": 0 if selected_period_index < 6 else (
                   100 if selected_period_index >= 11 else min(100, (selected_period_index - 5) * 20)),
        "Phase 4": 0 if selected_period_index < 11 else min(100, (selected_period_index - 10) * 33.33)
    }
    
    for phase, progress in progress_data.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(progress/100)
        with col2:
            st.write(f"{progress:.0f}%")

# Tab 3: Budget
with tabs[2]:
    st.header("Suivi du Budget")
    st.caption("Analyse des dépenses par rapport au budget")
    
    # Budget KPIs
    # Budget KPIs
    current_budget = data["budget_data"][selected_period]
    total_budget_initial = sum(item[0] for item in current_budget.values())
    total_budget_valide = sum(item[1] for item in current_budget.values())
    total_estime = sum(item[2] for item in current_budget.values())
    total_depense = sum(item[3] for item in current_budget.values())
    pourcentage_consomme = (total_depense / total_budget_valide) * 100 if total_budget_valide else 0
    reste_budget = total_budget_valide - total_depense
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Budget initial", f"{total_budget_initial:,.0f} €")
    col2.metric("Budget validé", f"{total_budget_valide:,.0f} €")
    col3.metric("Reste à dépenser", f"{reste_budget:,.0f} €")
    col4.metric("Consommation", f"{pourcentage_consomme:.1f}%")
    
    # Budget evolution
    st.subheader("Évolution du budget")
    st.caption("Analyse de l'évolution du budget au fil des périodes")
    
    # Prepare data
    budget_evolution = []
    for period in periods[:selected_period_index+1]:
        budget_period = data["budget_data"][period]
        budget_initial = sum(item[0] for item in budget_period.values())
        budget_valide = sum(item[1] for item in budget_period.values())
        estime = sum(item[2] for item in budget_period.values())
        depense = sum(item[3] for item in budget_period.values())
        budget_evolution.append({
            "Période": period,
            "Budget initial": budget_initial,
            "Budget validé": budget_valide,
            "Dépensé": depense
        })
    
    budget_df = pd.DataFrame(budget_evolution)
    
    fig = px.line(
        budget_df,
        x="Période",
        y=["Budget initial", "Budget validé", "Dépensé"],
        markers=True,
        color_discrete_map={
            "Budget initial": "#3498db",
            "Budget validé": "#9b59b6",
            "Dépensé": "#2ecc71"
        }
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Montant (€)",
        xaxis_title="Période"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Budget breakdown
    st.subheader("Répartition des dépenses par catégorie")
    st.caption("Analyse des dépenses par catégorie")
    
    budget_categories_detail = []
    for category, values in current_budget.items():
        budget_initial, budget_valide, estime, depense = values
        ratio = depense / budget_valide * 100 if budget_valide else 0
        statut = "Dépassement" if depense > budget_valide else "Dans le budget"
        
        budget_categories_detail.append({
            "Catégorie": category,
            "Budget initial": budget_initial,
            "Budget validé": budget_valide,
            "Estimé": estime,
            "Dépensé": depense,
            "% Consommé": ratio,
            "Statut": statut
        })
    
    budget_cat_df = pd.DataFrame(budget_categories_detail)
    
    # Afficher le tableau détaillé
    st.dataframe(
        budget_cat_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Budget initial": st.column_config.NumberColumn("Budget initial (€)", format="%.2f €"),
            "Budget validé": st.column_config.NumberColumn("Budget validé (€)", format="%.2f €"),
            "Estimé": st.column_config.NumberColumn("Estimé (€)", format="%.2f €"),
            "Dépensé": st.column_config.NumberColumn("Dépensé (€)", format="%.2f €"),
            "% Consommé": st.column_config.ProgressColumn("% Consommé", format="%.1f%%", min_value=0, max_value=150)
        }
    )
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Graphique en anneau pour la répartition des dépenses
        fig = px.pie(
            budget_cat_df,
            values="Dépensé",
            names="Catégorie",
            hole=0.4
        )
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.subheader("Répartition des dépenses par catégorie")
        st.caption("Analyse des dépenses par catégorie")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique en barres pour comparer budget vs dépenses
        fig = px.bar(
            budget_cat_df,
            y="Catégorie",
            x=["Budget validé", "Dépensé"],
            orientation="h",
            barmode="group",
            color_discrete_map={
                "Budget validé": "#3498db",
                "Dépensé": "#2ecc71"
            }
        )
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Montant (€)",
            yaxis_title=""
        )
        st.subheader("Comparaison Budget vs Dépenses")
        st.caption("Analyse de la consommation du budget")
        st.plotly_chart(fig, use_container_width=True)

# Dans l'onglet Risques (Tab 4), ajouter cette section pour afficher des détails supplémentaires
with tabs[3]:
    st.header("Gestion des Risques")
    # Risk matrix
    st.subheader("Matrice des risques")
    
    # Use fixed positions for risks regardless of other conditions
    risks_for_matrix = [
        {"Risque": "R01_Désistement des bénévoles", "Impact": 3, "Probabilité": 4, "Criticité": 3, "Niveau": "Majeur"},
        {"Risque": "R02_Risques sanitaires", "Impact": 4, "Probabilité": 3, "Criticité": 3, "Niveau": "Majeur"},
        {"Risque": "R03_Nombre de participants", "Impact": 4, "Probabilité": 4, "Criticité": 4, "Niveau": "Majeur"},
        {"Risque": "R04_Conditions extremes", "Impact": 4, "Probabilité": 3, "Criticité": 3, "Niveau": "Majeur"}
    ]
    
    risk_matrix_df = pd.DataFrame(risks_for_matrix)
    
    # Create scatter plot with 4x4 scale
    fig = px.scatter(
        risk_matrix_df,
        x="Probabilité",
        y="Impact",
        color="Criticité",
        text="Risque",
        color_continuous_scale=[COLOR_PALETTE["vert"], COLOR_PALETTE["jaune"], COLOR_PALETTE["orange"], COLOR_PALETTE["rouge"]],
        size_max=30,
        size=[20, 20, 25, 20],  # Make R03 (criticité 4) slightly larger
        range_color=[1, 4]
    )
    
    # Add grid lines for 4x4 matrix
    for i in range(1, 5):
        # Vertical grid lines
        fig.add_shape(
            type="line",
            x0=i, y0=0,
            x1=i, y1=4.5,
            line=dict(color="lightgrey", width=1),
            layer="below"
        )
        # Horizontal grid lines
        fig.add_shape(
            type="line",
            x0=0, y0=i,
            x1=4.5, y1=i,
            line=dict(color="lightgrey", width=1),
            layer="below"
        )
    
    # Add risk zones for 4x4 matrix
    # Criticité 4 (rouge foncé) - top right corner
    fig.add_shape(
        type="rect",
        x0=4, y0=4,
        x1=4.5, y1=4.5,
        fillcolor=f"rgba({int(COLOR_PALETTE['rouge'][1:3], 16)}, {int(COLOR_PALETTE['rouge'][3:5], 16)}, {int(COLOR_PALETTE['rouge'][5:7], 16)}, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    
    # Criticité 3 (rouge) - high impact or probability
    fig.add_shape(
        type="rect",
        x0=3, y0=4,
        x1=4, y1=4.5,
        fillcolor=f"rgba({int(COLOR_PALETTE['orange'][1:3], 16)}, {int(COLOR_PALETTE['orange'][3:5], 16)}, {int(COLOR_PALETTE['orange'][5:7], 16)}, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=4, y0=3,
        x1=4.5, y1=4,
        fillcolor="rgba(231, 76, 60, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=3, y0=3,
        x1=4, y1=4,
        fillcolor="rgba(231, 76, 60, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    
    # Criticité 2 (jaune) - medium impact and probability
    fig.add_shape(
        type="rect",
        x0=2, y0=3,
        x1=3, y1=4.5,
        fillcolor="rgba(243, 156, 18, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=3, y0=2,
        x1=4.5, y1=3,
        fillcolor="rgba(243, 156, 18, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=2, y0=2,
        x1=3, y1=3,
        fillcolor="rgba(243, 156, 18, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    
    # Criticité 1 (vert) - low risk
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=2, y1=2,
        fillcolor="rgba(46, 204, 113, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=0, y0=2,
        x1=2, y1=4.5,
        fillcolor="rgba(46, 204, 113, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=2, y0=0,
        x1=4.5, y1=2,
        fillcolor="rgba(46, 204, 113, 0.3)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add labels for criticality zones
    fig.add_annotation(
        x=4.25, y=4.25,
        text="Criticité 4",
        showarrow=False,
        font=dict(color="#7f0000", size=12)
    )
    fig.add_annotation(
        x=3.5, y=3.5,
        text="Criticité 3",
        showarrow=False, 
        font=dict(color="#c0392b", size=12)
    )
    fig.add_annotation(
        x=2.5, y=2.5,
        text="Criticité 2",
        showarrow=False,
        font=dict(color="#e67e22", size=12)
    )
    fig.add_annotation(
        x=1, y=1,
        text="Criticité 1",
        showarrow=False,
        font=dict(color="#27ae60", size=12)
    )
    
    # Configure axis for 4x4 scale
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        xaxis=dict(
            title="Probabilité",
            range=[0.5, 4.5],
            dtick=1,
            tickvals=[1, 2, 3, 4],
            ticktext=["1 - Rare", "2 - Peu probable", "3 - Probable", "4 - Très probable"]
        ),
        yaxis=dict(
            title="Impact",
            range=[0.5, 4.5],
            dtick=1,
            tickvals=[1, 2, 3, 4],
            ticktext=["1 - Négligeable", "2 - Mineur", "3 - Modéré", "4 - Majeur"]
        )
    )
    
    # Improve hover information
    fig.update_traces(
        hovertemplate="<b>%{text}</b><br>Impact: %{y}<br>Probabilité: %{x}<br>Criticité: %{marker.color}<extra></extra>"
    )
    
    st.caption("Matrice des risques du projet")
    # Affichage de la figure
    st.plotly_chart(fig, use_container_width=True)
    
    # Add legend for risk criticality
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-top: -20px; margin-bottom: 20px;">
        <div style="margin: 0 10px; display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; background-color: #27ae60; margin-right: 5px;"></div>
            <span>Criticité 1</span>
        </div>
        <div style="margin: 0 10px; display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; background-color: #f39c12; margin-right: 5px;"></div>
            <span>Criticité 2</span>
        </div>
        <div style="margin: 0 10px; display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; background-color: #e74c3c; margin-right: 5px;"></div>
            <span>Criticité 3</span>
        </div>
        <div style="margin: 0 10px; display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; background-color: #7f0000; margin-right: 5px;"></div>
            <span>Criticité 4</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Analyse détaillée des risques critiques")

    # Create tabs for each risk
    risk_detail_tabs = st.tabs([
        "R01: Désistement des bénévoles", 
        "R02: Risques sanitaires", 
        "R03: Nombre de participants", 
        "R04: Conditions extrêmes"
    ])

    with risk_detail_tabs[0]:
        st.markdown("### R01: Désistement des bénévoles")
        
        # Calculate response rate
        benevoles_objectif = current_objectives['Bénévoles']['cible']
        benevoles_actuels = current_objectives['Bénévoles']['actuel']
        response_rate = (benevoles_actuels / benevoles_objectif * 100) if benevoles_objectif > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Taux de réponse", f"{response_rate:.1f}%")
            st.progress(response_rate/100)
        
        with col2:
            st.metric("Bénévoles confirmés", f"{benevoles_actuels}/{benevoles_objectif}")
        
        # Actions recommandées
        st.subheader("Actions recommandées")
        if response_rate < 75:
            st.error("Niveau d'alerte : CRITIQUE")
            st.markdown("""
            - Lancer une campagne de relance urgente
            - Élargir le recrutement à d'autres réseaux
            - Prévoir un plan de secours avec moins de bénévoles
            """)
        elif response_rate < 90:
            st.warning("Niveau d'alerte : MODÉRÉ")
            st.markdown("""
            - Envoyer des rappels personnalisés
            - Confirmer la disponibilité des bénévoles déjà engagés
            """)
        else:
            st.success("Niveau d'alerte : MINEUR")
            st.markdown("""
            - Maintenir le contact avec les bénévoles confirmés
            - Prévoir quelques remplaçants en cas de désistement de dernière minute
            """)

    with risk_detail_tabs[1]:
        st.markdown("### R02: Risques sanitaires")
        
        # Calculate prevention measures completion
        prevention_steps = [
            "Plan de secours établi",
            "Équipe médicale confirmée",
            "Matériel de premiers soins préparé",
            "Formation des bénévoles aux gestes de premiers secours",
            "Coordination avec hôpitaux locaux"
        ]
        
        # Simulate completion status based on current period
        prevention_completed = [
            selected_period_index >= 6,
            selected_period_index >= 7,
            selected_period_index >= 8,
            selected_period_index >= 9,
            selected_period_index >= 10
        ]
        
        completion_rate = sum(prevention_completed) / len(prevention_completed) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mesures préventives en place", f"{completion_rate:.1f}%")
            st.progress(completion_rate/100)
        
        # Display checklist
        st.subheader("Liste des mesures préventives")
        for i, step in enumerate(prevention_steps):
            st.checkbox(step, value=prevention_completed[i], disabled=True)
        
        # Actions recommandées
        st.subheader("Actions recommandées")
        if completion_rate < 80:
            st.error("Niveau d'alerte : CRITIQUE")
            st.markdown("""
            - Accélérer la mise en place des mesures de prévention
            - Réunion d'urgence avec l'équipe de sécurité
            - Envisager de reporter l'événement si les mesures essentielles ne peuvent être mises en place
            """)
        elif completion_rate < 100:
            st.warning("Niveau d'alerte : MODÉRÉ")
            st.markdown("""
            - Finaliser les mesures restantes rapidement
            - Tester le dispositif de sécurité
            """)
        else:
            st.success("Niveau d'alerte : MINEUR")
            st.markdown("""
            - Vérifier une dernière fois tous les dispositifs
            - Prévoir une simulation de crise
            """)
    with risk_detail_tabs[2]:
        st.markdown("### R03: Nombre de participants")
        
        # Calculate participation rate
        participants_objectif = current_objectives['Participants']['cible']
        participants_actuels = current_objectives['Participants']['actuel']
        participation_rate = (participants_actuels / participants_objectif * 100) if participants_objectif > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Taux de participation", f"{participation_rate:.1f}%")
            st.progress(participation_rate/100)
        
        with col2:
            st.metric("Participants inscrits", f"{participants_actuels}/{participants_objectif}")
            max_participants = 1000
            st.caption(f"Capacité maximale: {max_participants} personnes")
        
        # Actions recommandées
        st.subheader("Actions recommandées")
        if participation_rate < 70:
            st.error("Niveau d'alerte : CRITIQUE")
            st.markdown("""
            - Intensifier la communication sur l'événement
            - Contacter directement les réseaux communautaires
            - Envisager des incitations pour encourager la participation
            """)
        elif participation_rate < 90:
            st.warning("Niveau d'alerte : MODÉRÉ")
            st.markdown("""
            - Relancer la campagne de communication
            - Demander aux participants confirmés d'inviter d'autres personnes
            """)
        else:
            st.success("Niveau d'alerte : MINEUR")
            st.markdown("""
            - Maintenir la communication régulière
            - Préparer un plan de gestion des flux en cas de forte affluence
            """)
    
    with risk_detail_tabs[3]:
        st.markdown("### R04: Conditions extrêmes")
        
        # Weather validation status
        meteo_periods = ["S9", "S10", "S11"]
        current_in_critical = selected_period in meteo_periods
        
        col1, col2 = st.columns(2)
        with col1:
            if current_in_critical:
                st.error("🌩️ Période critique pour validation météo")
            else:
                st.success("☀️ Hors période critique pour validation météo")
        
        # Display weather status for critical periods
        st.subheader("État des prévisions météo")
        for period in meteo_periods:
            is_validated = period < selected_period
            is_current = period == selected_period
            
            status = "✅ Validée" if is_validated else "⏳ En attente" if is_current else "❌ Non validée"
            color = "green" if is_validated else "orange" if is_current else "red"
            
            st.markdown(f"**{period}**: <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
        
        # Actions recommandées
        st.subheader("Actions recommandées")
        if current_in_critical:
            st.error("Niveau d'alerte : CRITIQUE")
            st.markdown("""
            - Consulter quotidiennement les prévisions météorologiques
            - Préparer un plan B en cas de météo défavorable
            - Vérifier la disponibilité d'espaces couverts
            """)
        else:
            st.success("Niveau d'alerte : MINEUR")
            st.markdown("""
            - Maintenir une surveillance régulière des prévisions
            - S'assurer que le plan B est toujours viable si nécessaire
            """)

# Tab 5: Team
with tabs[4]:
    st.header("Gestion de l'Équipe")
    
    # Team state data for current period
    team_data = data["team_states"]
    team_period_index = periods.index(selected_period)
    
    # Get team stats
    team_stats = {}
    total_members = 0
    for member, states in team_data.items():
        state = states[team_period_index]
        total_members += 1 if state != 0 else 0  # Don't count absent members
        state_name = ["Absent", "Formation", "Confrontation", "Normalisation", "Performance"][state]
        team_stats[state_name] = team_stats.get(state_name, 0) + 1
    
    # Display team metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Membres actifs", total_members - team_stats.get("Absent", 0))
    col2.metric("En performance", team_stats.get("Performance", 0))
    col3.metric("En formation", team_stats.get("Formation", 0) + team_stats.get("Confrontation", 0))
    col4.metric("Absents", team_stats.get("Absent", 0))
    
    # Team composition pie chart
    st.subheader("Composition de l'équipe par état")
    st.caption("Répartition des membres de l'équipe par état")
    team_composition = []
    for state, count in team_stats.items():
        if state != "Absent":  # Include only active states
            team_composition.append({
                "État": state,
                "Nombre": count
            })
    
    team_comp_df = pd.DataFrame(team_composition)
    
    fig = px.pie(
        team_comp_df,
        values="Nombre",
        names="État",
        color="État",
        color_discrete_map={
            "Formation": COLOR_PALETTE["jaune_pale"],
            "Confrontation": COLOR_PALETTE["jaune"], 
            "Normalisation": COLOR_PALETTE["orange"],
            "Performance": COLOR_PALETTE["vert"]
        }
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Team evolution
    st.subheader("Évolution de l'équipe")
    st.caption("Analyse de l'évolution des membres de l'équipe au fil des périodes")
    
    # Calculate team state evolution
    team_evolution = []
    for period_idx, period in enumerate(periods[:selected_period_index+1]):
        period_stats = {"Formation": 0, "Confrontation": 0, "Normalisation": 0, "Performance": 0}
        for member, states in team_data.items():
            state = states[period_idx]
            if state > 0:  # Skip absent members
                state_name = ["", "Formation", "Confrontation", "Normalisation", "Performance"][state]
                period_stats[state_name] += 1
                
        team_evolution.append({
            "Période": period,
            "Performance": period_stats["Performance"],
            "Normalisation": period_stats["Normalisation"],
            "Confrontation": period_stats["Confrontation"],
            "Formation": period_stats["Formation"]
        })
    
    team_evolution_df = pd.DataFrame(team_evolution)
    
    fig = px.area(
        team_evolution_df,
        x="Période",
        y=["Performance", "Normalisation", "Confrontation", "Formation"],
        color_discrete_map={
            "Performance": "#2ecc71",
            "Normalisation": "#9b59b6",
            "Confrontation": "#f39c12",
            "Formation": "#3498db"
        }
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Nombre de membres",
        xaxis_title="Période"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Team member status
    st.subheader("État des membres de l'équipe")
    st.caption("Analyse de l'état des membres de l'équipe pour la période actuelle")
    
    # Create member status table
    member_status = []
    for member, states in team_data.items():
        state = states[team_period_index]
        state_name = ["Absent", "Formation", "Confrontation", "Normalisation", "Performance"][state]
        
        # Calculate trend by comparing with previous period
        prev_state = states[max(0, team_period_index-1)]
        if state > prev_state:
            trend = "↑"
        elif state < prev_state:
            trend = "↓"
        else:
            trend = "→"
            
        member_status.append({
            "Membre": member,
            "État": state_name,
            "Tendance": trend
        })
    
    member_status_df = pd.DataFrame(member_status)
    
    st.dataframe(
        member_status_df,
        hide_index=True,
        use_container_width=True
    )