import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

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
    df = pd.DataFrame(columns=['ID', 'URL', 'Label'])

    for category_id in range(1, num_categories + 1):
        label = input(f"What is the category {category_id}: ")
        num_images = int(input(f"How many images for {label}: "))
        df = pd.concat([df, download_images(label, num_images, category_id)], ignore_index=True)

    # Save the DataFrame as CSV
    df.to_csv(CSV_File, index=False)
    print(f"CSV file '{CSV_File}' created successfully.")

def download_images(label, num_images, category_id):
    print(f'Searching Images for {label}....')

    search_url = Google_Image + 'q=' + label

    response = requests.get(search_url, headers=u_agnt)
    html = response.text

    b_soup = BeautifulSoup(html, 'html.parser')
    results = b_soup.findAll('img', {'class': 'rg_i Q4LuWd'})

    count = 0
    imagelinks = []
    for res in results:
        try:
            link = res['data-src']
            imagelinks.append(link)
            count = count + 1
            if count >= num_images:
                break
        except KeyError:
            continue

    # Create a DataFrame with ID, URL, and Label
    df_temp = pd.DataFrame({'ID': [f"{category_id}_{i+1}" for i in range(len(imagelinks))],
                            'URL': imagelinks,
                            'Label': label})

    print(f'Found {len(imagelinks)} images for {label}')

    return df_temp

if __name__ == '__main__':
    main()
