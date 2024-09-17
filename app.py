from flask import Flask, render_template_string
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# URL of the webpage containing the table
url = 'https://gta.fandom.com/wiki/Gun_Van'

# List of special weapons to search for
special_weapons = ['Up-n-Atomizer', 'Unholy Hellbringer', 'Widowmaker']

# Function to extract the table and special weapon names from the webpage
def extract_table_and_weapons():
    # Define the headers, including a user-agent string
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the section with the headline 'Current week'
        current_week_section = soup.find('span', id='Current_week')

        if current_week_section:
            # Search for special weapon names between the "Current week" text and the table
            special_weapons_found = []
            next_element = current_week_section.find_next()
            while next_element and next_element.name != 'table':
                text = next_element.get_text(strip=True)
                for weapon in special_weapons:
                    if weapon in text:
                        special_weapons_found.append(weapon)
                next_element = next_element.find_next()

            # Find the next table following the 'Current week' section
            table = current_week_section.find_next('table')

            # If a table is found, read it into a pandas DataFrame
            if table:
                # Use pandas to read the HTML table
                df = pd.read_html(str(table))[0]

                # Remove rows with NaN values
                df_cleaned = df.dropna()

                return df_cleaned, special_weapons_found
            else:
                return None, special_weapons_found
        else:
            return None, []
    else:
        return None, []

# Flask route to display the table and special weapons
@app.route('/')
def display_table():
    # Extract the table data and special weapons
    df, special_weapons_found = extract_table_and_weapons()

    if df is not None:
        # Convert the DataFrame to HTML
        table_html = df.to_html(classes='table table-bordered', index=False)
        
        # Create a list of special weapons found
        weapons_html = '<ul>'
        for weapon in special_weapons_found:
            weapons_html += f'<li>{weapon}</li>'
        weapons_html += '</ul>' if special_weapons_found else '<p>No special weapons found</p>'

        # Template to render the HTML
        template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Current Week Data</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container">
                <h1 class="mt-5">Current Week Gun Van Data</h1>
                <h2>Special Weapons Found</h2>
                {{ weapons_html|safe }}
                <div class="table-responsive">
                    {{ table_html|safe }}
                </div>
            </div>
        </body>
        </html>
        '''
        
        return render_template_string(template, table_html=table_html, weapons_html=weapons_html)
    else:
        return "<h1>Error: Failed to retrieve data or no table found</h1>"

if __name__ == '__main__':
    app.run(debug=True)
