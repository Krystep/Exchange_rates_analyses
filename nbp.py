# -*- coding: utf-8 -*-
"""
Spyder Editor

definition of classes that I need for my project

"""
import datetime
import json
import requests

from lxml import etree
from io import StringIO

class ExchangeRateTable:
    
    def __init__(self, name, effective_date, rates = None):
        self.name = name
        self.effective_date = effective_date
        self.rates = rates if rates else []
        
    def add_rate(self, rate):
        self.rates.append(rate)
        
    def get_rate(self, code):
        for rate in self.rates:
            if rate.code == code:
                return rate              
    
    def get_rate_table(self, code):
        rate_table = {rate: rate.code for rate in self.rates}
        

class ExchangeRate:
    
    def __init__(self, currency, code, ask_rate, bid_rate):
        self.currency = currency
        self.code = code
        self.ask_rate = ask_rate
        self.bid_rate = bid_rate
        
    def __str__(self):
        return f'<{self.currency} ({self.code}) \t{self.ask_rate} \t{self.bid_rate}>' 

def get_exchange_rate_table(date, format):
    url = f'http://api.nbp.pl/api/exchangerates/tables/C/{date}'
    resp = requests.get(url, params={'format': format})
    resp.raise_for_status()
    if format == 'json':
        return _from_json(resp.text)
    elif format == 'xml':
        return _from_xml(resp.text)
    else:
        return None

def _from_json(data):
    rates_dict = json.loads(data)[0]
    rates = [ExchangeRate(rate['currency'], rate['code'], rate['ask'], rate['bid']) for rate in rates_dict['rates']]
    table = ExchangeRateTable(rates_dict['no'], rates_dict['effectiveDate'], rates)
    return table


def _from_xml(data):
    data = data.encode('utf-8')
    parser = etree.XMLParser(recover=True, encoding='utf-8')
    tree = etree.fromstring(data, parser=parser)
    table_name = tree.xpath('//ExchangeRatesTable/No')[0].text
    effective_date = tree.xpath('//ExchangeRatesTable/EffectiveDate')[0].text
    rates = [ExchangeRate(rate.xpath('./Currency/text()')[0],
                          rate.xpath('./Code/text()')[0],
                          rate.xpath('./Ask/text()')[0],
                          rate.xpath('./Bid/text()')[0]) for rate in tree.xpath('//ExchangeRatesTable/Rates/Rate')]
    table = ExchangeRateTable(table_name, effective_date, rates)
    return table
        



