import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Rozterki małżeńskie", layout="wide")

st.title("Rozterki małżeńskie")
st.caption(
    "UWAGA gra na dwa fronty redukuje szanse o 20% na nowy nabytej tj. "
    "jeśli 50% redukcja=50\\*0,2=10%"
)

st.divider()

# ---------------------------------------------------------------------------
# WEJŚCIA UŻYTKOWNIKA
# ---------------------------------------------------------------------------
st.subheader("Prawdopodobieństwo")

col1, col2, col3 = st.columns(3)
with col1:
    p_better = st.slider("Nowa lepsza", 0, 100, 50, format="%d%%") / 100
with col2:
    p_want = st.slider("udany atak na serce nowej", 0, 100, 50, format="%d%%") / 100
with col3:
    p_discover = st.slider("obecna dowie się o twoich intrygach i zrywa", 0, 100, 30, format="%d%%") / 100

st.subheader("Wartości")

col4, col5, col6, col7 = st.columns(4)
with col4:
    V_stay = st.slider("obecny związek", -100, 100, 20)
with col5:
    V_alone = st.slider("samotność", -100, 100, -12)
with col6:
    V_better = st.slider("nowy związek gdy lepsza", -100, 100, 70)
with col7:
    V_worse = st.slider("Nowa gdy gorsza", -100, 100, -50)

st.divider()

# ---------------------------------------------------------------------------
# LOGIKA MODELU
# ---------------------------------------------------------------------------
# Redukcja szansy u nowej, gdy gra się na dwa fronty (opcja 3 - nie zrywa,
# ale zagaduje nową w tajemnicy): efektywna szansa = szansa * 0,2
# np. 50% -> 50 * 0,2 = 10%
TWO_FRONTS_MULTIPLIER = 0.2
p_want_two_fronts = p_want * TWO_FRONTS_MULTIPLIER

# --- Opcja 1: Zostań (pozostaje wierny) --------------------------------------
leaves_1 = [
    {"Strategia": "1. Pozostaje wierny", "Gałąź": "Zostaje z obecną",
     "Prawdopodobieństwo": 1.0, "Wartość": V_stay},
]
EV1 = V_stay

# --- Opcja 2: Zerwij (zrywam i atakuje nową) ---------------------------------
leaves_2 = [
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się lepsza",
     "Prawdopodobieństwo": p_want * p_better, "Wartość": V_better},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się gorsza",
     "Prawdopodobieństwo": p_want * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa nie chce – zostaje sam",
     "Prawdopodobieństwo": (1 - p_want), "Wartość": V_alone},
]
EV2 = sum(l["Prawdopodobieństwo"] * l["Wartość"] for l in leaves_2)

# --- Opcja 3: Po Cichu (zaatakuje nową w tajemnicy, gra na dwa fronty) -------
# Szansa "nowa go chce" jest tu zredukowana (TWO_FRONTS_MULTIPLIER), bo gra
# na dwa fronty osłabia atrakcyjność / wiarygodność u nowej.
leaves_3 = [
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa chce, lepsza",
     "Prawdopodobieństwo": p_discover * p_want_two_fronts * p_better, "Wartość": V_better},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa chce, gorsza",
     "Prawdopodobieństwo": p_discover * p_want_two_fronts * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa go olewa – sam",
     "Prawdopodobieństwo": p_discover * (1 - p_want_two_fronts), "Wartość": V_alone},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa chce, lepsza",
     "Prawdopodobieństwo": (1 - p_discover) * p_want_two_fronts * p_better, "Wartość": V_better},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa chce, gorsza",
     "Prawdopodobieństwo": (1 - p_discover) * p_want_two_fronts * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa olewa – zostaje z obecną",
     "Prawdopodobieństwo": (1 - p_discover) * (1 - p_want_two_fronts), "Wartość": V_stay},
]
EV3 = sum(l["Prawdopodobieństwo"] * l["Wartość"] for l in leaves_3)

evs = {
    "Pozostaje wierny": EV1,
    "Zrywam i atakuje nową": EV2,
    "Zaatakuje nową w tajemnicy": EV3,
}
best = max(evs, key=evs.get)

# ---------------------------------------------------------------------------
# WYNIKI
# ---------------------------------------------------------------------------
st.subheader("Wyniki - Expected Value")

c1, c2, c3 = st.columns(3)
for c, (name, val) in zip([c1, c2, c3], evs.items()):
    with c:
        st.markdown(f"**{name}**")
        st.markdown(f"<h2 style='margin-top:-10px'>EV= {val:.0f}</h2>", unsafe_allow_html=True)

st.caption(
    f"Efektywna szansa, że nowa chce (gra na dwa fronty, opcja 3): "
    f"{p_want*100:.0f}% × {TWO_FRONTS_MULTIPLIER} = {p_want_two_fronts*100:.0f}%"
)

# --- Wykres słupkowy w stylu na zdjęciu --------------------------------------
labels = ["Zostań", "Zerwij", "Po Cichu"]
values = [EV1, EV2, EV3]
colors = ["#5B9BD5", "#70AD47", "#ED7D31"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels,
    y=values,
    marker_color=colors,
    text=[f"{v:.0f}" for v in values],
    textposition=["outside" if v >= 0 else "outside" for v in values],
    width=0.5,
))
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=420,
    margin=dict(t=60, l=10, r=10, b=10),
    yaxis=dict(range=[-100, 100], dtick=50, gridcolor="#E5E5E5", zerolinecolor="#999999", zerolinewidth=1.5),
    xaxis=dict(showgrid=False),
    showlegend=False,
)
fig.add_annotation(
    text="Expected Value (EV) ↑", xref="paper", yref="paper",
    x=0, y=1.12, showarrow=False, font=dict(size=14, color="#444444"), align="left"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# PEŁNE ROZBICIE
# ---------------------------------------------------------------------------
st.subheader("Pełne rozbicie")

all_leaves = leaves_1 + leaves_2 + leaves_3
df = pd.DataFrame(all_leaves)
df["Wkład do EV"] = df["Prawdopodobieństwo"] * df["Wartość"]
df["Prawdopodobieństwo"] = (df["Prawdopodobieństwo"] * 100).round(1).astype(str) + "%"
df["Wartość"] = df["Wartość"].round(1)
df["Wkład do EV"] = df["Wkład do EV"].round(2)

strat_names = {
    "1. Pozostaje wierny": "1. Zostaje z obecną",
    "2. Zrywam i atakuje nową": "2. Zrywa i podrywa nową",
    "3. Zaatakuje nową w tajemnicy": "3. Zagaduje bez zrywania",
}
ev_lookup = {"1. Pozostaje wierny": EV1, "2. Zrywam i atakuje nową": EV2, "3. Zaatakuje nową w tajemnicy": EV3}

for strat, display_name in strat_names.items():
    with st.expander(f"{display_name} → EV = {ev_lookup[strat]:.1f}"):
        st.dataframe(
            df[df["Strategia"] == strat][["Gałąź", "Prawdopodobieństwo", "Wartość", "Wkład do EV"]],
            use_container_width=True,
            hide_index=True,
        )
