import os
import pandas as pd
from bs4 import BeautifulSoup
import tempfile
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from urllib.parse import urljoin

# Scraping function for Port Authority Professional Services using Selenium
def scrape_port_authority_professional_services():
    # Set up Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Go to the URL
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html'
    driver.get(url)

    # Wait for the table to load
    time.sleep(5)

    # Get the page source and close the browser
    content = driver.page_source
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Find the first table in the webpage
    table = soup.find('table')
    if not table:
        print("No table found on the page.")
        return

    # Ensure all links are absolute by converting relative URLs
    for a in table.find_all('a', href=True):
        # Convert relative URLs to absolute URLs
        a['href'] = urljoin(url, a['href'])

    # CSS styling for the table, button, and embedded links
    css = """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin-bottom: 20px;
            border: none;
            cursor: pointer;
            position: absolute;
            top: 20px;
            left: 20px;
        }
        .button:hover {
            background-color: #45a049;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: #ffffff;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        #search-input {
            margin-bottom: 20px;
            padding: 10px;
            width: 100%;
            box-sizing: border-box;
            font-size: 16px;
        }
        h1 {
            margin-top: 80px;
        }
    </style>
    <script>
        function filterTables() {
            var input, filter, table, tr, td, i, j, txtValue;
            input = document.getElementById('search-input');
            filter = input.value.toLowerCase();
            table = document.getElementsByTagName('table')[0];
            tr = table.getElementsByTagName('tr');
            for (i = 1; i < tr.length; i++) {
                tr[i].style.display = 'none'; // Hide the row initially
                td = tr[i].getElementsByTagName('td');
                for (j = 0; j < td.length; j++) {
                    if (td[j]) {
                        txtValue = td[j].textContent || td[j].innerText;
                        if (txtValue.toLowerCase().indexOf(filter) > -1) {
                            tr[i].style.display = ''; // Show the row if it matches the filter
                            break;
                        }
                    }
                }
            }
        }
    </script>
    """

    # HTML content with the "Website" button, CSS styling, search input, and the extracted table
    html_content = f"""
    <html>
    <head>
        <title>Professional Services Opportunity: Port Authority</title>
        {css}
    </head>
    <body>
        <a href="{url}" class="button" target="_blank">Website</a>
        <h1>Professional Services Opportunity: Port Authority</h1>
        <input type='text' id='search-input' onkeyup='filterTables()' placeholder='Search keyword...' />
        <h2>Professional Services Table</h2>
        {str(table)}
    </body>
    </html>
    """

    # Use a temporary directory for the HTML output
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, 'port_authority_professional_services.html')
    
    # Open file in write mode with UTF-8 encoding to handle Unicode characters
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"Table extracted and saved as '{output_file}'.")
    webbrowser.open(output_file)
