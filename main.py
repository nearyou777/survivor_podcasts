import os
import requests
import tls_client
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep

def get_links():
    s = tls_client.Session(client_identifier='chrome_105')
    r = s.get('https://robhasawebsite.com/shows/survivor-podcast-rhap/')
    seasons_links = []
    soup = BeautifulSoup(r.text, 'lxml')
    for item in soup.find('ul', class_='block-grid-xs-2 block-grid-sm-3 block-grid-md-3').find_all('li'):
        seasons_links.append(item.find('a').get('href'))

    links = []
    for url in seasons_links:
        s = tls_client.Session(client_identifier='chrome_105')
        r = s.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        print(r)
        try:
            page_count = soup.find('ul', class_='pagination').find_all('li')[-1].find('a').get('href').split('/')[-2]

        except:
            page_count = None 
        directory = soup.find('h1', class_='category-title').text.strip().replace('.', '').replace(':', '')
        parent_dir = "D:\work\podcasts"
        path = os.path.join(parent_dir, directory) 
        try:
            os.mkdir(path)
        except:
            pass
        if page_count:
            for page in range(1, int(page_count) + 1):
                r = s.get(f'{url}page/{page}/')
                print(f'{url}page/{page}/')
                soup = BeautifulSoup(r.text, 'lxml')
                
                for item in soup.find_all('article'):
                    links.append([directory,item.find('a').get('href')])
        else:
            r = s.get(f'{url}')
            print(f'{url}')
            soup = BeautifulSoup(r.text, 'lxml')
                
            for item in soup.find_all('article'):
                links.append([directory, item.find('a').get('href')])
    return links
def get_data(links:list):
    s = tls_client.Session(client_identifier='chrome_105')
    for url in links: 
        try:
            r = s.get(url[-1])
        except:
            sleep(10)
            try:
                r = s.get(url[-1])
            except:
                print(f'zalupaaa-----{url[-1]}')
                continue
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            mp3 = f"{soup.find('div', class_='audio-download audio-track download').find('a').get('href')}"
        except:
            print(url[-1])
            continue
        if 'https:' not in mp3:
            mp3 = f"https:{soup.find('div', class_='audio-download audio-track download').find('a').get('href')}"
        directory = url[0]
        file_name = soup.find('h1').text.strip().replace(':', '').replace('?', '').replace('\\', '').replace('/', '').replace('*', '').replace('"', '').replace('|', '-')
        parent_dir = "D:\work\podcasts"
        path = os.path.join(parent_dir, directory) 
        if os.path.exists(f"{path}/{file_name}.mp3"):
            print('skipped')
            continue
        try:
            r = requests.get(mp3)
        except:
            print(mp3)
        if os.path.exists(f"{path}/{file_name}.mp3"):
            print('skipped')
            continue
        with open(f"{path}/{file_name}.mp3", 'wb') as f:
            f.write(r.content)
        print('saved')


def main():
    links = get_links()
    num_threads = 8
    batch_size = len(links) // num_threads
    threads = []
    for i in range(num_threads):
        start = i * batch_size
        end = start + batch_size if i < num_threads - 1 else len(links)
        t = Thread(target=get_data, args=(links[start:end], ))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()