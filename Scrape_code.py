from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime, timedelta
import re

# Set Chrome options
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Uncomment for headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Automatically install the correct ChromeDriver version
chromedriver_autoinstaller.install()

# Initialize WebDriver
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # Set an explicit wait of 10 seconds


# Function to generate date ranges
def generate_dates(start_date, end_date, interval=7):
    date_ranges = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    final_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date + timedelta(days=interval) <= final_date:
        departure = current_date.strftime("%Y-%m-%d")
        return_date = (current_date + timedelta(days=interval)).strftime("%Y-%m-%d")
        date_ranges.append((departure, return_date))
        current_date += timedelta(days=interval)

    return date_ranges


# Function to get flight details
def get_flight_data():
    flights = []
    try:
        # Wait for all required elements to be present
        price_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "f8F1-price-text")))
        airline_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "VY2U")]//div[contains(@class, "c_cgF-mod-variant-default")]')))
        duration_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "xdW8")]//div[contains(@class, "vmXl-mod-variant-default")]')))
        transit_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "JWEO-stops-text")))
        competitor_price_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'QpsO')))

        for i in range(len(price_elements)):
            try:
                price = price_elements[i].text.strip() if i < len(price_elements) else "N/A"
                airline = airline_elements[i].text.strip() if i < len(airline_elements) else "N/A"

                # Extract and classify duration and transit properly
                raw_text = duration_elements[i].text.strip() if i < len(duration_elements) else "N/A"
                if "h" in raw_text or "m" in raw_text:  # Check if it contains time
                    duration = raw_text
                    transit = transit_elements[i].text.strip() if i < len(transit_elements) else "N/A"
                else:
                    duration = "N/A"  # If it doesn't contain time, assume duration is missing
                    transit = raw_text  # Assign transit value here

                # Extract competitor price (only the numeric value)
                competitor_price_raw = competitor_price_elements[i].text.strip() if i < len(
                    competitor_price_elements) else "N/A"
                competitor_price_match = re.search(r'\$\d+', competitor_price_raw)  # Extracts price like "$750"
                competitor_price = competitor_price_match.group() if competitor_price_match else "N/A"

                flights.append({
                    "Airline": airline,
                    "Duration": duration,
                    "Transit": transit,
                    "Price": price,
                    "Competitor Price": competitor_price
                })
            except Exception as e:
                print(f"Error extracting flight data: {e}")
    except Exception as e:
        print(f"Error waiting for flight results: {e}")

    return flights


# Define search parameters
origin = "RUH"
destination = "BEY"
start_date = "2025-03-31"
end_date = "2025-12-31"
interval = 7

# Generate date ranges
date_ranges = generate_dates(start_date, end_date, interval)

# Store all results
all_flight_data = []

# Loop through each date range
for departure, return_date in date_ranges:
    print(f"Scraping flights for {departure} to {return_date}")

    url = f"https://www.momondo.com/flight-search/{origin}-{destination}/{departure}/{return_date}?ucs=1gtrxv9&sort=bestflight_a"
    driver.get(url)

    # Wait for the page to load
    time.sleep(7)

    # Get flight data
    flight_data = get_flight_data()

    # Try to click the "Show More" button if it exists (limited to 3 times)
    max_clicks = 3
    click_count = 0

    while click_count < max_clicks:
        try:
            show_more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "show-more-button")))
            ActionChains(driver).move_to_element(show_more_button).click().perform()
            time.sleep(5)
            flight_data.extend(get_flight_data())
            click_count += 1
            print(f"Clicked 'Show More' {click_count} time(s)")
        except Exception:
            break

    # Add data to results
    for flight in flight_data:
        flight["Departure"] = departure
        flight["Return"] = return_date
        all_flight_data.append(flight)

# Close the browser
driver.quit()

# Save to CSV
df = pd.DataFrame(all_flight_data,
                  columns=["Departure", "Return", "Airline", "Duration", "Transit", "Price", "Competitor Price"])

if df.empty:
    print("No flight data scraped. CSV file will not be saved.")
else:
    df.to_csv(r"C:\Users\User\Desktop\Riyadh_scrape.csv", index=False, encoding="utf-8-sig")
    print("Scraping completed! Prices saved in 'Riyadh_scrape.csv'.")
print(df.head())
