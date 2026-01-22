from fastapi import FastAPI, UploadFile, File
from PIL import Image
import pytesseract
import io
import re

app = FastAPI(title="Lease Agreement OCR with Accuracy & Confidence")

# 👉 Update if your Tesseract path is different
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -------------------- Utilities --------------------

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def extract(pattern: str, text: str):
    match = re.search(pattern, text, re.IGNORECASE)
    return clean_text(match.group(1)) if match else None


# -------------------- Validators --------------------

def valid_text(v, min_len=3):
    return bool(v and len(v.strip()) >= min_len)

def valid_date(v):
    return bool(v and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v))

def valid_year(v):
    return isinstance(v, int) and 2000 <= v <= 2030

def valid_vin(v):
    return bool(v and len(v) >= 15)

def valid_money(v):
    return isinstance(v, (int, float)) and v > 0

def valid_miles(v):
    return isinstance(v, (int, float)) and v >= 10000

def valid_insurance(v):
    return bool(v and "insurance" in v.lower())


# -------------------- Confidence Logic --------------------

def score(is_valid: bool) -> int:
    return 90 if is_valid else 25


# -------------------- API --------------------

@app.post("/extract-lease")
async def extract_lease(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read()))
    raw_text = pytesseract.image_to_string(image)
    text = clean_text(raw_text)

    # -------- Extraction --------
    agreement_id = extract(r"Agreement ID\s*:\s*([A-Z0-9]+)", text)
    agreement_date = extract(r"Agreement Date\s*:\s*(\d{4}-\d{2}-\d{2})", text)
    commencement_date = extract(r"Commencement Date\s*:\s*(\d{4}-\d{2}-\d{2})", text)
    termination_date = extract(r"Termination Date\s*:\s*(\d{4}-\d{2}-\d{2})", text)

    lessor_name = extract(r"Lessor\s*:\s*([A-Za-z &]+)", text)
    lessee_name = extract(r"Lessee\s*:\s*([A-Za-z ]+)", text)

    make = extract(r"Make\s*:\s*([A-Za-z]+)", text)
    model = extract(r"Model\s*:\s*([A-Za-z0-9 ]+)", text)
    year_raw = extract(r"Year\s*:\s*(\d{4})", text)
    year = int(year_raw) if year_raw else None

    vin = extract(r"VIN\s*:\s*([A-Z0-9]+)", text)

    monthly_payment_raw = extract(r"Monthly Payment\s*:\s*\$?(\d+)", text)
    monthly_payment = float(monthly_payment_raw) if monthly_payment_raw else None

    annual_miles_raw = extract(r"Annual Mileage\s*:\s*([\d,]+)", text)
    annual_miles = int(annual_miles_raw.replace(",", "")) if annual_miles_raw else None

    insurance = extract(r"Insurance Requirements\s*(.{30,200})", text)

    # -------- Confidence Calculation --------
    confidence = {
        "agreement_id": score(valid_text(agreement_id)),
        "agreement_date": score(valid_date(agreement_date)),
        "commencement_date": score(valid_date(commencement_date)),
        "termination_date": score(valid_date(termination_date)),
        "lessor_name": score(valid_text(lessor_name)),
        "lessee_name": score(valid_text(lessee_name)),
        "vehicle_make": score(valid_text(make)),
        "vehicle_model": score(valid_text(model)),
        "vehicle_year": score(valid_year(year)),
        "vin": score(valid_vin(vin)),
        "monthly_payment": score(valid_money(monthly_payment)),
        "annual_miles": score(valid_miles(annual_miles)),
        "insurance_requirements": score(valid_insurance(insurance))
    }

    overall_confidence = min(
        sum(confidence.values()) // len(confidence),
        95
    )

    # -------------------- Accuracy Calculation --------------------
    valid_fields = [
        valid_text(agreement_id),
        valid_date(agreement_date),
        valid_date(commencement_date),
        valid_date(termination_date),
        valid_text(lessor_name),
        valid_text(lessee_name),
        valid_text(make),
        valid_text(model),
        valid_year(year),
        valid_vin(vin),
        valid_money(monthly_payment),
        valid_miles(annual_miles),
        valid_insurance(insurance)
    ]

    accuracy = round((sum(valid_fields) / len(valid_fields)) * 100, 2)

    # -------- Response --------
    return {
        "lease_agreement": {
            "agreement_id": agreement_id,
            "agreement_date": agreement_date,
            "commencement_date": commencement_date,
            "termination_date": termination_date,
            "lessor": {"name": lessor_name},
            "lessee": {"name": lessee_name},
            "vehicle_details": {
                "make": make,
                "model": model,
                "year": year,
                "vin": vin
            },
            "financial_terms": {
                "monthly_payment": monthly_payment,
                "annual_miles": annual_miles
            },
            "insurance_requirements": insurance
        },
        "metrics": {
            "accuracy": f"{accuracy}%",
            "confidence": {
                "per_field": confidence,
                "overall_confidence": f"{overall_confidence}%"
            }
        }
    }
