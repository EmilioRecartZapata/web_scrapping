import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession

Google_Image = 'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

u_agnt = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}

Image_Folder = 'Images'
CSV_File = 'image_data.csv'

def main():
    if not os.path.exists(Image_Folder):
        os.mkdir(Image_Folder)

    num_categories = int(input("Insert how many categories you want to scrape: "))

    # Create an empty DataFrame
    df = pd.DataFrame(columns=['ID', 'URL', 'Label', 'Source'])

    for category_id in range(1, num_categories + 1):
        label = input(f"What is the category {category_id}: ")
        num_images = int(input(f"How many images for {label}: "))
        num_loops = int(input(f"How many loops for {label}: "))
        
        unique_urls = set()  # To store unique URLs for each category

        for loop in range(num_loops):
            df_temp = download_images(label, num_images, category_id, 'google', unique_urls)
            df = pd.concat([df, df_temp], ignore_index=True)

        # Pexels web scraping
        pexels_df = download_images_pexels(label, num_images, category_id)
        df = pd.concat([df, pexels_df], ignore_index=True)

    # Save the DataFrame as CSV
    df.to_csv(CSV_File, index=False)
    print(f"CSV file '{CSV_File}' created successfully.")

def download_images(label, num_images, category_id, source='google', unique_urls=set()):
    print(f'Searching Images for {label} from {source}....')

    imagelinks = []

    if source == 'google':
        search_url = Google_Image + 'q=' + label
        response = requests.get(search_url, headers=u_agnt)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.findAll('img', {'class': 'rg_i Q4LuWd'})

        for res in results:
            if 'data-src' in res.attrs:
                url = res['data-src']
                if url not in unique_urls:
                    imagelinks.append(url)
                    unique_urls.add(url)

                if len(imagelinks) >= num_images:
                    break

    elif source == 'pexels':
        pexels_search_url = f'https://www.pexels.com/search/{label}/'
        session = HTMLSession()
        response = session.get(pexels_search_url)

        pexels_links = []
        images = response.html.find('img[src^="https://images.pexels.com/photos/"]')
        for image in images:
            url = image.attrs['src']
            if url not in unique_urls:
                pexels_links.append(url)
                unique_urls.add(url)

            if len(pexels_links) >= num_images:
                break

        imagelinks = pexels_links

    # Create a DataFrame with ID, URL, Label, and Source
    df_temp = pd.DataFrame({'ID': [f"{category_id}_{i + 1}" for i in range(len(imagelinks))],
                            'URL': imagelinks,
                            'Label': label,
                            'Source': source})

    print(f'Found {len(imagelinks)} unique images for {label} from {source}')

    return df_temp

def download_images_pexels(label, num_images, category_id):
    print(f'Searching Images for {label} from Pexels....')

    imagelinks = []

    pexels_search_url = f'https://www.pexels.com/search/{label}/'
    session = HTMLSession()
    response = session.get(pexels_search_url)

    pexels_links = []
    images = response.html.find('img[src^="https://images.pexels.com/photos/"]')
    for image in images:
        url = image.attrs['src']
        pexels_links.append(url)

    imagelinks = pexels_links[:num_images]

    # Create a DataFrame with ID, URL, Label, and Source
    df_temp = pd.DataFrame({'ID': [f"{category_id}_{i + 1}" for i in range(len(imagelinks))],
                            'URL': imagelinks,
                            'Label': label,
                            'Source': 'pexels'})

    print(f'Found {len(imagelinks)} unique images for {label} from Pexels')

    return df_temp

if __name__ == '__main__':
    main()
