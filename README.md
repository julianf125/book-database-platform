# Book Database Management Platform

## Description
As an avid reader, I like to maintain a database of the books I want to read, as well as those that I have already read and my ratings of them. The code in this repository accomplishes aids in maintaining and enriching this database. With the use of web scraping, this platform uses the given title of the book to retrieve the author, publication year and genre of the book, alongside many other pieces of insightful matadata, and store them alongside the aforementioned title for ease of access. Goodreads is used for web scraping, while Notion holds the database that is being managed.

## Usage
This program is intended to be run from the command line. One of 3 flags can be passed, with each triggering the execution of a different function:
* **--fetch_new**:
