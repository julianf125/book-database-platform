import requests
from bs4 import BeautifulSoup
from utilities import process_summary, format_name, truncate_string, add_newline_after_closing_quote, remove_asin_isbn_sentences, adjust_spaces_around_quotes
from notion_api import update_with_packet, refresh_with_packet, update_page, find_page_by_title
from IPython.display import display, Image
from config import NOTION_TOKEN, DATABASE_ID
from notion_api import notion_client
from tqdm import tqdm

"""
Function that takes the title of a book as input and return a dictionary that holds
the metadata for the best match for the title.
"""
def get_goodreads_id(title):
    search_url = f"https://www.goodreads.com/search?q=\"{title}\""

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    # Fetch the search page
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Assuming the first search result is the book we're looking for
        # This is where you'll need to adjust based on the actual HTML structure of Goodreads search results
        book_link = soup.find('a', class_='bookTitle')  # Hypothetical selector; adjust based on actual structure

        if book_link and 'href' in book_link.attrs:
            if book_link['href'].split('/')[-1].split('.')[0].isdigit():
                book_id = book_link['href'].split('/')[-1].split('.')[0]  # Extracting book ID from the link
            else:
                book_id = book_link['href'].split('/')[-1].split('-')[0]

            return book_id

        else:
            print("Book not found")
            return None
    else:
        print("Failed to retrieve search results")
        return None

def scrape_book_info(book_id):
    book_url = 'https://www.goodreads.com/book/show/' + book_id
    # Headers to simulate a browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Fetch the page
    response = requests.get(book_url, headers=headers)

    metadata = {}

    if response.status_code == 200:
        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title using the class and data-testid attribute
        title = soup.find('h1', {'data-testid': 'bookTitle'}).get_text(strip=True)
        metadata['title'] = title.replace('\u200b', '')

        # Extract author
        author = soup.find('span', {'data-testid': 'name'}).get_text(strip=True)
        metadata['author'] = author.strip('\n')

        # Extract publication date
        pub_date = soup.find('p', {'data-testid': 'publicationInfo'}).get_text(strip=True)
        metadata['publication date'] = pub_date.replace("First published ", '')

        # Extract rating
        rating = soup.find('div', {'class': 'RatingStatistics__rating'}).get_text(strip=True)
        metadata['rating'] = rating

        # Extract number of ratings
        num_ratings = soup.find('span', {'data-testid': 'ratingsCount'}).get_text(strip=True)
        metadata['num ratings'] = num_ratings.strip('ratings')

        # Extract page count
        pages = soup.find('p', {'data-testid': 'pagesFormat'}).get_text(strip=True)
        metadata['pages'] = pages.split(' ')[0]

        # Extract summary
        summary = soup.find('div', class_='DetailsLayoutRightParagraph__widthConstrained').get_text(strip=False)
        summary = process_summary(summary)
        metadata['summary'] = summary

        # Extract genres
        genres = soup.find('div', {'data-testid': 'genresList'}).find_all('span', class_='Button__labelItem')
        for i in range(len(genres)):
            genres[i] = genres[i].get_text(strip=True)
        metadata['genres'] = genres[:-1]

        # Extract series info
        series = soup.find('h3', class_='Text Text__title3 Text__italic Text__regular Text__subdued')
        if series is not None:
            metadata['series'] = series.get_text(strip=False).replace(' (Publication Order)', '')

        metadata['pid'] = book_id

        # Get cover image
        image_tag = soup.find('img', {'class': 'ResponsiveImage'})['src']
        metadata['cover'] = image_tag

        # Format author name for sorting
        sort_author = format_name(author.strip('\n'))
        metadata['sort author'] = sort_author
    else:
        print("Failed to retrieve the page")
        metadata = None

    return metadata

"""
  Iterates through all entries in a Notion database, checks if the "ID" field is empty,
  and if so, updates it with get_goodreads_id(title).
  Displays the title, author, and publication date corresponding to the retrieved ID.
  Titles are all updates, using either a new ID or the one stored in the database
"""
def check_and_fetch_ids():
    print('The following pages were updated with new IDs:')
    old_updates = 0
    new_updates = 0
    try:
        # Query the database to get all entries
        query_results = notion_client.databases.query(database_id=DATABASE_ID)

        for page in query_results.get("results", []):
            # Extract the Name (title) of the entry
            name_property = page["properties"].get("Name", {}).get("title", [{}])

            if name_property:
                name = name_property[0].get("text", {}).get("content", "")

                # Extract the ID property to check if it's empty
                id_property = page["properties"].get("ID", {}).get("rich_text", [{}])
                if id_property == []:
                    # ID field is empty
                    goodreads_id = get_goodreads_id(name)
                    print('\n ----- ' + name + ' -----')
                    print(f"      Found ID #{goodreads_id}")
                    metadata = scrape_book_info(goodreads_id)
                    update_with_packet(page['id'], metadata)
                    print('      ' + metadata['title'] + ' --- ' + metadata['author'] + ((' --- ' + metadata.get('series')) if metadata.get('series') is not None else ''))
                    print('      ' + metadata['publication date'] + ' --- ' + metadata['rating'] + ' with ' + metadata['num ratings'] + ' ratings')
    except Exception as e:
        print(f"An error occurred: {e}")

def update_all_ids(all_props=False):
    print('Updating data for all known IDs...')
    try:
        # Query the database to get all entries
        query_results = notion_client.databases.query(database_id=DATABASE_ID)
        results = query_results.get("results", [])

        # Initialize progress bar with dynamic total based on the number of results
        with tqdm(total=len(results), desc="Updating IDs", unit="entry") as pbar:
            for page in results:
                # Extract the Name (title) of the entry
                name_property = page["properties"].get("Name", {}).get("title", [{}])
                title = name_property[0].get('text', {}).get('content', 'Unknown Title') if name_property else 'Unknown Title'

                # Extract the ID property to check if it's filled
                id_property = page["properties"].get("ID", {}).get("rich_text", [{}])
                if id_property:
                    # Extract ID
                    id = id_property[0]['text']['content']
                    # Update progress bar description with the current title being processed
                    pbar.set_description(f"Updating: {title}")

                    if not all_props:
                        # Refresh book information with minimal properties
                        refresh_with_packet(page['id'], scrape_book_info(id))
                    else:
                        # Update with complete information
                        p = scrape_book_info(id)
                        update_page(page['id'], cover=p['cover'])
                        display(Image(url=p['cover']))
                        print('--- ' + p['title'] + ' ---')

                # Update progress bar after processing each entry
                pbar.update(1)

    except Exception as e:
        print(f"An error occurred: {e}")

def fix_match():
    response = input("Enter title to fix or Q to quit:  ")
    while response != "Q" and response != "q":
        page = find_page_by_title(response)
        if page == []:
            print("No page for title " + response + " found in database")
        else:
            page = page[0]
            new_id = input("Enter new Goodreads ID: ")
            print('Scraping book info...')
            packet = scrape_book_info(new_id)
            print(packet['title'] + ' by ' + packet['author'] + ' --- ' + packet['publication date'])
            conf = input('Set new ID (' + new_id +') for ' + response + '? (Y/N) ')
            if conf == 'Y' or conf == 'y':
                update_with_packet(page['id'], packet)
                print('ID #' + new_id + ' set for ' + response + '\n')
            elif conf == 'N' or conf == 'n':
                print('Operation cancelled\n')
        response = input("Enter title to fix or Q to quit:  ")