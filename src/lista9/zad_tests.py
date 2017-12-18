import re
import unittest

import lista9.zad as downloader


class TestDownloader(unittest.TestCase):
    correct_url = 'http://www.ii.uni.wroc.pl/~marcinm'
    www_regex = re.compile('http|www')
    found_urls = ['https://zapisy.ii.uni.wroc.pl/users/profile/employee/35',
                  'http://www.ii.uni.wroc.pl/~marcinm/dyd/ruby/', 'http://www.ii.uni.wroc.pl/~marcinm/dyd/zwinne/',
                  'http://www.uni.wroc.pl/', 'http://www.ii.uni.wroc.pl/',
                  'http://www.ii.uni.wroc.pl/~marcinm/dyd/obiekty', 'http://www.ii.uni.wroc.pl/~marcinm/dyd/rozp',
                  'http://www.ii.uni.wroc.pl/~marcinm/dyd/translatory', 'http://www.ii.uni.wroc.pl/~marcinm/dyd/gnome',
                  'http://www.ii.uni.wroc.pl/~marcinm/dyd/python/']

    def test_should_parse_url_tag_and_do_nothing(self):
        res = downloader.parse_url_tag(self.correct_url, self.correct_url, self.www_regex)
        self.assertEqual(self.correct_url, res)

    def test_should_get_none_on_wrong_url(self):
        res = downloader.parse_url_tag(self.correct_url, 'abrakadabra', self.www_regex)
        self.assertIsNone(res)

    def test_should_find_urls(self):
        res = downloader.find_urls(self.correct_url)
        self.assertEquals(self.found_urls, res)


if __name__ == "__main__":
    unittest.main()
