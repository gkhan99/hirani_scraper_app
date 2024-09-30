import requests
import pandas as pd
from bs4 import BeautifulSoup
import tempfile
import os
import webbrowser

# Scraping function for NYS DOT Designation
def scrape_nys_dot_designation():
    url = 'https://www.dot.ny.gov/doing-business/opportunities/eng-designation'
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')
    main_table = soup.find('table', {'id': 'rg151694'})

    dates = []
    descriptions = []

    inner_tables = main_table.find_all('table', class_='bcbanregion1')

    for inner_table in inner_tables:
        rows = inner_table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='bcgroup', valign='top')
            info_td = row.find('td', class_='bcbanregion2')
            
            if date_td and info_td:
                date = date_td.get_text(strip=True)
                
                if '2024' in date:
                    description_html = str(info_td)
                    description_start = description_html.find('<br>') + 4
                    description_end = description_html.find('</td>')
                    description = description_html[description_start:description_end].strip()
                    
                    soup_desc = BeautifulSoup(description, 'html.parser')
                    for strong_tag in soup_desc.find_all('strong'):
                        strong_tag.decompose()
                    
                    description = soup_desc.get_text(strip=True)
                    description = description.replace('class="bcbanregion2">', '').strip()
                    
                    dates.append(date)
                    descriptions.append(description)

    df = pd.DataFrame({
        'Date': dates,
        'Description': descriptions
    })

    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', ascending=False, inplace=True)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Engineering Opportunities Designation</title>
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
            #opportunities th:first-child, #opportunities td:first-child {
                width: 150px;
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
        </style>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.3/css/jquery.dataTables.css">
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.js"></script>
        <script>
            $(document).ready(function() {
                $('#opportunities').DataTable({
                    "order": [[ 0, "desc" ]],
                    "pageLength": 25
                });
            });
        </script>
    </head>
    <body>
        <a href="https://www.dot.ny.gov/doing-business/opportunities/eng-designation" class="link-button" target="_blank">Website</a>
        <h1>Engineering Opportunities Designation</h1>
        {table}
    </body>
    </html>
    """

    html_table = df.to_html(escape=False, index=False, table_id="opportunities")
    html_output = html_template.replace("{table}", html_table)

    # Use a temporary directory for the HTML output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, 'Engineering_Opportunities_Designation_2024.html')
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_output)

    print("HTML file with dates and descriptions for 2024 has been created successfully.")
    webbrowser.open(output_path)
