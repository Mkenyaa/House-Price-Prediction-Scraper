import csv
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Initialize the geocoder with a custom user agent
geolocator = Nominatim(user_agent="property_scraper")

# Define Nairobi's coordinates (latitude, longitude) and maximum distance (in km) for the area of interest
NAIROBI_COORDS = (-1.2921, 36.8219)
MAX_DISTANCE = 30  # km

def is_within_nairobi_area(location):
    """
    Check if a given location is within the defined Nairobi area.
    
    Args:
    location (str): The location to check.
    
    Returns:
    bool: True if the location is within the defined area, False otherwise.
    """
    try:
        # Geocode the location, adding "Kenya" for more accurate results
        location_info = geolocator.geocode(location + ", Kenya")
        if location_info:
            property_coords = (location_info.latitude, location_info.longitude)
            # Calculate the distance between the property and Nairobi's center
            distance = geodesic(NAIROBI_COORDS, property_coords).km
            return distance <= MAX_DISTANCE
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
    return False

def extract_price(details_url):
    """
    Extract the price from a property's detail page.
    
    Args:
    details_url (str): The URL of the property's detail page.
    
    Returns:
    str: The extracted price or 'None' if not found.
    """
    try:
        response = requests.get(details_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find('span', class_='block text-right text-xl font-semibold leading-7 md:text-xxl md:font-extrabold')
        return price_tag.text.strip() if price_tag else 'None'
    except Exception as e:
        print(f"Error fetching details from {details_url}: {e}")
        return 'None'

def get_property_type(url):
    """
    Determine the property type and purchase type based on the URL.
    
    Args:
    url (str): The URL of the property listing page.
    
    Returns:
    tuple: A tuple containing the property type and purchase type.
    """
    property_types = {
        'houses-for-sale': ('House', 'Sale'),
        'flats-apartments-for-sale': ('Apartment', 'Sale'),
        'houses-for-rent': ('House', 'Rent'),
        'flats-apartments-for-rent': ('Apartment', 'Rent'),
        'bedsitters-for-rent': ('Bedsitter', 'Rent')
    }
    for key, value in property_types.items():
        if key in url:
            return value
    return 'Unknown', 'Unknown'

def parse_location(location_text):
    """
    Parse the location text to separate the main location from other details.
    
    Args:
    location_text (str): The full location text from the property listing.
    
    Returns:
    tuple: A tuple containing the main location and other location details.
    """
    if ',' in location_text:
        location, other_details = location_text.split(',', 1)
        return location.strip(), other_details.strip()
    return location_text.strip(), ''

def fetch_properties(url):
    """
    Fetch and yield property data from a given URL.
    
    Args:
    url (str): The URL of the property listing page.
    
    Yields:
    list: A list containing details of each property.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        properties = soup.find_all('div', class_='relative w-full overflow-hidden rounded-2xl bg-white')
        
        property_type, purchase_type = get_property_type(url)
        
        for prop in properties:
            # Extract various details from the property listing
            location = prop.find('p', class_='ml-1 truncate text-sm font-normal capitalize text-grey-650')
            size = prop.find('span', class_='whitespace-nowrap', attrs={'data-cy': 'card-area'})
            bedrooms = prop.find('span', class_='whitespace-nowrap', attrs={'data-cy': 'card-beds'})
            bathrooms = prop.find('span', class_='whitespace-nowrap font-normal', attrs={'data-cy': 'card-bathrooms'})
            price_tag = prop.find('a', class_='no-underline')
            
            location_text, other_location_details = parse_location(location.text.strip()) if location else ('None', 'None')
            
            # Skip properties not within the Nairobi area
            if not is_within_nairobi_area(location_text):
                continue
            
            # Extract and format other property details
            size_text = size.text.strip() if size else 'None'
            bedrooms_text = bedrooms.text.strip() if bedrooms else 'None'
            bathrooms_text = bathrooms.text.strip() if bathrooms else 'None'
            details_url = 'https://www.buyrentkenya.com' + price_tag['href'] if price_tag else 'None'
            
            detailed_price = extract_price(details_url)
            
            yield [location_text, other_location_details, size_text, bedrooms_text, bathrooms_text, detailed_price, property_type, purchase_type]
    except Exception as e:
        print(f"Error fetching properties from {url}: {e}")

def has_next_page(soup):
    """
    Check if there is a next page of listings.
    
    Args:
    soup (BeautifulSoup): The parsed HTML of the current page.
    
    Returns:
    bool: True if there is a next page, False otherwise.
    """
    next_button_div = soup.find('div', class_='mt-4 flex w-full flex-row items-center justify-center space-x-1 md:space-x-3')
    return next_button_div and soup.find('svg', class_='fill-current transform -rotate-90 inline-block text-secondary w-3')

def scrape_all_properties(base_urls):
    """
    Scrape properties from all given base URLs and save to a CSV file.
    
    Args:
    base_urls (list): A list of base URLs to scrape from.
    """
    with open('nairobi_property_listings.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Location', 'Other Location Details', 'Size', 'Bedrooms', 'Bathrooms', 'Price', 'Property Type', 'Purchase Type'])
        
        for base_url in base_urls:
            page = 1
            while True:
                url = f"{base_url}?page={page}" if page > 1 else base_url
                print(f"Fetching data from {url}...")
                
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                properties_found = False
                for property_data in fetch_properties(url):
                    writer.writerow(property_data)
                    properties_found = True
                
                # Break the loop if no properties are found or there's no next page
                if not properties_found or not has_next_page(soup):
                    break
                
                page += 1

if __name__ == "__main__":
    # Define the base URLs for different types of property listings
    base_urls = [
        'https://www.buyrentkenya.com/houses-for-sale',
        'https://www.buyrentkenya.com/flats-apartments-for-sale',
        'https://www.buyrentkenya.com/houses-for-rent',
        'https://www.buyrentkenya.com/flats-apartments-for-rent',
        'https://www.buyrentkenya.com/bedsitters-for-rent'
    ]
    
    # Start the scraping process
    scrape_all_properties(base_urls)
    print('File saved successfully')