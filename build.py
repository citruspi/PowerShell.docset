from bs4 import BeautifulSoup 
import requests
import shutil
import os

INDEX = 'https://technet.microsoft.com/en-us/library/jj821831%28v=sc.20%29.aspx'

if os.path.exists('cmdlet.docset'):
    shutil.rmtree('cmdlet.docset')
os.makedirs('cmdlet.docset/Contents/Resources/Documents/')

page = requests.get(INDEX).content
soup = BeautifulSoup(page)

entries = []

for div in soup.find_all('div'):

    try:
        if div['data-toclevel'] == '2':
            link = div.a.attrs['href'].strip()
            title = div.a.attrs['title']

            destination = open('cmdlet.docset/Contents/Resources/Documents/'+title+'.html', 'w')
            destination.write(requests.get(link).content)
            destination.close()

            entries.append(title)

    except KeyError:
        pass
