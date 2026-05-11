import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time
from datetime import date

# Sostituisci l'URL con il tuo link 'Raw' di GitHub
ICON_URL = "https://raw.githubusercontent.com/donariccardo42-sketch/workout.app/4ad2a84bfda587cb5abd794c9497f9978e8acfb8/image.png"

st.markdown(
    f"""
    <head>
        <link rel="apple-touch-icon" href="{ICON_URL}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
    """,
    unsafe_allow_html=True
)


# 1. Configurazione Pagina & Estetica
st.set_page_config(page_title="Workout Tracker", layout="wide", page_icon="🏋️‍♂️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    .exercise-card { 
        padding: 20px; 
        border-radius: 10px; 
        background-color: #1e1e26; 
        margin-bottom: 15px; 
        border-left: 5px solid #00d4ff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .stButton>button { width: 100%; background-color: #00d4ff; color: black; font-weight: bold; }
    .download-btn { color: #00d4ff !important; text-decoration: none; border: 1px solid #00d4ff; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Esercizi
workout_plan = {
    "Lunedì: PULL (Front Lever)": ["Tuck FL Hold (sec)", "Pull-ups (Tempo)", "Advanced Tuck Raises", "Banded Facepulls", "Bicep BW Curls"],
    "Martedì: PUSH (Esplosività)": ["High Pull-ups", "Banded Dips", "Archer Push-ups", "Slow Eccentric Dips", "Banded Triceps"],
    "Mercoledì: LEGS & CORE": ["Pistol Squats", "Banded Bulgarian Squats", "L-Sit Hold (sec)", "Leg Raises", "Copenhagen Plank"],
    "Giovedì: PULL (Volume)": ["Banded Pull-ups", "Chin-ups", "Australian Pull-ups", "Scapular Pull-ups", "Hollow Body Rock"],
    "Venerdì: PUSH (Spalle/Tri)": ["Elevated Pike Push-ups", "Pseudo Planche Push-ups", "Lean Forward Dips", "Banded Lateral Raises", "Tiger Bend Push-ups"]
}

# 3. Funzioni Gestione Dati (CSV Locale)
DB_FILE = "workout_log.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    return pd.DataFrame(columns=["Data", "Esercizio", "Media_Reps", "Serie_Raw"])

def save_data(new_entries):
    df = load_data()
    new_df = pd.DataFrame(new_entries)
    updated_df = pd.concat([df, new_df], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)

# 4. Sidebar: Timer & Backup
with st.sidebar:
    st.header("⏱️ Timer")
    
    # Timer
    st.subheader("Rest Timer")
    t_min = st.number_input("Min", 0, 5, 1)
    t_sec = st.number_input("Sec", 0, 59, 30)
    if st.button("Avvia Timer"):
        ts = t_min * 60 + t_sec
        ph = st.empty()
        for i in range(ts, 0, -1):
            ph.metric("Recupero", f"{i}s")
            time.sleep(1)
        st.success("🔥 Vai!")
    
    st.markdown("---")
    
    # TASTO BACKUP (La novità)
    st.subheader("💾 Gestione Dati")
    df_for_backup = load_data()
    if not df_for_backup.empty:
        csv = df_for_backup.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Backup CSV",
            data=csv,
            file_name=f'workout_backup_{date.today()}.csv',
            mime='text/csv',
        )
        st.caption("Consiglio: scarica il file a fine settimana per non perdere i dati online.")
    else:
        st.caption("Nessun dato da scaricare.")

# 5. UI Principale
st.title("💪 Workout Tracker")
day = st.selectbox("Seleziona la sessione:", list(workout_plan.keys()))

current_results = []
for ex in workout_plan[day]:
    st.markdown(f'<div class="exercise-card">', unsafe_allow_html=True)
    cols = st.columns([2, 2])
    with cols[0]: st.markdown(f"### {ex}")
    with cols[1]: reps = st.text_input(f"Serie", key=f"in_{ex}", placeholder="es: 8, 8, 7")
    
    if reps:
        try:
            nums = [float(x.strip()) for x in reps.split(',')]
            current_results.append({"Data": date.today(), "Esercizio": ex, "Media_Reps": round(sum(nums)/len(nums), 2), "Serie_Raw": reps})
        except: pass
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("💾 Salva Allenamento"):
    if current_results:
        save_data(current_results)
        st.success("Dati salvati localmente!")
        st.rerun() # Ricarica per aggiornare i grafici e il tasto download
    else:
        st.warning("Inserisci i dati prima di salvare.")

# 6. Analisi Avanzata
st.markdown("---")
st.header("📊 Analytics")
df_history = load_data()

if not df_history.empty:
    def calc_volume(row):
        try: return sum([float(x.strip()) for x in str(row).split(',')])
        except: return 0
    df_history['Volume_Totale'] = df_history['Serie_Raw'].apply(calc_volume)
    
    tab1, tab2 = st.tabs(["📈 Progressi", "📉 Stress Settimanale"])
    with tab1:
        ex_list = df_history['Esercizio'].unique()
        target = st.selectbox("Esercizio:", ex_list)
        df_ex = df_history[df_history['Esercizio'] == target].sort_values('Data')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_ex['Data'], y=df_ex['Volume_Totale'], name="Volume", marker_color='#00d4ff', opacity=0.4))
        fig.add_trace(go.Scatter(x=df_ex['Data'], y=df_ex['Media_Reps'], name="Intensità", line=dict(color='#ff4b4b', width=4), yaxis="y2"))
        fig.update_layout(template="plotly_dark", yaxis2=dict(overlaying="y", side="right"))
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        df_history['Settimana'] = df_history['Data'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly = df_history.groupby('Settimana')['Volume_Totale'].sum().reset_index()
        st.plotly_chart(go.Figure(go.Bar(x=weekly['Settimana'], y=weekly['Volume_Totale'], marker_color='#ff4b4b')).update_layout(template="plotly_dark"), use_container_width=True)
