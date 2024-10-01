import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import httpx

# Embed the website link in the title
st.markdown(
    """
    <h1 style="text-align: center;">
        <a href="https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html" 
        target="_blank" style="text-decoration:none; color:inherit;">
            Port Authority Professional Services Opportunities
        </a>
    </h1>
    """, 
    unsafe_allow_html=True
)

# Async function using httpx for scraping
async def scrape_port_authority_professional_services():
    url = 'https://panynj.gov/port-authority/en/business-opportunities/solicitations-advertisements/professional-services.html'
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first table in the webpage
            table = soup.find('table')
            if not table:
                st.error("No table found on the page.")
                return None

            # Extract table headers and rows for DataFrame
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr')[1:]:
                cells = [td.get_text(strip=True) if not td.find('a') else f'<a href="{td.find("a")["href"]}" target="_blank">{td.get_text(strip=True)}</a>' for td in tr.find_all('td')]
                rows.append(cells)

            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            return df

    except httpx.RequestError as e:
        st.error(f"Error fetching webpage: {e}")
        return None

# Streamlit Page
async def show_page():
    # Scrape when button is clicked
    if st.button("Scrape Port Authority Professional Services"):
        df = await scrape_port_authority_professional_services()
        if df is not None:
            st.session_state["scraped_table"] = df
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


# Entry point
if __name__ == "__main__":
    show_page()
