# Book Database Management Platform

## Description
As an avid reader, I like to maintain a database of the books I want to read, as well as those that I have already read and my ratings of them. The code in this repository accomplishes aids in maintaining and enriching this database. With the use of web scraping, this platform uses the given title of the book to retrieve the author, publication year and genre of the book, alongside many other pieces of insightful matadata, and store them alongside the aforementioned title for ease of access. Goodreads is used for web scraping, while Notion holds the database that is being managed.

## Usage
```bash
Python main.py --flag
```
This program is intended to be run from the command line. One of 3 flags can be passed, with each triggering the execution of a different function:
* **--get_new:**  This flag executes the check_and_fetch_ids() function. This function examines the database, identifying all titles for which the data in the database is incomplete. It then uses these incomplete titles to perform a search on Goodreads. The top result of each search is identified as the most likely match for a given title, and the corresponding metadata is scraped from Goodreads and written to the Notion database. Titles with already-complete entries in Notion remain unmodified.
* **--fix_match:**  This flag is used to correct an erroneous match that has been made by the check_and_fetch_ids() function. When used, the program will first prompt the user for the title whose match they want to fix. Next, they will be provided with a space to enter the Goodreads identifier to the correct book. Finally, this identifier will be used to scrape new metadata from Goodreads. After allowing the user to confirm that this data matches their intended title, it will replace the previously-retrieved erroneous data.
* **--update:**  This flag calls the update_all_ids() function, which retrieves update Goodreads data for all items in the database with a valid Goodreads identifier present. It leaves the cover, title, author, genres, and publication year the same, and refreshes all other data fields. A progress bar of the current execution's progress will be shown to the user in real-time.
