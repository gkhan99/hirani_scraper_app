import os
import pandas as pd
from bs4 import BeautifulSoup
import tempfile
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Scraping function for PASSPort Construction Opportunities using Selenium
def fetch_table_passport(driver):
    try:
        # Wait for the table to load
        time.sleep(5)
        content = driver.page_source
        return content
    except Exception as e:
        print(f"An error occurred while fetching the table: {e}")
        return None

def parse_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find("table", class_="iv-grid-view")

    if table:
        headers = table.find_all('th')
        titles = [header.text.strip() for header in headers]
        rows = table.find_all('tr', {'data-id': True})  # Get rows with data-id attribute
        page_data = []
        for row in rows:
            data = row.find_all('td')
            row_data = []
            for i, td in enumerate(data):
                # Extract the onclick link from 'Procurement Name'
                if i == 3 and 'onclick' in str(td):
                    link = td.find('button')['onclick'].split("'")[1]
                    full_link = f"https://passport.cityofnewyork.us{link}"
                    row_data.append(f'<a href="{full_link}" target="_blank">{td.text.strip().replace("Edit", "").strip()}</a>')
                else:
                    row_data.append(td.text.strip().replace('Edit', '').strip())
            page_data.append(row_data)
        return titles, page_data
    else:
        return None, None

def scrape_passport(max_pages=6):
    all_data = []
    titles = None

    # Set up Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        url = "https://passport.cityofnewyork.us/page.aspx/en/rfp/request_browse_public"
        driver.get(url)
        time.sleep(5)  # Wait for the initial page to load

        page_number = 1
        while page_number <= max_pages:
            content = fetch_table_passport(driver)
            if content is None:
                break
            page_titles, page_data = parse_table(content)
            if page_data:
                if not titles:
                    titles = page_titles
                all_data.extend(page_data)
                if page_number < max_pages:
                    # Go to the next page
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next page']")
                        next_button.click()
                        time.sleep(5)  # Wait for the next page to load
                        page_number += 1
                    except Exception as e:
                        print(f"Could not navigate to the next page: {e}")
                        break
                else:
                    break
            else:
                break

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        driver.quit()

    # Create a DataFrame if data is found
    if titles and all_data:
        df = pd.DataFrame(all_data, columns=titles)

        # Drop the first column
        df = df.iloc[:, 1:]
        
        # Select specific columns, adjust the indices accordingly
        selective_df = df.iloc[:, [0, 1, 3, 4, 5, 6, 10]]  # Adjusted to Python 0-based indexing
        
        # Filter by specified industries
        industries_to_keep = [
            'Construction', 
            'Professional Services', 
            'Professional Services - Construction Related', 
            'Professional Services - Architecture/Engineering', 
            'Standard Services', 
            'Standard Services - Construction Related'
        ]
        selective_df = selective_df[selective_df['Industry'].isin(industries_to_keep)]
        
        # Filter by RFx Status 'Released'
        selective_df = selective_df[selective_df['RFx Status'] == 'Released']
        
        # CSS styling
        css = """
        <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            background-color: #f2f2f2;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            text-align: left;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .link-button {
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #007acc;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }
        .link-button:hover {
            background-color: #005f99;
        }
        #filter-container {
            margin-bottom: 20px;
        }
        .filter-label {
            margin-right: 10px;
            font-weight: bold;
        }
        .filter-input {
            margin-right: 20px;
        }
        </style>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.3/css/jquery.dataTables.css">
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.js"></script>
        <script>
            $(document).ready(function() {
                var table = $('#opportunities').DataTable({
                    "order": [[ 0, "desc" ]],
                    "pageLength": 25
                });

                $('#industry-filter').on('change', function() {
                    var filterValue = this.value;
                    if (filterValue === 'All') {
                        table.column(1).search('').draw();
                    } else {
                        table.column(1).search('^' + filterValue + '$', true, false).draw();
                    }
                });

                $('#procurement-filter').on('keyup', function() {
                    table.column(2).search(this.value).draw();
                });
            });

            function openUrl() {
                window.open("https://passport.cityofnewyork.us/page.aspx/en/rfp/request_browse_public", "_blank");
            }
        </script>
        """
        
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scraped Data</title>
            {css}
        </head>
        <body>
            <a href="javascript:void(0);" class="link-button" onclick="openUrl()">Website</a>
            <h1>Construction Opportunities</h1>
            <div id="filter-container">
                <label class="filter-label" for="industry-filter">Industry:</label>
                <select id="industry-filter" class="filter-input">
                    <option value="All">All</option>
                    <option value="Construction">Construction</option>
                    <option value="Professional Services">Professional Services</option>
                    <option value="Professional Services - Construction Related">Professional Services - Construction Related</option>
                    <option value="Professional Services - Architecture/Engineering">Professional Services - Architecture/Engineering</option>
                    <option value="Standard Services">Standard Services</option>
                    <option value="Standard Services - Construction Related">Standard Services - Construction Related</option>
                </select>
                <label class="filter-label" for="procurement-filter">Procurement Name:</label>
                <input type="text" id="procurement-filter" class="filter-input" placeholder="Filter by Procurement Name">
            </div>
            {table}
        </body>
        </html>
        """
        
        # Convert the DataFrame to an HTML table
        html_table = selective_df.to_html(escape=False, index=False, table_id="opportunities")
        
        # Combine the HTML parts
        html_output = html_template.format(css=css, table=html_table)
        
        # Open the HTML in the default web browser
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_output)
            webbrowser.open('file://' + os.path.realpath(f.name))
        
        print("HTML file with filters has been created successfully.")
    else:
        print("No data found in the table.")
