import os
import random
import uuid
import requests
import datetime as dt
from faker import Faker

fake = Faker("it_IT")
SEGMENT_KEY = os.getenv("SEGMENT_WRITE_KEY")
API = "https://api.segment.io/v1/"

if not SEGMENT_KEY:
    raise SystemExit("❌  Imposta la variabile d'ambiente SEGMENT_WRITE_KEY")

def send(kind: str, payload: dict) -> None:
    """Invia chiamata identify/track a Segment."""
    r = requests.post(API + kind, json=payload, auth=(SEGMENT_KEY, ""))
    r.raise_for_status()


def gen_vat() -> str:
    return "IT" + "".join(str(random.randint(0, 9)) for _ in range(11))


def rand_past_datetime(max_days: int = 60) -> dt.datetime:
    """Ritorna un datetime UTC casuale entro i *max_days* passati."""
    now = dt.datetime.utcnow()
    return now - dt.timedelta(seconds=random.randint(0, max_days * 86_400))


def compute_rfm(recency_days: int, invoices: int, revenue: float) -> int:
    """Calcola rfm_score (0-100) con pesi R 50 %, F 35 %, M 15 %."""
    r_score = max(0, 100 - recency_days * 3)          # 0-100 – ogni giorno vale -3
    f_score = min(100, invoices * 25)                  # 4+ fatture = 100
    m_score = min(100, int(revenue / 150) * 10)        # 1500 € ~ 100
    return int(round(r_score * 0.50 + f_score * 0.35 + m_score * 0.15))

for i in range(100):
    uid = f"user_{uuid.uuid4().hex[:8]}"
    is_demo = i < 20  # primi 20 demo, altri 20 paid

    invoices_count = random.randint(1, 4)
    total_revenue = 0.0

    # Timestamp di creazione utente (fino a 60 giorni fa)
    created_ts = rand_past_datetime(60)

    traits = {
        "account_type": "demo" if is_demo else "paid",
        "is_demo": is_demo,
        "company_name": fake.company(),
        "vat_number": gen_vat(),
        "bank_id": f"{random.choice(['INTESA','BPM','UNICREDIT'])}-{random.randint(100000, 999999)}",
        "email": fake.unique.company_email(),
        "phone": fake.phone_number().replace(" ", ""),
    }

    send("identify", {"userId": uid, "traits": traits, "timestamp": created_ts.isoformat()})

    # Eventi
    for _ in range(invoices_count):
        base_ts = rand_past_datetime(60)  # ogni fattura parte da un suo momento storico

        # Step wizard
        send("track", {"userId": uid, "event": "fe_invoicing_started", "timestamp": base_ts.isoformat()})

        # Fattura inviata
        sent_ts = base_ts + dt.timedelta(hours=random.randint(1, 6))
        send("track", {"userId": uid, "event": "fe_invoice_sent", "timestamp": sent_ts.isoformat()})

        # Import XML (60 %)
        if random.random() < 0.6:
            send(
                "track",
                {
                    "userId": uid,
                    "event": "fe_invoice_xml_imported",
                    "timestamp": (sent_ts + dt.timedelta(minutes=5)).isoformat(),
                },
            )

        # Copia cortesia (70 %)
        if random.random() < 0.7:
            send(
                "track",
                {
                    "userId": uid,
                    "event": "fe_invoice_courtesy_copy_sent",
                    "timestamp": (sent_ts + dt.timedelta(minutes=10)).isoformat(),
                },
            )

        # Pagamento (solo paid, 80 %)
        if not is_demo and random.random() < 0.8:
            amount = round(random.uniform(50, 1500), 2)
            total_revenue += amount
            pay_ts = sent_ts + dt.timedelta(days=random.randint(1, 7))
            send(
                "track",
                {
                    "userId": uid,
                    "event": "payment_emitted",
                    "properties": {"amount_eur": amount},
                    "timestamp": pay_ts.isoformat(),
                },
            )
            send("track", {"userId": uid, "event": "fe_invoice_paid", "timestamp": pay_ts.isoformat()})

        # Scadenzario / CTA (60 %)
        if random.random() < 0.6:
            scad_ts = sent_ts + dt.timedelta(days=random.randint(0, 3))
            send("track", {"userId": uid, "event": "scadenzario_accessed", "timestamp": scad_ts.isoformat()})
            if not is_demo and random.random() < 0.4:
                send(
                    "track",
                    {
                        "userId": uid,
                        "event": "payment_cta_clicked",
                        "timestamp": (scad_ts + dt.timedelta(minutes=2)).isoformat(),
                    },
                )

    # Aggiorna RFM finale con recency calcolata sul tempo dalla creazione utente ad ora
    recency_days = (dt.datetime.utcnow() - created_ts).days
    final_rfm = compute_rfm(recency_days, invoices_count, total_revenue)
    send("identify", {"userId": uid, "traits": {"rfm_score": final_rfm}})

print("✅ 40 utenti generati (20 demo / 20 paid) – timestamp randomizzati su 60 giorni")
