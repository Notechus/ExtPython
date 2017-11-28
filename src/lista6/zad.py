import re
from bs4 import BeautifulSoup
import concurrent.futures
import requests


def parse_url_tag(base_url, href, reg_exp):
    if href is None:
        pass
    if href.strip('#') and href != '\\' and href != '/':
        if not base_url.endswith('/'):
            base_url = base_url + '/'
        res_url = href if reg_exp.match(href) else base_url + href
        res_url = res_url.split('#')[0]
        try:
            if requests.head(res_url).status_code < 400:
                return res_url
        except:
            print('Invalid url: ' + res_url)


def find_urls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    page_a = soup.find_all('a', href=True)
    reg_exp = re.compile('http|www')
    urls = []
    for a in page_a:
        link = parse_url_tag(url, a['href'], reg_exp)
        if link is not None:
            urls.append(link)

    return urls


def find_urls_in_steps(base, depth=0):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)
    url_registry = [base]
    results = [base]
    futures = []
    for i in range(depth + 1):
        print('Searching depth ' + str(i))
        for url in url_registry:
            print('Searching urls for: ' + url)
            futures.append(executor.submit(find_urls, url))

        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            print('Found ' + str(len(res)) + ' urls')
            results += res
    print('Found total ' + str(len(results)) + ' urls')
    return results


def return_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.text


def find_on_page(url, reg_exp):
    page = return_text_from_url(url)

    found_results = reg_exp.findall(page)

    result = {url: found_results}

    return result


def sort_results(results):
    print('Sorting results')
    for k, v in results.items():
        results[k] = sorted(v.items(), key=lambda x: x[1], reverse=True)
    return results


def search_engine(base_url, words_str, steps):
    words = words_str.split(' ')
    words_exp = re.compile('|'.join(words), re.IGNORECASE)
    results = {x.lower(): {} for x in words}
    print('Searching urls')
    url_reg = find_urls_in_steps(base_url, steps)
    print('Searching for results on ' + str(len(url_reg)) + ' pages')

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        futures = {executor.submit(find_on_page, item, words_exp): item for item in url_reg}
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
            except Exception as exc:
                print('generated an exception: %s' % exc)
            else:
                print(res)

    print(sort_results(results))


ur = 'http://www.ii.uni.wroc.pl/~marcinm'
wor = 'Python Ruby sqrt'
search_engine(ur, wor, 0)
