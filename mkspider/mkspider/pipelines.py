# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
from twisted.enterprise import adbapi
from mkspider.settings import *
import datetime
import MySQLdb.cursors


class MkspiderPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', db=MYSQL_DBNAME,
                                            user=MYSQL_USER, passwd=MYSQL_PASSWD,
                                            cursorclass=MySQLdb.cursors.DictCursor, host=MYSQL_HOST,
                                            charset='utf8', use_unicode=True)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self._handle_error)
        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        sql = "select * FROM mkcourse where LessID = '%(LessID)s'" % item
        tx.execute(sql)
        result = tx.fetchone()
        if result:
            log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        else:
            try:
                tx.execute(
                    '''INSERT INTO mkcourse(LessID,LessName,LessHref,LessVideo,pLessID,pLessName,pLessHref)
                     values (%s, %s,%s,%s,%s,%s,%s) ''',
                    (item["LessID"], item["LessName"], item["LessHref"], item["LessVideo"], item["pLessID"],
                     item["pLessName"], item["pLessHref"])
                )
            except Exception:
                print(Exception.message)
                log.msg("Eorror: %s" % Exception.message, level=log.DEBUG)
                pass

    def _handle_error(self, e):
        log.err(e)
