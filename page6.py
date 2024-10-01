import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tempfile
import webbrowser

# Retrieve the ScraperAPI Key from Streamlit secrets
API_KEY = st.secrets["SCRAPER_API_KEY"]

# Async scraping function for Port Authority Professional Services
async def scrape_port_authority_professional_services():
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html'
    
    # Use ScraperAPI to get the fully rendered HTML of the page
    api_url = f'http://api.scraperapi.com?api_key={API_KEY}&url={url}&render=true'
    
    try:
        async with requests.AsyncClient() as client:
            response = await client.get(api_url)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the first table in the webpage
            table = soup.find('table')
            if not table:
                st.error("No table found on the page.")
                return None

            # Ensure all links are absolute by converting relative URLs
            for a in table.find_all('a', href=True):
                a['href'] = urljoin(url, a['href'])

            # Extract table headers and rows for DataFrame
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr')[1:]:
                cells = [
                    td.get_text(strip=True) if not td.find('a') 
                    else f'<a href="{td.find("a")["href"]}" target="_blank">{td.get_text(strip=True)}</a>'
                    for td in tr.find_all('td')
                ]
                rows.append(cells)

            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            return df
        else:
            st.error(f"Failed to scrape the page. Status code: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"An error occurred: {e}")
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
        df = st.experimental_asyncio.run(scrape_port_authority_professional_services())
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

        # Add CSS to make the table full-width and styled
        st.markdown("""
            <style>
            .full-width-table {
                width: 100%;
                margin-left: 0;
                margin-right: 0;
                border-collapse: collapse;
            }
            .full-width-table th, .full-width-table td {
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }
            .full-width-table th {
                background-color: #4CAF50;
                color: white;
            }
            .full-width-table tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .full-width-table tr:hover {
                background-color: #ddd;
            }
            a {
                color: #4CAF50;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display the filtered table in Streamlit with full-width and aligned left
        st.markdown(df_filtered.to_html(escape=False, index=False, classes='full-width-table'), unsafe_allow_html=True)

    # Back to Home button
    if st.button("Back to Home"):
        st.session_state['page'] = 'main'
