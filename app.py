import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import io

# 🔐 PROTECTION IMMEDIATA - MODIFICA QUESTA PASSWORD
PASSWORD = "maniscalco2024"  # Cambia con una password tua!

# Check password
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Il Maniscalco - Accesso Protetto")
    password_input = st.text_input("Inserisci la password di accesso:", type="password")
    
    if st.button("Accedi"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Password errata!")
    st.stop()
    
# Configurazione pagina
st.set_page_config(
    page_title="Il Maniscalco - Podologia Bovina",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "database.db"

def init_database():
    """Inizializza il database con tutte le tabelle"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabella aziende - COMPLETATA
    c.execute('''
        CREATE TABLE IF NOT EXISTS aziende (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            telefono TEXT,
            email TEXT,
            indirizzo TEXT,
            responsabile TEXT,
            note TEXT,
            data_inserimento TEXT,
            attiva INTEGER DEFAULT 1
        )
    ''')
    
    # Tabella bovini - AGGIORNATA con eliminazione soft
    c.execute('''
        CREATE TABLE IF NOT EXISTS bovini (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            azienda_id INTEGER,
            razza TEXT,
            eta INTEGER,
            stato_fisiologico TEXT,
            data_inserimento TEXT,
            note TEXT,
            eliminato INTEGER DEFAULT 0,
            motivo_eliminazione TEXT,
            data_eliminazione TEXT,
            FOREIGN KEY (azienda_id) REFERENCES aziende (id)
        )
    ''')
    
    # Tabella trattamenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS trattamenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            bovino_id TEXT NOT NULL,
            tipo_attivo TEXT,
            sottotipo_trattamento TEXT,
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
    
    # Dati esempio aziende
    c.execute("SELECT COUNT(*) FROM aziende")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO aziende (nome, telefono, email, indirizzo, responsabile, note, data_inserimento)
            VALUES 
            ('Az. Agricola Rossi', '+39 0123 456789', 'rossi@email.com', 'Via Roma 123, Torino (TO)', 'Mario Rossi', 'Clienti da 5 anni', datetime('now')),
            ('Az. Agricola Bianchi', '+39 0123 456788', 'bianchi@email.com', 'Via Milano 45, Cuneo (CN)', 'Laura Bianchi', 'Nuovi clienti', datetime('now'))
        ''')
    
    # Dati esempio bovini
    c.execute("SELECT COUNT(*) FROM bovini")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO bovini (id, nome, azienda_id, razza, eta, stato_fisiologico, data_inserimento, note)
            VALUES 
            ('BOV001', 'Margherita', 1, 'Frisona', 4, 'Lattazione', datetime('now'), 'Bovina tranquilla'),
            ('BOV002', 'Stella', 2, 'Bruna Alpina', 5, 'Asciutta', datetime('now'), 'Attenzione zoccoli posteriori')
        ''')
    
    conn.commit()
    conn.close()

# Inizializza DB
init_database()

# ============================================================================
# FUNZIONI AZIENDE
# ============================================================================
def aggiungi_azienda(nome, telefono, email, indirizzo, responsabile, note):
    try:
        if not nome:
            return False, "❌ Nome azienda obbligatorio"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Controlla se esiste già
        c.execute("SELECT nome FROM aziende WHERE nome = ?", (nome,))
        if c.fetchone():
            conn.close()
            return False, "❌ Azienda già esistente"
        
        data_inserimento = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        c.execute('''
            INSERT INTO aziende (nome, telefono, email, indirizzo, responsabile, note, data_inserimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, telefono, email, indirizzo, responsabile, note, data_inserimento))
        
        conn.commit()
        conn.close()
        return True, f"✅ Azienda '{nome}' aggiunta!"
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"

def carica_aziende(attive=True):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT id, nome, telefono, email, indirizzo, responsabile FROM aziende WHERE attiva = 1 ORDER BY nome"
        if not attive:
            query = "SELECT id, nome, telefono, email, indirizzo, responsabile FROM aziende ORDER BY nome"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def cerca_aziende(testo):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT id, nome, telefono, email, indirizzo, responsabile 
        FROM aziende 
        WHERE attiva = 1 AND (
            nome LIKE ? OR 
            indirizzo LIKE ? OR 
            responsabile LIKE ? OR
            telefono LIKE ?
        )
        ORDER BY nome
        """
        parametro = f'%{testo}%'
        df = pd.read_sql_query(query, conn, params=[parametro, parametro, parametro, parametro])
        conn.close()
        return df
    except:
        return pd.DataFrame()

def carica_azienda_dettaglio(azienda_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, nome, telefono, email, indirizzo, responsabile, note, data_inserimento
            FROM aziende 
            WHERE id = ? AND attiva = 1
        ''', (azienda_id,))
        azienda = c.fetchone()
        conn.close()
        return azienda
    except:
        return None

def carica_bovini_azienda(azienda_id, solo_attivi=True):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT id, nome, razza, eta, stato_fisiologico, data_inserimento, note
        FROM bovini 
        WHERE azienda_id = ? AND eliminato = 0
        ORDER BY nome
        """
        if not solo_attivi:
            query = """
            SELECT id, nome, razza, eta, stato_fisiologico, data_inserimento, note, eliminato
            FROM bovini 
            WHERE azienda_id = ?
            ORDER BY nome
            """
        
        df = pd.read_sql_query(query, conn, params=(azienda_id,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def cerca_bovini_azienda(azienda_id, testo):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT id, nome, razza, eta, stato_fisiologico, data_inserimento, note
        FROM bovini 
        WHERE azienda_id = ? AND eliminato = 0 AND (
            id LIKE ? OR 
            nome LIKE ? OR 
            razza LIKE ?
        )
        ORDER BY nome
        """
        parametro = f'%{testo}%'
        df = pd.read_sql_query(query, conn, params=(azienda_id, parametro, parametro, parametro))
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ============================================================================
# FUNZIONI BOVINI
# ============================================================================
def aggiungi_bovino(id, nome, azienda_id, razza, eta, stato_fisiologico, note):
    try:
        if not id or not nome or not azienda_id:
            return False, "❌ ID, Nome e Azienda obbligatori"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Controlla se esiste già
        c.execute("SELECT id FROM bovini WHERE id = ?", (id,))
        if c.fetchone():
            conn.close()
            return False, "❌ ID già usato"
        
        data_inserimento = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        c.execute('''
            INSERT INTO bovini (id, nome, azienda_id, razza, eta, stato_fisiologico, data_inserimento, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, nome, azienda_id, razza, eta, stato_fisiologico, data_inserimento, note))
        
        conn.commit()
        conn.close()
        return True, f"✅ {nome} aggiunto!"
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"

def elimina_bovino(bovino_id, motivo):
    try:
        if not motivo:
            return False, "❌ Specifica il motivo dell'eliminazione"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        data_eliminazione = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        c.execute('''
            UPDATE bovini 
            SET eliminato = 1, motivo_eliminazione = ?, data_eliminazione = ?
            WHERE id = ?
        ''', (motivo, data_eliminazione, bovino_id))
        
        conn.commit()
        conn.close()
        return True, f"✅ Bovino eliminato (motivo: {motivo})"
    except Exception as e:
        return False, f"❌ Errore: {str(e)}"

def carica_bovini_eliminati():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT b.id, b.nome, b.razza, a.nome as azienda, 
               b.motivo_eliminazione, b.data_eliminazione
        FROM bovini b
        JOIN aziende a ON b.azienda_id = a.id
        WHERE b.eliminato = 1
        ORDER BY b.data_eliminazione DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def carica_lista_bovini():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT b.id, b.nome, a.nome as azienda
            FROM bovini b
            JOIN aziende a ON b.azienda_id = a.id
            WHERE b.eliminato = 0
            ORDER BY b.nome
        ''')
        bovini = c.fetchall()
        conn.close()
        return [(f"{bovino[0]} - {bovino[1]} ({bovino[2]})", bovino[0]) for bovino in bovini]
    except:
        return []

# ============================================================================
# FUNZIONI TRATTAMENTI (ESISTENTI)
# ============================================================================
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
        SELECT t.data, b.nome as bovino, a.nome as azienda, 
               t.tipo_attivo, t.sottotipo_trattamento,
               t.zoccolo_ad, t.zoccolo_as, t.zoccolo_pd, t.zoccolo_ps,
               t.costo, t.prossimo_controllo
        FROM trattamenti t
        JOIN bovini b ON t.bovino_id = b.id
        JOIN aziende a ON b.azienda_id = a.id
        ORDER BY t.data DESC
        LIMIT 20
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ============================================================================
# STATISTICHE
# ============================================================================
def carica_statistiche():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Conta aziende attive
        c.execute("SELECT COUNT(*) FROM aziende WHERE attiva = 1")
        aziende_attive = c.fetchone()[0]
        
        # Conta bovini attivi
        c.execute("SELECT COUNT(*) FROM bovini WHERE eliminato = 0")
        bovini_attivi = c.fetchone()[0]
        
        # Conta trattamenti mese
        mese_corrente = datetime.now().strftime("%m/%Y")
        c.execute("SELECT COUNT(*) FROM trattamenti WHERE strftime('%m/%Y', data) = ?", (mese_corrente,))
        trattamenti_mese = c.fetchone()[0]
        
        # Conta bovini eliminati
        c.execute("SELECT COUNT(*) FROM bovini WHERE eliminato = 1")
        bovini_eliminati = c.fetchone()[0]
        
        conn.close()
        
        return {
            "aziende": aziende_attive,
            "bovini": bovini_attivi,
            "trattamenti_mese": trattamenti_mese,
            "eliminati": bovini_eliminati
        }
    except:
        return {"aziende": 0, "bovini": 0, "trattamenti_mese": 0, "eliminati": 0}

# ============================================================================
# INTERFACCIA STREAMLIT
# ============================================================================
def main():
    # CSS personalizzato
    st.markdown("""
    <style>
    .main-title {
        color: #8B4513;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
    }
    .azienda-card {
        background: #f8f9fa;
        border-left: 4px solid #8B4513;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-title">🐄 Il Maniscalco</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="subtitle">Gestione Podologia Bovina</h3>', unsafe_allow_html=True)
    
    # Menu principale - RIORGANIZZATO
    menu = st.sidebar.radio(
        "📋 MENU PRINCIPALE",
        ["🏠 Dashboard", "🏢 Aziende", "🐄 Bovini", "🔧 Trattamenti", "📊 Storico", "🗑️ Eliminazioni"]
    )
    
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "🏢 Aziende":
        show_aziende()
    elif menu == "🐄 Bovini":
        show_bovini()
    elif menu == "🔧 Trattamenti":
        show_trattamenti()
    elif menu == "📊 Storico":
        show_storico()
    elif menu == "🗑️ Eliminazioni":
        show_eliminazioni()

def show_dashboard():
    st.header("📊 Dashboard")
    
    stats = carica_statistiche()
    
    # Statistiche
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Aziende Attive", stats["aziende"])
    
    with col2:
        st.metric("🐄 Bovini Attivi", stats["bovini"])
    
    with col3:
        st.metric("🔧 Trattamenti Mese", stats["trattamenti_mese"])
    
    with col4:
        st.metric("🗑️ Bovini Eliminati", stats["eliminati"])
    
    # Ultime aziende
    st.subheader("🏢 Ultime Aziende")
    aziende = carica_aziende()
    if not aziende.empty:
        st.dataframe(aziende[['nome', 'responsabile', 'telefono']].head(5), use_container_width=True)
    else:
        st.info("Nessuna azienda registrata")
    
    # Prossimi controlli
    st.subheader("🔄 Prossimi Controlli")
    trattamenti = carica_trattamenti()
    if not trattamenti.empty:
        prossimi = trattamenti.head(3)[['bovino', 'azienda', 'prossimo_controllo']]
        for _, row in prossimi.iterrows():
            st.write(f"• **{row['bovino']}** ({row['azienda']}) - {row['prossimo_controllo']}")
    else:
        st.info("Nessun controllo programmato")

def show_aziende():
    st.header("🏢 Gestione Aziende")
    
    tab1, tab2, tab3 = st.tabs(["➕ Nuova Azienda", "🔍 Cerca Aziende", "📋 Elenco Aziende"])
    
    with tab1:
        with st.form("nuova_azienda"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("🏢 Nome Azienda *", placeholder="Az. Agricola Rossi")
                telefono = st.text_input("📞 Telefono", placeholder="+39 0123 456789")
                email = st.text_input("📧 Email", placeholder="azienda@email.com")
            
            with col2:
                indirizzo = st.text_area("📍 Indirizzo", placeholder="Via Roma 123, Città (PR)", height=100)
                responsabile = st.text_input("👤 Responsabile", placeholder="Mario Rossi")
                note = st.text_area("📝 Note", placeholder="Note importanti...")
            
            if st.form_submit_button("💾 SALVA AZIENDA", use_container_width=True):
                if nome:
                    success, msg = aggiungi_azienda(nome, telefono, email, indirizzo, responsabile, note)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("⚠️ Nome azienda obbligatorio")
    
    with tab2:
        st.subheader("🔍 Cerca Azienda")
        ricerca = st.text_input("Cerca per nome, indirizzo, responsabile...")
        
        if ricerca:
            aziende = cerca_aziende(ricerca)
            if not aziende.empty:
                for idx, row in aziende.iterrows():
                    with st.container():
                        st.markdown(f'''
                        <div class="azienda-card">
                            <h4>🏢 {row['nome']}</h4>
                            <p>👤 <strong>Responsabile:</strong> {row['responsabile']}</p>
                            <p>📍 <strong>Indirizzo:</strong> {row['indirizzo']}</p>
                            <p>📞 <strong>Telefono:</strong> {row['telefono']}</p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Pulsante per vedere i bovini dell'azienda
                        if st.button(f"👀 Vedi Bovini {row['nome']}", key=f"vedi_{row['id']}"):
                            st.session_state.azienda_selezionata = row['id']
                            st.session_state.nome_azienda = row['nome']
                            st.rerun()
            else:
                st.info("Nessuna azienda trovata")
    
    with tab3:
        st.subheader("📋 Elenco Aziende")
        aziende = carica_aziende()
        if not aziende.empty:
            st.dataframe(aziende, use_container_width=True)
        else:
            st.info("Nessuna azienda registrata")
    
    # Se è stata selezionata un'azienda, mostra i suoi bovini
    if "azienda_selezionata" in st.session_state:
        st.divider()
        show_bovini_azienda(st.session_state.azienda_selezionata, st.session_state.nome_azienda)

def show_bovini_azienda(azienda_id, nome_azienda):
    st.header(f"🐄 Bovini - {nome_azienda}")
    
    # Cerca bovini nell'azienda
    ricerca = st.text_input(f"🔍 Cerca bovini in {nome_azienda}...")
    
    if ricerca:
        bovini = cerca_bovini_azienda(azienda_id, ricerca)
    else:
        bovini = carica_bovini_azienda(azienda_id)
    
    if not bovini.empty:
        st.dataframe(bovini, use_container_width=True)
    else:
        st.info("Nessun bovino registrato per questa azienda")
    
    # Aggiungi bovino a questa azienda
    with st.expander("➕ AGGIUNGI BOVINO A QUESTA AZIENDA", expanded=False):
        with st.form("nuovo_bovino_azienda"):
            col1, col2 = st.columns(2)
            
            with col1:
                bovino_id = st.text_input("📋 ID BOVINO *", placeholder="BOV003")
                nome = st.text_input("🐮 NOME *", placeholder="Nuovo bovino")
                razza = st.selectbox("🎯 RAZZA", ["Frisona", "Bruna", "Pezzata Rossa", "Jersey", "Altro"])
            
            with col2:
                eta = st.number_input("📅 ETÀ (anni)", min_value=0, max_value=20, value=3)
                stato = st.selectbox("🔄 STATO FISIOLOGICO *", ["Lattazione", "Asciutta"])
                note = st.text_area("📝 NOTE", placeholder="Note importanti...")
            
            if st.form_submit_button("💾 AGGIUNGI BOVINO", use_container_width=True):
                if bovino_id and nome:
                    success, msg = aggiungi_bovino(bovino_id, nome, azienda_id, razza, eta, stato, note)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("⚠️ ID e Nome obbligatori")

def show_bovini():
    st.header("🐄 Gestione Bovini")
    
    tab1, tab2 = st.tabs(["➕ Nuovo Bovino", "❌ Elimina Bovino"])
    
    with tab1:
        # Seleziona azienda prima di aggiungere bovino
        aziende = carica_aziende()
        if aziende.empty:
            st.error("❌ Prima registra almeno un'azienda")
            return
        
        aziende_opzioni = [(row['nome'], row['id']) for _, row in aziende.iterrows()]
        azienda_selezionata = st.selectbox(
            "🏢 SELEZIONA AZIENDA *",
            options=[a[1] for a in aziende_opzioni],
            format_func=lambda x: [a[0] for a in aziende_opzioni if a[1] == x][0]
        )
        
        with st.form("nuovo_bovino_generale"):
            col1, col2 = st.columns(2)
            
            with col1:
                bovino_id = st.text_input("📋 ID BOVINO *", placeholder="BOV003")
                nome = st.text_input("🐮 NOME *", placeholder="Nuovo bovino")
                razza = st.selectbox("🎯 RAZZA", ["Frisona", "Bruna", "Pezzata Rossa", "Jersey", "Altro"])
            
            with col2:
                eta = st.number_input("📅 ETÀ (anni)", min_value=0, max_value=20, value=3)
                stato = st.selectbox("🔄 STATO FISIOLOGICO *", ["Lattazione", "Asciutta"])
                note = st.text_area("📝 NOTE", placeholder="Note importanti...")
            
            if st.form_submit_button("💾 SALVA BOVINO", use_container_width=True):
                if bovino_id and nome and azienda_selezionata:
                    success, msg = aggiungi_bovino(bovino_id, nome, azienda_selezionata, razza, eta, stato, note)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("⚠️ ID, Nome e Azienda obbligatori")
    
    with tab2:
        st.subheader("❌ Elimina Bovino")
        
        bovini_lista = carica_lista_bovini()
        if not bovini_lista:
            st.error("Nessun bovino registrato")
            return
        
        bovino_selezionato = st.selectbox(
            "Seleziona bovino da eliminare:",
            options=[b[0] for b in bovini_lista],
            format_func=lambda x: x
        )
        
        bovino_id = [b[1] for b in bovini_lista if b[0] == bovino_selezionato][0]
        
        motivo = st.selectbox(
            "Motivo eliminazione:",
            ["Venduto", "Deceduto", "Trasferito", "Altro"]
        )
        
        if motivo == "Altro":
            motivo = st.text_input("Specifica motivo:")
        
        conferma = st.checkbox("Confermo di voler eliminare questo bovino")
        
        if st.button("🗑️ ELIMINA BOVINO", type="primary", disabled=not conferma):
            success, msg = elimina_bovino(bovino_id, motivo)
            if success:
                st.error(msg)  # Usiamo error per attirare l'attenzione
                st.rerun()
            else:
                st.error(msg)

def show_trattamenti():
    # (MANTENIAMO IL TUO CODICE ESISTENTE PER I TRATTAMENTI)
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
            format_func=lambda x: x.split(" - ")[0]  # Mostra solo ID e nome
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
        
        # Zoccoli
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
    st.header("📊 Storico Trattamenti")
    
    trattamenti = carica_trattamenti()
    if not trattamenti.empty:
        # Filtri
        col1, col2 = st.columns(2)
        with col1:
            cerca_bovino = st.text_input("🔍 Cerca bovino o azienda")
        with col2:
            cerca_tipo = st.selectbox("🔧 Filtra per tipo", ["Tutti"] + list(trattamenti['tipo_attivo'].unique()))
        
        # Applica filtri
        trattamenti_filtrati = trattamenti
        if cerca_bovino:
            trattamenti_filtrati = trattamenti_filtrati[
                trattamenti_filtrati['bovino'].str.contains(cerca_bovino, case=False) |
                trattamenti_filtrati['azienda'].str.contains(cerca_bovino, case=False)
            ]
        if cerca_tipo != "Tutti":
            trattamenti_filtrati = trattamenti_filtrati[trattamenti_filtrati['tipo_attivo'] == cerca_tipo]
        
        st.dataframe(trattamenti_filtrati, use_container_width=True)
    else:
        st.info("📝 Nessun trattamento registrato")

def show_eliminazioni():
    st.header("🗑️ Bovini Eliminati")
    
    eliminati = carica_bovini_eliminati()
    if not eliminati.empty:
        st.dataframe(eliminati, use_container_width=True)
        
        # Export CSV
        csv = eliminati.to_csv(index=False)
        st.download_button(
            label="📥 Scarica storico eliminazioni (CSV)",
            data=csv,
            file_name=f"eliminazioni_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nessun bovino eliminato")

if __name__ == "__main__":
    main()
