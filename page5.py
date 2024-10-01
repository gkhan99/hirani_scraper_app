import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

API_KEY = st.secrets["SCRAPER_API_KEY"]

# Scraping function for Port Authority Construction Opportunities using ScraperAPI
def fetch_table_port_authority():
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/Construction.html'
    api_url = f'http://api.scraperapi.com?api_key={API_KEY}&url={url}&render=true'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate all table elements
        table_containers = soup.find_all('div', {'class': 'Text med black'})

        table_names = [
            "Solicitations/Advertisements",
            "Catalog of Upcoming Procurements at John F. Kennedy (JFK) International Airport",
            "RTQ (Request to Qualify)",
            "VVP (Verification and Validation Process)",
            "Others"
        ]

        all_tables = []
        table_counter = 0

        for container in table_containers:
            tables = container.find_all('table')
            for table in tables:
                if table is None or table_counter >= len(table_names):
                    continue

                headers = ['Full Description']
                for th in table.find_all('th'):
                    headers.append(th.get_text(strip=True))

                rows = []
                base_url = 'https://panynj.gov'
                for tr in table.find_all('tr')[1:]:  # Skip the header row
                    cells = []
                    full_description = ''
                    for idx, td in enumerate(tr.find_all('td')):
                        cell_content = []
                        if td.find('a'):
                            for a in td.find_all('a'):
                                href = a['href']
                                if not href.startswith('http'):
                                    href = urljoin(base_url, href)
                                cell_content.append(f'<a href="{href}" target="_blank">{a.get_text(strip=True)}</a>')
                            cells.append("<br>".join(cell_content))
                        else:
                            cells.append(td.get_text(strip=True))

                        if idx == 2:
                            first_paragraph = td.find('p')
                            if first_paragraph and first_paragraph.contents:
                                full_description = str(first_paragraph.contents[0]).strip()

                    cells.insert(0, full_description)  # Insert the full description at the beginning
                    rows.append(cells)

                df = pd.DataFrame(rows, columns=headers)
                all_tables.append((table_names[table_counter], df))
                table_counter += 1

        return all_tables
    else:
        st.error(f"Failed to scrape the page. Status code: {response.status_code}")
        return []

# Function to show the page in Streamlit
def show_page():
    title_html = """
    <h2><a href='https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/Construction.html' 
    target='_blank'>Port Authority Construction Opportunities</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    if st.button("Scrape Port Authority Construction Opportunities"):
        all_tables = fetch_table_port_authority()
        st.session_state["scraped_tables"] = all_tables
        st.success("Scraping completed! Start typing to filter the tables.")

    if "scraped_tables" in st.session_state:
        all_tables = st.session_state["scraped_tables"]

        # Text input for keyword filter (Dynamic filtering)
        filter_keyword = st.text_input("Filter for relevant keywords:", "")

        for table_name, df in all_tables:
            st.markdown(f"### {table_name}")

            # Apply the filter as the user types
            if filter_keyword:
                df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(filter_keyword, case=False).any(), axis=1)]
            else:
                df_filtered = df

            # Custom CSS for table styling
            st.markdown("""
                <style>
                .styled-table {
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    font-family: 'Arial', sans-serif;
                    width: 100%;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }
                .styled-table thead tr {
                    background-color: #009879;
                    color: #ffffff;
                    text-align: left;
                }
                .styled-table th, .styled-table td {
                    padding: 12px 15px;
                }
                .styled-table tbody tr {
                    border-bottom: 1px solid #dddddd;
                }
                .styled-table tbody tr:nth-of-type(even) {
                    background-color: #f3f3f3;
                }
                .styled-table tbody tr:last-of-type {
                    border-bottom: 2px solid #009879;
                }
                .styled-table tbody tr.active-row {
                    font-weight: bold;
                    color: #009879;
                }
                </style>
            """, unsafe_allow_html=True)

            # Display the filtered table dynamically
            table_html = df_filtered.to_html(index=False, escape=False, classes='styled-table')
            st.markdown(table_html, unsafe_allow_html=True)

    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
