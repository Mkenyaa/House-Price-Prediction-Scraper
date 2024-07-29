# Property Scraper

This Python script scrapes property listings from BuyRentKenya.com, filters them based on their location within Nairobi, and saves the data to a CSV file.

## Requirements

- Python 3.x
- Requests library
- BeautifulSoup4 library
- Geopy library

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 geopy
```

## Functionality

The script performs the following tasks:

1. **Initialize Geocoder**:
   - Uses Geopy's Nominatim service to geocode locations.

2. **Define Nairobi Coordinates and Maximum Distance**:
   - Sets the coordinates for Nairobi and a maximum distance to filter properties.

3. **Functions**:
   - `is_within_nairobi_area(location)`: Checks if a given location is within the specified distance from Nairobi.
   - `extract_price(details_url)`: Extracts the price of a property from its details page.
   - `get_property_type(url)`: Determines the property type and purchase type based on the URL.
   - `parse_location(location_text)`: Parses location text to extract the main location and additional details.
   - `fetch_properties(url)`: Fetches property data from the given URL and yields relevant details.
   - `has_next_page(soup)`: Checks if there is a next page of property listings.
   - `scrape_all_properties(base_urls)`: Scrapes all property listings from the provided base URLs and saves them to a CSV file.

## Usage

Run the script by executing the following command in your terminal:

```bash
python property_scraper.py
```

The script will fetch property listings from the specified URLs, filter them based on their location within Nairobi, and save the data to `nairobi_property_listings.csv`.

## Example

```python
if __name__ == "__main__":
    base_urls = [
        'https://www.buyrentkenya.com/houses-for-sale',
        'https://www.buyrentkenya.com/flats-apartments-for-sale',
        'https://www.buyrentkenya.com/houses-for-rent',
        'https://www.buyrentkenya.com/flats-apartments-for-rent',
        'https://www.buyrentkenya.com/bedsitters-for-rent'
    ]
    
    scrape_all_properties(base_urls)
    print('File saved successfully')
```

This will scrape the property listings from the provided URLs and save them to `nairobi_property_listings.csv`.

## File Structure

- **property_scraper.py**: The main script file.
- **nairobi_property_listings.csv**: The output file containing the scraped property data.

## CSV File Format

The CSV file will have the following columns:

- Location
- Other Location Details
- Size
- Bedrooms
- Bathrooms
- Price
- Property Type
- Purchase Type

## Notes

- Ensure you have a stable internet connection as the script makes multiple web requests.
- The script filters properties based on their location within a 30 km radius of Nairobi.
- In case of any errors during geocoding or fetching property details, appropriate messages will be printed to the console.

Feel free to modify the script to suit your specific requirements.