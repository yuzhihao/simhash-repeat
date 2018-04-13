#coding=utf8
# yuzhihao
import traceback
import jieba.posseg as pseg
from simhash import Simhash

from lib.mongo_db import MongDb
from lib.simhash_db import Client

mongo_conf_insert = {
    'host': 'Crawler-DataServer2',
    'port': 40042,
    'final_db': 'final_data',
    'username': "work",
    'password': "haizhi",
}

ignore = ['x', 'uj', 'ul', 'y', 'p', 'c', 'd']
#ignore = []

def getWords(data):
    words = pseg.cut(data)
    res = {}
    for word, flag in words:
#        print(word, flag)
        if flag in ignore:
            continue
        if word in res:
            res[word] = res[word] + 1
        else:
            res[word] = 1
    return res

def getDis(hash1, hash2):
    dis = 0
    for i in range(0, 64):
        if ((hash1>>i)&1) ^ ((hash2>>i)&1) == 1:
            dis = dis + 1;
    return dis

class NewsNoRepeat:
    def __init__(self):
        self.sourceTable = 'news'
        self.client = Client('mongo', 'news_no_repeat', 6, 3, ['Crawler-DataServer2'], 40042)
        self.db_final_data = MongDb(mongo_conf_insert['host'], mongo_conf_insert['port'], mongo_conf_insert['final_db'],
                               mongo_conf_insert['username'],
                               mongo_conf_insert['password'])

    def full_remove_dup(self):
        # 获取要清洗的数据
        cursor = self.db_final_data.select(self.sourceTable)

        count = 0
        count_dup = 0
        try:

            for tmp in cursor:
                count += 1
                hashvalue = Simhash(getWords(tmp.get('content'))).value
                ret = self.client.find_all(hashvalue)
                if ret:
                    print "存在重复:{1}".format(ret)
                    count_dup +=1
                else:
                    self.client.insert(hashvalue)
                if count>1000:
                    break
        except Exception as e:
            print e.message
            print traceback.format_exc()
        finally:
            cursor.close()
        print "结束，执行{1}条，重复{2}条".format(count,count_dup)



if __name__ == "__main__":
    import time
    print("start")
    begin_time = time.time()

    #从备份数据表中读取要清洗的数据，并写入目地数据库
    news_no_repeat = NewsNoRepeat()
    news_no_repeat.full_remove_dup()

    print("time_cost:", time.time() - begin_time)
