import gradio as gr
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "database.db"

def init_database():
    """Inizializza il database per bovini"""
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
            stadio_lattazione TEXT,
            data_inserimento TEXT,
            note TEXT
        )
    ''')
    
    # Tabella trattamenti - SPECIALIZZATA PER BOVINI
    c.execute('''
        CREATE TABLE IF NOT EXISTS trattamenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            bovino_id TEXT NOT NULL,
            tipo_trattamento TEXT,
            condizione_zoccolo INTEGER,
            lesioni_riscontrate TEXT,
            materiali TEXT,
            durata_minuti INTEGER,
            costo REAL,
            note TEXT,
            prossimo_controllo TEXT,
            FOREIGN KEY (bovino_id) REFERENCES bovini (id)
        )
    ''')
    
    # Tabella aziende zootecniche - COMPLETATA
    c.execute('''
        CREATE TABLE IF NOT EXISTS aziende (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT,
            telefono TEXT,
            email TEXT,
            indirizzo TEXT,
            capienza INTEGER,
            specializzazione TEXT,
            data_inserimento TEXT,
            note TEXT
        )
    ''')
    
    # Dati di esempio per bovini
    c.execute("SELECT COUNT(*) FROM bovini")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO bovini (id, nome, azienda, razza, eta, stadio_lattazione, data_inserimento, note)
            VALUES 
            ('BOV001', 'Margherita', 'Az. Agricola Rossi', 'Frisona', 4, 'Picco lattazione', datetime('now'), 'Produttiva, zoccoli sani'),
            ('BOV002', 'Stella', 'Az. Agricola Bianchi', 'Bruna Alpina', 5, 'Fine lattazione', datetime('now'), 'Tendenza a dermatite digitale'),
            ('BOV003', 'Bianca', 'Az. Agricola Verdi', 'Pezzata Rossa', 3, 'Inizio lattazione', datetime('now'), 'Zoccoli fragili, controlli frequenti')
        ''')
        
        # Trattamenti di esempio per bovini
        c.execute('''
            INSERT INTO trattamenti (data, bovino_id, tipo_trattamento, condizione_zoccolo, lesioni_riscontrate, materiali, durata_minuti, costo, note, prossimo_controllo)
            VALUES 
            (datetime('now', '-15 days'), 'BOV001', 'Trim correttivo', 4, 'Nessuna', 'Tosa zoccoli, lima', 25, 35.0, 'Zoccoli in ottime condizioni', datetime('now', '+60 days')),
            (datetime('now', '-8 days'), 'BOV002', 'Trattamento dermatite', 2, 'Dermatite digitale', 'Disinfettante, bendaggio', 40, 50.0, 'Applicato antibatterico', datetime('now', '+30 days')),
            (datetime('now', '-3 days'), 'BOV003', 'Trim preventivo', 3, 'Leggera ulcera soleare', 'Silicone protettivo', 35, 45.0, 'Monitorare evoluzione ulcera', datetime('now', '+45 days'))
        ''')
    
    # Dati di esempio per aziende
    c.execute("SELECT COUNT(*) FROM aziende")
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO aziende (nome, tipo, telefono, email, indirizzo, capienza, specializzazione, data_inserimento, note)
            VALUES 
            ('Az. Agricola Rossi', 'Allevamento da latte', '+39 0123 456789', 'rossi@email.com', 'Via Roma 123, Torino (TO)', 120, 'Frisona, alta produzione', datetime('now'), 'Clienti da 5 anni, molto professionali'),
            ('Az. Agricola Bianchi', 'Allevamento misto', '+39 0123 456788', 'bianchi@email.com', 'Via Milano 45, Cuneo (CN)', 80, 'Bruna Alpina, biologico', datetime('now'), 'Nuovi clienti, attenti al benessere animale'),
            ('Centro Zootecnico Verde', 'Centro servizi', '+39 0123 456777', 'info@verde.com', 'Via Verdi 67, Asti (AT)', 200, 'Multi-razza, consulenza', datetime('now'), 'Grande azienda, richiedono sconti quantità')
        ''')
    
    conn.commit()
    conn.close()
    return "Database bovini inizializzato!"

# FUNZIONI BOVINI
def aggiungi_bovino(id, nome, azienda, razza, eta, stadio_lattazione, note):
    try:
        if not id or not nome:
            return "❌ ID e Nome sono obbligatori!"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT id FROM bovini WHERE id = ?", (id,))
        if c.fetchone():
            conn.close()
            return "❌ ID già esistente! Usa un ID univoco."
        
        data_inserimento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO bovini (id, nome, azienda, razza, eta, stadio_lattazione, data_inserimento, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, nome, azienda, razza, eta, stadio_lattazione, data_inserimento, note))
        
        conn.commit()
        conn.close()
        return f"✅ Bovino '{nome}' aggiunto con successo!"
    except Exception as e:
        return f"❌ Errore: {str(e)}"

def carica_bovini():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, nome, azienda, razza, eta, stadio_lattazione FROM bovini ORDER BY nome", conn)
        conn.close()
        return df if not df.empty else pd.DataFrame({"id": [], "nome": [], "azienda": [], "razza": [], "eta": [], "stadio_lattazione": []})
    except Exception as e:
        return pd.DataFrame({"id": [], "nome": [], "azienda": [], "razza": [], "eta": [], "stadio_lattazione": []})

def cerca_bovini(testo_ricerca):
    try:
        if not testo_ricerca.strip():
            return carica_bovini()
            
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT id, nome, azienda, razza, eta, stadio_lattazione 
        FROM bovini 
        WHERE id LIKE ? OR nome LIKE ? OR azienda LIKE ? OR razza LIKE ?
        ORDER BY nome
        """
        parametro = f'%{testo_ricerca}%'
        df = pd.read_sql_query(query, conn, params=[parametro, parametro, parametro, parametro])
        conn.close()
        return df if not df.empty else pd.DataFrame({"id": [], "nome": [], "azienda": [], "razza": [], "eta": [], "stadio_lattazione": []})
    except Exception as e:
        return pd.DataFrame({"id": [], "nome": [], "azienda": [], "razza": [], "eta": [], "stadio_lattazione": []})

# FUNZIONI TRATTAMENTI BOVINI
def carica_lista_bovini():
    """Carica la lista dei bovini per i dropdown"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM bovini ORDER BY nome")
        bovini = c.fetchall()
        conn.close()
        return [f"{bovino[0]} - {bovino[1]}" for bovino in bovini] if bovini else []
    except:
        return []

def carica_lista_aziende():
    """Carica la lista delle aziende per i dropdown"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nome FROM aziende ORDER BY nome")
        aziende = c.fetchall()
        conn.close()
        return [azienda[0] for azienda in aziende] if aziende else []
    except:
        return []

def aggiungi_trattamento(bovino_selezionato, tipo_trattamento, condizione_zoccolo, lesioni_riscontrate, materiali, durata, costo, note_trattamento, prossimo_controllo):
    try:
        if not bovino_selezionato:
            return "❌ Seleziona un bovino!", None
        
        bovino_id = bovino_selezionato.split(" - ")[0]
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        data_trattamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO trattamenti (data, bovino_id, tipo_trattamento, condizione_zoccolo, lesioni_riscontrate, materiali, durata_minuti, costo, note, prossimo_controllo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data_trattamento, bovino_id, tipo_trattamento, condizione_zoccolo, lesioni_riscontrate, materiali, durata, costo, note_trattamento, prossimo_controllo))
        
        conn.commit()
        conn.close()
        return f"✅ Trattamento registrato per {bovino_selezionato}!", None
    except Exception as e:
        return f"❌ Errore: {str(e)}", None

def carica_trattamenti():
    """Carica tutti i trattamenti per la visualizzazione"""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT t.id, t.data, b.nome as bovino, t.tipo_trattamento, t.condizione_zoccolo, 
               t.lesioni_riscontrate, t.materiali, t.durata_minuti, t.costo, t.note, t.prossimo_controllo
        FROM trattamenti t
        JOIN bovini b ON t.bovino_id = b.id
        ORDER BY t.data DESC
        LIMIT 50
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y %H:%M')
            df['prossimo_controllo'] = pd.to_datetime(df['prossimo_controllo']).dt.strftime('%d/%m/%Y')
            return df
        else:
            return pd.DataFrame({
                "id": [], "data": [], "bovino": [], "tipo_trattamento": [], "condizione_zoccolo": [],
                "lesioni_riscontrate": [], "materiali": [], "durata_minuti": [], "costo": [], "note": [], "prossimo_controllo": []
            })
    except Exception as e:
        return pd.DataFrame({
            "id": [], "data": [], "bovino": [], "tipo_trattamento": [], "condizione_zoccolo": [],
            "lesioni_riscontrate": [], "materiali": [], "durata_minuti": [], "costo": [], "note": [], "prossimo_controllo": []
        })

# FUNZIONI AZIENDE
def aggiungi_azienda(nome, tipo, telefono, email, indirizzo, capienza, specializzazione, note):
    try:
        if not nome:
            return "❌ Nome azienda obbligatorio!"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        data_inserimento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO aziende (nome, tipo, telefono, email, indirizzo, capienza, specializzazione, data_inserimento, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, tipo, telefono, email, indirizzo, capienza, specializzazione, data_inserimento, note))
        
        conn.commit()
        conn.close()
        return f"✅ Azienda '{nome}' aggiunta con successo!"
    except Exception as e:
        return f"❌ Errore: {str(e)}"

def carica_aziende():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT nome, tipo, telefono, email, indirizzo, capienza, specializzazione FROM aziende ORDER BY nome", conn)
        conn.close()
        return df if not df.empty else pd.DataFrame({"nome": [], "tipo": [], "telefono": [], "email": [], "indirizzo": [], "capienza": [], "specializzazione": []})
    except Exception as e:
        return pd.DataFrame({"nome": [], "tipo": [], "telefono": [], "email": [], "indirizzo": [], "capienza": [], "specializzazione": []})

def cerca_aziende(testo_ricerca):
    try:
        if not testo_ricerca.strip():
            return carica_aziende()
            
        conn = sqlite3.connect(DB_PATH)
        query = """
        SELECT nome, tipo, telefono, email, indirizzo, capienza, specializzazione 
        FROM aziende 
        WHERE nome LIKE ? OR tipo LIKE ? OR indirizzo LIKE ? OR specializzazione LIKE ?
        ORDER BY nome
        """
        parametro = f'%{testo_ricerca}%'
        df = pd.read_sql_query(query, conn, params=[parametro, parametro, parametro, parametro])
        conn.close()
        return df if not df.empty else pd.DataFrame({"nome": [], "tipo": [], "telefono": [], "email": [], "indirizzo": [], "capienza": [], "specializzazione": []})
    except Exception as e:
        return pd.DataFrame({"nome": [], "tipo": [], "telefono": [], "email": [], "indirizzo": [], "capienza": [], "specializzazione": []})

# INTERFACCIA PRINCIPALE PER BOVINI
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="green"
    ),
    title="Il Maniscalco - Gestione Podologia Bovina",
    css="""
    .header { 
        text-align: center; 
        padding: 20px; 
        background: linear-gradient(135deg, #8B4513 0%, #2E8B57 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stat-card { 
        background: white; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 4px solid #8B4513;
        margin: 10px 0;
    }
    """
) as app:
    
    init_database()
    
    # Header
    with gr.Column(elem_classes="header"):
        gr.Markdown("# 🐄 Il Maniscalco")
        gr.Markdown("### Gestione Professionale per Maniscalchi e Professionisti della podologia bovina!")
    
    with gr.Tab("🏠 Dashboard"):
        gr.Markdown("## Panoramica Attività Bovini")
        
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Column(elem_classes="stat-card"):
                    gr.Markdown("### 📊 Statistiche")
                    totale_bovini = gr.Textbox(label="Bovini registrati", value="Caricamento...", interactive=False)
                    trattamenti_mese = gr.Textbox(label="Trattamenti (30 giorni)", value="Caricamento...", interactive=False)
                    totale_aziende = gr.Textbox(label="Aziende clienti", value="Caricamento...", interactive=False)
            
            with gr.Column(scale=2):
                gr.Markdown("### 🎯 Azioni Rapide")
                with gr.Row():
                    btn_agg_bovino = gr.Button("➕ Nuovo Bovino")
                    btn_agg_trattamento = gr.Button("🔧 Nuovo Trattamento")
                    btn_agg_azienda = gr.Button("🏢 Nuova Azienda")
                
                gr.Markdown("### 📝 Situazione Zoccoli")
                situazione_html = gr.HTML(value="<div style='color: #666;'>Caricamento situazione zoccoli...</div>")

    with gr.Tab("🐄 Archivio Bovini"):
        gr.Markdown("## Gestione Archivio Bovini")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Aggiungi Nuovo Bovino")
                bovino_id = gr.Textbox(label="ID Bovino *", placeholder="Es: BOV001")
                nome_bovino = gr.Textbox(label="Nome *", placeholder="Nome del bovino")
                azienda = gr.Dropdown(
                    label="Azienda *",
                    choices=carica_lista_aziende(),
                    allow_custom_value=True
                )
                
                with gr.Row():
                    razza = gr.Dropdown(
                        choices=["Frisona", "Bruna Alpina", "Pezzata Rossa", "Jersey", "Simmental", "Charolaise", "Altro"],
                        label="Razza",
                        value="Frisona"
                    )
                    eta = gr.Number(label="Età (anni)", precision=0, minimum=0, maximum=15)
                
                stadio_lattazione = gr.Dropdown(
                    choices=["Asciutta", "Inizio lattazione", "Picco lattazione", "Fine lattazione", "Vitella"],
                    label="Stadio Lattazione",
                    value="Picco lattazione"
                )
                
                note_bovino = gr.Textbox(label="Note", lines=2, placeholder="Note comportamentali, problemi zoccoli, storia clinica...")
                
                btn_salva_bovino = gr.Button("💾 Salva Bovino", variant="primary")
                output_msg = gr.Textbox(label="Stato", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### Bovini Registrati")
                
                with gr.Row():
                    barra_ricerca = gr.Textbox(
                        placeholder="🔍 Cerca per ID, nome, azienda...",
                        show_label=False
                    )
                    btn_carica_bovini = gr.Button("🔄 Aggiorna")
                
                tabella_bovini = gr.Dataframe(
                    headers=["ID", "Nome", "Azienda", "Razza", "Età", "Stadio Lattazione"],
                    interactive=False
                )

    with gr.Tab("🔧 Trattamenti Zoccoli"):
        gr.Markdown("## Registro Trattamenti Podologici")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Nuovo Trattamento")
                
                bovino_selezionato = gr.Dropdown(
                    label="Seleziona Bovino *",
                    choices=carica_lista_bovini(),
                    interactive=True
                )
                
                tipo_trattamento = gr.Dropdown(
                    choices=["Trim correttivo", "Trim preventivo", "Trattamento dermatite", 
                            "Cura ulcera", "Applicazione solea", "Controllo routine", "Altro"],
                    label="Tipo di Trattamento *",
                    value="Trim preventivo"
                )
                
                condizione_zoccolo = gr.Slider(
                    minimum=1, maximum=5, value=3, step=1,
                    label="Condizione Zoccolo (1=pessima, 5=ottima)",
                    info="Valutazione generale dello stato zoccolo"
                )
                
                lesioni_riscontrate = gr.Dropdown(
                    choices=["Nessuna", "Dermatite digitale", "Ulcera soleare", "Fessurazione", 
                            "Ematoma", "Ascesso", "Laminite", "Multiple"],
                    label="Lesioni Riscotrate",
                    value="Nessuna"
                )
                
                materiali = gr.Textbox(
                    label="Materiali Utilizzati",
                    placeholder="Es: Tosa zoccoli, lima, disinfettante, bendaggio, silicone...",
                    lines=2
                )
                
                with gr.Row():
                    durata = gr.Number(label="Durata (minuti)", minimum=10, maximum=120, value=30)
                    costo = gr.Number(label="Costo (€)", minimum=0, maximum=200, value=40)
                
                note_trattamento = gr.Textbox(
                    label="Note Trattamento",
                    placeholder="Descrizione intervento, problemi riscontrati, consigli gestionali...",
                    lines=3
                )
                
                prossimo_controllo = gr.Textbox(
                    label="Prossimo Controllo (GG/MM/AAAA)",
                    placeholder="Es: 15/12/2024",
                    value=(datetime.now() + timedelta(days=45)).strftime("%d/%m/%Y")
                )
                
                btn_salva_trattamento = gr.Button("💾 Registra Trattamento", variant="primary")
                output_trattamento = gr.Textbox(label="Stato", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### Storico Trattamenti")
                btn_carica_trattamenti = gr.Button("🔄 Aggiorna Storico")
                storico_trattamenti = gr.Dataframe(
                    label="Ultimi Trattamenti",
                    headers=["Data", "Bovino", "Tipo", "Cond.Zoccolo", "Lesioni", "Materiali", "Durata", "Costo", "Prossimo Controllo"],
                    interactive=False
                )

    with gr.Tab("🏢 Aziende Zootecniche"):
        gr.Markdown("## Database Aziende Clienti")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Nuova Azienda")
                
                nome_azienda = gr.Textbox(label="Nome Azienda *", placeholder="Es: Az. Agricola Rossi")
                tipo_azienda = gr.Dropdown(
                    choices=["Allevamento da latte", "Allevamento misto", "Allevamento da carne", "Centro servizi", "Altro"],
                    label="Tipo Azienda",
                    value="Allevamento da latte"
                )
                
                telefono = gr.Textbox(label="Telefono", placeholder="+39 0123 456789")
                email = gr.Textbox(label="Email", placeholder="azienda@email.com")
                indirizzo = gr.Textbox(label="Indirizzo", placeholder="Via Roma 123, Città (PR)", lines=2)
                
                capienza = gr.Number(label="Capienza (numero bovini)", minimum=0, maximum=1000, value=100)
                specializzazione = gr.Textbox(label="Specializzazione", placeholder="Es: Frisona, alta produzione, biologico...")
                
                note_azienda = gr.Textbox(label="Note", lines=2, placeholder="Note commerciali, rapporti, particolarità...")
                
                btn_salva_azienda = gr.Button("💾 Salva Azienda", variant="primary")
                output_azienda = gr.Textbox(label="Stato", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### Aziende Registrate")
                
                with gr.Row():
                    ricerca_aziende = gr.Textbox(
                        placeholder="🔍 Cerca per nome, tipo, specializzazione...",
                        show_label=False
                    )
                    btn_carica_aziende = gr.Button("🔄 Aggiorna")
                
                tabella_aziende = gr.Dataframe(
                    headers=["Nome", "Tipo", "Telefono", "Email", "Indirizzo", "Capienza", "Specializzazione"],
                    interactive=False
                )

    with gr.Tab("🔍 Ricerca"):
        gr.Markdown("## Motore di Ricerca Avanzato")
        ricerca_avanzata = gr.Textbox(
            label="Cerca in tutto il database",
            placeholder="Inserisci ID, nome bovino, azienda, tipo trattamento..."
        )
        btn_ricerca_avanzata = gr.Button("🔍 Cerca", variant="primary")
        risultati_ricerca = gr.Dataframe(
            label="Risultati Ricerca",
            headers=["ID", "Nome", "Azienda", "Razza", "Età", "Stadio Lattazione"],
            interactive=False
        )

    # EVENT HANDLERS
    # Bovini
    btn_salva_bovino.click(
        fn=aggiungi_bovino,
        inputs=[bovino_id, nome_bovino, azienda, razza, eta, stadio_lattazione, note_bovino],
        outputs=output_msg
    ).then(
        fn=carica_bovini,
        outputs=tabella_bovini
    ).then(
        fn=carica_lista_bovini,
        outputs=bovino_selezionato
    )
    
    btn_carica_bovini.click(
        fn=carica_bovini,
        outputs=tabella_bovini
    )
    
    barra_ricerca.change(
        fn=cerca_bovini,
        inputs=barra_ricerca,
        outputs=tabella_bovini
    )
    
    # Trattamenti
    btn_salva_trattamento.click(
        fn=aggiungi_trattamento,
        inputs=[bovino_selezionato, tipo_trattamento, condizione_zoccolo, lesioni_riscontrate, materiali, durata, costo, note_trattamento, prossimo_controllo],
        outputs=[output_trattamento, bovino_selezionato]
    ).then(
        fn=carica_trattamenti,
        outputs=storico_trattamenti
    )
    
    btn_carica_trattamenti.click(
        fn=carica_trattamenti,
        outputs=storico_trattamenti
    )
    
    # Aziende
    btn_salva_azienda.click(
        fn=aggiungi_azienda,
        inputs=[nome_azienda, tipo_azienda, telefono, email, indirizzo, capienza, specializzazione, note_azienda],
        outputs=output_azienda
    ).then(
        fn=carica_aziende,
        outputs=tabella_aziende
    ).then(
        fn=carica_lista_aziende,
        outputs=azienda
    )
    
    btn_carica_aziende.click(
        fn=carica_aziende,
        outputs=tabella_aziende
    )
    
    ricerca_aziende.change(
        fn=cerca_aziende,
        inputs=ricerca_aziende,
        outputs=tabella_aziende
    )
    
    # Ricerca
    btn_ricerca_avanzata.click(
        fn=cerca_bovini,
        inputs=ricerca_avanzata,
        outputs=risultati_ricerca
    )

    # Carica tutto all'avvio
    def aggiorna_dashboard():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM bovini")
        totale_bovini = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM trattamenti WHERE date(data) >= date('now', '-30 days')")
        trattamenti_mese = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM aziende")
        totale_aziende = c.fetchone()[0]
        
        # Statistiche condizioni zoccoli
        c.execute('''
            SELECT 
                COUNT(*) as totale,
                SUM(CASE WHEN condizione_zoccolo <= 2 THEN 1 ELSE 0 END) as critici,
                SUM(CASE WHEN condizione_zoccolo = 3 THEN 1 ELSE 0 END) as medi,
                SUM(CASE WHEN condizione_zoccolo >= 4 THEN 1 ELSE 0 END) as buoni
            FROM trattamenti 
            WHERE id IN (
                SELECT MAX(id) FROM trattamenti GROUP BY bovino_id
            )
        ''')
        stats = c.fetchone()
        conn.close()
        
        situazione_html = f"""
        <div style='background: #f8f9fa; padding: 15px; border-radius: 8px;'>
            <div><strong>📊 Situazione Zoccoli:</strong></div>
            <div>• 🟢 Buoni: {stats[3]}</div>
            <div>• 🟡 Medi: {stats[2]}</div>
            <div>• 🔴 Critici: {stats[1]}</div>
        </div>
        """
        
        return (
            f"🐄 {totale_bovini} bovini", 
            f"🔧 {trattamenti_mese} trattamenti",
            f"🏢 {totale_aziende} aziende",
            situazione_html
        )
    
    app.load(
        fn=aggiorna_dashboard,
        outputs=[totale_bovini, trattamenti_mese, totale_aziende, situazione_html]
    ).then(
        fn=carica_bovini,
        outputs=tabella_bovini
    ).then(
        fn=carica_trattamenti,
        outputs=storico_trattamenti
    ).then(
        fn=carica_lista_bovini,
        outputs=bovino_selezionato
    ).then(
        fn=carica_aziende,
        outputs=tabella_aziende
    ).then(
        fn=carica_lista_aziende,
        outputs=azienda
    )

app.launch(server_name="0.0.0.0", server_port=7860, share=False)
