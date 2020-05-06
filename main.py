import requests
from lxml import html
import os
import time

try:os.mkdir('spotted')
except: pass


def open_connetion(link):
    try:
        r = requests.get(link)
        return r
    except IndexError:
        print(link, '- this link has been blocked.')
        print('Waiting 5 seconds...')
        time.sleep(5)
        return open_connetion(link)


def clean_dirname(dirname):
    for symbol in [
            "/", "\\", ":", ":", "*", "<", ">", "|", '"', ",", "?", '=', '\t',
            '\n'
    ]:
        dirname = dirname.replace(symbol, '')
    return str(dirname[:50]).rstrip()


def get_stuff(_r):
    list = []
    tree = html.fromstring(_r.content)
    titles = tree.xpath("//header[1]/h2[1]/a[1]")
    time = tree.xpath("//li/time[1]")
    print(len(titles))

    for number, title in enumerate(titles):
        time_ = clean_dirname(time[number].text_content())
        title_ = clean_dirname(title.text_content())
        href_ = title.get("href")

        list.append([title_, href_, time_])

    return list


def create_folders(list_):
    _folder_paths = []
    _folder_paths_good = []

    for line in list_:
        date = str(line[2][3:]).split(" ")
        date = '{} {} {} {}'.format(date[3], date[2], date[1], date[0])
        folder_path = 'spotted\\{}'.format(date)
        _folder_paths.append([line[0], line[1], folder_path])
        _folder_paths_good.append(
            [line[0], line[1], (folder_path + '\\' + line[0])])

    return _folder_paths_good, _folder_paths


def get_photos_and_text(_r):
    _linki_url_zdjecia = []
    tree = html.fromstring(_r.content)
    text = tree.xpath("//div[@class='itemIntroText']/p[1]")
    text2 = tree.xpath("//div[@class='itemFullText']/p[1]")
    try:
        calosc = str(text[0].text_content() + text2[0].text_content())
    except:
        calosc = 'Brak'

    for i in range(1, 1000):
        photo = tree.xpath("//img[{}]".format(str(i)))
        try:
            photo[0].get('src')
        except:
            break
        for link in photo:
            if '/images/photos/' in link.get("src"):
                _linki_url_zdjecia.append('https://www.spottedskarzysko.pl' +
                                          link.get("src"))

    return calosc, _linki_url_zdjecia


def save_main(paths, paths_bad):
    for number, line in enumerate(paths):
        try:
            os.mkdir(paths_bad[number][2])
        except:
            pass
        try:
            os.mkdir(line[2])
        except:
            continue

        url = 'https://www.spottedskarzysko.pl{}'.format(line[1])
        print(url)
        _r = open_connetion(url)
        text, linki_url_zdjecia = get_photos_and_text(_r)
        save_text(text, line[2])

        for number, link in enumerate(linki_url_zdjecia):
            time.sleep(1)
            _r = open_connetion(link)
            path = line[2] + '\\zdjecie{}.jpg'.format(number)
            print(path)
            save_photos(_r.content, path)


def save_photos(bytes, path):
    with open(path, 'wb') as file:
        file.write(bytes)
        file.close()


def save_text(text, path):
    with open(path + '\\text.txt', 'w+', encoding='utf-8') as file:
        file.write(text)
        file.close()


def get_how_many_sites():
    _r = open_connetion('https://www.spottedskarzysko.pl/fakty.html?start=0')
    tree = html.fromstring(_r.content)
    howmany = tree.xpath(
        "//li[@class='pagination-end']/a[@class='pagenav' and 1]")[0].get(
            'href')
    howmany = str(howmany).split('=')[-1]
    return int(howmany)


def main():
    howmany = get_how_many_sites()
    for i in range(0, howmany + 1, 30):
        url = 'https://www.spottedskarzysko.pl/fakty.html?start={}'.format(
            str(i))
        print(url, i / 30, ' z ', (howmany) / 30)
        r = open_connetion(url)
        lista = get_stuff(r)
        lista_good, lista_bad = create_folders(lista)
        save_main(lista_good, lista_bad)


if __name__ == '__main__':
    main()
