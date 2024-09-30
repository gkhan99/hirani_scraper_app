import requests
import pandas as pd
from bs4 import BeautifulSoup
import tempfile
import os
import webbrowser
from datetime import datetime

# Scraping function for NYS DOT Detailed Ads
def scrape_nys_dot_detail_ads():
    url = 'https://www.dot.ny.gov/doing-business/opportunities/eng-detailad'
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')
    main_table = soup.find('table', {'id': 'rg151682'})

    dates = []
    descriptions = []
    links = []

    inner_tables = main_table.find_all('table', class_='bcbanregion1')

    for inner_table in inner_tables:
        rows = inner_table.find_all('tr')
        for row in rows:
            date_td = row.find('td', class_='bcgroup')
            info_td = row.find('td', class_='bcbanregion2')
            
            if date_td and info_td:
                date = date_td.get_text(strip=True)
                # Change the date format to yyyy/mm/dd
                try:
                    date_obj = datetime.strptime(date, '%m/%d/%Y')  # Adjust the format if needed
                    date = date_obj.strftime('%Y/%m/%d')
                except ValueError:
                    pass  # Handle the case where the date format is not as expected
                
                description_html = str(info_td)
                description_start = description_html.find('&nbsp;') + 6  # find index after '&nbsp;'
                description_end = description_html.find('<ul>')
                if (description_end == -1):
                    description_end = description_html.find('</td>')
                description = description_html[description_start:description_end].strip()
                
                description = description.replace('lass="bcbanregion2">', '').replace('\n', '').strip()
                
                link_tag = info_td.find('a', target='_blank')
                if link_tag:
                    link_href = link_tag['href']
                    full_link = 'https://www.dot.ny.gov' + link_href
                    link_text = link_tag.get_text(strip=True)
                    link = f'<a href="{full_link}" target="_blank">{link_text}</a>'
                else:
                    link = None
                
                dates.append(date)
                descriptions.append(description)
                links.append(link)

    df = pd.DataFrame({
        'Date': dates,
        'Description': descriptions,
        'Link': links
    })

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Engineering Opportunities Detailed Ad</title>
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
        <a href="https://www.dot.ny.gov/doing-business/opportunities/eng-detailad" class="link-button" target="_blank">Website</a>
        <h1>Engineering Opportunities Detailed Ad</h1>
        {table}
    </body>
    </html>
    """

    html_table = df.to_html(escape=False, index=False, table_id="opportunities")
    html_output = html_template.replace("{table}", html_table)

    # Use a temporary directory for the HTML output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, 'Engineering_Opportunities_Detailed_Ad.html')
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_output)

    print("HTML file with clickable links, sortable date column, and 25 entries per page has been created successfully.")
    webbrowser.open(output_path)
