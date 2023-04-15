Nintendo Game of the Year Awards Scraper

This Python script scrapes Game of the Year (GOTY) awards data from Wikipedia, fetches associated game review scores from GameSpot, and compiles the data into an Excel file.
Features

    Web Scraping: Utilizes BeautifulSoup to extract tables of GOTY awards from Wikipedia.
    Game Reviews: Fetches GameSpot, Metacritic, and user average ratings for each game.
    Data Cleaning: Processes and cleans game names, removing extraneous characters and adjusting URLs for accurate review lookups.
    Excel Export: Saves the combined data in a well-formatted Excel file using pandas and xlsxwriter.