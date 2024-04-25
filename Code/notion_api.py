from notion_client import Client
from config import NOTION_TOKEN, DATABASE_ID
from utilities import parse_date

notion_client = Client(auth=NOTION_TOKEN)

def find_page_by_title(title):
    """
    Query the database for a page with a specific 'Title' (or 'Name').
    """
    try:
        query_results = notion_client.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Name",  # This targets the main title of a database entry. Adjust if your schema is different.
                "title": {  # Note the change here to 'title' to accurately reflect the property type
                    "equals": title
                }
            }
        )
        return query_results.get("results")
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def find_page_by_id(id):
    """
    Query the database for a page with a specific 'Title' (or 'Name').
    """
    try:
        query_results = notion_client.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "ID",
                "rich_text": {
                    "equals": id
                }
            }
        )
        return query_results.get("results")
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

"""
    Update a Notion page with given values for text, number, and multi-select properties.

    Args:
        page_id (str): The ID of the page to update.
        text_value (str): The new value for the text property.
        number_value (int or float): The new value for the number property.
        multi_select_values (list): A list of strings representing the new values for the multi-select property.
"""
def update_page(page_id, series=None, rating=None, num_ratings=None, page_cnt=None, genres=None, pub_date=None,
               summary=None, author=None, pid=None, cover=None, sort_author=None):

    # Prepare the properties payload
    data = {}

    if series is not None:
        data["Series"] = {
            "type": "rich_text",
            "rich_text": [{"text": {"content": series}}]
        }

    if pid is not None:
        data["ID"] = {
            "type": "rich_text",
            "rich_text": [{"text": {"content": pid}}]
        }

    if rating is not None:
        data["Goodreads Rating"] = {
            "type": "number",
            "number": rating
        }

    if num_ratings is not None:
        data["Number of Ratings"] = {
            "type": "number",
            "number": num_ratings
        }

    if page_cnt is not None:
        data["Page Count"] = {
            "type": "number",
            "number": page_cnt
        }

    if genres is not None:
        genres = list(set(genres).intersection(fetch_genres_options(DATABASE_ID)))
        data["Genres"] = {
            "type": "multi_select",
            "multi_select": [{"name": value} for value in genres]
        }

    if pub_date is not None:
        # Format the date to include only the date part (YYYY-MM-DD)
        formatted_date = parse_date(pub_date).date().isoformat()
        data["Publication Date"] = {
            "date": {
            "start": formatted_date,
            }
        }

    if summary is not None:
        data["Summary"] = {
            "type": "rich_text",
            "rich_text": [{"text": {"content": summary}}]
        }

    if author is not None:
        data["Author"] = {
            "type": "rich_text",
            "rich_text": [{"text": {"content": author}}]
        }

    if sort_author is not None:
        data["Sort Author"] = {
            "type": "rich_text",
            "rich_text": [{"text": {"content": sort_author}}]
        }

    # Prepare the cover payload separately
    cover_data = None
    if cover is not None:
        cover_data = {
            "cover": {
                "type": "external",
                "external": {
                    "url": cover
                }
            }
        }

    # Make the API request to update the page
    try:
        update_payload = {"properties": data}
        if cover_data:
            update_payload.update(cover_data)  # Include cover data if available

        response = notion_client.pages.update(page_id=page_id, **update_payload)
    except Exception as e:
        print(f"Failed to update page: {str(e)}")

def get_all_ids():
    """
    Query the database to get all entries and their 'ID' property values.
    """
    ids = []
    try:
        query_results = notion_client.databases.query(
            database_id=DATABASE_ID
        )
        for page in query_results.get("results", []):
            id_property = page["properties"].get("ID", {}).get("rich_text", [{}])
            if id_property:
                id_value = id_property[0].get("text", {}).get("content", "")
                if id_value:
                    ids.append(id_value)
    except Exception as e:
        print(f"An error occurred: {e}")
    return ids

def fetch_genres_options(database_id):
    # Fetch the database metadata
    database_metadata = notion_client.databases.retrieve(database_id=database_id)

    # Extract properties from the database metadata
    properties = database_metadata.get("properties", {})

    # Extract the "Genres" multi-select property
    genres_property = properties.get("Genres")

    # Check if "Genres" is indeed a multi-select property
    if genres_property and genres_property.get("type") == "multi_select":
        # Extract and return the options
        options = genres_property["multi_select"]["options"]
        return [option["name"] for option in options]
    else:
        print("The 'Genres' property is not found or not a multi-select type.")
        return []
    
def refresh_with_packet(page_id, packet):
    update_page(page_id, rating=float(packet.get('rating')), num_ratings=int(packet.get('num ratings').replace(',', '')))

def update_with_packet(page_id, packet):
    update_page(page_id, packet.get('series'), float(packet.get('rating')),
                int(packet.get('num ratings').replace(',', '')), int(packet.get('pages').strip(',')),
                packet.get('genres'), packet.get('publication date'), packet.get('summary'), packet.get('author'),
                packet.get('pid'), packet.get('cover'), packet.get('sort author'))
