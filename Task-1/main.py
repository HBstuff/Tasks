from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import json

# image folder location
image_folder_location = 'C:/Users/henri/OneDrive/Desktop/Images/'

my_url = 'https://mekass.wixsite.com/website'
more_pages_available = True
page_list = []  # stores pages urls
image_links = []  # stores image urls
image_number = 0

# json nesting
tag_list = []  # nests tags
section_list = []  # nest sections
group_list = []  # nest groups (header, main, footer)
pages = []  # nest into pages


def save_image():
    global image_number
    imgs = section.findAll('img')
    if imgs:
        for img in imgs:
            if img.get('src'):
                image_src = img.get('src').split('/v1/')[0]
                if image_src not in image_links:
                    image_number += 1
                    image_location = image_folder_location + 'image' + str(image_number) + '.jpeg'
                    image_links.append(image_src)
                    with open(image_location, 'wb') as image_file:
                        image_file.write(uReq(image_src).read())


# finds all h and/or p tags and nests them
def get_text():
    global section_list
    tags = section.findAll(['h1', 'h2', 'h3', 'p'])
    for tag in tags:
        if tag.getText():
            section_list.append({tag.name: tag.getText()})
    tag_list.append({'section': section_list})
    section_list = []


# main program
while more_pages_available:
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    name_of_page = page_soup.find('title').getText().split(' |')[0]
    new_soup = page_soup.find('div', {'class': 'SITE_ROOT'})
    body = new_soup.findAll(['header', 'main', 'footer'])
    for group in body:
        if group.findAll('section'):
            parent = group.find('section').find_parent('div')
            all_sections = parent.findAll('section', recursive=False)
            for section in all_sections:
                if section.getText():
                    # find images and save them / find h/p tags and nest them into section;
                    save_image()
                    get_text()
        else:
            # find images and save them / find h/p tags and nest them into sections;
            section = group
            save_image()
            get_text()

        # nest sections into groups
        group_list.append({group.name: tag_list})
        tag_list = []

    # nest groups into pages
    pages.append({name_of_page: group_list})
    group_list = []

    # goes to next page
    nav_links = new_soup.find('nav').findAll('a')
    for link in nav_links:
        if link.get('href'):
            page_list.append(link.get('href'))
    if my_url == page_list[-1]:
        more_pages_available = False
    else:
        my_url = page_list[page_list.index(my_url) + 1]

# write JSON
with open('information.json', 'w') as f:
    json.dump({'webpage': pages}, f, indent=2)
