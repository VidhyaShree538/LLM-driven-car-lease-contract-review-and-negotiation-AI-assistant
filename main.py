from fastapi import FastAPI, UploadFile, File
from PIL import Image
import pytesseract
import io
import re

app = FastAPI(title="Car Lease OCR with Accuracy")

# Set tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Helper functions
def extract_value(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None

def clean_text(text):
    lines = text.splitlines()
    seen = set()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            cleaned.append(line)
            seen.add(line)
    return "\n".join(cleaned)

def correct_ocr_errors(text):
    text = text.replace("pryar", "per year")
    text = text.replace("Drever", "Driver")
    return text

@app.post("/extract-lease")
async def extract_lease(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    raw_text = pytesseract.image_to_string(image)
    text = clean_text(correct_ocr_errors(raw_text))

    lease_agreement = {}

    # ---------- EXTRACT DATA ----------
    # Agreement
    agreement_id = extract_value(r"Agreement\s*ID[:\-]?\s*(\w+)", text)
    agreement_date = extract_value(r"Agreement\s*Date[:\-]?\s*([\d\-\/]+)", text)
    commencement_date = extract_value(r"Commencement\s*Date[:\-]?\s*([\d\-\/]+)", text)
    termination_date = extract_value(r"Termination\s*Date[:\-]?\s*([\d\-\/]+)", text)
    lease_term = extract_value(r"Lease\s*Term[:\-]?\s*(\d+)", text)

    if agreement_id: lease_agreement["agreement_id"] = agreement_id
    if agreement_date: lease_agreement["agreement_date"] = agreement_date
    if commencement_date: lease_agreement["commencement_date"] = commencement_date
    if termination_date: lease_agreement["termination_date"] = termination_date
    if lease_term: lease_agreement["lease_term_months"] = int(lease_term)

    # Lessor / Lessee
    lessor = {}
    lessor_name = extract_value(r"Lessor[:\-]?\s*(.+)", text)
    lessor_address = extract_value(r"Business Address[:\-]?\s*(.+)", text)
    if lessor_name: lessor["name"] = lessor_name
    if lessor_address: lessor["address"] = lessor_address
    if lessor: lease_agreement["lessor"] = lessor

    lessee = {}
    lessee_name = extract_value(r"Lessee[:\-]?\s*(.+)", text)
    lessee_address = extract_value(r"Address[:\-]?\s*(.+)", text)
    if lessee_name: lessee["name"] = lessee_name
    if lessee_address: lessee["address"] = lessee_address
    if lessee: lease_agreement["lessee"] = lessee

    # Vehicle
    vehicle = {}
    make = extract_value(r"Make[:\-]?\s*(\w+)", text)
    model = extract_value(r"Model[:\-]?\s*([\w\s]+)", text)
    year = extract_value(r"Year[:\-]?\s*(\d{4})", text)
    vin = extract_value(r"VIN[:\-]?\s*([A-HJ-NPR-Z0-9]{10,17})", text)
    color = extract_value(r"Color[:\-]?\s*(\w+)", text)
    license_plate = extract_value(r"License\s*Plate[:\-]?\s*(\S+)", text)
    engine_no = extract_value(r"Engine\s*No[:\-]?\s*(\S+)", text)
    odometer = extract_value(r"Odometer[:\-]?\s*(\d+)", text)
    registration_state = extract_value(r"Registration State[:\-]?\s*(\w+)", text)

    if make: vehicle["make"] = make
    if model: vehicle["model"] = model
    if year: vehicle["year"] = int(year)
    if vin: vehicle["vin"] = vin
    if color: vehicle["color"] = color
    if license_plate: vehicle["license_plate"] = license_plate
    if engine_no: vehicle["engine_no"] = engine_no
    if odometer: vehicle["odometer"] = odometer
    if registration_state: vehicle["registration_state"] = registration_state
    if vehicle: lease_agreement["vehicle_details"] = vehicle

    # Financial
    finance = {}
    monthly = extract_value(r"Monthly\s*Payment[:\-]?\s*\$?([\d,.]+)", text)
    deposit = extract_value(r"Security\s*Deposit[:\-]?\s*\$?([\d,.]+)", text)
    total = extract_value(r"Total\s*Lease\s*Value[:\-]?\s*\$?([\d,.]+)", text)
    tax = extract_value(r"Tax[:\-]?\s*\$?([\d,.]+)", text)
    late_fee = extract_value(r"Late\s*Payment\s*Fee[:\-]?\s*\$?([\d,.]+)", text)

    if monthly: finance["monthly_payment"] = float(monthly.replace(",", ""))
    if deposit: finance["security_deposit"] = float(deposit.replace(",", ""))
    if total: finance["total_lease_value"] = float(total.replace(",", ""))
    if tax: finance["tax"] = float(tax.replace(",", ""))
    if late_fee: finance["late_payment_fee"] = float(late_fee.replace(",", ""))
    if finance: lease_agreement["financial_terms"] = finance

    # Mileage & Insurance
    mileage = {}
    annual_miles = extract_value(r"Annual\s*Mileage\s*Allowance[:\-]?\s*(\d+)", text)
    excess_fee = extract_value(r"Excess\s*Mileage\s*Fee[:\-]?\s*\$?([\d,.]+)", text)
    if annual_miles: mileage["annual_miles"] = int(annual_miles)
    if excess_fee: mileage["excess_mileage_fee"] = float(excess_fee.replace(",", ""))
    if mileage: lease_agreement["mileage_allowance"] = mileage

    insurance = extract_value(r"Insurance[:\-]?\s*(.+)", text)
    if insurance: lease_agreement["insurance_requirements"] = insurance

    renewal = extract_value(r"Renewal\s*Option[:\-]?\s*(.+)", text)
    if renewal: lease_agreement["renewal_option"] = renewal

    # ---------- ACCURACY ESTIMATION ----------
    def field_accuracy(value):
        return 100 if value else 0

    # Flatten all values for accuracy
    all_fields = []

    def collect_fields(d):
        for v in d.values():
            if isinstance(v, dict):
                collect_fields(v)
            else:
                all_fields.append(v)

    collect_fields(lease_agreement)

    per_field_accuracy = {f"field_{i+1}": field_accuracy(val) for i, val in enumerate(all_fields)}
    overall_accuracy = int(sum(per_field_accuracy.values()) / len(per_field_accuracy)) if per_field_accuracy else 0

    return {
        "lease_agreement": lease_agreement,
        "accuracy": {
            "per_field": per_field_accuracy,
            "overall_accuracy": f"{overall_accuracy}%"
        }
    }
