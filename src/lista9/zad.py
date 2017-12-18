import re
from bs4 import BeautifulSoup
import concurrent.futures
import requests


def parse_url_tag(base_url, href, reg_exp):
    """
    This function parses value of href element in HTML a tag.
    Takes into consideration relative paths.
    @:param base_url base url of the page we browsed for links
    @:param href href content
    @:param reg_exp regex expression to match with beginning of url (http or www)
    @:returns parsed url
    """
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
    """
    Function to find urls in a page. Searches for a tags and retrieves href elements from them
    @:param url page to be traversed
    @:returns list of urls in given page
    """
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
    """
    Function will return url registry from all links from pages in given depth.
    eg. for page A and depth 2 it will return all links from A and all links of it's links
    @:param base base url to traverse
    @:depth given depth
    @:returns list of all urls in given depth
    """
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)
    url_registry = [base]
    results = set([base])
    futures = []
    for i in range(depth + 1):
        print('Searching depth ' + str(i))
        for url in url_registry:
            print('Searching urls for: ' + url)
            futures.append(executor.submit(find_urls, url))

        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            print('Found ' + str(len(res)) + ' urls')
            url_registry = []
            for url in res:
                results.add(url)
                if url not in url_registry:
                    url_registry.append(url)
    print('Found total ' + str(len(results)) + ' urls')
    return results


def return_text_from_url(url):
    """
    Return text content of given url
    @:param url url to process
    @:returns text content of page
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.text


def find_on_page(url, reg_exp):
    """
    Find on given page everything what matches given regular expression
    @:param url url to search
    @:param reg_exp regular expression to match
    @:returns result as a pair (url, list of results from url)
    """
    page = return_text_from_url(url)
    found_results = reg_exp.findall(page)
    result = (url, found_results)

    return result


def sort_results(results):
    """
    Sorts and returns dictionary in descending order
    @:param results dictionary to be sorted
    @:returns sorted dictionary
    """
    print('Sorting results')
    for k, v in results.items():
        results[k] = sorted(v.items(), key=lambda x: x[1], reverse=True)
    return results


def add_result(res, results):
    """
    Adds search result to result dictionary
    @:param res found result
    @:param results result collection
    """
    url = res[0]
    for item in res[1]:
        results[item.lower()][url] = results[item.lower()].get(url, 0) + 1


def search_engine(base_url, words_str, steps):
    """
    Function which will search and output amount of found words in all pages which are linked from base page
    @:param base_url starting page
    @:param words_str string containing words to search
    @:param steps depth of searching
    """
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
                add_result(res, results)
            except Exception as exc:
                print('generated an exception: %s' % exc)

    print(sort_results(results))


if __name__ == "__main__":
    ur = 'http://www.ii.uni.wroc.pl/~marcinm'
    wor = 'Python Ruby sqrt'
    search_engine(ur, wor, 0)
