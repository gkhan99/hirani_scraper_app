import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set the page layout to wide
st.set_page_config(layout="wide")

# Scraping function for Port Authority Professional Services using requests and BeautifulSoup
def scrape_port_authority_professional_services():
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html'
    
    try:
        # Fetch the page content using requests
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first table in the webpage
        table = soup.find('table')
        if not table:
            st.error("No table found on the page.")
            return None

        # Ensure all links are absolute by converting relative URLs
        for a in table.find_all('a', href=True):
            # Convert relative URLs to absolute URLs
            a['href'] = urljoin(url, a['href'])

        # Extract table headers and rows for DataFrame
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = [
                td.get_text(strip=True) if not td.find('a') else f'<a href="{td.find("a")["href"]}" target="_blank">{td.get_text(strip=True)}</a>'
                for td in tr.find_all('td')
            ]
            rows.append(cells)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the webpage: {e}")
        return None

# Function to show the page in Streamlit
def show_page():
    # Embedded hyperlink in the title
    title_html = """
    <h2><a href='https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html' 
    target='_blank'>Port Authority Professional Services Opportunities</a></h2>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    # Scrape the data when the button is clicked
    if st.button("Scrape Port Authority Professional Services"):
        df = scrape_port_authority_professional_services()
        if df is not None:
            st.session_state["scraped_table"] = df  # Store the scraped table in session state
            st.success("Scraping completed! Now you can filter the table.")

    # Check if data is available in session state
    if "scraped_table" in st.session_state:
        df = st.session_state["scraped_table"]

        # Text input for keyword filter
        filter_keyword = st.text_input("Filter for relevant keywords:", "")

        # Filter the DataFrame based on the keyword input
        if filter_keyword:
            df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(filter_keyword, case=False).any(), axis=1)]
        else:
            df_filtered = df

        # Add CSS to make the table full-width and aligned to the left
        st.markdown("""
            <style>
            .full-width-table {
                width: 100%;
                margin-left: 0;  /* Align the table to the left */
                margin-right: 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display the filtered table in Streamlit with full-width and aligned left
        st.markdown(df_filtered.to_html(escape=False, index=False, classes='full-width-table'), unsafe_allow_html=True)

    # Back to Home button
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'

