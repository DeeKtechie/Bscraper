from playwright.sync_api import sync_playwright
import pandas as pd


def main():
    
    with sync_playwright() as p:
        
        # IMPORTANT: Change dates to future dates, otherwise it won't work
        checkin_date = '2023-03-23'
        checkout_date = '2023-03-24'
        
        page_url = f'https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4As7W7rgGwAIB0gIkMGI3YWVkODAtNjhjYy00ZTc2LWE4MGEtZTg0MjBjOTE4ZTcw2AIF4AIB&sid=0326c178dad3beb7705af941d2be3173&aid=304142&checkin=2025-01-21&checkout=2025-01-22&dest_id=224&dest_type=country&latitude=38.97079849243164&longitude=-98.26319885253906&sb_travel_purpose=leisure&nflt=ht_id%3D204%3Bprice%3DGBP-min-max-1&order=popularity&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&age=&req_age=&slp_r_match_to=0&shw_aparth=0'

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)
                    
        hotels = page.locator('//div[@data-testid="property-card"]').all()
        print(f'There are: {len(hotels)} hotels.')

        hotels_list = []
        for hotel in hotels:
            hotel_dict = {}
            hotel_dict['hotel'] = hotel.locator('//div[@data-testid="title"]').inner_text()
            hotel_dict['price'] = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text()
            hotel_dict['address'] = hotel.locator('//span[@data-testid="address"]').inner_text()
            hotel_dict['score'] = hotel.locator('//div[@data-testid="review-score"]/div[1]').inner_text()
            hotel_dict['avg review'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text()
            hotel_dict['reviews count'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text().split()[0]

            hotels_list.append(hotel_dict)
        
        df = pd.DataFrame(hotels_list)
        df.to_excel('hotels_list.xlsx', index=False) 
        df.to_csv('hotels_list.csv', index=False) 
        
        browser.close()
            
if __name__ == '__main__':
    main()
