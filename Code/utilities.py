import re
from datetime import datetime

def add_newline_after_closing_quote(text):
    # Split the text into segments by quotation marks
    segments = text.split('"')

    # Initialize an empty list to hold processed segments
    processed_segments = []

    # Process each segment
    for i, segment in enumerate(segments):
        # If the segment is followed by an even-indexed segment (indicating it's a closing quote)
        # and the next segment starts with an alphanumeric character, add a newline
        if i % 2 == 1:  # This means the quote before this segment was an opening quote
            if i + 1 < len(segments) and re.match(r'^[A-Za-z0-9]', segments[i + 1]):
                segment += '"\n'  # Add a newline after the closing quote
            else:
                segment += '"'  # Otherwise, just reattach the closing quote without a newline
        elif i + 1 < len(segments):  # For the odd segments, which are outside quotes
            segment += '"'
        processed_segments.append(segment)

    # Join the processed segments back together
    return ''.join(processed_segments)

def remove_asin_isbn_sentences(text):
    # Split the text into sentences based on periods
    sentences = text.split('.')

    # Check and remove "ASIN" or "ISBN" from the first sentence if present
    if sentences and ("ASIN" in sentences[0] or "ISBN" in sentences[0]):
        sentences[0] = ''  # Remove the first sentence
        if len(sentences) > 1 and sentences[1].startswith('\n'):
            sentences[1] = sentences[1].lstrip('\n')  # Remove leading newline from the next sentence

    # Check and remove "ASIN" or "ISBN" from the last sentence if present
    if sentences and ("ASIN" in sentences[-1] or "ISBN" in sentences[-1]):
        if sentences[-1].startswith('\n'):
            sentences[-1] = sentences[-1].lstrip('\n')  # Remove leading newline from the last sentence
        sentences[-1] = ''  # Remove the last sentence

    # Reassemble the text, removing any empty sentences
    modified_text = '.'.join(sentence for sentence in sentences if sentence).strip('.')

    # Ensure proper spacing and period placement between sentences
    modified_text = modified_text.replace('.\n', '.\n ').replace('..', '.').strip()

    return modified_text

def truncate_string(s):
    # Check if the string length exceeds 2000 characters
    if len(s) > 2000:
        # Truncate to the first 1995 characters and append " ..."
        return s[:1995] + " ..."
    else:
        # Return the original string if it's not longer than 2000 characters
        return s

def adjust_spaces_around_quotes(text):
    # Split the text into segments by quotation marks
    segments = text.split('"')

    # Initialize an empty list to hold processed segments
    adjusted_segments = []

    # Flag to track whether the current segment is inside quotes
    inside_quotes = False

    for i, segment in enumerate(segments):
        # For segments outside of quotes (even indices), check and adjust the space before the closing quote
        if not inside_quotes:
            if i > 0:  # Ensure this is not the first segment
                # Remove space at the end if it's before a closing quote
                adjusted_segments[-1] = adjusted_segments[-1].rstrip()
        else:
            # For segments inside quotes (odd indices), adjust the space after the opening quote
            segment = segment.lstrip()

        adjusted_segments.append(segment)
        inside_quotes = not inside_quotes  # Toggle the inside_quotes flag

    # Join the adjusted segments back together
    return '"'.join(adjusted_segments)

def process_summary(summary):
    # Replace every period that is not followed by a space or is not at the end of the string with a period followed by a newline


    summary = re.sub(r'([.?!])(?=(?!\s)[0-9A-Za-z])', r'\1\n', summary)
    summary = adjust_spaces_around_quotes(summary)

    # Regular expression to match 'ASIN ' or 'ISBN ' followed by the alphanumeric identifier,
    # then capture everything after it, ensuring we start with a capital letter that is
    # followed by a lowercase letter (indicating the start of the desired text).
    match = re.search(r'(ASIN|ISBN) [A-Z0-9]+(?=[A-Z][a-z])', summary)
    # Check if a match is found
    if match:
        # Extract the desired part of the string starting from the match end position
        summary = summary[match.end():]
    # Check if the final character is alphanumeric and add a period if it is
    if summary and summary[-1].isalnum():
        summary = summary + "."
    summary = summary.replace('An alternate cover for this ISBN can be found here', '')
    summary = summary.replace('This is an alternate cover edition of ISBN 9780451529305.\n', '')
    summary = re.sub(r'\n\.$', '', summary)
    summary = add_newline_after_closing_quote(summary)
    summary = remove_asin_isbn_sentences(summary)
    summary = re.sub(r' +\n', '\n', summary)
    summary = re.sub(r'\n+ ', '\n\t', summary)

    return truncate_string(summary)

def format_name(name):
    """
    Format a name from 'First Last' to 'Last, First'.
    This function includes hardcoded lists of prefixes and suffixes to correctly format complex names.

    :param name: str, name in 'First Last' format or similar
    :return: str, name in 'Last, First' format
    """
    # Hardcoded lists of common prefixes and suffixes
    prefixes = ['Le', 'De', 'La', 'Van', 'Von']
    suffixes = ['Jr.', 'Sr.', 'II', 'III', 'IV']

    parts = name.split()

    # Identify if the name contains a prefix or suffix
    last_name_parts = []
    for i, part in enumerate(parts[1:], start=1):  # Skip the first name for checking
        if parts[i] in prefixes or parts[i-1] in prefixes or part in suffixes:
            last_name_parts.append(part)
        else:
            # Once a non-prefix/non-suffix part is found (in middle names), add remaining parts to last_name_parts
            last_name_parts.extend(parts[i:])
            break

    if not last_name_parts:  # If no prefixes/suffixes were found, assume the last part is the last name
        last_name_parts = [parts[-1]]

    first_name = parts[0]
    last_name = " ".join(last_name_parts)

    return f"{last_name}, {first_name}"

"""
    Parse a date string in the format 'January 1, 2024' into a datetime object without time.
    Args:
        date_string (str): The date string to parse.
    Returns:
        datetime: A datetime object representing the date.
"""
def parse_date(date_string):
    # Define the full date format
    full_date_format = "%B %d, %Y"
    # Define the year-only format
    year_only_format = "%Y"

    try:
        # Attempt to parse the full date string
        parsed_date = datetime.strptime(date_string, full_date_format)
    except ValueError:
        try:
            # If the full date parsing fails, extract the year part and parse it
            # Assuming the year is always at the end and has four digits
            year_part = date_string[-4:]
            parsed_date = datetime.strptime(year_part, year_only_format)
            print(f"Only the year was parsed successfully: {parsed_date.year}")
        except ValueError as e:
            # If parsing the year alone also fails, handle the error
            print(f"An error occurred while parsing the year: {e}")
            return None
    return parsed_date