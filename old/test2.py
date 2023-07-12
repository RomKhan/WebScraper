import yadisk

# y = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
# y.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'
# if y.exists('test'):
#     y.remove('test')
# time.sleep(2)
# y.mkdir('test')
# y.upload_url('https://spb.cian.ru/sale/flat/286944730/', 'test/page.html')

# importing geopy library
# from geopy.geocoders import Nominatim
#
# t1 = time.time()
# # calling the Nominatim tool
# loc = Nominatim(user_agent="GetLoc")
#
# # entering the location name
# getLoc = loc.geocode("Санкт-Петербург, ул. Адмирала Коновалова, 2-4")
#
# # printing address
# print(getLoc.address)
#
# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)
# t2 = time.time()
# print(t2-t1)
import cloudscraper

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
# Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
print(scraper.get("https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&sale_price__lte=10000000&sort=published&sort_dir=desc&sale_price__gte=100000&offset=0").text)  # => "<!DOCTYPE html><html><head>..."
