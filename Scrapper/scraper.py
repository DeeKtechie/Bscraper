from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time


def main():
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()
        page_url = f'https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaFCIAQGYAQm4ARfIAQzYAQHoAQGIAgGoAgO4As7W7rgGwAIB0gIkMGI3YWVkODAtNjhjYy00ZTc2LWE4MGEtZTg0MjBjOTE4ZTcw2AIF4AIB&sid=0326c178dad3beb7705af941d2be3173&aid=304142&ss=United+States&ssne=United+States&ssne_untouched=United+States&efdco=1&lang=en-gb&src=searchresults&dest_id=224&dest_type=country&checkin=2025-01-21&checkout=2025-01-22&group_adults=2&no_rooms=1&group_children=0&nflt=price%3DGBP-min-max-1%3Bht_id%3D204'
        page.goto(page_url, timeout=120000, wait_until="networkidle")

        property_count_text = page.locator('h1').inner_text() # count how many properties from the search result
        total_properties = int(re.search(r'(\d[\d,]*) properties found', property_count_text).group(1).replace(',', ''))
        print(f'Total properties to scrape: {total_properties}')

        all_data = []

        page_data = [] #temporary store data

        while len(page_data) < total_properties:
            # Ensure property cards are loaded
            page.wait_for_selector('div[data-testid="property-card"]', timeout=60000)
            items = page.locator('div[data-testid="property-card"]').all()

            page_data = [] # reset page data to avoid duplicate

            # Extract details from each property card on the current page
            for item in items:
                try:
                    data = {
                        "name": item.locator('div[data-testid="title"]').inner_text(),
                        "price": item.locator('span[data-testid="price-and-discounted-price"]').inner_text(),
                        "address": item.locator('span[data-testid="address"]').inner_text(),
                        "score": item.locator('//div[@data-testid="review-score"]/div[1]').inner_text(),
                        "avg review": item.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text(),
                        "reviews count": item.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text().split()[0]
                    }
                    page_data.append(data)
                except Exception as e:
                    print(f"Error extracting data from a property card: {e}")
                    continue

            print(f'Scraped {len(page_data)} properties so far...')

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)") # scroll to the bottom to look for  the button

            try:
                next_button = page.locator("button:has-text('Load more results')")
                next_button.scroll_into_view_if_needed(timeout=10000)
                next_button.click(force=True)
                time.sleep(2)
            except Exception as e:
                print(f"Error clicking 'Load more results': {e}")
                break
        all_data.extend(page_data)
        # Save the final data to an Excel and CSV file
        df = pd.DataFrame(all_data)
        df.to_excel('hotels_list.xlsx', index=False)
        df.to_csv('hotels_list.csv', index=False)

        print(f'Scraped a total of {len(all_data)} properties.')
        browser.close()


if __name__ == '__main__':
    main()
