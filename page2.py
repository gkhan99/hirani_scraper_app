import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_nys_general_services():
    url = 'https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/esbConsultantOpsIndex.asp'
    base_url = 'https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/'

    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the webpage: {e}")
        return

    def extract_table_data(table, title, base_url):
        if table is None:
            return pd.DataFrame([["No data found"]], columns=[title])
        
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
                        row_data[0] = f'<a href="{link_url}" target="_blank">{row_data[0]}</a>'  # Make the first column clickable
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

    # Display tables in Streamlit
    if tables:
        for table_name, df in tables:
            st.markdown(f"### {table_name}")
            if not df.empty:
                # Convert the DataFrame to HTML with escape=False to allow rendering of clickable links
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)  # Render as raw HTML
            else:
                st.write("No data available.")

# Function to show the page
def show_page():
    # Embedded hyperlink in the title
    title_html = """
    <h2><a href='https://online2.ogs.ny.gov/dnc/contractorConsultant/esb/esbConsultantOpsIndex.asp' 
    target='_blank'>NYS General Services</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    if st.button("Scrape NYS General Services"):
        scrape_nys_general_services()
    
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
