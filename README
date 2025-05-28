# 🧪 Simulazione di Utenti per Segment via API

Questo script Python genera **100 utenti fittizi** e simula la loro attività su una piattaforma, inviando eventi a Segment tramite API HTTP. Lo scopo è testare flussi di analytics con dati realistici, randomizzati e diversificati.

---

## 📌 Funzionalità principali

- Creazione di **100 utenti**, di cui:
  - **20 demo** (gratuiti)
  - **80 paid** (clienti paganti)
- Ogni utente ha:
  - Dati aziendali generati in modo casuale (nome azienda, email, P.IVA)
  - Un ID utente univoco (`user_<8cifre>`)
  - Eventi di interazione con la piattaforma (fatture, pagamenti, CTA)
- Ogni azione è **marcata temporalmente** con un timestamp casuale entro gli ultimi **60 giorni**
- Calcolo e assegnazione di un punteggio **RFM** finale

---

## 🔄 Come avviene la randomizzazione

### 1. **Identità e dati aziendali**
- I dati di ogni utente vengono generati con la libreria `faker` in italiano (`it_IT`)
- Il campo `vat_number` è simulato con prefisso `IT` e 11 cifre casuali
- L’email è aziendale, univoca per ciascun utente
- Il campo `bank_id` è composto da una banca casuale + codice numerico

### 2. **Data di creazione**
- Ogni utente ha una data di creazione casuale negli ultimi **60 giorni** (`rand_past_datetime(60)`)

### 3. **Eventi**
Per ogni utente viene simulato un numero casuale di fatture (1-4). Ogni fattura genera una sequenza di eventi:

| Evento                          | Probabilità    | Note                                                            |
|--------------------------------|----------------|-----------------------------------------------------------------|
| `fe_invoicing_started`         | 100%           | Timestamp casuale per ogni fattura                              |
| `fe_invoice_sent`              | 100%           | 1-6 ore dopo il precedente                                      |
| `fe_invoice_xml_imported`      | 60%            | 5 minuti dopo `invoice_sent`                                    |
| `fe_invoice_courtesy_copy_sent`| 70%            | 10 minuti dopo `invoice_sent`                                   |
| `payment_emitted`              | 80% (solo paid)| Pagamento da 50€ a 1500€, registrato 1-7 giorni dopo invio      |
| `fe_invoice_paid`              | 80% (solo paid)| Conseguente a `payment_emitted`                                 |
| `scadenzario_accessed`         | 60%            | Entro 3 giorni da invio fattura                                 |
| `payment_cta_clicked`          | 40% (solo paid)| Solo se `scadenzario_accessed` avviene                          |

### 4. **Distribuzione account**
- I **primi 20 utenti** sono classificati come `demo`
- I successivi **80 utenti** sono `paid`

### 5. **Punteggio RFM**
Ogni utente riceve un punteggio finale da 0 a 100, calcolato su:

- **Recency**: giorni dall’ultimo evento
- **Frequency**: numero di fatture inviate
- **Monetary**: somma dei pagamenti simulati

---

## ⚙️ Requisiti

- Python 3.8+
- Variabile d’ambiente `SEGMENT_WRITE_KEY`
- Pacchetti: `requests`, `faker`

Installa i pacchetti mancanti con:

```bash
pip install requests faker
