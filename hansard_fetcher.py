# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:20:50 2015

@author: andy
"""

import urllib2
import bs4
import re
import pandas as pd 
import dateutil
import os

DEBATES_LINKS = 'http://www.theyworkforyou.com/pwdata/scrapedxml/debates'

def fetch_debates_filenames():
    html = urllib2.urlopen(DEBATES_LINKS).read()
    
    filename_re = re.compile('(?<!")debates\d\d\d\d-\d\d-\d\d[a-z]?.xml(?!")')
    filenames = filename_re.findall(html)
    
    return filenames

def extract_dates(filenames):
    results = pd.DataFrame(columns=['date', 'part', 'filename'], index=range(len(filenames)))
    date_re = re.compile('\d\d\d\d-\d\d-\d\d')
    part_re = re.compile('[a-z](?=.xml)')
    for i, filename in enumerate(filenames):
        date_string = date_re.findall(filename)[0]
        date = dateutil.parser.parse(date_string)        
        
        optional_part = part_re.findall(filename)
        part = optional_part[0] if optional_part else None       
        
        results.loc[i] = [date, part, filename]
    
    new_index = pd.to_datetime(results['date'])
    results.index = new_index
    
    return results.sort_index()
    
def get_debate_xmls(filenames):
    urls = [DEBATES_LINKS + '/' + filename for filename in filenames]
    
    results = []
    for url in urls:
        print('Fetching {0}'.format(url))
        result = urllib2.urlopen(url).read()
        results.append(result)
        
    return results
    
def get_debate_xml_since(datestring, dated_filenames):
    filenames = dated_filenames.loc[datestring:, 'filename']
    xmls = get_debate_xmls(filenames)
    
    return xmls
    
def extract_speeches(xml):
    soup = bs4.BeautifulSoup(xml, 'lxml')
    speeches = soup.find_all(name='speech')
    
    results = pd.DataFrame(columns=['speech_id', 'speaker_id', 'name', 'time', 'strings'], dtype='object', index=range(len(speeches)))
    for i, speech in enumerate(speeches):
        speech_id = speech.get('id', '')
        speaker_id = speech.get('speakerid', '')
        name = speech.get('speakername', '')
        time = speech.get('time', '')
        strings = list(speech.stripped_strings)
        
        results.loc[i] = [speech_id, speaker_id, name, time, None]
        results.loc[i, 'strings'] = strings
        
    return results

def extract_speeches_multiple(xmls):
    speeches_list = [extract_speeches(xml) for xml in xmls]
    speeches = pd.concat(speeches_list)
    speeches.index = range(speeches.shape[0])
    
    return speeches


#filenames = fetch_debates_filenames()
#dated_filenames = extract_dates(filenames)
#xmls = get_debate_xml_since('2015-3-20', dated_filenames)