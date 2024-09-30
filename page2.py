import requests
import pandas as pd
from bs4 import BeautifulSoup
import tempfile
import os
import webbrowser

def scrape_nys_general_services():
    url = 'https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/esbConsultantOpsIndex.asp'
    base_url = 'https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/'

    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    def extract_table_data(table, title, base_url):
        rows = table.find_all('tr')
        if len(rows) > 2:
            header = [th.get_text(strip=True) for th in rows[1].find_all('td')]
            data = []
            for row in rows[2:]:
                cols = row.find_all('td')
                if len(cols) == len(header):
                    row_data = [col.get_text(strip=True) for col in cols]
                    link_tag = cols[0].find('a')
                    if link_tag:
                        link_url = base_url + link_tag['href']
                        row_data[0] = f'<a href="{link_url}" target="_blank">{row_data[0]}</a>'
                    data.append(row_data)
            if data:
                return pd.DataFrame(data, columns=header)
        return pd.DataFrame([["No submissions at this time."]], columns=[title])

    tables = []
    current_opportunities_table = soup.find('table', {'bgcolor': '#FFFFFF', 'cellspacing': '0', 'border': '1', 'cellpadding': '0', 'width': '100%'})
    tables.append(('Current Opportunities', extract_table_data(current_opportunities_table, 'Current Opportunities', base_url)))

    submission_under_review_table = current_opportunities_table.find_next('table', {'bgcolor': '#FFFFFF', 'cellspacing': '0', 'border': '1', 'cellpadding': '0', 'width': '100%'})
    tables.append(('Submission Under Review', extract_table_data(submission_under_review_table, 'Submission Under Review', base_url)))

    short_listed_table = submission_under_review_table.find_next('table', {'bgcolor': '#FFFFFF', 'cellspacing': '0', 'border': '1', 'cellpadding': '0', 'width': '100%'})
    tables.append(('Short-Listed', extract_table_data(short_listed_table, 'Short-Listed', base_url)))

    selected_award_pending_table = short_listed_table.find_next('table', {'bgcolor': '#FFFFFF', 'cellspacing': '0', 'border': '1', 'cellpadding': '0', 'width': '100%'})
    tables.append(('Selected - Award Pending', extract_table_data(selected_award_pending_table, 'Selected - Award Pending', base_url)))

    html_content = """
    <html>
    <head>
        <title>New York State Office of General Services</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h2 {
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
    </head>
    <body>
        <a href="https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/esbConsultantOpsIndex.asp" class="link-button" target="_blank">Website</a>
    """

    for table_name, df in tables:
        html_content += f"<h2>{table_name}</h2>"
        html_content += df.to_html(escape=False, index=False)
        html_content += "<br><br>"

    html_content += "</body></html>"

    # Use a temporary directory for the HTML output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, 'All_Tables.html')
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Open the HTML file in the default browser
    webbrowser.open(output_path)
