import urllib2
from bs4 import BeautifulSoup

filepath = 'states.txt'
fo = open("cities.txt", "w")
with open(filepath) as fp:
    for line in fp:
        line = line.strip()
        state, url = line.split("|")
        url = "https://geo.craigslist.org/iso/us/in"
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        try:
            cities = [li.find('a') for li in soup.find('ul', attrs={"class":"geo-site-list"}).find_all('li')]
        except Exception:
            print url
            pass
        if cities:
            for city in cities:
                if city is not None:
                    try:
                        fo.write("N|{}|{}|{}\n".format(state.encode('utf-8'),
                                                  city.string.encode('utf-8'),
                                                  city['href']))
                    except Exception:
                        pass
fo.close()
