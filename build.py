from bs4 import BeautifulSoup 
import requests
import shutil
import os
import sqlite3

indexes = [
    # System Center Automation - App Controller
    'https://technet.microsoft.com/en-us/library/jj899760(v=sc.20).aspx',
    # System Center Automation - Configuration Manager
    'https://technet.microsoft.com/en-us/library/jj821831%28v=sc.20%29.aspx',
    # System Center Automation - Configuration Manager (Support Center)
    'https://technet.microsoft.com/en-us/library/dn688184(v=sc.20).aspx',
    # System Center Automation - Data Protection Manager
    'https://technet.microsoft.com/en-us/library/hh881679(v=sc.20).aspx'
    # System Center Automation - Microsoft Monitoring Agent
    'https://technet.microsoft.com/en-us/library/dn472748(v=sc.20).aspx',
    # System Center Automation - Operations Manager
    'https://technet.microsoft.com/en-us/library/hh920227(v=sc.20).aspx',
    # System Center Automation - Operations Manager (Linux and UNIX)
    'https://technet.microsoft.com/en-us/library/hh545209(v=sc.20).aspx',
    # System Center Automation - Operations Manager (System Center Advisor Connector)
    'https://technet.microsoft.com/en-us/library/dn720227(v=sc.20).aspx',
    # System Center Automation - Service Management Automation
    'https://technet.microsoft.com/en-us/library/dn502585(v=sc.20).aspx',
    # System Center Automation - Service Manager
    'https://technet.microsoft.com/en-us/library/hh305227(v=sc.20).aspx',
    # System Center Automation - Service Manager (Data Warehouse)
    'https://technet.microsoft.com/en-us/library/hh541724(v=sc.20).aspx',
    # System Center Automation - Service Provider Automation
    'https://technet.microsoft.com/en-us/library/jj612525(v=sc.20).aspx',
    # System Center Automation - Virtual Machine Manager
    'https://technet.microsoft.com/en-us/library/jj654428(v=sc.20).aspx'
]

if os.path.exists('cmdlet.docset'):
    shutil.rmtree('cmdlet.docset')
os.makedirs('cmdlet.docset/Contents/Resources/Documents/')

db = sqlite3.connect('cmdlet.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()
try: cur.execute('DROP TABLE searchIndex;')
except: pass

cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

entries = []

for index in indexes:

    page = requests.get(index).content
    soup = BeautifulSoup(page)

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

for entry in entries:
    insert = (entry, 'Command', entry+'.html')
    cur.execute('insert into searchIndex(name, type, path) values (?,?,?)', insert)

db.commit()

infoplist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>cmdlet</string>
    <key>CFBundleName</key>
    <string>CMDlet</string>
    <key>DocSetPlatformFamily</key>
    <string>cmdlet</string>
    <key>isDashDocset</key>
    <true/>
</dict>
</plist>"""

with open('cmdlet.docset/Contents/Info.plist', 'w') as f:
    f.write(infoplist)

for entry in entries:

    source = open('cmdlet.docset/Contents/Resources/Documents/'+entry+'.html', 'r+')

    soup = BeautifulSoup(source.read())

    try:
        soup.find(id='megabladeContainer').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='ux-header').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='isd_print').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='isd_printABook').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='expandCollapseAll').decompose()
    except AttributeError:
        pass

    try:
        soup.find(id='leftNav').decompose()
    except AttributeError:
        pass

    try:
        soup.find_all('div', class_='feedbackContainer')[0].decompose()
    except AttributeError:
        pass
    except IndexError:
        pass

    try:
        soup.find(id='ux-footer').decompose()
    except AttributeError:
        pass

    for link in soup.find_all('a'):
        if link.get_text() in entries:
            link.attrs['href'] = link.get_text()+'.html'

    source.seek(0)
    source.write(str(soup))
    source.truncate()
    source.close()

