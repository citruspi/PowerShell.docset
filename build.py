from bs4 import BeautifulSoup 
import requests

INDEX = 'https://technet.microsoft.com/en-us/library/jj821831%28v=sc.20%29.aspx'

page = requests.get(INDEX).content
soup = BeautifulSoup(page)

entries = []

for div in soup.find_all('div'):

    try:
        if div['data-toclevel'] == '2':
            link = div.a.attrs['href'].strip()
            title = div.a.attrs['title']

            destination = open('build/'+title+'.html', 'w')
            destination.write(requests.get(link).content)
            destination.close()

            entries.append(title)

    except KeyError:
        pass
