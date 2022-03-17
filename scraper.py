import string
import requests
from bs4 import BeautifulSoup
import os
import shutil

# need to add page number when requesting
URL = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page="
BASE_URL = "https://www.nature.com"


def remove_directories():
    all_dir = os.listdir()
    dir_keyword = 'Page_'

    for num, directory in enumerate(all_dir):
        dir_path = dir_keyword+ str(num)
        if dir_path in all_dir:
            try:
                shutil.rmtree(dir_path)
            except OSError as e:
                print(e)


def save_articles(total_pages, article_category):
    article_list = []
    remove_directories()

    for page_num in range(total_pages):
        new_dir_name = f'Page_{page_num+1}'
        os.mkdir(new_dir_name)
        response = requests.get(URL + str(page_num+1))
        if response.status_code == 200:
            soup1 = BeautifulSoup(response.content, 'html.parser')
            all_articles = soup1.find_all('article')

            article_count = 1
            for article in all_articles:
                category = article.find('span', {'data-test': 'article.type'}).text.strip()

                if category == article_category:
                    article_link = article.find('a', {'data-track-action': 'view article'})
                    article_title = article_link.text.translate(str.maketrans('', '', string.punctuation))
                    clean_title = "_".join(article_title.split())
                    article_list.append(f"{clean_title}.txt")
                    article_response = requests.get(BASE_URL + article_link.get('href'))

                    if article_response.status_code == 200:
                        soup2 = BeautifulSoup(article_response.content, 'html.parser')
                        article_text = soup2.find_all('div', {'class': 'c-article-body u-clearfix'})

                        if len(article_text) != 0:

                            for para in article_text:
                                with open(f'./{new_dir_name}/{clean_title}.txt', 'wb') as file:
                                    file.write(bytes(para.text.strip(), encoding='UTF-8'))
                                    print(f'> Saved Article From Page: {page_num+1} | Title: {article_title}')
                                    article_count += 1
                        
                        else:
                            print(f'> Content Unavailable | Page: {page_num+1} | Title: {article_title} ')


                    else:
                        print('Error Retrieving Article!')

        else:
            print(f"\nThe URL returned {response.status_code}!")
            article_list = None

    return article_list


def main():

    num_pages = int(input("Num of Pages: "))
    article_category = input("Search Category: ")
    print('Connecting...')
    saved_article_list = save_articles(num_pages, article_category)

    if len(saved_article_list) == 0:
        print(f'No articles found from category: {article_category}')
    else:
        print('> Total Articles Found: ', len(saved_article_list))


if __name__ == "__main__":
    main()
