from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
from RPA.HTTP import HTTP
import re
import datetime

# Initialize the libraries
browser = Selenium()
excel = Files()
work_items = WorkItems()
http = HTTP()

# Load the work item by its ID
work_item_id = "28e90c50-509b-4a6c-a64c-a7a687a9c5e8"
work_item = work_items.get_work_item_variable(work_item_id)

# Get the search phrase and news category from the work item
search_phrase = work_item.get("search_phrase")
news_category = work_item.get("news_category", "news_section", "news_topic")

# Get the number of months from the work item, with a default value of 1
num_months = work_item.get("num_months", 1)

# Open the site
browser.open_available_browser("https://www.aljazeera.com/")

# Enter the search phrase
browser.input_text("<your-search-field-locator>", search_phrase)

# Select the news category if possible
if news_category:
    browser.select_from_list_by_label('id("category-dropdown")', news_category)

# Get the news items
news_items = browser.find_elements('xpath("//ul[@id="news-list"]/li")')

# Filter the news items based on the date
filtered_news_items = []
for item in news_items:
    date_str = browser.get_text('.date', element=item)
    try:
        date = datetime.datetime.strptime(date_str,'%Y-%m-%d').date()
        if date >= datetime.datetime.now() - datetime.timedelta(days=30*num_months):
            filtered_news_items.append(item)
    except ValueError:
        continue
       
# Process the filtered news items
for item in filtered_news_items:
    # Get the values
    title = browser.get_text('#title', element=item)
    date = browser.get_text('.date', element=item)
    description = browser.get_text('div#container > p', element=item)

    # Download the picture
    picture_url = browser.get_attribute("src", '#picture', element=item)
    picture_filename = http.download(picture_url)

    # Count the search phrases in the title and description
    count = sum(title.count(search_phrase) for search_phrase in search_phrase)

    # Add the information to the work
    contains_money = bool(re.search(r"\$\d+(\.\d{1,2})?|\d+ dollars|\d+ USD", title + description))

    # Store in an Excel file
    excel.append_rows_to_worksheet([[title, date, description, picture_filename, count, contains_money]])
    
    excel.save_workbook(path="${OUTPUT_DIR}${OUTPUT_NAME}.xlsx")
    
    # Close the browser
    browser.close_browser()