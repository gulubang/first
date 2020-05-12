import requests, json, os, base64, codecs, re, time, pprint, sqlite3, neMusicDBTool, jieba, neMusicPainter
from Crypto.Cipher import AES
from collections import Counter

# AES加密
def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    if isinstance(text,bytes):
        text=text.decode('utf-8')
    text = text + str(pad * chr(pad))
    encryptor = AES.new(secKey.encode('utf-8'), AES.MODE_CBC, '0102030405060708'.encode('utf-8'))
    ciphertext = encryptor.encrypt(text.encode('utf-8'))
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext

# RSA加密
def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'),'hex_codec'), 16)**int(pubKey, 16)%int(modulus, 16)
    return format(rs, 'x').zfill(256)

# 生成加密随机字符串
def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), str(os.urandom(size)))))[0:16]

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

# 获取评论
def getComments(url):
    url='https://music.163.com/weapi/v1/resource/comments/R_SO_4_'+url+'?csrf_token='
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36 Edg/81.0.416.64'
    }
    comment_list=[]
    count=0
    f=codecs.open('neMusicComments.txt','w',encoding='utf-8')
    # 获取评论，一页二十条
    for i in range(20):
        fTag=False
        if i==0:
            fTag=True
        # text = {
        #     'username': '',
        #     'password': '',
        #     'rememberLogin': 'true',
        #     'offset': i*20
        # }
        text={
            'rid':'R_SO_4_'+url,
            'offset':i*20,
            'total':fTag,
            'limit':'20',
            'csrf_token':''
        }
        text = json.dumps(text)
        secKey = createSecretKey(16)
        # print(secKey)
        encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
        encSecKey = rsaEncrypt(secKey, pubKey, modulus)
        payload = {
                'params': encText,
                'encSecKey': encSecKey
        }
        print('正在获取第%d至%d条评论。。。'%(i*20+1,i*20+20))
        response=requests.post(url,headers=headers,data=payload)
        response.raise_for_status
        print('请求状态码:',response.status_code)
        try:
            r=json.loads(response.text)
            # pprint.pprint(r)
        except:
            print('json.loads(response.text)出错了')
        r_comment=r['comments']
        currentCounter=0
        for i in r_comment:
            # 去表情[XXX]、换行、@XXX、话题#XXX#、书名号、长空格为空格
            flush_comment=re.sub(r'\[(.+)\]',' ',i.get('content'))
            flush_comment=re.sub(r'\n',' ',flush_comment)
            flush_comment=re.sub(r'\@\S+\s?',' ',flush_comment)
            flush_comment=re.sub(r'\#(.+)\#\s?',' ',flush_comment)
            flush_comment=re.sub(r'[《》]',' ',flush_comment)
            flush_comment=re.sub(r'\s+',' ',flush_comment)
            flush_comment=re.sub(r'[\.…。，！？?,!]+',' ',flush_comment)
            comment_list.append([count,r['comments'][currentCounter]['user']['userId'],r['comments'][currentCounter]['user']['nickname'],r['comments'][currentCounter]['user']['vipType'],i.get('likedCount'),i.get('content')])
            f.write(flush_comment+'\n')
            currentCounter+=1
            count+=1
        print('完成获取评论,本次%d条\n'%len(r_comment))
        time.sleep(0.5)
    f.close()
    print('获取到%d条评论。'%len(comment_list))
    print(' 序 ： 用户ID  ： 昵称 ： VIP类型 ： 点赞数 ： 评论内容 \n')
    return comment_list

def dbsShower():
    rowCount=0
    dbdata=neMusicDBTool.queryTable()
    print(' 序 ：用户ID  ： 昵称 ： VIP类型 ： 点赞数 ： 评论内容 \n')
    for data in dbdata:
        print(rowCount,'.',data[0],data[1],data[2],data[3],data[4])
        rowCount+=1

def word_segmentation():
    f=codecs.open('neMusicComments.txt','r','utf-8')
    content=f.read()
    counter=Counter()
    words=jieba.cut(content,cut_all=True)
    for word in words:
        if len(word)>1 and word !='\r\n':
            counter[word]+=1
    f.close()
    return counter.most_common(20)

def neHotWordsWriter(topWords):
    f=codecs.open('neMusicHotWords.txt','w','utf-8')
    print('\n热词词频Top20：\n')
    for (k,v) in topWords:
        print(k,str(v)+'次')
        f.write(k+' '+str(v)+'次'+'\n')
    f.close()

if __name__=='__main__':
    comment=getComments('28830388')
    for i in comment:
        print(i)
    if(input('写入数据库？ Y/n\n').strip(' ') in 'Yy'):
        changeCount=neMusicDBTool.createTable()
        neMusicDBTool.insertTable(comment,changeCount)
        print('来自数据库：\n')
        dbsShower()
        neMusicDBTool.closeDB()
    else:
        print('已爬取并写入文件，未写入库')
    topWords=word_segmentation()
    neHotWordsWriter(topWords)
    neMusicPainter.drewler(topWords)
    