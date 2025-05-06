import requests
import datetime
from mailersend import emails
import os

MAILERSEND_TOKEN = os.getenv("MAILERSEND_TOKEN")
RECIPIENT_EMAIL = "gwardzikmarcin@gmail.com"

def search_flights():
    origin_destinations = [("WRO", "BCN"), ("POZ", "VLC")]
    start_date = datetime.date(2025, 8, 1)
    end_date = start_date + datetime.timedelta(days=180)
    max_price = 400

    found_flights = []
    for origin, dest in origin_destinations:
        date = start_date
        while date <= end_date:
            for stay_length in range(3, 6):
                return_date = date + datetime.timedelta(days=stay_length)
                url = f"https://www.ryanair.com/api/booking/v4/en-gb/Availability?DepartureAirportCode={origin}&ArrivalAirportCode={dest}&DepartureDate={date}&ReturnDate={return_date}&FlexDaysBeforeOut=3&FlexDaysOut=3&FlexDaysBeforeIn=3&FlexDaysIn=3&RoundTrip=true&ToUs=AGREED"
                try:
                    response = requests.get(url)
                    data = response.json()
                    if "trips" in data:
                        for trip in data["trips"]:
                            for date_trip in trip["dates"]:
                                for flight in date_trip["flights"]:
                                    price = flight["regularFare"]["fares"][0]["amount"] if "regularFare" in flight else 9999
                                    if price <= max_price:
                                        found_flights.append(f"{origin} → {dest} za {price} zł, {date}–{return_date}")
                except Exception as e:
                    print(f"Error for {origin}–{dest} on {date}: {e}")
            date += datetime.timedelta(days=7)
    return found_flights

def send_email(content):
    if not content:
        return
    mailer = emails.NewEmail(token=MAILERSEND_TOKEN)
    mail_body = "\n".join(content)
    mailer.set_mail_from("FlightBot <no-reply@mailersend.com>")
    mailer.set_subject("Tanie loty znalezione!")
    mailer.set_text(mail_body)
    mailer.set_recipients([{"email": RECIPIENT_EMAIL}])
    mailer.send()

if __name__ == "__main__":
    flights = search_flights()
    send_email(flights)