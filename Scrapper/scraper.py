from playwright.sync_api import sync_playwright
import pandas as pd

def main():
    with sync_playwright() as p:
        page_url = f'https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4As7W7rgGwAIB0gIkMGI3YWVkODAtNjhjYy00ZTc2LWE4MGEtZTg0MjBjOTE4ZTcw2AIF4AIB&sid=0326c178dad3beb7705af941d2be3173&aid=304142&ss=United+States&ssne=United+States&ssne_untouched=United+States&efdco=1&lang=en-gb&src=searchresults&dest_id=224&dest_type=country&checkin=2025-01-21&checkout=2025-01-22&group_adults=2&no_rooms=1&group_children=0&nflt=price%3DGBP-min-max-1%3Bht_id%3D204'

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        hotels_list = []
        
        # Loop through pages
        while True:
            # Wait for the hotel cards to load on the page
            page.wait_for_selector('//div[@data-testid="property-card"]')
            hotels = page.locator('//div[@data-testid="property-card"]').all()

            print(f'Found {len(hotels)} hotels on this page.')

            # Extract data from each hotel card
            for hotel in hotels:
                hotel_dict = {}
                hotel_dict['hotel'] = hotel.locator('//div[@data-testid="title"]').inner_text()
                hotel_dict['price'] = hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text()
                hotel_dict['Address'] = hotel.locator('//span[@data-testid="address"]').inner_text()
                
                # Get state information from the address
                address = hotel_dict['Address']
                hotel_dict['state'] = address.split(',')[-2].strip() if ',' in address else 'Unknown'
                
                # Review score and count
                hotel_dict['score'] = hotel.locator('//div[@data-testid="review-score"]/div[1]').inner_text()
                hotel_dict['avg review'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text()
                hotel_dict['reviews count'] = hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text().split()[0]

                hotels_list.append(hotel_dict)

            # Check for "Next" button to navigate to the next page
            next_button = page.locator('button[aria-label="Next"]')
            if next_button.is_visible():
                next_button.click()
                page.wait_for_timeout(3000)  # Wait a moment for the next page to load
            else:
                break  # No more pages to load, exit the loop

        # Save the collected data to Excel and CSV files
        df = pd.DataFrame(hotels_list)
        df.to_excel('hotels_list.xlsx', index=False) 
        df.to_csv('hotels_list.csv', index=False) 
        browser.close()

if __name__ == '__main__':
    main()
