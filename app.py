import streamlit as st
import pandas as pd
from datetime import date

# Configurazione Pagina
st.set_page_config(page_title="TS900 Workout Tracker", layout="centered")

# Database Allenamenti
workout_plan = {
    "Lunedì: PULL (Front Lever)": ["Tuck FL Hold (sec)", "Pull-ups (Tempo)", "Advanced Tuck Raises", "Banded Facepulls", "Bicep BW Curls"],
    "Martedì: PUSH (Esplosività)": ["High Pull-ups", "Banded Dips", "Archer Push-ups", "Slow Eccentric Dips", "Banded Triceps"],
    "Mercoledì: LEGS & CORE": ["Pistol Squats", "Banded Bulgarian Squats", "L-Sit Hold (sec)", "Leg Raises", "Copenhagen Plank"],
    "Giovedì: PULL (Volume)": ["Banded Pull-ups", "Chin-ups", "Australian Pull-ups", "Scapular Pull-ups", "Hollow Body Rock"],
    "Venerdì: PUSH (Spalle/Tri)": ["Elevated Pike Push-ups", "Pseudo Planche Push-ups", "Lean Forward Dips", "Banded Lateral Raises", "Tiger Bend Push-ups"]
}

st.title("🚀 TS900 Calisthenics Tracker")

# Selezione Giorno
day = st.selectbox("Cosa alleniamo oggi?", list(workout_plan.keys()))
exercises = workout_plan[day]

st.subheader(f"Scheda del {day}")

# Input Progressi
results = []
for ex in exercises:
    cols = st.columns([2, 1, 1])
    with cols[0]:
        st.write(f"**{ex}**")
    with cols[1]:
        reps = st.number_input("Reps/Sec", key=f"{ex}_reps", step=1)
    with cols[2]:
        sets = st.number_input("Serie", key=f"{ex}_sets", step=1)
    results.append({"Esercizio": ex, "Reps/Sec": reps, "Serie": sets, "Data": date.today()})

# Salvataggio
if st.button("Salva Allenamento"):
    df = pd.DataFrame(results)
    try:
        existing_df = pd.read_csv("workout_log.csv")
        final_df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        final_df = df
    
    final_df.to_csv("workout_log.csv", index=False)
    st.success("Allenamento salvato con successo in workout_log.csv!")

# Visualizzazione Progressi
if st.checkbox("Mostra Storico Progressi"):
    try:
        history = pd.read_csv("workout_log.csv")
        st.dataframe(history)
    except FileNotFoundError:
        st.warning("Nessun dato ancora salvato.")
