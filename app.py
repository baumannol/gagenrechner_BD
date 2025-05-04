import streamlit as st
from datetime import datetime, time
from fpdf import FPDF
import io

# ========================
# App-Konfiguration & Titel
# ========================
st.set_page_config(page_title="Brass Department Gagenrechner", layout="wide")
st.title("Brass Department Gagenrechner")

# ========================
# Session State Defaults
# ========================
if 'saved_gigs' not in st.session_state:
    st.session_state.saved_gigs = {}
if 'current_gig' not in st.session_state:
    st.session_state.current_gig = ""

# ========================
# 🎨 Globales Design & Responsive
# ========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Space+Mono&display=swap');

h1, h2, h3, h4, h5, h6, .stButton>button {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
}
p, ul, li, div, span,
.stTextInput>div>div>input,
.stNumberInput>div>input {
  font-family: 'Space Mono', monospace;
}

.stButton>button {
  background-color: #004D59;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 16px;
}
.stButton>button:hover {
  background-color: #00738A;
}

footer { visibility: hidden; }
footer:after {
  content: 'Built with ❤️ by Brass Department';
  visibility: visible;
  display: block;
  padding: 10px;
  text-align: center;
  font-family: 'Space Mono', monospace;
  font-size: 14px;
  color: #004D59;
}

.musiker-section { background-color: #FDF1E7; padding: 20px; border-radius: 20px; margin-bottom: 20px; }
.technik-section { background-color: #E3F2FD; padding: 20px; border-radius: 20px; margin-bottom: 20px; }

.summary-box { background-color: #FDF1E7; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #004D59; }
.proposal-box { background-color: #004D59; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: white; text-align: center; }
.result-box { background-color: #F7A600; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #004D59; }

@media (max-width: 768px) {
  .css-1lcbmhc.e1tzin5v1 { flex-direction: column !important; }
}
</style>
""", unsafe_allow_html=True)

# ========================
# Funktionen: Speichern & Laden
# ========================
def save_concert(name):
    st.session_state.saved_concerts[name] = {
        k: v for k, v in st.session_state.items()
        if k not in ["saved_concerts", "current_concert"]
    }
    st.session_state.current_concert = name
    st.success(f"Konzert '{name}' gespeichert!")

def load_concert(name):
    data = st.session_state.saved_concerts[name]
    for k, v in data.items():
        st.session_state[k] = v
    st.session_state.current_concert = name
    st.success(f"Konzert '{name}' geladen!")

if "saved_concerts" not in st.session_state:
    st.session_state.saved_concerts = {}
if "current_concert" not in st.session_state:
    st.session_state.current_concert = ""

# ========================
# 🎫 Konzert laden / speichern (ganz oben)
# ========================
with st.expander("🎫 Konzert laden / speichern", expanded=False):
    if st.session_state.saved_concerts:
        chosen = st.selectbox(
            "Gespeicherte Konzerte",
            list(st.session_state.saved_concerts.keys()),
            key="load_dropdown"
        )
        if st.button("📂 Laden"):
            load_concert(chosen)
    else:
        st.info("Noch keine Konzerte gespeichert.")
    st.markdown("---")
    cn = st.text_input(
        "Konzert-Name",
        value=st.session_state.current_concert,
        key="concert_name_input"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Speichern", disabled=(cn == "")):
            save_concert(cn)
    with col2:
        if st.button("✏️ Aktualisieren", disabled=(cn == "" or cn not in st.session_state.saved_concerts)):
            save_concert(cn)

# ========================
# — Musiker-Wahl —
# ========================
with st.expander("🎵 Musiker wählen", expanded=False):
    st.markdown("<div class='musiker-section'>", unsafe_allow_html=True)
    all_players = [
        "Niels","Sevi J.","Raphi","Duno","Oli","Joni","Oskar",
        "Valerian","Thomas","Sevi G.","Adrian","Laurent",
        "J.J.","Michi","Markus"
    ]
    prof1 = ["J.J.","Niels","Sevi J."]
    prof2 = ["Michi","Oskar","Valerian"]
    norm  = ["Joni","Oli","Raphi","Adrian","Laurent","Markus","Sevi G.","Duno","Thomas"]

    sel = []
    all_cb = st.checkbox("Alle auswählen")
    cols = st.columns(2)
    for i, m in enumerate(all_players):
        with cols[i % 2]:
            if st.checkbox(m, value=all_cb, key=f"cb_{m}"):
                sel.append(m)
    st.markdown("</div>", unsafe_allow_html=True)

# ========================
# — Gagen & Optionen —
# ========================
with st.expander("🎛️ Gagen & Optionen", expanded=False):
    st.markdown("<div class='technik-section'>", unsafe_allow_html=True)
    n1 = sum(1 for m in sel if m in prof1)
    n2 = sum(1 for m in sel if m in prof2)
    n3 = sum(1 for m in sel if m in norm)

    g1 = st.slider("Profis Tarif 1 (CHF)", 100, 500, 350, 25)
    g2 = st.slider("Profis Tarif 2 (CHF)", 100, 500, 250, 25)
    g3 = st.slider("Musiker (CHF)",           100, 500, 150, 25)

    dur   = st.selectbox(
        "Musikdauer (ab 45 min, je 15 min +500 CHF)",
        [20,30,45,60,75,90,105,120],
        index=2
    )
    opt1  = st.checkbox("Verstärkung +500 CHF")
    opt2  = st.checkbox("Tontechniker +500 CHF")
    opt3  = st.checkbox("Lichttechniker +500 CHF")
    rab   = st.checkbox("Kulturrabatt 20 % (außer Technik)")
    sonst = st.number_input("Sonstiges (CHF)", 0, step=50)
    st.markdown("</div>", unsafe_allow_html=True)

# ========================
# — Fahrt & Anwesenheit —
# ========================
with st.expander("🚗 Fahrt & Anwesenheit", expanded=False):
    no_sp = st.checkbox("Keine Spesen verrechnen", value=True)
    fd    = st.slider("Fahrtzeit (Minuten)", 0, 300, step=5)
    sp    = 0 if no_sp else (500 if fd<=60 else 800 if fd<=120 else 1200)
    st.info(f"Spesen: {sp} CHF")

    no_ah = st.checkbox("Keine Anwesenheit", value=True)
    stt   = st.time_input("Startzeit", time(17,0))
    ett   = st.time_input("Endzeit", time(20,0))
    ah    = (
        datetime.combine(datetime.today(), ett)
      - datetime.combine(datetime.today(), stt)
    ).seconds / 3600

    ph = st.number_input("CHF/Stunde Musiker", 0, step=10, value=50)

# ========================
# — Berechnung —
# ========================
base    = n1*g1 + n2*g2 + n3*g3
add     = ((dur-45)//15)*500 if dur>45 else 0
c1, c2, c3 = (500 if opt1 else 0), (500 if opt2 else 0), (500 if opt3 else 0)
anw     = 0 if no_ah else ah * ph * (n1+n2+n3)
rab_amt = (base+add+c1+sp+sonst)*0.2 if rab else 0
total   = base + add + c1 + c2 + c3 + sp + sonst + anw - rab_amt

# Für Summary & Erfolgsrechnung
profi_count  = n1 + n2
profi_sum    = n1*g1 + n2*g2
mus_count    = n3
mus_sum      = n3*g3
musik_extra  = dur-45 if dur>45 else 0

# ========================
# — Zusammenfassung & Gagenvorschlag —
# ========================
with st.expander("📋 Zusammenfassung", expanded=False):
    st.markdown(f"""
    <div class='summary-box'>
      <h4>Musiker</h4>
      Profi Musiker ({profi_count} Pers.): {profi_sum:.2f} CHF<br>
      Musiker ({mus_count} Pers.): {mus_sum:.2f} CHF<br>
      Anzahl Personen: {profi_count + mus_count}
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='summary-box'>
      <h4>Zuschläge</h4>
      Musik (+{musik_extra} min): {add:.2f} CHF<br>
      Verstärkung: {c1:.2f} CHF<br>
      Tontechnik: {c2:.2f} CHF<br>
      Lichttechnik: {c3:.2f} CHF<br>
      Anfahrt/Spesen: {sp:.2f} CHF<br>
      Anwesenheit: {anw:.2f} CHF<br>
      Sonstiges: {sonst:.2f} CHF<br>
      <strong>Kulturrabatt:</strong> −{rab_amt:.2f} CHF
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='proposal-box'>
      <h4>Gagenvorschlag</h4>
      <p style='font-size:24px; margin:0;'>{total:.2f} CHF</p>
    </div>""", unsafe_allow_html=True)

# ========================
# — Erfolgsrechnung für die Band —
# ========================
with st.expander("💪 Erfolgsrechnung", expanded=False):
    offer = st.number_input("Offerierte Gage (CHF)", 0, step=50, key="offer")
    kosten_profis    = profi_sum
    kosten_spesen    = sp
    kosten_ton       = c2
    kosten_licht     = c3
    netto_gewinn     = offer - (kosten_profis + kosten_spesen + kosten_ton + kosten_licht)

    st.markdown(f"""
    <div class='result-box'>
      <strong>Offerierte Gage:</strong> {offer:.2f} CHF<br><br>
      <strong>Effektive Kosten:</strong><br>
      &nbsp;&nbsp;Profis: {kosten_profis:.2f} CHF<br>
      &nbsp;&nbsp;Spesen: {kosten_spesen:.2f} CHF<br>
      &nbsp;&nbsp;Tontechnik: {kosten_ton:.2f} CHF<br>
      &nbsp;&nbsp;Lichttechnik: {kosten_licht:.2f} CHF<br><br>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='proposal-box'>
      <h4>Netto-Gewinn der Band</h4>
      <p style='font-size:24px; margin:0;'>{netto_gewinn:.2f} CHF</p>
    </div>""", unsafe_allow_html=True)

# ========================
# 📄 PDF-Export mit Branding & Erfolgsrechnung
# ========================
st.header("📄 PDF-Export")
if st.button("PDF erzeugen"):
    pdf = FPDF()
    pdf.add_page()

    # ── Kopfzeile ──
    pdf.set_fill_color(0, 77, 89)        # Petrol
    pdf.rect(0, 0, 210, 12, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Brass Department Gagenrechner", ln=True, align='C')
    pdf.ln(5)

    # ── Konzert-Name ──
    concert_title = st.session_state.get("current_gig", "Konzert")
    pdf.set_text_color(0, 77, 89)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Konzert: {concert_title}", ln=True)
    pdf.ln(3)

    # ── Musiker ──
    pdf.set_fill_color(247, 166, 0)      # Orange
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Musiker", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f"Profi Musiker ({profi_count} Pers.): {profi_sum:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Musiker ({mus_count} Pers.): {mus_sum:.2f} CHF", ln=True)
    pdf.ln(4)

    # ── Zuschläge ──
    pdf.set_fill_color(253, 241, 231)    # Beige
    pdf.set_text_color(0, 77, 89)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Zuschläge", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f"Musik (+{musik_extra} min): {add:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Verstärkung: {c1:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Tontechniker: {c2:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Lichttechniker: {c3:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Anfahrt/Spesen: {sp:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Anwesenheit: {anw:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Sonstiges: {sonst:.2f} CHF", ln=True)
    if rab:
        pdf.cell(0, 6, f"Kulturrabatt: -{rab_amt:.2f} CHF", ln=True)
    pdf.ln(5)

    # ── Gagenvorschlag ──
    pdf.set_fill_color(0, 115, 138)      # Dunkler Petrol
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Gagenvorschlag", ln=True, fill=True)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f"{total:.2f} CHF", ln=True, align='C')
    pdf.ln(5)

    # ── Netto-Erfolgsrechnung der Band ──
    pdf.set_fill_color(247, 166, 0)      # Orange
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Netto-Erfolgsrechnung der Band", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f"Offerierte Gage: {offer:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Kosten Profis: {kosten_profis:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Spesen: {kosten_spesen:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Tontechnik: {kosten_ton:.2f} CHF", ln=True)
    pdf.cell(0, 6, f"Lichttechnik: {kosten_licht:.2f} CHF", ln=True)
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Netto-Gewinn: {netto:.2f} CHF", ln=True)

    # ── In-Memory-Stream & Download ──
    pdf_buffer = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_bytes)
    pdf_buffer.seek(0)

    st.download_button(
        label="PDF herunterladen",
        data=pdf_buffer,
        file_name=f"{concert_title.replace(' ', '_')}_Gagen.pdf",
        mime="application/pdf"
    )
