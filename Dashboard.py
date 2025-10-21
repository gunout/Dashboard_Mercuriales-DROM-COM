# dashboard_daaf_mercuriales_drom_com.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
from functools import lru_cache
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Mercuriales DAAF - DROM-COM",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #28a745, #17a2b8, #ffc107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #28a745;
        border-bottom: 2px solid #17a2b8;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .product-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #28a745;
        background-color: #f8f9fa;
    }
    .price-change {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .positive { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
    .negative { background-color: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
    .neutral { background-color: #e2e3e5; border-left: 4px solid #6c757d; color: #383d41; }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .territory-flag {
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        color: white;
    }
    .reunion-flag { background: linear-gradient(90deg, #0055A4 33%, #EF4135 33%, #EF4135 66%, #FFFFFF 66%); }
    .guadeloupe-flag { background: linear-gradient(90deg, #ED2939 50%, #002395 50%); }
    .martinique-flag { background: linear-gradient(90deg, #009739 33%, #002395 33%, #002395 66%, #FCD116 66%); }
    .guyane-flag { background: linear-gradient(90deg, #009739 50%, #FCD116 50%); }
    .mayotte-flag { background: linear-gradient(90deg, #FFFFFF 25%, #ED2939 25%, #ED2939 50%, #002395 50%, #002395 75%, #FCD116 75%); }
    .spierre-flag { background: linear-gradient(90deg, #002395 33%, #FFFFFF 33%, #FFFFFF 66%, #ED2939 66%); }
    .stbarth-flag { background: linear-gradient(90deg, #FFFFFF 50%, #FCD116 50%); }
    .stmartin-flag { background: linear-gradient(90deg, #ED2939 50%, #002395 50%); }
    .wallis-flag { background: linear-gradient(90deg, #ED2939 33%, #002395 33%, #002395 66%, #FCD116 66%); }
    .polynesie-flag { background: linear-gradient(90deg, #ED2939 25%, #FFFFFF 25%, #FFFFFF 50%, #FCD116 50%, #FCD116 75%, #002395 75%); }
    .caledonie-flag { background: linear-gradient(90deg, #002395 33%, #FCD116 33%, #FCD116 66%, #ED2939 66%); }
    .territory-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #28a745;
        margin-bottom: 1rem;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    .seasonal-indicator {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .high-season { background-color: #dc3545; color: white; }
    .medium-season { background-color: #ffc107; color: black; }
    .low-season { background-color: #28a745; color: white; }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'territories_data' not in st.session_state:
    st.session_state.territories_data = {}
if 'selected_territory' not in st.session_state:
    st.session_state.selected_territory = 'REUNION'
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Fonctions globales avec cache
@st.cache_data(ttl=3600)
def get_territories_definitions():
    """Définit les territoires DROM-COM"""
    return {
        'REUNION': {
            'nom_complet': 'La Réunion',
            'type': 'DROM',
            'population': 860000,
            'superficie': 2511,
            'pib': 19.8,
            'drapeau': 'reunion-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'GUADELOUPE': {
            'nom_complet': 'Guadeloupe',
            'type': 'DROM',
            'population': 384000,
            'superficie': 1628,
            'pib': 9.1,
            'drapeau': 'guadeloupe-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'MARTINIQUE': {
            'nom_complet': 'Martinique',
            'type': 'DROM',
            'population': 376000,
            'superficie': 1128,
            'pib': 8.9,
            'drapeau': 'martinique-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'GUYANE': {
            'nom_complet': 'Guyane',
            'type': 'DROM',
            'population': 290000,
            'superficie': 83534,
            'pib': 4.8,
            'drapeau': 'guyane-flag',
            'monnaie': 'EUR',
            'climat': 'Équatorial'
        },
        'MAYOTTE': {
            'nom_complet': 'Mayotte',
            'type': 'DROM',
            'population': 270000,
            'superficie': 374,
            'pib': 2.4,
            'drapeau': 'mayotte-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'STPIERRE': {
            'nom_complet': 'Saint-Pierre-et-Miquelon',
            'type': 'COM',
            'population': 6000,
            'superficie': 242,
            'pib': 0.2,
            'drapeau': 'spierre-flag',
            'monnaie': 'EUR',
            'climat': 'Océanique'
        },
        'STBARTH': {
            'nom_complet': 'Saint-Barthélemy',
            'type': 'COM',
            'population': 10000,
            'superficie': 21,
            'pib': 0.6,
            'drapeau': 'stbarth-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'STMARTIN': {
            'nom_complet': 'Saint-Martin',
            'type': 'COM',
            'population': 32000,
            'superficie': 54,
            'pib': 0.9,
            'drapeau': 'stmartin-flag',
            'monnaie': 'EUR',
            'climat': 'Tropical'
        },
        'WALLIS': {
            'nom_complet': 'Wallis-et-Futuna',
            'type': 'COM',
            'population': 11500,
            'superficie': 142,
            'pib': 0.2,
            'drapeau': 'wallis-flag',
            'monnaie': 'XPF',
            'climat': 'Tropical'
        },
        'POLYNESIE': {
            'nom_complet': 'Polynésie française',
            'type': 'COM',
            'population': 280000,
            'superficie': 4167,
            'pib': 7.2,
            'drapeau': 'polynesie-flag',
            'monnaie': 'XPF',
            'climat': 'Tropical'
        },
        'CALEDONIE': {
            'nom_complet': 'Nouvelle-Calédonie',
            'type': 'COM',
            'population': 271000,
            'superficie': 18575,
            'pib': 9.7,
            'drapeau': 'caledonie-flag',
            'monnaie': 'XPF',
            'climat': 'Tropical'
        }
    }

@st.cache_data(ttl=3600)
def get_produits_definitions(territory_code):
    """Définit les produits agricoles et alimentaires pour un territoire donné"""
    # Facteurs d'ajustement selon le territoire
    territory_factor = {
        'REUNION': 1.0,
        'GUADELOUPE': 1.05,
        'MARTINIQUE': 1.08,
        'GUYANE': 1.15,
        'MAYOTTE': 1.12,
        'STPIERRE': 1.25,
        'STBARTH': 1.35,
        'STMARTIN': 1.30,
        'WALLIS': 1.20,
        'POLYNESIE': 1.18,
        'CALEDONIE': 1.10
    }
    
    factor = territory_factor.get(territory_code, 1.0)
    
    # Produits de base avec ajustements selon le territoire
    produits_base = {
        'BANANE': {
            'nom_complet': 'Banane',
            'categorie': 'Fruits',
            'sous_categorie': 'Fruits locaux',
            'unite': 'kg',
            'prix_moyen': 2.8 * factor,
            'prix_min': 1.8 * factor,
            'prix_max': 4.2 * factor,
            'couleur': '#FFD700',
            'production_locale': 0.85,
            'importation': 0.15,
            'saisonnalite': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Disponible toute l'année
            'description': 'Banane locale, variétés différentes selon territoires'
        },
        'ANANAS': {
            'nom_complet': 'Ananas',
            'categorie': 'Fruits',
            'sous_categorie': 'Fruits tropicaux',
            'unite': 'pièce',
            'prix_moyen': 3.2 * factor,
            'prix_min': 2.0 * factor,
            'prix_max': 5.5 * factor,
            'couleur': '#FFA500',
            'production_locale': 0.90,
            'importation': 0.10,
            'saisonnalite': [0.8, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.8, 0.8, 0.8],
            'description': 'Ananas Victoria et autres variétés locales'
        },
        'MANGUE': {
            'nom_complet': 'Mangue',
            'categorie': 'Fruits',
            'sous_categorie': 'Fruits tropicaux',
            'unite': 'kg',
            'prix_moyen': 4.5 * factor,
            'prix_min': 2.5 * factor,
            'prix_max': 8.0 * factor,
            'couleur': '#FF8C00',
            'production_locale': 0.95,
            'importation': 0.05,
            'saisonnalite': [0.2, 0.2, 0.3, 0.6, 0.9, 1.0, 1.0, 0.9, 0.7, 0.4, 0.3, 0.2],
            'description': 'Mangues locales, saison de décembre à mars'
        },
        'LETTUCE': {
            'nom_complet': 'Laitue',
            'categorie': 'Légumes',
            'sous_categorie': 'Légumes feuilles',
            'unite': 'pièce',
            'prix_moyen': 1.8 * factor,
            'prix_min': 1.2 * factor,
            'prix_max': 3.0 * factor,
            'couleur': '#90EE90',
            'production_locale': 0.70,
            'importation': 0.30,
            'saisonnalite': [0.8, 0.8, 0.9, 1.0, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.0, 0.9],
            'description': 'Laitue cultivée localement'
        },
        'TOMATE': {
            'nom_complet': 'Tomate',
            'categorie': 'Légumes',
            'sous_categorie': 'Légumes fruits',
            'unite': 'kg',
            'prix_moyen': 3.5 * factor,
            'prix_min': 2.0 * factor,
            'prix_max': 6.0 * factor,
            'couleur': '#FF6347',
            'production_locale': 0.80,
            'importation': 0.20,
            'saisonnalite': [0.7, 0.7, 0.8, 0.9, 1.0, 1.0, 0.9, 0.8, 0.9, 1.0, 0.9, 0.8],
            'description': 'Tomates locales, différentes variétés'
        },
        'CAROTTE': {
            'nom_complet': 'Carotte',
            'categorie': 'Légumes',
            'sous_categorie': 'Légumes racines',
            'unite': 'kg',
            'prix_moyen': 2.8 * factor,
            'prix_min': 1.8 * factor,
            'prix_max': 4.5 * factor,
            'couleur': '#FFA500',
            'production_locale': 0.60,
            'importation': 0.40,
            'saisonnalite': [0.9, 0.9, 1.0, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0, 0.9],
            'description': 'Carottes locales et importées'
        },
        'POULET': {
            'nom_complet': 'Poulet',
            'categorie': 'Viandes',
            'sous_categorie': 'Volaille',
            'unite': 'kg',
            'prix_moyen': 12.5 * factor,
            'prix_min': 9.0 * factor,
            'prix_max': 18.0 * factor,
            'couleur': '#F4A460',
            'production_locale': 0.75,
            'importation': 0.25,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Poulet local et importé'
        },
        'POISSON': {
            'nom_complet': 'Poisson frais',
            'categorie': 'Poissons',
            'sous_categorie': 'Produits mer',
            'unite': 'kg',
            'prix_moyen': 18.0 * factor,
            'prix_min': 12.0 * factor,
            'prix_max': 25.0 * factor,
            'couleur': '#1E90FF',
            'production_locale': 0.95,
            'importation': 0.05,
            'saisonnalite': [0.9, 0.9, 1.0, 1.0, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0],
            'description': 'Poissons pêchés localement'
        },
        'RIZ': {
            'nom_complet': 'Riz',
            'categorie': 'Céréales',
            'sous_categorie': 'Base alimentaire',
            'unite': 'kg',
            'prix_moyen': 2.2 * factor,
            'prix_min': 1.5 * factor,
            'prix_max': 3.5 * factor,
            'couleur': '#FFF8DC',
            'production_locale': 0.20,
            'importation': 0.80,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Riz importé majoritairement'
        },
        'PAIN': {
            'nom_complet': 'Pain',
            'categorie': 'Boulangerie',
            'sous_categorie': 'Pains',
            'unite': 'pièce',
            'prix_moyen': 1.5 * factor,
            'prix_min': 1.0 * factor,
            'prix_max': 2.5 * factor,
            'couleur': '#D2B48C',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Pain traditionnel local'
        }
    }
    
    # Produits spécifiques selon le territoire
    if territory_code == 'POLYNESIE':
        produits_base['NOIX_COCO'] = {
            'nom_complet': 'Noix de coco',
            'categorie': 'Fruits',
            'sous_categorie': 'Fruits tropicaux',
            'unite': 'pièce',
            'prix_moyen': 1.5 * factor,
            'prix_min': 1.0 * factor,
            'prix_max': 2.5 * factor,
            'couleur': '#8B4513',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Noix de coco fraîche'
        }
        produits_base['POISSON_CRU'] = {
            'nom_complet': 'Poisson cru',
            'categorie': 'Poissons',
            'sous_categorie': 'Spécialités',
            'unite': 'kg',
            'prix_moyen': 22.0 * factor,
            'prix_min': 15.0 * factor,
            'prix_max': 30.0 * factor,
            'couleur': '#4682B4',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Poisson cru mariné (spécialité polynésienne)'
        }
    
    elif territory_code == 'CALEDONIE':
        produits_base['IGNAME'] = {
            'nom_complet': 'Ignames',
            'categorie': 'Légumes',
            'sous_categorie': 'Tubercules',
            'unite': 'kg',
            'prix_moyen': 3.8 * factor,
            'prix_min': 2.5 * factor,
            'prix_max': 6.0 * factor,
            'couleur': '#8B7355',
            'production_locale': 0.95,
            'importation': 0.05,
            'saisonnalite': [0.8, 0.8, 0.9, 1.0, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.0, 0.9],
            'description': 'Ignames locales, aliment de base traditionnel'
        }
        produits_base['BOUGNA'] = {
            'nom_complet': 'Bougna',
            'categorie': 'Plats préparés',
            'sous_categorie': 'Traditionnel',
            'unite': 'portion',
            'prix_moyen': 15.0 * factor,
            'prix_min': 12.0 * factor,
            'prix_max': 20.0 * factor,
            'couleur': '#A0522D',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Plat traditionnel kanak'
        }
    
    elif territory_code == 'GUYANE':
        produits_base['MANIOC'] = {
            'nom_complet': 'Manioc',
            'categorie': 'Légumes',
            'sous_categorie': 'Tubercules',
            'unite': 'kg',
            'prix_moyen': 2.5 * factor,
            'prix_min': 1.5 * factor,
            'prix_max': 4.0 * factor,
            'couleur': '#D2691E',
            'production_locale': 0.90,
            'importation': 0.10,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Manioc, aliment de base en Guyane'
        }
        produits_base['COUAC'] = {
            'nom_complet': 'Couac',
            'categorie': 'Céréales',
            'sous_categorie': 'Transformés',
            'unite': 'kg',
            'prix_moyen': 4.0 * factor,
            'prix_min': 3.0 * factor,
            'prix_max': 6.0 * factor,
            'couleur': '#F5DEB3',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Semoule de manioc'
        }
    
    elif territory_code in ['REUNION', 'MAYOTTE']:
        produits_base['LITCHI'] = {
            'nom_complet': 'Litchi',
            'categorie': 'Fruits',
            'sous_categorie': 'Fruits tropicaux',
            'unite': 'kg',
            'prix_moyen': 6.5 * factor,
            'prix_min': 4.0 * factor,
            'prix_max': 10.0 * factor,
            'couleur': '#FF69B4',
            'production_locale': 0.98,
            'importation': 0.02,
            'saisonnalite': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.3, 0.7, 1.0, 0.5],
            'description': 'Litchis de saison (novembre-décembre)'
        }
        produits_base['VANILLE'] = {
            'nom_complet': 'Vanille',
            'categorie': 'Épices',
            'sous_categorie': 'Luxe',
            'unite': 'g',
            'prix_moyen': 0.8 * factor,
            'prix_min': 0.5 * factor,
            'prix_max': 1.5 * factor,
            'couleur': '#8B4513',
            'production_locale': 1.00,
            'importation': 0.00,
            'saisonnalite': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'description': 'Vanille Bourbon de qualité'
        }
    
    return produits_base

@st.cache_data(ttl=1800)
def generate_historical_data(territory_code, produits):
    """Génère les données historiques de prix"""
    dates = pd.date_range('2022-01-01', datetime.now(), freq='W')
    data = []
    
    for date in dates:
        # Impact saisonnier et variations
        current_month = date.month
        
        for produit_code, info in produits.items():
            # Coefficient saisonnier
            seasonal_factor = info['saisonnalite'][current_month - 1]
            
            # Variation aléatoire
            random_variation = random.uniform(0.9, 1.1)
            
            # Prix calculé avec saisonnalité et variation
            prix_courant = info['prix_moyen'] * seasonal_factor * random_variation
            prix_courant = max(info['prix_min'], min(info['prix_max'], prix_courant))
            
            # Volume de transaction simulé
            volume = random.uniform(1000, 5000) * seasonal_factor
            
            data.append({
                'date': date,
                'territoire': territory_code,
                'produit': produit_code,
                'prix_moyen': prix_courant,
                'volume_transaction': volume,
                'categorie': info['categorie'],
                'sous_categorie': info['sous_categorie'],
                'unite': info['unite'],
                'saisonnalite': seasonal_factor
            })
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def generate_current_data(territory_code, produits, historical_data):
    """Génère les données courantes de prix"""
    current_data = []
    current_date = datetime.now()
    current_month = current_date.month
    
    for produit_code, info in produits.items():
        # Dernières données historiques
        last_data = historical_data[historical_data['produit'] == produit_code].iloc[-1]
        
        # Variation hebdomadaire simulée
        change_pct = random.uniform(-0.05, 0.05)
        prix_courant = last_data['prix_moyen'] * (1 + change_pct)
        
        # Saisonnalité actuelle
        seasonal_factor = info['saisonnalite'][current_month - 1]
        
        current_data.append({
            'territoire': territory_code,
            'produit': produit_code,
            'nom_complet': info['nom_complet'],
            'categorie': info['categorie'],
            'sous_categorie': info['sous_categorie'],
            'unite': info['unite'],
            'prix_courant': prix_courant,
            'variation_pct': change_pct * 100,
            'prix_moyen_historique': info['prix_moyen'],
            'prix_min_historique': info['prix_min'],
            'prix_max_historique': info['prix_max'],
            'production_locale': info['production_locale'] * 100,
            'importation': info['importation'] * 100,
            'volume_transaction': last_data['volume_transaction'] * random.uniform(0.9, 1.1),
            'saisonnalite_actuelle': seasonal_factor,
            'couleur': info['couleur'],
            'description': info['description']
        })
    
    return pd.DataFrame(current_data)

@st.cache_data(ttl=600)
def generate_market_data(territory_code):
    """Génère les données par marché"""
    marches_base = [
        {'marché': 'Marché Central', 'ville': 'Saint-Denis', 'type': 'Couvert', 'superficie': 2500, 'nombre_vendeurs': 85},
        {'marché': 'Marché Forain', 'ville': 'Saint-Pierre', 'type': 'Plein air', 'superficie': 1800, 'nombre_vendeurs': 65},
        {'marché': 'Marché de Quartier', 'ville': 'Le Port', 'type': 'Semi-couvert', 'superficie': 1200, 'nombre_vendeurs': 45},
        {'marché': 'Marché Agricole', 'ville': 'Saint-Paul', 'type': 'Plein air', 'superficie': 2000, 'nombre_vendeurs': 70},
        {'marché': 'Marché Bio', 'ville': 'Saint-Denis', 'type': 'Couvert', 'superficie': 800, 'nombre_vendeurs': 25},
    ]
    
    # Ajustement selon le territoire
    territory_adjustment = {
        'REUNION': 1.0, 'GUADELOUPE': 0.9, 'MARTINIQUE': 0.9, 'GUYANE': 0.7,
        'MAYOTTE': 0.6, 'STPIERRE': 0.3, 'STBARTH': 0.4, 'STMARTIN': 0.5,
        'WALLIS': 0.4, 'POLYNESIE': 0.8, 'CALEDONIE': 0.85
    }
    
    factor = territory_adjustment.get(territory_code, 1.0)
    for marche in marches_base:
        marche['superficie'] *= factor
        marche['nombre_vendeurs'] = int(marche['nombre_vendeurs'] * factor)
    
    return pd.DataFrame(marches_base)

@st.cache_data(ttl=3600)
def generate_comparison_data(territories):
    """Génère les données de comparaison entre territoires"""
    comparison_data = []
    
    for territory_code, territory_info in territories.items():
        produits = get_produits_definitions(territory_code)
        
        # Calcul des indicateurs moyens
        prix_moyen_total = np.mean([p['prix_moyen'] for p in produits.values()])
        production_locale_moyenne = np.mean([p['production_locale'] for p in produits.values()]) * 100
        nombre_produits = len(produits)
        
        # Indice des prix (normalisé)
        indice_prix = prix_moyen_total / 3.5  # Base de référence
        
        comparison_data.append({
            'territoire': territory_code,
            'nom_complet': territory_info['nom_complet'],
            'type': territory_info['type'],
            'population': territory_info['population'],
            'superficie': territory_info['superficie'],
            'pib': territory_info['pib'],
            'prix_moyen_total': prix_moyen_total,
            'production_locale_moyenne': production_locale_moyenne,
            'nombre_produits': nombre_produits,
            'indice_prix': indice_prix,
            'climat': territory_info['climat']
        })
    
    return pd.DataFrame(comparison_data)

class MercurialesDashboard:
    def __init__(self):
        self.territories = get_territories_definitions()
        
    def get_territory_data(self, territory_code):
        """Récupère les données d'un territoire avec cache"""
        if territory_code not in st.session_state.territories_data:
            with st.spinner(f"Chargement des données pour {self.territories[territory_code]['nom_complet']}..."):
                produits = get_produits_definitions(territory_code)
                historical_data = generate_historical_data(territory_code, produits)
                current_data = generate_current_data(territory_code, produits, historical_data)
                market_data = generate_market_data(territory_code)
                
                st.session_state.territories_data[territory_code] = {
                    'produits': produits,
                    'historical_data': historical_data,
                    'current_data': current_data,
                    'market_data': market_data,
                    'last_update': datetime.now()
                }
        
        return st.session_state.territories_data[territory_code]
    
    def update_live_data(self, territory_code):
        """Met à jour les données en temps réel"""
        if territory_code in st.session_state.territories_data:
            data = st.session_state.territories_data[territory_code]
            current_data = data['current_data'].copy()
            
            # Mise à jour légère des prix
            for idx in current_data.index:
                if random.random() < 0.2:  # 20% de chance de changement
                    variation = random.uniform(-0.03, 0.03)
                    current_data.loc[idx, 'prix_courant'] *= (1 + variation)
                    current_data.loc[idx, 'variation_pct'] = variation * 100
                    current_data.loc[idx, 'volume_transaction'] *= random.uniform(0.95, 1.05)
            
            st.session_state.territories_data[territory_code]['current_data'] = current_data
            st.session_state.territories_data[territory_code]['last_update'] = datetime.now()
    
    def display_territory_selector(self):
        """Affiche le sélecteur de territoire optimisé"""
        st.markdown('<div class="territory-selector">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            territory_options = {v['nom_complet']: k for k, v in self.territories.items()}
            
            # Utilisation de session_state pour éviter le rerun
            current_name = self.territories[st.session_state.selected_territory]['nom_complet']
            selected_territory_name = st.selectbox(
                "🌍 SÉLECTIONNEZ UN TERRITOIRE:",
                options=list(territory_options.keys()),
                index=list(territory_options.keys()).index(current_name),
                key="territory_selector_main"
            )
            
            new_territory = territory_options[selected_territory_name]
            if new_territory != st.session_state.selected_territory:
                st.session_state.selected_territory = new_territory
                # Précharger les données en arrière-plan
                self.get_territory_data(new_territory)
                st.success(f"✅ Changement vers {selected_territory_name} effectué!")
        
        with col2:
            territory_info = self.territories[st.session_state.selected_territory]
            st.metric("Type", territory_info['type'])
        
        with col3:
            st.metric("Population", f"{territory_info['population']:,}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        territory_info = self.territories[st.session_state.selected_territory]
        
        st.markdown(f'<h1 class="main-header">🏪 Dashboard Mercuriales DAAF - {territory_info["nom_complet"]}</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 DONNÉES MARCHÉS EN TEMPS RÉEL</div>', 
                       unsafe_allow_html=True)
            st.markdown(f"**Surveillance et analyse des prix des produits agricoles et alimentaires**")
        
        # Bannière drapeau du territoire
        st.markdown(f"""
        <div class="territory-flag {territory_info['drapeau']}">
            <strong>{territory_info['nom_complet']} - Mercuriales DAAF</strong><br>
            <small>Type: {territory_info['type']} | Population: {territory_info['population']:,} | Climat: {territory_info['climat']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés des mercuriales"""
        data = self.get_territory_data(st.session_state.selected_territory)
        current_data = data['current_data']
        
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS MERCURIALES</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques
        prix_moyen_total = current_data['prix_courant'].mean()
        variation_moyenne = current_data['variation_pct'].mean()
        produits_hausse = len(current_data[current_data['variation_pct'] > 0])
        production_locale_moyenne = current_data['production_locale'].mean()
        
        # Indice de saisonnalité moyen
        saisonnalite_moyenne = current_data['saisonnalite_actuelle'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Prix Moyen des Produits",
                f"{prix_moyen_total:.2f}€",
                f"{variation_moyenne:+.2f}%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Produits en Hausse",
                f"{produits_hausse}/{len(current_data)}",
                f"{produits_hausse - (len(current_data) - produits_hausse):+d} vs baisse"
            )
        
        with col3:
            st.metric(
                "Taux Production Locale",
                f"{production_locale_moyenne:.1f}%",
                f"{random.uniform(-2, 3):.1f}% vs période précédente"
            )
        
        with col4:
            saison_indicator = "Haute" if saisonnalite_moyenne > 0.8 else "Basse" if saisonnalite_moyenne < 0.5 else "Moyenne"
            st.metric(
                "Saisonnalité Moyenne",
                saison_indicator,
                f"{(saisonnalite_moyenne-0.5)*100:+.1f}% vs moyenne"
            )
        
        # Métriques spécifiques au territoire
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Nombre de Produits Suivis",
                f"{len(current_data)}",
                f"{random.randint(0, 5)} vs mois dernier"
            )
        
        with col2:
            st.metric(
                "Indice de Diversité",
                f"{(len(current_data['categorie'].unique()) / len(current_data)) * 100:.1f}%",
                f"{random.uniform(-1, 2):.1f}%"
            )
        
        with col3:
            st.metric(
                "Volumes Transactions",
                f"{current_data['volume_transaction'].sum()/1000:.0f}K",
                f"{random.randint(-8, 12)}% vs semaine dernière"
            )
    
    def create_mercuriales_overview(self):
        """Crée la vue d'ensemble des mercuriales"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE MERCURIALES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Évolution Prix", "Répartition Catégories", "Top Produits", "Analyse Saisonnalité"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution des prix moyens
                evolution_totale = data['historical_data'].groupby('date')['prix_moyen'].mean().reset_index()
                
                fig = px.line(evolution_totale, 
                             x='date', 
                             y='prix_moyen',
                             title=f'Évolution du Prix Moyen - {self.territories[st.session_state.selected_territory]["nom_complet"]}',
                             color_discrete_sequence=['#28a745'])
                fig.update_layout(yaxis_title="Prix Moyen (€)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Performance par catégorie
                performance_categories = data['current_data'].groupby('categorie').agg({
                    'variation_pct': 'mean',
                    'prix_courant': 'mean'
                }).reset_index()
                
                fig = px.bar(performance_categories, 
                            x='categorie', 
                            y='variation_pct',
                            title='Variation Hebdomadaire par Catégorie (%)',
                            color='categorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Variation (%)")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(data['current_data'], 
                            values='prix_courant', 
                            names='categorie',
                            title='Répartition des Prix par Catégorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(data['current_data'], 
                            x='categorie', 
                            y='volume_transaction',
                            title='Volume de Transactions par Catégorie',
                            color='categorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Volume de Transactions")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                top_cher = data['current_data'].nlargest(10, 'prix_courant')
                fig = px.bar(top_cher, 
                            x='prix_courant', 
                            y='produit',
                            orientation='h',
                            title='Top 10 des Produits les Plus Chers',
                            color='prix_courant',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                top_croissance = data['current_data'].nlargest(10, 'variation_pct')
                fig = px.bar(top_croissance, 
                            x='variation_pct', 
                            y='produit',
                            orientation='h',
                            title='Top 10 des Hausses de Prix (%)',
                            color='variation_pct',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab4:
            st.subheader("Analyse de la Saisonnalité des Prix")
            
            # Heatmap de saisonnalité
            seasonal_analysis = data['historical_data'].copy()
            seasonal_analysis['mois'] = seasonal_analysis['date'].dt.month
            seasonal_analysis['annee'] = seasonal_analysis['date'].dt.year
            
            heatmap_data = seasonal_analysis.pivot_table(
                index='produit',
                columns='mois',
                values='saisonnalite',
                aggfunc='mean'
            )
            
            fig = px.imshow(heatmap_data,
                           title='Saisonnalité des Produits par Mois',
                           color_continuous_scale='Blues',
                           aspect="auto")
            fig.update_layout(xaxis_title="Mois", yaxis_title="Produit")
            fig.update_xaxes(tickvals=list(range(12)), 
                           ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Dec'])
            st.plotly_chart(fig, config={'displayModeBar': False})
    
    def create_produits_live(self):
        """Affiche les produits en temps réel"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">🏪 PRODUITS ALIMENTAIRES EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Tableau des Prix", "Analyse Catégorie", "Simulateur Panier"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                categorie_filtre = st.selectbox("Catégorie:", 
                                              ['Toutes'] + list(data['current_data']['categorie'].unique()))
            with col2:
                performance_filtre = st.selectbox("Performance:", 
                                                ['Tous', 'En hausse', 'En baisse', 'Stable'])
            with col3:
                tri_filtre = st.selectbox("Trier par:", 
                                        ['Prix courant', 'Variation %', 'Volume transaction', 'Production locale'])
            
            # Application des filtres
            produits_filtres = data['current_data'].copy()
            if categorie_filtre != 'Toutes':
                produits_filtres = produits_filtres[produits_filtres['categorie'] == categorie_filtre]
            if performance_filtre == 'En hausse':
                produits_filtres = produits_filtres[produits_filtres['variation_pct'] > 0]
            elif performance_filtre == 'En baisse':
                produits_filtres = produits_filtres[produits_filtres['variation_pct'] < 0]
            elif performance_filtre == 'Stable':
                produits_filtres = produits_filtres[produits_filtres['variation_pct'] == 0]
            
            # Tri
            if tri_filtre == 'Prix courant':
                produits_filtres = produits_filtres.sort_values('prix_courant', ascending=False)
            elif tri_filtre == 'Variation %':
                produits_filtres = produits_filtres.sort_values('variation_pct', ascending=False)
            elif tri_filtre == 'Volume transaction':
                produits_filtres = produits_filtres.sort_values('volume_transaction', ascending=False)
            elif tri_filtre == 'Production locale':
                produits_filtres = produits_filtres.sort_values('production_locale', ascending=False)
            
            # Affichage optimisé
            for _, produit in produits_filtres.iterrows():
                change_class = "positive" if produit['variation_pct'] > 0 else "negative" if produit['variation_pct'] < 0 else "neutral"
                saison_class = "high-season" if produit['saisonnalite_actuelle'] > 0.8 else "low-season" if produit['saisonnalite_actuelle'] < 0.5 else "medium-season"
                saison_text = "Haute" if produit['saisonnalite_actuelle'] > 0.8 else "Basse" if produit['saisonnalite_actuelle'] < 0.5 else "Moyenne"
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{produit['produit']}**")
                    st.markdown(f"*{produit['categorie']}*")
                with col2:
                    st.markdown(f"**{produit['nom_complet']}**")
                    st.markdown(f"Unité: {produit['unite']}")
                    st.markdown(f"<span class='seasonal-indicator {saison_class}'>{saison_text} saison</span>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"**{produit['prix_courant']:.2f}€**")
                    st.markdown(f"Prod. locale: {produit['production_locale']:.0f}%")
                with col4:
                    variation_str = f"{produit['variation_pct']:+.2f}%"
                    st.markdown(f"**{variation_str}**")
                    st.markdown(f"Vol: {produit['volume_transaction']:,.0f}")
                with col5:
                    st.markdown(f"<div class='price-change {change_class}'>{variation_str}</div>", 
                               unsafe_allow_html=True)
                    st.markdown(f"Local: {produit['production_locale']:.0f}%")
                
                st.markdown("---")
        
        with tab2:
            categorie_selectionnee = st.selectbox("Sélectionnez une catégorie:", 
                                                data['current_data']['categorie'].unique(), key="cat_analysis")
            
            if categorie_selectionnee:
                produits_categorie = data['current_data'][
                    data['current_data']['categorie'] == categorie_selectionnee
                ]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(produits_categorie, 
                                x='produit', 
                                y='variation_pct',
                                title=f'Variation des Prix - {categorie_selectionnee}',
                                color='variation_pct',
                                color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                with col2:
                    fig = px.pie(produits_categorie, 
                                values='prix_courant', 
                                names='produit',
                                title=f'Répartition des Prix - {categorie_selectionnee}')
                    st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Simulateur de Panier Alimentaire")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🛒 Composition du Panier")
                panier_produits = {}
                
                for produit in data['current_data'].itertuples():
                    quantite = st.number_input(
                        f"{produit.nom_complet} ({produit.unite})",
                        min_value=0.0,
                        value=0.0,
                        step=0.5,
                        key=f"panier_{produit.produit}"
                    )
                    if quantite > 0:
                        panier_produits[produit.produit] = {
                            'nom': produit.nom_complet,
                            'prix': produit.prix_courant,
                            'quantite': quantite,
                            'unite': produit.unite
                        }
            
            with col2:
                st.markdown("### 💰 Calcul du Coût")
                
                if panier_produits:
                    cout_total = 0
                    details_panier = []
                    
                    for produit_id, info in panier_produits.items():
                        cout_produit = info['prix'] * info['quantite']
                        cout_total += cout_produit
                        details_panier.append({
                            'Produit': info['nom'],
                            'Quantité': f"{info['quantite']} {info['unite']}",
                            'Prix Unitaire': f"{info['prix']:.2f}€",
                            'Coût': f"{cout_produit:.2f}€"
                        })
                    
                    details_df = pd.DataFrame(details_panier)
                    st.dataframe(details_df, use_container_width=True)
                    
                    st.success(f"""
                    **Résultat du calcul:**
                    - Nombre de produits: {len(panier_produits)}
                    - **Coût total du panier: {cout_total:.2f}€**
                    - Coût moyen par produit: {cout_total/len(panier_produits):.2f}€
                    """)
                    
                    # Comparaison avec la moyenne du territoire
                    prix_moyen_territoire = data['current_data']['prix_courant'].mean()
                    st.info(f"💡 Le prix moyen sur le territoire est de {prix_moyen_territoire:.2f}€ par produit")
                else:
                    st.warning("Veuillez ajouter des produits à votre panier")
    
    def create_categorie_analysis(self):
        """Analyse par catégorie détaillée"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">📊 ANALYSE PAR CATÉGORIE DÉTAILLÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Performance Catégorielle", "Comparaison Catégories", "Tendances"])
        
        with tab1:
            categorie_performance = data['current_data'].groupby('categorie').agg({
                'variation_pct': 'mean',
                'volume_transaction': 'sum',
                'prix_courant': 'mean',
                'production_locale': 'mean',
                'produit': 'count'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(categorie_performance, 
                            x='categorie', 
                            y='variation_pct',
                            title='Variation Moyenne par Catégorie (%)',
                            color='variation_pct',
                            color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.scatter(categorie_performance, 
                               x='prix_courant', 
                               y='variation_pct',
                               size='volume_transaction',
                               color='categorie',
                               title='Performance vs Prix par Catégorie',
                               hover_name='categorie',
                               size_max=60)
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            categorie_evolution = data['historical_data'].groupby([
                data['historical_data']['date'].dt.to_period('M').dt.to_timestamp(),
                'categorie'
            ])['prix_moyen'].mean().reset_index()
            
            fig = px.line(categorie_evolution, 
                         x='date', 
                         y='prix_moyen',
                         color='categorie',
                         title=f'Évolution Comparative - {self.territories[st.session_state.selected_territory]["nom_complet"]}',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(yaxis_title="Prix Moyen (€)")
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Tendances et Perspectives par Catégorie")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Catégories en Hausse
                
                **🍎 Fruits Tropicaux:**
                - Forte demande export
                - Conditions climatiques favorables
                - Saisonnalité marquée
                
                **🐟 Produits de la Mer:**
                - Pêche durable encouragée
                - Tourisme alimentaire
                - Qualité reconnue
                
                **🌿 Produits Bio:**
                - Consommation responsable
                - Aides à la conversion
                - Circuits courts
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Catégories en Baisse
                
                **🍚 Céréales Importées:**
                - Fluctuations cours mondiaux
                - Coût transport accru
                - Concurrence production locale
                
                **🥩 Viandes Importées:**
                - Préférence produits locaux
                - Enjeux environnementaux
                - Coût logistique
                
                **🥫 Produits Transformés:**
                - Consommation fraîche privilégiée
                - Sensibilisation nutrition
                - Préférence fait maison
                """)
    
    def create_evolution_analysis(self):
        """Analyse de l'évolution des prix"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">📈 ÉVOLUTION DES PRIX</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Analyse Historique", "Saisonnalité", "Projections"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                cumulative_data = data['historical_data'].copy()
                cumulative_data['date_group'] = cumulative_data['date'].dt.to_period('M').dt.to_timestamp()
                monthly_totals = cumulative_data.groupby('date_group')['prix_moyen'].mean().reset_index()
                monthly_totals['indice_prix'] = (monthly_totals['prix_moyen'] / monthly_totals['prix_moyen'].iloc[0]) * 100
                
                fig = px.line(monthly_totals, 
                             x='date_group', 
                             y='indice_prix',
                             title=f'Indice des Prix - {self.territories[st.session_state.selected_territory]["nom_complet"]} (Base 100)')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                monthly_heatmap = monthly_totals.copy()
                monthly_heatmap['annee'] = monthly_heatmap['date_group'].dt.year
                monthly_heatmap['mois'] = monthly_heatmap['date_group'].dt.month
                
                heatmap_data = monthly_heatmap.pivot_table(
                    index='annee',
                    columns='mois',
                    values='prix_moyen',
                    aggfunc='mean'
                )
                
                fig = px.imshow(heatmap_data,
                               title=f'Prix Mensuels par Année - {self.territories[st.session_state.selected_territory]["nom_complet"]} (€)',
                               color_continuous_scale='Blues',
                               aspect="auto")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            saisonnalite_data = data['historical_data'].copy()
            saisonnalite_data['mois'] = saisonnalite_data['date'].dt.month
            
            saisonnalite_moyenne = saisonnalite_data.groupby('mois')['prix_moyen'].mean().reset_index()
            
            fig = px.line(saisonnalite_moyenne, 
                         x='mois', 
                         y='prix_moyen',
                         title=f'Saisonnalité des Prix - {self.territories[st.session_state.selected_territory]["nom_complet"]}',
                         markers=True)
            fig.update_layout(xaxis_title="Mois", yaxis_title="Prix Moyen (€)")
            fig.update_xaxes(tickvals=list(range(1, 13)), 
                           ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Dec'])
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Projections des Prix")
            
            derniere_date = data['historical_data']['date'].max()
            dates_futures = pd.date_range(derniere_date + timedelta(days=7), 
                                        periods=12, freq='W')
            
            projections = []
            prix_base = data['current_data']['prix_courant'].mean()
            
            for i, date in enumerate(dates_futures):
                # Simulation de tendance avec inflation et saisonnalité
                inflation = random.uniform(0.001, 0.003)
                prix_projete = prix_base * (1 + inflation) ** (i + 1)
                projections.append({
                    'date': date,
                    'prix_projete': prix_projete,
                    'type': 'Projection'
                })
            
            projections_df = pd.DataFrame(projections)
            
            historique_recent = data['historical_data'][
                data['historical_data']['date'] >= (derniere_date - timedelta(days=180))
            ].groupby('date')['prix_moyen'].mean().reset_index()
            historique_recent['type'] = 'Historique'
            
            comparaison_data = pd.concat([
                historique_recent.rename(columns={'prix_moyen': 'valeur'}),
                projections_df.rename(columns={'prix_projete': 'valeur'})
            ])
            
            fig = px.line(comparaison_data, 
                         x='date', 
                         y='valeur',
                         color='type',
                         title=f'Projection des Prix - {self.territories[st.session_state.selected_territory]["nom_complet"]} - 12 Semaines',
                         color_discrete_sequence=['#28a745', '#17a2b8'])
            fig.update_layout(yaxis_title="Prix (€)")
            st.plotly_chart(fig, config={'displayModeBar': False})
    
    def create_territory_comparison(self):
        """Crée une vue de comparaison entre territoires"""
        comparison_data = generate_comparison_data(self.territories)
        
        st.markdown('<h3 class="section-header">🌍 COMPARAISON INTER-TERRITOIRES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Vue d'Ensemble", "Performance", "Analyse Détaillée"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(comparison_data, 
                            x='nom_complet', 
                            y='prix_moyen_total',
                            title='Prix Moyen par Territoire',
                            color='type',
                            color_discrete_map={'DROM': '#28a745', 'COM': '#17a2b8'})
                fig.update_layout(yaxis_title="Prix Moyen (€)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(comparison_data, 
                            x='nom_complet', 
                            y='production_locale_moyenne',
                            title='Taux de Production Locale',
                            color='type',
                            color_discrete_map={'DROM': '#28a745', 'COM': '#17a2b8'})
                fig.update_layout(yaxis_title="Production Locale (%)")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(comparison_data, 
                               x='pib', 
                               y='prix_moyen_total',
                               size='population',
                               color='type',
                               title='Prix vs PIB par Territoire',
                               hover_name='nom_complet',
                               color_discrete_map={'DROM': '#28a745', 'COM': '#17a2b8'},
                               size_max=60)
                fig.update_layout(xaxis_title="PIB (M€)", yaxis_title="Prix Moyen (€)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.scatter(comparison_data, 
                               x='population', 
                               y='indice_prix',
                               size='superficie',
                               color='climat',
                               title='Population vs Indice des Prix',
                               hover_name='nom_complet',
                               size_max=60)
                fig.update_layout(xaxis_title="Population", yaxis_title="Indice des Prix")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Tableau Comparatif Détaillé")
            
            territoires_a_comparer = st.multiselect(
                "Sélectionnez les territoires à comparer:",
                options=comparison_data['nom_complet'].tolist(),
                default=comparison_data['nom_complet'].tolist()[:5],
                key="territory_compare"
            )
            
            if territoires_a_comparer:
                donnees_filtrees = comparison_data[
                    comparison_data['nom_complet'].isin(territoires_a_comparer)
                ]
                
                donnees_filtrees['densite'] = donnees_filtrees['population'] / donnees_filtrees['superficie']
                donnees_filtrees['pib_par_habitant'] = donnees_filtrees['pib'] * 1e6 / donnees_filtrees['population']
                
                # Create the display dataframe with renamed columns
                display_df = donnees_filtrees[
                    ['nom_complet', 'type', 'population', 'superficie', 'pib', 
                     'prix_moyen_total', 'production_locale_moyenne', 'nombre_produits',
                     'indice_prix', 'climat', 'densite', 'pib_par_habitant']
                ].rename(columns={
                    'nom_complet': 'Territoire',
                    'type': 'Type',
                    'population': 'Population',
                    'superficie': 'Superficie (km²)',
                    'pib': 'PIB (M€)',
                    'prix_moyen_total': 'Prix Moyen (€)',
                    'production_locale_moyenne': 'Production Locale (%)',
                    'nombre_produits': 'Nb Produits Suivis',
                    'indice_prix': 'Indice Prix',
                    'climat': 'Climat',
                    'densite': 'Densité (hab/km²)',
                    'pib_par_habitant': 'PIB/Habitant (€)'
                })
                
                # Sort by the renamed column
                display_df = display_df.sort_values('Prix Moyen (€)', ascending=False)
                
                st.dataframe(display_df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(donnees_filtrees, 
                                x='nom_complet', 
                                y='nombre_produits',
                                title='Nombre de Produits Suivis',
                                color='type',
                                color_discrete_map={'DROM': '#28a745', 'COM': '#17a2b8'})
                    fig.update_layout(yaxis_title="Nombre de Produits")
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                with col2:
                    fig = px.bar(donnees_filtrees, 
                                x='nom_complet', 
                                y='pib_par_habitant',
                                title='PIB par Habitant (€)',
                                color='type',
                                color_discrete_map={'DROM': '#28a745', 'COM': '#17a2b8'})
                    fig.update_layout(yaxis_title="PIB par Habitant (€)")
                    st.plotly_chart(fig, config={'displayModeBar': False})
    
    def create_market_analysis(self):
        """Analyse des marchés et points de vente"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">🏪 ANALYSE DES MARCHÉS</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Carte des Marchés", "Caractéristiques", "Performance"])
        
        with tab1:
            st.subheader("Répartition Géographique des Marchés")
            
            # Simulation de données géographiques
            market_locations = []
            villes = data['market_data']['ville'].unique()
            
            for ville in villes:
                market_locations.append({
                    'ville': ville,
                    'lat': random.uniform(-21.3, -20.8) if st.session_state.selected_territory == 'REUNION' else random.uniform(14.0, 15.0),
                    'lon': random.uniform(55.2, 55.8) if st.session_state.selected_territory == 'REUNION' else random.uniform(-62.0, -60.0),
                    'nombre_marches': len(data['market_data'][data['market_data']['ville'] == ville]),
                    'vendeurs_total': data['market_data'][data['market_data']['ville'] == ville]['nombre_vendeurs'].sum()
                })
            
            locations_df = pd.DataFrame(market_locations)
            
            fig = px.scatter_mapbox(locations_df, 
                                  lat="lat", 
                                  lon="lon", 
                                  size="vendeurs_total",
                                  color="nombre_marches",
                                  hover_name="ville",
                                  hover_data={"vendeurs_total": True, "nombre_marches": True},
                                  color_continuous_scale=px.colors.cyclical.IceFire,
                                  zoom=9,
                                  height=500)
            
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(data['market_data'], 
                            values='superficie', 
                            names='type',
                            title='Répartition de la Superficie par Type de Marché')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(data['market_data'], 
                            x='ville', 
                            y='nombre_vendeurs',
                            color='type',
                            title='Nombre de Vendeurs par Ville',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Performance des Marchés")
            
            # Simulation de données de performance
            performance_data = []
            for marche in data['market_data'].itertuples():
                performance_data.append({
                    'marché': marche.marché,
                    'ville': marche.ville,
                    'type': marche.type,
                    'frequentation_journaliere': random.randint(500, 3000),
                    'chiffre_affaires_mensuel': random.randint(20000, 150000),
                    'satisfaction_clients': random.uniform(3.5, 5.0),
                    'taux_occupation': random.uniform(0.7, 0.95)
                })
            
            performance_df = pd.DataFrame(performance_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(performance_df, 
                               x='frequentation_journaliere', 
                               y='chiffre_affaires_mensuel',
                               size='satisfaction_clients',
                               color='type',
                               title='Performance des Marchés',
                               hover_name='marché',
                               size_max=20)
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(performance_df, 
                            x='marché', 
                            y='taux_occupation',
                            title='Taux d\'Occupation des Marchés',
                            color='type',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Taux d'Occupation")
                st.plotly_chart(fig, config={'displayModeBar': False})
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=180))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        st.sidebar.markdown("### 🏪 Sélection des catégories")
        data = self.get_territory_data(st.session_state.selected_territory)
        categories_selectionnees = st.sidebar.multiselect(
            "Catégories à afficher:",
            list(data['current_data']['categorie'].unique()),
            default=list(data['current_data']['categorie'].unique())[:3]
        )
        
        st.sidebar.markdown("### ⚙️ Options")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=False)
        show_details = st.sidebar.checkbox("Afficher détails techniques", value=False)
        comparison_mode = st.sidebar.checkbox("Mode comparaison", value=False)
        market_analysis = st.sidebar.checkbox("Analyse marchés", value=False)
        
        if st.sidebar.button("🔄 Rafraîchir les données"):
            self.update_live_data(st.session_state.selected_territory)
            st.success("Données mises à jour!")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💹 INDICATEURS ÉCONOMIQUES")
        
        indicateurs = {
            'Inflation Alimentaire': {'valeur': 3.2 + random.uniform(-0.3, 0.3), 'variation': random.uniform(-0.2, 0.2)},
            'Production Agricole': {'valeur': 4.5 + random.uniform(-0.5, 0.5), 'variation': random.uniform(-1, 2)},
            'Tourisme': {'valeur': 8.2 + random.uniform(-1, 1), 'variation': random.uniform(-2, 3)},
            'Exportations': {'valeur': 2.8 + random.uniform(-0.2, 0.2), 'variation': random.uniform(-1, 1)}
        }
        
        for indicateur, data in indicateurs.items():
            st.sidebar.metric(
                indicateur,
                f"{data['valeur']:.1f}%",
                f"{data['variation']:+.1f}%"
            )
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'categories_selectionnees': categories_selectionnees,
            'auto_refresh': auto_refresh,
            'show_details': show_details,
            'comparison_mode': comparison_mode,
            'market_analysis': market_analysis
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Préchargement des données du territoire sélectionné
        self.get_territory_data(st.session_state.selected_territory)
        
        # Affichage du sélecteur de territoire
        self.display_territory_selector()
        
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        if controls['comparison_mode']:
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                "🌍 Comparaison Territoires", 
                "📈 Vue d'Ensemble", 
                "🏪 Produits", 
                "📊 Catégories", 
                "📈 Évolution", 
                "🏪 Marchés",
                "💡 Insights",
                "ℹ️ À Propos"
            ])
            
            with tab1:
                self.create_territory_comparison()
            
            with tab2:
                self.create_mercuriales_overview()
            
            with tab3:
                self.create_produits_live()
            
            with tab4:
                self.create_categorie_analysis()
            
            with tab5:
                self.create_evolution_analysis()
            
            with tab6:
                self.create_market_analysis()
            
            with tab7:
                st.markdown("## 💡 INSIGHTS STRATÉGIQUES")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    ### 🎯 TENDANCES ALIMENTAIRES INTER-TERRITOIRES
                    
                    **📈 Dynamiques de Prix:**
                    - Forte saisonnalité fruits tropicaux
                    - Stabilité relative céréales importées
                    - Hausse produits de qualité
                    
                    **🏝️ Facteurs Spécifiques:**
                    - Isolation géographique impactant prix
                    - Spécialisations agricoles locales
                    - Tourisme influençant demande
                    
                    **💰 Impact Économique:**
                    - Sécurité alimentaire territoriale
                    - Développement circuits courts
                    - Valorisation productions locales
                    """)
                
                with col2:
                    st.markdown("""
                    ### 🚨 DÉFIS ET OPPORTUNITÉS
                    
                    **⚡ Défis à Relever:**
                    - Dépendance aux importations
                    - Changement climatique
                    - Compétition usage sols
                    
                    **💡 Opportunités:**
                    - Agriculture biologique
                    - Transformation locale
                    - Tourisme culinaire
                    
                    **🔮 Perspectives:**
                    - Autonomie alimentaire croissante
                    - Valorisation biodiversité
                    - Innovation agricole
                    """)
                
                st.markdown("""
                ### 📋 RECOMMANDATIONS OPÉRATIONNELLES
                
                1. **Diversification:** Encourager la diversité des cultures
                2. **Circuits Courts:** Développer vente directe
                3. **Formation:** Former aux techniques durables
                4. **Innovation:** Investir agriculture de précision
                5. **Qualité:** Valoriser signes officiels qualité
                6. **Résilience:** Anticiper changement climatique
                7. **Coopération:** Renforcer échanges inter-territoires
                """)
            
            with tab8:
                st.markdown("## 📋 À propos de ce dashboard")
                st.markdown(f"""
                Ce dashboard présente une analyse en temps réel des mercuriales DAAF 
                pour l'ensemble des DROM-COM.
                
                **Territoire actuel:** {self.territories[st.session_state.selected_territory]['nom_complet']}
                
                **Couverture:**
                - {len([t for t in self.territories.values()])} territoires DROM-COM
                - 10+ produits agricoles principaux par territoire
                - Données historiques depuis 2022
                - Analyse par catégorie et marché
                
                **⚡ Performance:**
                - Cache intelligent pour un chargement rapide
                - Mises à jour en temps réel optimisées
                - Navigation fluide entre territoires
                
                **⚠️ Avertissement:** 
                Ce dashboard est un outil d'aide à la décision.
                Les données peuvent être sujettes à révision.
                """)
                
                st.markdown("---")
                st.markdown("""
                **📞 Contact:**
                - Direction de l'Alimentation, de l'Agriculture et de la Forêt (DAAF)
                - Site web: www.daaf.gouv.fr
                - Email: contact@daaf.gouv.fr
                """)
        else:
            tabs = ["📈 Vue d'Ensemble", "🏪 Produits", "📊 Catégories", "📈 Évolution"]
            if controls['market_analysis']:
                tabs.append("🏪 Marchés")
            tabs.extend(["💡 Insights", "ℹ️ À Propos"])
            
            all_tabs = st.tabs(tabs)
            
            with all_tabs[0]:
                self.create_mercuriales_overview()
            
            with all_tabs[1]:
                self.create_produits_live()
            
            with all_tabs[2]:
                self.create_categorie_analysis()
            
            with all_tabs[3]:
                self.create_evolution_analysis()
            
            if controls['market_analysis']:
                with all_tabs[4]:
                    self.create_market_analysis()
                insight_tab = all_tabs[5]
                about_tab = all_tabs[6]
            else:
                insight_tab = all_tabs[4]
                about_tab = all_tabs[5]
            
            with insight_tab:
                st.markdown("## 💡 INSIGHTS STRATÉGIQUES")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    ### 🎯 TENDANCES ALIMENTAIRES - {self.territories[st.session_state.selected_territory]['nom_complet']}
                    
                    **📈 Dynamiques de Prix:**
                    - Forte saisonnalité fruits tropicaux
                    - Stabilité relative céréales importées
                    - Hausse produits de qualité
                    
                    **🏝️ Facteurs Locaux:**
                    - Conditions climatiques favorables
                    - Traditions culinaires riches
                    - Tourisme influençant demande
                    """)
                
                with col2:
                    st.markdown("""
                    ### 🚨 DÉFIS ET OPPORTUNITÉS
                    
                    **⚡ Défis à Relever:**
                    - Dépendance aux importations
                    - Changement climatique
                    - Compétition usage sols
                    
                    **💡 Opportunités:**
                    - Agriculture biologique
                    - Transformation locale
                    - Tourisme culinaire
                    """)
                
                st.markdown("""
                ### 📋 RECOMMANDATIONS OPÉRATIONNELLES
                
                1. **Diversification:** Encourager la diversité des cultures
                2. **Circuits Courts:** Développer vente directe
                3. **Formation:** Former aux techniques durables
                4. **Innovation:** Investir agriculture de précision
                5. **Qualité:** Valoriser signes officiels qualité
                """)
            
            with about_tab:
                st.markdown("## 📋 À propos de ce dashboard")
                st.markdown(f"""
                Ce dashboard présente une analyse en temps réel des mercuriales DAAF 
                à {self.territories[st.session_state.selected_territory]['nom_complet']}.
                
                **Couverture:**
                - {len(self.get_territory_data(st.session_state.selected_territory)['produits'])} produits agricoles principaux
                - Données historiques depuis 2022
                - Analyse par catégorie et marché
                
                **⚡ Performance:**
                - Cache intelligent pour un chargement rapide
                - Mises à jour en temps réel optimisées
                
                **⚠️ Avertissement:** 
                Ce dashboard est un outil d'aide à la décision.
                Les données peuvent être sujettes à révision.
                """)
                
                st.markdown("---")
                st.markdown("""
                **📞 Contact:**
                - Direction de l'Alimentation, de l'Agriculture et de la Forêt (DAAF)
                - Site web: www.daaf.gouv.fr
                - Email: contact@daaf.gouv.fr
                """)
        
        # Mise à jour automatique désactivée par défaut pour éviter les ralentissements
        if controls['auto_refresh']:
            time.sleep(30)
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = MercurialesDashboard()
    dashboard.run_dashboard()