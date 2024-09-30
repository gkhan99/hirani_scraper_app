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

# Scraping function for Port Authority Construction Opportunities using Selenium
def fetch_table_port_authority():
    # Set up Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Go to the URL
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/Construction.html'
    driver.get(url)

    # Wait for the table to load
    time.sleep(5)

    # Get the page source and close the browser
    content = driver.page_source
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Locate all table elements
    table_containers = soup.find_all('div', {'class': 'Text med black'})

    table_names = [
        "Solicitations/Advertisements",
        "Catalog of Upcoming Procurements at John F. Kennedy (JFK) International Airport",
        "RTQ (Request to Qualify)",
        "VVP (Verification and Validation Process)",
        "Others"
    ]

    all_tables_html = ""
    table_counter = 0

    # Process each table
    for container in table_containers:
        tables = container.find_all('table')
        for table in tables:
            if table is None or table_counter >= len(table_names):
                continue

            # Extract table headers
            headers = ['Full Description']
            for th in table.find_all('th'):
                headers.append(th.get_text(strip=True))

            # Extract table rows
            rows = []
            base_url = 'https://panynj.gov'
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = []
                full_description = ''
                for idx, td in enumerate(tr.find_all('td')):
                    cell_content = []
                    # Extract the text content and handle <a> tags
                    if td.find('a'):
                        for a in td.find_all('a'):
                            href = a['href']
                            if not href.startswith('http'):
                                href = base_url + href
                            cell_content.append(f'<a href="{href}" target="_blank">{a.get_text(strip=True)}</a>')
                        cells.append("<br>".join(cell_content))
                    else:
                        cells.append(td.get_text(strip=True))
                    
                    # If this is the third column, capture the text content before any <br> tag
                    if idx == 2:
                        first_paragraph = td.find('p')
                        if first_paragraph and first_paragraph.contents:
                            full_description = str(first_paragraph.contents[0]).strip()

                cells.insert(0, full_description)  # Insert the full description at the beginning
                rows.append(cells)

            # Create a DataFrame
            df = pd.DataFrame(rows, columns=headers)

            # Convert DataFrame to HTML
            table_html = df.to_html(index=False, escape=False, classes='styled-table', table_id=f'table_{table_counter}')

            # Add a title for the table
            table_name = table_names[table_counter]
            all_tables_html += f"<h2>{table_name}</h2>"
            all_tables_html += table_html

            table_counter += 1

    # Generate HTML with CSS styling and JavaScript for the text filter
    html_output = f"""
    <html>
    <head>
        <style>
            .styled-table {{
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 0.9em;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                width: 100%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
            .styled-table thead tr {{
                background-color: #009879;
                color: #ffffff;
                text-align: left;
            }}
            .styled-table th, .styled-table td {{
                padding: 12px 15px;
            }}
            .styled-table tbody tr {{
                border-bottom: 1px solid #dddddd;
            }}
            .styled-table tbody tr:nth-of-type(even) {{
                background-color: #f3f3f3;
            }}
            .styled-table tbody tr:last-of-type {{
                border-bottom: 2px solid #009879;
            }}
            .filter-input {{
                margin-bottom: 20px;
                padding: 10px;
                font-size: 1em;
                width: 100%;
                box-sizing: border-box;
            }}
        </style>
        <script>
            function filterTable(event) {{
                const filter = event.target.value.toLowerCase();
                const tables = document.querySelectorAll('.styled-table tbody tr');
                tables.forEach(row => {{
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                }});
            }}
        </script>
    </head>
    <body>
        <h1>Construction Opportunities</h1>
        <input type="text" class="filter-input" placeholder="Type to filter..." onkeyup="filterTable(event)">
        {all_tables_html}
    </body>
    </html>
    """

    # Use a temporary directory for the HTML output
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, 'output_tables_with_links.html')
    
    with open(output_file, 'w') as file:
        file.write(html_output)

    print(f"Tables extracted and saved as '{output_file}'.")
    webbrowser.open(output_file)
