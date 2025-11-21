import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Configurazione pagina
st.set_page_config(
    page_title="Il Maniscalco - Podologia Bovina",
    page_icon="logoicona.png"
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<head>
    <meta property="og:image" content="https://ilmaniscalco.onrender.com/imgapp.png">
    <meta property="og:title" content="Il Maniscalco - Podologia Bovina">
    <meta property="og:description" content="Gestione professionale trattamenti podologici per bovini">
</head>
""", unsafe_allow_html=True)
DB_PATH = "database.db"

def init_database():
    """Inizializza il database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabella bovini
    c.execute('''
        CREATE TABLE IF NOT EXISTS bovini (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            azienda TEXT,
            razza TEXT,
            eta INTEGER,
            stato_fisiologico TEXT,
            data_inserimento TEXT,
            note TEXT
        )
    ''')
    
    # Tabella trattamenti - SEMPLIFICATA
    c.execute('''
        CREATE TABLE IF NOT EXISTS trattamenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            bovino_id TEXT NOT NULL,
            tipo_attivo TEXT,
            sottotipo_trattamento TEXT,
            
            -- Zoccoli specifici SEMPLIFICATI
            zoccolo_ad TEXT,
            zoccolo_as TEXT,
            zoccolo_pd TEXT,
            zoccolo_ps TEXT,
            
            materiali TEXT,
            durata_minuti INTEGER,
            costo REAL,
            note TEXT,
            prossimo_controllo TEXT,
            FOREIGN KEY (bovino_id) REFERENCES bovini (id)
        )
    ''')
    
    # Dati esempio
    c.execute("SELECT COUNT(*) FROM bovini")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO bovini (id, nome, azienda, razza, eta, stato_fisiologico, data_inserimento, note)
            VALUES 
            ('BOV001', 'Margherita', 'Az. Agricola Rossi', 'Frisona', 4, 'Lattazione', datetime('now'), 'Bovina tranquilla'),
            ('BOV002', 'Stella', 'Az. Agricola Bianchi', 'Bruna Alpina', 5, 'Asciutta', datetime('now'), 'Attenzione zoccoli posteriori')
        ''')
    
    conn.commit()
    conn.close()

# Inizializza DB
init_database()

# FUNZIONI DATABASE SEMPLIFICATE
def aggiungi_bovino(id, nome, azienda, razza, eta, stato_fisiologico, note):
    try:
        if not id or not nome:
            return "❌ Inserisci ID e Nome"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT id FROM bovini WHERE id = ?", (id,))
        if c.fetchone():
            conn.close()
            return "❌ ID già usato"
        
        data_inserimento = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        c.execute('''
            INSERT INTO bovini (id, nome, azienda, razza, eta, stato_fisiologico, data_inserimento, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, nome, azienda, razza, eta, stato_fisiologico, data_inserimento, note))
        
        conn.commit()
        conn.close()
        return f"✅ {nome} aggiunto!"
    except Exception as e:
        return f"❌ Errore: {str(e)}"

def carica_bovini():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, nome, azienda, razza, eta, stato_fisiologico FROM bovini ORDER BY nome", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def carica_lista_bovini():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM bovini ORDER BY nome")
        bovini = c.fetchall()
        conn.close()
        return [(f"{bovino[0]} - {bovino[1]}", bovino[0]) for bovino in bovini]
    except:
        return []

def aggiungi_trattamento(bovino_id, tipo_attivo, sottotipo_trattamento, 
                        zoccolo_ad, zoccolo_as, zoccolo_pd, zoccolo_ps,
                        materiali, durata, costo, note, prossimo_controllo):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        data_trattamento = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        c.execute('''
            INSERT INTO trattamenti (
                data, bovino_id, tipo_attivo, sottotipo_trattamento,
                zoccolo_ad, zoccolo_as, zoccolo_pd, zoccolo_ps,
                materiali, durata_minuti, costo, note, prossimo_controllo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data_trattamento, bovino_id, tipo_attivo, sottotipo_trattamento,
              zoccolo_ad, zoccolo_as, zoccolo_pd, zoccolo_ps,
              materiali, durata, costo, note, prossimo_controllo))
        
        conn.commit()
        conn.close()
        return True, "✅ Trattamento salvato!"
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"

def carica_trattamenti():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT t.data, b.nome as bovino, t.tipo_attivo, t.sottotipo_trattamento,
               t.zoccolo_ad, t.zoccolo_as, t.zoccolo_pd, t.zoccolo_ps,
               t.costo, t.prossimo_controllo
        FROM trattamenti t
        JOIN bovini b ON t.bovino_id = b.id
        ORDER BY t.data DESC
        LIMIT 20
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# DIAGRAMMA ZOCCOLI VISIVO SEMPLICE
def mostra_diagramma_zoccoli(ad_val="", as_val="", pd_val="", ps_val=""):
    """Diagramma visivo semplice con emoji"""
    st.markdown("""
    <style>
    .zoccolo-box {
        background: #f8f9fa;
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        min-height: 80px;
    }
    .zoccolo-label {
        font-weight: bold;
        color: #8B4513;
        font-size: 14px;
    }
    .zoccolo-value {
        font-size: 12px;
        color: #2E8B57;
        min-height: 40px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout a forma di bovino
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("**ANTERIORI**")
        
    with col2:
        # Zoccoli anteriori
        col_ad, col_as = st.columns(2)
        with col_ad:
            st.markdown(f'''
            <div class="zoccolo-box">
                <div class="zoccolo-label">🦶 ANTERIORE DESTRO</div>
                <div class="zoccolo-value">{ad_val if ad_val else "Nessun trattamento"}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_as:
            st.markdown(f'''
            <div class="zoccolo-box">
                <div class="zoccolo-label">🦶 ANTERIORE SINISTRO</div>
                <div class="zoccolo-value">{as_val if as_val else "Nessun trattamento"}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Corpo bovino (semplice)
        st.markdown("<div style='text-align: center; margin: 10px 0;'>🐄</div>", unsafe_allow_html=True)
        
        # Zoccoli posteriori
        col_pd, col_ps = st.columns(2)
        with col_pd:
            st.markdown(f'''
            <div class="zoccolo-box">
                <div class="zoccolo-label">🦶 POSTERIORE DESTRO</div>
                <div class="zoccolo-value">{pd_val if pd_val else "Nessun trattamento"}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_ps:
            st.markdown(f'''
            <div class="zoccolo-box">
                <div class="zoccolo-label">🦶 POSTERIORE SINISTRO</div>
                <div class="zoccolo-value">{ps_val if ps_val else "Nessun trattamento"}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown("**POSTERIORI**")

# INTERFACCIA PRINCIPALE SEMPLIFICATA
def main():
    # Header semplice
    st.title("🐄 Il Maniscalco")
    st.markdown("**Gestione trattamenti podologici bovini**")
    
    # Menu semplice
    menu = st.sidebar.radio(
        "MENU PRINCIPALE",
        ["🏠 Dashboard", "🐄 Bovini", "🔧 Trattamenti", "📋 Storico"]
    )
    
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "🐄 Bovini":
        show_bovini()
    elif menu == "🔧 Trattamenti":
        show_trattamenti()
    elif menu == "📋 Storico":
        show_storico()

def show_dashboard():
    st.header("📊 Riepilogo")
    
    bovini = carica_bovini()
    trattamenti = carica_trattamenti()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Bovini registrati", len(bovini))
    
    with col2:
        st.metric("Trattamenti totali", len(trattamenti))
    
    with col3:
        oggi = datetime.now().strftime("%d/%m/%Y")
        trattamenti_oggi = len([t for t in trattamenti.values if t[0].startswith(oggi)])
        st.metric("Trattamenti oggi", trattamenti_oggi)
    
    # Prossimi controlli
    st.subheader("🔄 Prossimi controlli")
    if not trattamenti.empty:
        prossimi = trattamenti.head(3)[['bovino', 'prossimo_controllo']]
        for _, row in prossimi.iterrows():
            st.write(f"• **{row['bovino']}** - {row['prossimo_controllo']}")
    else:
        st.info("Nessun controllo programmato")

def show_bovini():
    st.header("🐄 Gestione Bovini")
    
    # Form nuovo bovino
    with st.expander("➕ AGGIUNGI NUOVO BOVINO", expanded=True):
        with st.form("nuovo_bovino"):
            col1, col2 = st.columns(2)
            
            with col1:
                bovino_id = st.text_input("📋 ID BOVINO *", help="Es: BOV001")
                nome = st.text_input("🐮 NOME *", help="Es: Margherita")
                azienda = st.text_input("🏢 AZIENDA", help="Es: Az. Agricola Rossi")
            
            with col2:
                razza = st.selectbox("🎯 RAZZA", ["Frisona", "Bruna", "Pezzata Rossa", "Jersey", "Altro"])
                eta = st.number_input("📅 ETÀ (anni)", min_value=0, max_value=20, value=4)
                stato = st.selectbox("🔄 STATO FISIOLOGICO *", ["Lattazione", "Asciutta"])
            
            note = st.text_area("📝 NOTE", placeholder="Note importanti...")
            
            if st.form_submit_button("💾 SALVA BOVINO", use_container_width=True):
                if bovino_id and nome:
                    risultato = aggiungi_bovino(bovino_id, nome, azienda, razza, eta, stato, note)
                    st.success(risultato)
                else:
                    st.error("⚠️ Inserisci ID e Nome")
    
    # Lista bovini
    st.subheader("📋 BOVINI REGISTRATI")
    bovini = carica_bovini()
    if not bovini.empty:
        st.dataframe(bovini, use_container_width=True)
    else:
        st.info("📝 Nessun bovino registrato")

def show_trattamenti():
    st.header("🔧 Nuovo Trattamento")
    
    bovini_lista = carica_lista_bovini()
    if not bovini_lista:
        st.error("❌ Prima registra almeno un bovino")
        return
    
    with st.form("nuovo_trattamento"):
        # Selezione bovino
        bovino_selezionato = st.selectbox(
            "🐮 SELEZIONA BOVINO *",
            options=[b[0] for b in bovini_lista],
            format_func=lambda x: x.split(" - ")[1]
        )
        bovino_id = [b[1] for b in bovini_lista if b[0] == bovino_selezionato][0]
        
        # Tipo trattamento
        col1, col2 = st.columns(2)
        with col1:
            tipo_attivo = st.selectbox("🔧 TIPO ATTIVO *", ["Pareggio", "Rivista"])
            sottotipo = st.text_input("📋 Sottotipo", placeholder="Es: correttivo, preventivo...")
        
        with col2:
            durata = st.number_input("⏱️ DURATA (minuti)", min_value=5, max_value=180, value=30)
            costo = st.number_input("💰 COSTO (€)", min_value=0.0, value=40.0)
        
        # DIAGRAMMA ZOCCOLI
        st.subheader("🦶 TRATTAMENTI ZOCCOLI")
        st.info("Inserisci i trattamenti per ogni zoccolo:")
        
        col_ad, col_as, col_pd, col_ps = st.columns(4)
        
        with col_ad:
            zoccolo_ad = st.text_area("**Anteriore Destro**", placeholder="Es: Soletta\nUlcera", height=80)
        
        with col_as:
            zoccolo_as = st.text_area("**Anteriore Sinistro**", placeholder="Es: Fascia\nDermatite", height=80)
        
        with col_pd:
            zoccolo_pd = st.text_area("**Posteriore Destro**", placeholder="Es: Limatura\nNessuna", height=80)
        
        with col_ps:
            zoccolo_ps = st.text_area("**Posteriore Sinistro**", placeholder="Es: Controllo\nNormale", height=80)
        
        # Anteprima diagramma
        st.subheader("👀 ANTEPRIMA TRATTAMENTI")
        mostra_diagramma_zoccoli(zoccolo_ad, zoccolo_as, zoccolo_pd, zoccolo_ps)
        
        # Altri dati
        materiali = st.text_input("🛠️ MATERIALI USATI", placeholder="Es: Tosa, lime, disinfettante...")
        note = st.text_area("📝 NOTE TRATTAMENTO")
        prossimo = st.date_input("📅 PROSSIMO CONTROLLO", value=datetime.now() + timedelta(days=45))
        
        if st.form_submit_button("💾 REGISTRA TRATTAMENTO", use_container_width=True):
            success, messaggio = aggiungi_trattamento(
                bovino_id, tipo_attivo, sottotipo,
                zoccolo_ad, zoccolo_as, zoccolo_pd, zoccolo_ps,
                materiali, durata, costo, note, prossimo.strftime("%d/%m/%Y")
            )
            if success:
                st.success(messaggio)
                st.balloons()
            else:
                st.error(messaggio)

def show_storico():
    st.header("📋 Storico Trattamenti")
    
    trattamenti = carica_trattamenti()
    if not trattamenti.empty:
        # Filtri semplici
        col1, col2 = st.columns(2)
        with col1:
            cerca_bovino = st.text_input("🔍 Cerca bovino")
        with col2:
            cerca_tipo = st.selectbox("🔧 Filtra per tipo", ["Tutti"] + list(trattamenti['tipo_attivo'].unique()))
        
        # Applica filtri
        trattamenti_filtrati = trattamenti
        if cerca_bovino:
            trattamenti_filtrati = trattamenti_filtrati[trattamenti_filtrati['bovino'].str.contains(cerca_bovino, case=False)]
        if cerca_tipo != "Tutti":
            trattamenti_filtrati = trattamenti_filtrati[trattamenti_filtrati['tipo_attivo'] == cerca_tipo]
        
        st.dataframe(trattamenti_filtrati, use_container_width=True)
        
        # Dettaglio trattamento selezionato
        if len(trattamenti_filtrati) > 0:
            st.subheader("👀 DETTAGLIO TRATTAMENTO")
            idx = st.selectbox("Seleziona trattamento", range(len(trattamenti_filtrati)), 
                             format_func=lambda x: f"{trattamenti_filtrati.iloc[x]['bovino']} - {trattamenti_filtrati.iloc[x]['data']}")
            
            trattamento = trattamenti_filtrati.iloc[idx]
            mostra_diagramma_zoccoli(
                trattamento['zoccolo_ad'], 
                trattamento['zoccolo_as'], 
                trattamento['zoccolo_pd'], 
                trattamento['zoccolo_ps']
            )
    else:
        st.info("📝 Nessun trattamento registrato")

if __name__ == "__main__":
    main()
