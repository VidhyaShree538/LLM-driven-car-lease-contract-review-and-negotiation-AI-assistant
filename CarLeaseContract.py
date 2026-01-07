import re
with open("CarLeaseContract.py", "r", encoding="utf-8") as f:
    text = f.read()


make = re.search(r"Make:\s*(.*)", text)
model = re.search(r"Model:\s*(.*)", text)
year = re.search(r"Year:\s*(.*)", text)
color = re.search(r"Color:\s*(.*)", text)
vin = re.search(r"VIN:\s*(.*)", text)
mileage = re.search(r"Mileage:\s*(.*)", text)

start_date = re.search(r"Start Date:\s*(.*)", text)
end_date = re.search(r"End Date:\s*(.*)", text)

mileage_limit = re.search(r"\[  \]\s*No mileage limit\s*\[  \]\s*(.*) miles", text)


daily_fee = re.search(r"Fees:\s*\$\s*(.*) per day", text)
deposit = re.search(r"Deposit:\s*\$\s*(.*)", text)
fuel = re.search(r"Fuel:\s*(.*)", text)
excess_mileage = re.search(r"Excess Mileage:\s*\$\s*(.*) per mile", text)


renter_name = re.search(r"ACCEPTED BY RENTER:.\nName\s(.*)", text)
owner_name = re.search(r"ACCEPTED BY OWNER:.\nName\s(.*)", text)

print("Vehicle Info ")
print("Make:", make.group(1) if make else "Not found")
print("Model:", model.group(1) if model else "Not found")
print("Year:", year.group(1) if year else "Not found")
print("Color:", color.group(1) if color else "Not found")
print("VIN:", vin.group(1) if vin else "Not found")
print("Mileage:", mileage.group(1) if mileage else "Not found")

print("\n Rental Period ")
print("Start Date:", start_date.group(1) if start_date else "Not found")
print("End Date:", end_date.group(1) if end_date else "Not found")
print("Mileage Limit:", mileage_limit.group(1) if mileage_limit else "No limit or Not found")

print("\n Rental Fees ")
print("Daily Fee:", daily_fee.group(1) if daily_fee else "Not found")
print("Deposit:", deposit.group(1) if deposit else "Not found")
print("Fuel Responsibility:", fuel.group(1) if fuel else "Not found")
print("Excess Mileage Fee:", excess_mileage.group(1) if excess_mileage else "Not found")

print("\n  Signatures ")
print("Renter Name:", renter_name.group(1) if renter_name else "Not found")
print("Owner Name:", owner_name.group(1) if owner_name else "Not found")