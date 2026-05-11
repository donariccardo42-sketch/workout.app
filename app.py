import streamlit as st
import pandas as pd
import time
from datetime import date
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAZIONE & CONNESSIONE (Il "Motore")
# ==========================================
st.set_page_config(page_title="TS900 Lab - Cloud Edition", layout="wide", page_icon="☁️")

# DICHIARAZIONE DELLA CONNESSIONE (Deve stare qui, all'inizio!)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Errore nella creazione della connessione: {e}")

# Funzione per leggere i dati con gestione errori avanzata
def get_data():
    try:
        # Specifichiamo chiaramente il nome del foglio "Log"
        return conn.read(worksheet="Log", ttl=0)
    except Exception as e:
        st.warning(f"Tab 'Log' non trovata o link errato. Provo a leggere il primo foglio... (Errore: {e})")
        try:
            return conn.read(ttl=0)
        except:
            return pd.DataFrame() # Restituisce un foglio vuoto se tutto fallisce

# ==========================================
# 2. ESTETICA & UI
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    .exercise-card { padding: 20px; border-radius: 10px; background-color: #1e1e26; margin-bottom: 15px; border-left: 5px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATABASE ESERCIZI (La tua scheda)
# ==========================================
workout_plan = {
    "Lunedì: PULL (Front Lever)": ["Tuck FL Hold (sec)", "Pull-ups (Tempo)", "Advanced Tuck Raises", "Banded Facepulls", "Bicep BW Curls"],
    "Martedì: PUSH (Esplosività)": ["High Pull-ups", "Banded Dips", "Archer Push-ups", "Slow Eccentric Dips", "Banded Triceps"],
    "Mercoledì: LEGS & CORE": ["Pistol Squats", "Banded Bulgarian Squats", "L-Sit Hold (sec)", "Leg Raises", "Copenhagen Plank"],
    "Giovedì: PULL (Volume)": ["Banded Pull-ups", "Chin-ups", "Australian Pull-ups", "Scapular Pull-ups", "Hollow Body Rock"],
    "Venerdì: PUSH (Spalle/Tri)": ["Elevated Pike Push-ups", "Pseudo Planche Push-ups", "Lean Forward Dips", "Banded Lateral Raises", "Tiger Bend Push-ups"]
}

# ================= : 4. SIDEBAR TIMER =================
with st.sidebar:
    st.header("⏱️ Rest Timer")
    t_min = st.number_input("Min", 0, 5, 1)
    t_sec = st.number_input("Sec", 0, 59, 30)
    if st.button("Avvia"):
        ts = t_min * 60 + t_sec
        ph = st.empty()
        for i in range(ts, 0, -1):
            ph.metric("Recupero", f"{i}s")
            time.sleep(1)
        st.success("🔥 Vai!")

# ================= : 5. MAIN UI & INPUT =================
st.title("💪 TS900 Lab - Cloud Tracker")
day = st.selectbox("Sessione:", list(workout_plan.keys()))

results = []
for ex in workout_plan[day]:
    st.markdown(f'<div class="exercise-card">', unsafe_allow_html=True)
    cols = st.columns([2, 2])
    with cols[0]: st.markdown(f"### {ex}")
    with cols[1]: reps_input = st.text_input(f"Serie (es: 8, 8, 7)", key=f"in_{ex}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if reps_input:
        try:
            nums = [float(x.strip()) for x in reps_input.split(',')]
            results.append({
                "Data": str(date.today()), 
                "Esercizio": ex, 
                "Media_Reps": sum(nums)/len(nums), 
                "Serie_Raw": reps_input
            })
        except: pass

if st.button("💾 Salva nel Cloud"):
    if results:
        try:
            existing_data = get_data()
            new_data = pd.DataFrame(results)
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Log", data=updated_df)
            st.success("Dati sincronizzati con Google Sheets!")
            st.balloons()
        except Exception as e:
            st.error(f"Errore nel salvataggio: {e}")

# ================= : 6. ANALISI PROGRESSI =================
st.markdown("---")
st.header("📈 Analisi Volume & Stress")

df_history = get_data()

if not df_history.empty:
    df_history['Data'] = pd.to_datetime(df_history['Data'])
    
    def calculate_volume(raw_str):
        try: return sum([float(x.strip()) for x in str(raw_str).split(',')])
        except: return 0
    
    df_history['Volume_Totale'] = df_history['Serie_Raw'].apply(calculate_volume)
    
    tab1, tab2 = st.tabs(["📈 Sovraccarico Progressivo", "📉 Stress Settimanale"])
    
    with tab1:
        ex_list = df_history['Esercizio'].unique()
        target = st.selectbox("Seleziona esercizio:", ex_list)
        df_plot = df_history[df_history['Esercizio'] == target].sort_values('Data')
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=df_plot['Data'], y=df_plot['Volume_Totale'], name="Volume", marker_color='#00d4ff', opacity=0.6))
        fig_vol.add_trace(go.Scatter(x=df_plot['Data'], y=df_plot['Media_Reps'], name="Intensità", line=dict(color='#ff4b4b', width=3), yaxis="y2"))
        fig_vol.update_layout(template="plotly_dark", yaxis2=dict(overlaying="y", side="right"))
        st.plotly_chart(fig_vol, use_container_width=True)

    with tab2:
        df_history['Settimana'] = df_history['Data'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly_volume = df_history.groupby('Settimana')['Volume_Totale'].sum().reset_index()
        fig_stress = go.Figure(go.Bar(x=weekly_volume['Settimana'], y=weekly_volume['Volume_Totale'], marker_color='#ff4b4b'))
        fig_stress.update_layout(template="plotly_dark", title="Workload Settimanale Cumulativo")
        st.plotly_chart(fig_stress, use_container_width=True)
else:
    st.info("Nessun dato ancora presente nel cloud.")

