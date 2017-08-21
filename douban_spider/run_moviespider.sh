#!/bin/sh

# scrapy crawl moviespider -o movies.json -s LOG_FILE=scrapy.log
scrapy crawl moviespider -s LOG_FILE=scrapy.log
#scrapy crawl bookspider
