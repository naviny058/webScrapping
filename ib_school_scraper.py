from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

# URL of the IB school search page
base_url = "https://www.ibo.org/programmes/find-an-ib-school/"

# Path to your ChromeDriver
driver_path = 'path/to/chromedriver'  # Make sure to update this to your actual path

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(executable_path=driver_path)
driver.get(base_url)

# Function to extract school details from each school's page
def get_school_details(school_url):
    try:
        driver.get(school_url)
        school_name = driver.find_element(By.TAG_NAME, "h1").text
        address = driver.find_element(By.CLASS_NAME, "address").text
        try:
            contact = driver.find_element(By.CLASS_NAME, "contact").text
        except:
            contact = "N/A"
        programmes_offered = [elem.text for elem in driver.find_elements(By.CLASS_NAME, "programme")]

        return {
            "School Name": school_name,
            "Address": address,
            "Contact": contact,
            "Programmes Offered": ', '.join(programmes_offered)
        }
    except Exception as e:
        print(f"Error scraping {school_url}: {e}")
        return None

# Function to scrape school links from a specific region
def scrape_schools_for_region(region_value):
    schools_data = []

    # Select the region from the dropdown
    region_select = Select(driver.find_element(By.ID, 'SearchFields_Region'))
    region_select.select_by_value(region_value)

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_button.click()

    time.sleep(2)  # Wait for the page to load

    # Find all school links
    school_links = driver.find_elements(By.CSS_SELECTOR, "a.school-link")

    for link in school_links:
        school_url = link.get_attribute('href')
        school_details = get_school_details(school_url)
        if school_details:
            schools_data.append(school_details)

        # To avoid overwhelming the server, introduce a delay
        time.sleep(1)

    return schools_data

# Main function to scrape all regions and save data
def scrape_all_regions():
    # Get the dropdown options for regions
    region_select = Select(driver.find_element(By.ID, 'SearchFields_Region'))
    region_options = region_select.options

    all_schools_data = []

    for option in region_options:
        region_value = option.get_attribute('value')
        region_name = option.text.strip()

        if region_value:  # Skip invalid or empty values
            print(f"Scraping schools for region: {region_name}")
            region_schools_data = scrape_schools_for_region(region_value)
            all_schools_data.extend(region_schools_data)

    return all_schools_data

# Run the scraping process and save to an Excel file
def main():
    print("Scraping IB schools for all regions...")
    all_schools_data = scrape_all_regions()

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(all_schools_data)

    # Save the DataFrame to an Excel file
    df.to_excel("ib_schools_data_selenium.xlsx", index=False)

    print("Data scraping completed and saved to ib_schools_data_selenium.xlsx")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
