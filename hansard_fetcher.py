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
import itertools as it 

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
    for i, url in enumerate(urls):
        print('Fetching {0} of {1}, {2}'.format(i, len(urls), url))
        result = urllib2.urlopen(url).read()
        results.append(result)
        
    return results
    
def get_debate_xml_since(datestring, dated_filenames):
    """Dates should be in yyyy-m-d format"""
    filenames = dated_filenames.loc[datestring:, 'filename']
    xmls = get_debate_xmls(filenames)
    
    return xmls
    
def clean_up_id(sid):
    return sid.split('/')[-1]
    
def extract_speeches(xml):
    soup = bs4.BeautifulSoup(xml, 'lxml')
    speeches = soup.find_all(name='speech')
    
    results = pd.DataFrame(columns=['speech_id', 'speaker_id', 'name', 'time', 'strings'], dtype='object', index=range(len(speeches)))
    for i, speech in enumerate(speeches):
        speech_id = clean_up_id(speech.get('id', ''))
        speaker_id = clean_up_id(speech.get('speakerid', ''))
        name = speech.get('speakername', '')
        time = speech.get('time', '')
        strings = list(speech.stripped_strings)
        
        results.loc[i] = [speech_id, speaker_id, name, time, None]
        results.loc[i, 'strings'] = strings
        
    return results

def load_test_speeches():
    return pd.read_json('temporary/speeches_since_2015-01-05.json')

def extract_speeches_multiple(xmls):
    speeches_list = [extract_speeches(xml) for xml in xmls]
    speeches = pd.concat(speeches_list)
    speeches.index = range(speeches.shape[0])
    
    return speeches

def save_speeches_since(datestring):
    filenames = fetch_debates_filenames()
    dated_filenames = extract_dates(filenames)
    xmls = get_debate_xml_since(datestring, dated_filenames)
    speeches = extract_speeches_multiple(xmls)
    
    speeches.to_json('temporary/speeches_since_{0}.json'.format(datestring))

def index_by_speaker(speeches):
    return speeches.set_index(['speaker_id', 'speech_id']).sort_index()

def get_text_by_speaker(speeches):
    grouped_by_speaker = speeches.groupby(['speaker_id'])['strings']
    text_grouped_by_speaker = grouped_by_speaker.aggregate(lambda df: list(it.chain(*df.values)))
    
    return text_grouped_by_speaker

#filenames = fetch_debates_filenames()
#dated_filenames = extract_dates(filenames)
#xmls = get_debate_xml_since('2015-01-05', dated_filenames)