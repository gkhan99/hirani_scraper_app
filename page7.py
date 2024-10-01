import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import httpx

# Retrieve the ScraperAPI Key from Streamlit secrets
API_KEY = st.secrets["SCRAPER_API_KEY"]

# Scraping function using ScraperAPI for PASSPort Construction Opportunities
def fetch_passport_data_scraperapi(max_pages=6):
    url = 'https://passport.cityofnewyork.us/page.aspx/en/rfp/request_browse_public'
    api_url = f'http://api.scraperapi.com?api_key={API_KEY}&url={url}&render=true'

    all_data = []
    titles = None

    page_number = 1
    while page_number <= max_pages:
        response = httpx.get(api_url)
        if response.status_code != 200:
            st.error(f"Failed to fetch page {page_number}.")
            break
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        page_titles, page_data = parse_table(soup)

        if page_data:
            if not titles:
                titles = page_titles
            all_data.extend(page_data)
            page_number += 1
        else:
            break

    # Convert data to a pandas DataFrame
    if titles and all_data:
        df = pd.DataFrame(all_data, columns=titles)
        return df
    return None

# HTML parser function using BeautifulSoup
def parse_table(soup):
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
                # Extract the onclick link from 'Procurement Name' and embed it as a clickable link
                if i == 3 and 'onclick' in str(td):
                    link = td.find('button')['onclick'].split("'")[1]
                    full_link = f"https://passport.cityofnewyork.us{link}"
                    # Embed the link in the Procurement Name text as a clickable link
                    row_data.append(f'<a href="{full_link}" target="_blank">{td.text.strip()}</a>')
                else:
                    row_data.append(td.text.strip().replace('Edit', '').strip())
            page_data.append(row_data)
        return titles, page_data
    else:
        return None, None

# Function to show the page in Streamlit
def show_page():
    # Embed the website link in the title
    st.markdown(
        """
        <h1 style="text-align: center;">
            <a href="https://passport.cityofnewyork.us/page.aspx/en/rfp/request_browse_public" target="_blank" style="text-decoration:none; color:inherit;">
                PASSPort Construction Opportunities
            </a>
        </h1>
        """, 
        unsafe_allow_html=True
    )

    # Initialize session state for persistent data
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None

    # Button to trigger scraping
    if st.button("Scrape NYC PASSPort"):
        st.session_state.scraped_data = fetch_passport_data_scraperapi()
        if st.session_state.scraped_data is not None:
            st.success("Data scraped successfully!")

    # If data is scraped, display filters and the table
    if st.session_state.scraped_data is not None:
        # Remove unwanted columns
        columns_to_drop = ["EPIN", "Release Date (Your Local Time)", "Remaining time", "Main Commodity"]
        filtered_data = st.session_state.scraped_data.drop(columns=columns_to_drop, errors='ignore')
        
        # Filter by 'RFx Status' containing 'Released'
        if 'RFx Status' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['RFx Status'].str.contains('Released', case=False)]
        
        # Filter to keep only specified industries
        industries_to_keep = [
            'Construction', 
            'Professional Services', 
            'Professional Services - Construction Related', 
            'Professional Services - Architecture/Engineering', 
            'Standard Services', 
            'Standard Services - Construction Related'
        ]
        
        if 'Industry' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Industry'].isin(industries_to_keep)]
        
        # Industry dropdown filter
        selected_industry = st.selectbox(
            "Filter by Industry",
            options=["All"] + industries_to_keep,
            index=0
        )

        # Keyword text filter
        keyword_filter = st.text_input("Search by Keyword", "")

        # Apply Industry filter if selected
        if selected_industry != "All" and 'Industry' in filtered_data:
            filtered_data = filtered_data[filtered_data['Industry'] == selected_industry]
        
        # Apply keyword search filter (case-insensitive)
        if keyword_filter:
            filtered_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.contains(keyword_filter, case=False).any(), axis=1)]
        
        # Add serial numbers after filtering to avoid gaps
        filtered_data.insert(0, 'Serial Number', range(1, len(filtered_data) + 1))
        
        # Add CSS to style the table
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

        # Display the dataframe in wide mode, with serial numbers and clickable links
        st.markdown(filtered_data.to_html(escape=False, index=False, classes='full-width-table'), unsafe_allow_html=True)

        # Add "Back to Home" button
        if st.button("Back to Home"):
            st.session_state['page'] = 'main'
    else:
        st.write("Click the button to scrape data.")
