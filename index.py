from time import sleep
import requests
from datetime import datetime
from twilio.rest import Client
import os
from dotenv import load_dotenv
from short_url import ShortUrl

class FlightPrice:
    def __init__(self, ogn: str, dst: str, doj: str, no_of_adults: int, desired_amount: int, phone_no: str):
        self.ogn = ogn
        self.dst = dst
        self.date = datetime.strptime(doj, "%d-%m-%Y")
        self.desired_amount = desired_amount
        self.no_of_adults = no_of_adults
        self.phone_no = phone_no

    def find_cheapest_flight(self) -> int:
        payload = {
            "query": {
                "market": "IN",
                "locale": "en-GB",
                "currency": "INR",
                "cabinClass": "CABIN_CLASS_ECONOMY",
                "queryLegs": [
                    {
                        "originPlaceId": {
                            "iata": self.ogn
                        },
                        "destinationPlaceId": {
                            "iata": self.dst
                        },

                        "date": {
                            "year": self.date.year,
                            "month": self.date.month,
                            "day": self.date.day
                        }
                    }
                ],
                "adults": self.no_of_adults,
            }
        }
        res = requests.post("https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create",
                            json=payload,
                            headers={"x-api-key": "prtl6749387986743898559646983194"}).json()
        itinerary_Id = res["content"]["sortingOptions"]["cheapest"][0]["itineraryId"]
        cheapest_flight = res["content"]["results"]["itineraries"][itinerary_Id]
        return cheapest_flight

    def notify_user(self, price: int, link: str):
        load_dotenv()
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        twilio_phone_no = os.getenv("TWILIO_PHONE_NO")
        shortened_link = ShortUrl(link)
        
        try:
            client.messages.create(
                body=f'\nYour flight price is down @Rs {price}.\n Check out: {shortened_link}',
                from_=twilio_phone_no,
                to=self.phone_no
            )
        except:
            print("Something wrong with the Twilio account")

    def check_price(self, interval: float):
        cheapest_flight = self.find_cheapest_flight()
        curr_price = int(cheapest_flight["pricingOptions"][0]["price"]["amount"][:4])

        if curr_price < self.desired_amount:
            booking_link = cheapest_flight["pricingOptions"][0]["items"][0]["deepLink"]
            self.notify_user(curr_price, booking_link)
            return
        else:
            sleep(interval)
            self.check_price(interval)


def main():
    fl = FlightPrice("DBR", "BLR", "24-09-2022", 1, 4500, "+916204477194")
    fl.check_price(300)

if __name__ == "__main__":
    main()
