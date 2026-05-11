import streamlit as st
import pandas as pd
import time
from datetime import date
import os

# 1. Configurazione Pagina & Estetica
st.set_page_config(page_title="Training Tracker", layout="wide", page_icon="💪")

# CSS Personalizzato per un look più "Pro"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { background-color: #262730; color: white; }
    .exercise-card { padding: 20px; border-radius: 10px; background-color: #1e1e26; margin-bottom: 15px; border-left: 5px solid #ff4b4b; }
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

# 3. Sidebar: Timer & Info
with st.sidebar:
    st.header("⏱️ Rest Timer")
    t_min = st.number_input("Minuti", 0, 5, 1)
    t_sec = st.number_input("Secondi", 0, 59, 30)
    if st.button("Avvia Timer"):
        total_seconds = t_min * 60 + t_sec
        bar = st.progress(100)
        for i in range(total_seconds):
            time.sleep(1)
            remaining = total_seconds - i - 1
            bar.progress(int((remaining / total_seconds) * 100))
        st.success("🔥 Torna alla sbarra!")
        st.balloons()
    
    st.markdown("---")
    st.info("Registra ogni serie separata da una virgola (es: 8, 7, 6, 6)")

# 4. Main App
st.title("Workout Tracker")
day = st.selectbox("Seleziona la sessione di oggi:", list(workout_plan.keys()))
exercises = workout_plan[day]

st.subheader(f"Log Allenamento - {date.today().strftime('%d/%m/%Y')}")

results = []
# Creazione dei campi di input per ogni esercizio
for ex in exercises:
    with st.container():
        st.markdown(f'<div class="exercise-card">', unsafe_allow_html=True)
        cols = st.columns([2, 2])
        with cols[0]:
            st.markdown(f"### {ex}")
        with cols[1]:
            reps_input = st.text_input(f"Serie (es: 8, 8, 7)", key=f"input_{ex}", placeholder="Inserisci le ripetizioni...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if reps_input:
            # Calcoliamo la media per il grafico e il volume totale
            try:
                reps_list = [float(x.strip()) for x in reps_input.split(',')]
                avg_reps = sum(reps_list) / len(reps_list)
                results.append({"Data": date.today(), "Esercizio": ex, "Media_Reps": avg_reps, "Serie_Raw": reps_input})
            except:
                pass

# Tasto Salvataggio
if st.button("💾 Salva Sessione"):
    if results:
        df_new = pd.DataFrame(results)
        if os.path.exists("workout_log.csv"):
            df_old = pd.read_csv("workout_log.csv")
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
        df_final.to_csv("workout_log.csv", index=False)
        st.success("Dati salvati! Ottimo lavoro.")
    else:
        st.warning("Inserisci almeno un risultato prima di salvare.")

# 5. Analisi Progressi
st.markdown("---")
st.header("📈 Analisi Progressi")

if os.path.exists("workout_log.csv"):
    df_history = pd.read_csv("workout_log.csv")
    df_history['Data'] = pd.to_datetime(df_history['Data'])
    
    selected_ex = st.selectbox("Scegli l'esercizio da monitorare:", df_history['Esercizio'].unique())
    
    chart_data = df_history[df_history['Esercizio'] == selected_ex].sort_values('Data')
    
    if not chart_data.empty:
        st.line_chart(chart_data.set_index('Data')['Media_Reps'])
        st.write("Dettaglio ultime sessioni:")
        st.table(chart_data[['Data', 'Serie_Raw']].tail(5))
else:
    st.info("Nessun dato storico trovato. Inizia ad allenarti per vedere i grafici!")
