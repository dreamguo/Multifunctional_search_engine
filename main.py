# coding:utf-8
# https://news.sina.com.cn/
from urllib.request import urlopen, Request, urljoin
from html.parser import HTMLParser
from urllib.parse import urlparse
import numpy
import requests
from bs4 import BeautifulSoup
from tkinter import *
import re
import jieba
import wordcloud
import io
from PIL import Image, ImageTk

all_news = ''
all_keys = []
mode = 0


class MyHTMLParser(HTMLParser):
    def __init__(self, url, name=[]):
        HTMLParser.__init__(self)
        self.url = url
        self.name = name
        self.stack = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            # print(attrs)
            for item in attrs:
                if item[0] == "href" and item[1] != self.url:
                    try:
                        web = urlparse(item[1])
                        if web.scheme == "http" or web.scheme == "https":
                            web = item[1]
                        elif len(web.path) == 0:
                            break
                        elif web.scheme == '' and web.netloc == '':
                            web = urljoin(self.url, item[1])
                        elif web.scheme == '' and web.netloc != '':
                            web = urljoin('http:', item[1])
                        else:
                            break
                        if web != self.url and web in self.name:
                            if web in self.stack:
                                self.stack[web] += 1
                            else:
                                self.stack[web] = 1
                        break
                    except:
                        break


class FirstHTMLParser(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.stack = {}
        self.waste = ['collection', 'http://bj.house.sina.com.cn/', 'http://bj.leju.com/', 'video']

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for item in attrs:
                if item[0] == "href" and item[1] != self.url:
                    try:
                        web = urlparse(item[1])
                        if web.scheme == "http" or web.scheme == "https":
                            web = item[1]
                        elif len(web.path) == 0:
                            break
                        elif web.scheme == '' and web.netloc == '':
                            web = urljoin(self.url, item[1])
                        elif web.scheme == '' and web.netloc != '':
                            web = urljoin('http:', item[1])
                        else:
                            break

                        if web == self.url or not ('/2020-' in web) or web == 'https://news.sina.com.cn/china/':
                            break
                        flag = 0
                        for c in self.waste:
                            if c in web:
                                flag = 1
                                break
                        if flag == 1:
                            break
                        try:
                            r = Request(web, headers={'User-agent': 'Mozilla 5.10'})
                            t = urlopen(r)
                        except:
                            break
                        if web in self.stack:
                            self.stack[web] += 1
                        else:
                            # print(web)
                            self.stack[web] = 1
                        break
                    except:
                        break


class Example(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.canvas = Canvas(root, borderwidth=0, background="Mint cream")
        self.frame = Frame(self.canvas, background="Mint cream")
        self.vsb = Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.populate(root)

    def populate(self, root):
        frm = Frame(self.frame, background="Mint cream", padx=100)  # 主框架
        frm.pack()
        frm_top = Frame(frm, background="Mint cream")  # 顶部框架
        frm_top.pack()

        pil_image_welcome = Image.open(r'welcome.png')  # 以一个PIL图像对象打开  【调整待转图片格式】
        pil_image_resized_welcome = resize(370, 150, pil_image_welcome)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】
        tk_image_welcome = ImageTk.PhotoImage(
            pil_image_resized_welcome)  # 把PIL图像对象转变为Tkinter的PhotoImage对象  【转换格式，方便在窗口展示】
        label_welcome = Label(frm_top, image=tk_image_welcome, width=370, height=150, background="Mint cream")
        label_welcome.pack(padx=5, pady=5)  # padx,pady是图像与窗口边缘的距离

        var_entry = StringVar()
        entry = Entry(frm_top, textvariable=var_entry, width=100)  # 输入框
        entry.pack(side=LEFT)

        frm0 = Frame(frm, background="Mint cream")  # 提示框架
        frm0.pack()

        var0 = StringVar()  # 提示文本
        T0 = Label(frm0, textvariable=var0, height=2, width=50, background="Mint cream")
        T0.pack()

        frm_L = Frame(frm, background="Mint cream")  # 左侧框架
        frm_L.pack(side=LEFT)
        frm_R = Frame(frm, background="Mint cream")  # 右侧框架
        frm_R.pack(side=RIGHT)

        frm1 = Frame(frm_L, background="Mint cream")  # 新闻框架1
        var1 = StringVar()  # 标题文本
        T1 = Message(frm1, textvariable=var1, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T1.pack()
        var_1 = StringVar()  # 内容文本
        t1 = Message(frm1, textvariable=var_1, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t1.pack()
        frm1.pack()

        frm2 = Frame(frm_L, background="Mint cream")  # 新闻框架2
        var2 = StringVar()
        T2 = Message(frm2, textvariable=var2, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T2.pack()
        var_2 = StringVar()
        t2 = Message(frm2, textvariable=var_2, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t2.pack()
        frm2.pack()

        frm3 = Frame(frm_L, background="Mint cream")  # 新闻框架3
        var3 = StringVar()
        T3 = Message(frm3, textvariable=var3, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T3.pack()
        var_3 = StringVar()
        t3 = Message(frm3, textvariable=var_3, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t3.pack()
        frm3.pack()

        frm4 = Frame(frm_L, background="Mint cream")  # 新闻框架4
        var4 = StringVar()
        T4 = Message(frm4, textvariable=var4, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T4.pack()
        var_4 = StringVar()
        t4 = Message(frm4, textvariable=var_4, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t4.pack()
        frm4.pack()

        frm5 = Frame(frm_L, background="Mint cream")  # 新闻框架5
        var5 = StringVar()
        T5 = Message(frm5, textvariable=var5, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T5.pack()
        var_5 = StringVar()
        t5 = Message(frm5, textvariable=var_5, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t5.pack()
        frm5.pack()

        frm6 = Frame(frm_L, background="Mint cream")  # 新闻框架6
        var6 = StringVar()
        T6 = Message(frm6, textvariable=var6, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T6.pack()
        var_6 = StringVar()
        t6 = Message(frm6, textvariable=var_6, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t6.pack()
        frm6.pack()

        frm7 = Frame(frm_L, background="Mint cream")  # 新闻框架7
        var7 = StringVar()
        T7 = Message(frm7, textvariable=var7, width=700, font=("宋体", 14, "bold"), background="Mint cream")
        T7.pack()
        var_7 = StringVar()
        t7 = Message(frm7, textvariable=var_7, width=700, font=("宋体", 10, "normal"), background="Mint cream")
        t7.pack()
        frm7.pack()

        var_wordcloud = StringVar()
        label_wordcloud = Label(frm_R, textvariable=var_wordcloud, font=("宋体", 10, "normal"), background="Mint cream")
        var_wordcloud.set("实时热搜关键词(云图版)：")

        w_box = 300
        h_box = 300
        pil_image = Image.open(r'wordcloud.png')  # 以一个PIL图像对象打开  【调整待转图片格式】
        pil_image_resized = resize(w_box, h_box, pil_image)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】
        tk_image = ImageTk.PhotoImage(pil_image_resized)  # 把PIL图像对象转变为Tkinter的PhotoImage对象  【转换格式，方便在窗口展示】
        label = Label(frm_R, image=tk_image, width=w_box, height=h_box, background="Mint cream")

        var_word = StringVar()
        label_word = Label(frm_R, textvariable=var_word, font=("宋体", 10, "normal"), background="Mint cream")
        var_word.set("实时热搜关键词(点击搜索)：")

        frm_R_D = Frame(frm_R)  # 右侧下部框架        

        def print_item(event):
            var_entry.set(lb.get(lb.curselection()))

        lb = Listbox(frm_R_D, height=5, selectmode=BROWSE, font=("宋体", 14, "bold"), background="Mint cream")  # Listbox
        list_item = []
        scrl = Scrollbar(frm_R_D)  # Listbox的滚动条
        lb.configure(yscrollcommand=scrl.set)
        lb.bind('<ButtonRelease-1>', print_item)
        scrl['command'] = lb.yview

        def ButtonFunction():
            search_txt = var_entry.get()
            search_txt = re.sub('\s', '', search_txt)
            var1.set('')
            var_1.set('')
            var2.set('')
            var_2.set('')
            var3.set('')
            var_3.set('')
            var4.set('')
            var_4.set('')
            var5.set('')
            var_5.set('')
            var6.set('')
            var_6.set('')
            var7.set('')
            var_7.set('')
            label_wordcloud.pack()

            label.pack(padx=5, pady=5)  # padx,pady是图像与窗口边缘的距离
            label_word.pack()
            frm_R_D.pack()
            scrl.pack(side=RIGHT, fill=Y)
            lb.pack(fill=BOTH)
            # try:
            text_url = search(search_txt, int(mode))
            # except:
            #    print('Can not open the web: ' + var_entry.get())
            #    var0.set('Can not open the web ...\nPlease check it')
            #    return
            list_item = text_url[-1]
            for item in list_item:
                lb.insert(END, item)
            if len(text_url) > 1:
                var1.set(text_url[0][1])
                var_1.set(text_url[0][2])
                if len(text_url) == 2:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var2.set(text_url[1][1])
                var_2.set(text_url[1][2])
                if len(text_url) == 3:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var3.set(text_url[2][1])
                var_3.set(text_url[2][2])
                if len(text_url) == 4:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var4.set(text_url[3][1])
                var_4.set(text_url[3][2])
                if len(text_url) == 5:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var5.set(text_url[4][1])
                var_5.set(text_url[4][2])
                if len(text_url) == 6:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var6.set(text_url[5][1])
                var_6.set(text_url[5][2])
                if len(text_url) == 7:
                    var0.set('一共搜索到{0:d}篇相关新闻：'.format(len(text_url)))
                    return
                var7.set(text_url[6][1])
                var_7.set(text_url[6][2])
                var0.set('一共搜索到{0:d}篇相关新闻\n给您推荐7篇最热新闻：'.format(len(text_url)))
            else:
                var0.set('暂时搜不到相关新闻，请您更换查询词（网址）后查询\n可以参考右下方的热搜词')
            print('done!')

        button = Button(frm_top, text="search", bg="#4169E1", font=("Arial", 12), padx=10, command=ButtonFunction)
        button.pack(side=LEFT)

        def radiobutton_function():
            global mode
            mode = var_radiobutton.get()

        var_radiobutton = StringVar()
        var_radiobutton.set(0)
        radiobutton1 = Radiobutton(frm_top, value=0, text='按热度（默认）', command=radiobutton_function,
                                   activebackground='#87CEFA ', variable=var_radiobutton, background="Mint cream")
        radiobutton1.pack(anchor=W)
        radiobutton2 = Radiobutton(frm_top, value=1, text='按时间', command=radiobutton_function,
                                   activebackground='#87CEFA', variable=var_radiobutton, background="Mint cream")
        radiobutton2.pack(anchor=W)
        radiobutton3 = Radiobutton(frm_top, value=2, text='按相关度', command=radiobutton_function,
                                   activebackground='#87CEFA', variable=var_radiobutton, background="Mint cream")
        radiobutton3.pack(anchor=W)

        root.mainloop()

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


def resize(w_box, h_box, pil_image):  # 参数是：要适应的窗口宽、高、Image.open后的图片
    w, h = pil_image.size  # 获取图像的原始大小
    f1 = 1.0 * w_box / w
    f2 = 1.0 * h_box / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


def word_cloud():
    ls = jieba.lcut(all_news)
    f = open('stopwords.txt', 'r', encoding='UTF-8')
    stopwords = f.read().split()
    i = 0
    while i < len(ls):
        if ls[i] in stopwords:
            del ls[i]
            i -= 1
        i += 1
    f.close()

    txt = " ".join(ls)
    txt = re.sub('\d', '', txt)
    w = wordcloud.WordCloud( \
        width=1000, height=700, \
        background_color="white",
        font_path="msyh.ttc", max_words=200
    )
    print(len(txt))
    w.generate(txt)
    w.to_file("wordcloud.png")
    keyword = word_sort(txt, '', all_keys, 1)
    for i in range(len(keyword)):
        keyword[i] = keyword[i][0]
    return keyword[:10]


def word_sort(txt, title, keywords, slt=0):
    if len(txt) == 0:
        return []
    words = jieba.lcut(txt)
    words_title = jieba.lcut(title)
    counts = {}
    for word in words:
        if len(word) == 1:
            continue
        counts[word] = counts.get(word, 0) + 1
    for word in words_title:
        if len(word) == 1:
            continue
        if slt == 0:
            counts[word] = counts.get(word, 0) + int(len(words) / 200)
        else:
            counts[word] = counts.get(word, 0) + 1
    for word in keywords:
        if len(word) == 1:
            continue
        if slt == 0:
            counts[word] = counts.get(word, 0) + int(len(words) / 5)
        else:
            counts[word] = counts.get(word, 0) + 1
    for c in counts:
        counts[c] = counts[c] / len(words) * 100
    items = list(counts.items())
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def add(Markov, diction, cnt, name):
    if len(diction) > 0:
        sumnum = 0
        for i in range(len(name)):
            if name[i] in diction:
                sumnum += diction[name[i]]
        if sumnum > 0:
            for i in range(len(name)):
                if name[i] in diction:
                    Markov[cnt][i] = diction[name[i]] / sumnum
                else:
                    Markov[cnt][i] = 0
            return Markov
    for i in range(len(Markov[cnt])):
        Markov[cnt][i] = 1 / len(Markov[cnt])
    return Markov


def get_urltxt(url, key_word, mode):
    #    print(url)
    global all_news
    global all_keys
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    #    print(soup)
    try:
        time = soup.find("span", {"class": "date"})
    except:
        pass
    if time == None:
        try:
            time = soup.find("span", {"id": "pub_date"})
        except:
            pass
    if time == None:
        try:
            time = soup.find("p", {"class": "from"}).find("em")
        except:
            pass
    if time == None:
        try:
            time = soup.find("span", {"class": "titer"})
        except:
            pass
    if time == None:
        try:
            time = soup.find("div", {"class": "txtdetail"})
        except:
            pass
    if time == None:
        try:
            time = soup.find("p", {"class": "source-time"})
        except:
            pass
    if time == None:
        try:
            time = soup.find("span", {"class": "time"})
        except:
            pass
    time = re.sub(r'<(.|\n)*?>', '', str(time))
    time = re.sub('\\\\u3000', '', str(time))
    time = time.split()
    if len(time) > 1:
        time = time[:2]
        time[1] = time[1][:5]
    if '0' < time[0][-1] and time[0][-1] < '9':
        time[0] = time[0][0:4] + '年' + time[0][5:7] + '月' + time[0][8:10] + '日'
    if time[0][0] != '[':
        time.insert(0, '[')
        time.append(']')
    time = ''.join(time)
    #    print(time)
    keys = soup.title.string
    keys = re.sub('\s', '', keys)
    keys = keys.split('|')
    keys[-1:] = keys[-1].split('_')
    title = keys[0]
    keys = keys[1:-1]

    contents = []
    try:
        for item in soup.find("div", {"class": "article"}).findAll("p"):
            contents.append(item.text)
    except:
        pass
    if contents == []:
        try:
            for item in soup.find("div", {"id": "artibody"}).findAll("p"):
                contents.append(item.text)
        except:
            pass
    if contents == []:
        try:
            for item in soup.find("em", {"task": "oldinfor"}).findAll("p"):
                contents.append(item.text)
        except:
            pass
    contents = contents[1:-1]
    new = ''.join(contents)
    new = re.sub('\s', '', new)
    items = word_sort(new, title, keys)  # 调用word_sort
    if items == []:
        return []
    i = 0
    while i < len(keys):
        if '新浪' in keys[i] or '闻' in keys[i] or "创事记" in keys[i]:
            del keys[i]
            i -= 1
        i += 1
    title = title + ' '
    all_news += new + ' ' + title * 3 + ' '
    for i in range(int(len(items) / 20)):
        for c in keys:
            all_keys.append(c)
    if key_word != '':
        flag = 0
        for i in range(int(len(items) / 10)):
            if items[i][0] == key_word:
                flag = 1
                break
        if flag == 0:
            return []
    inf = []
    inf.append(url)
    inf.append("标题：" + title)
    inf.append('    ' + time + new[:140] + ' ...\n')
    inf.append(time)
    if mode == 1:
        try:
            time_cnt = int(time[1:5]) * 365 * 24 * 60 + int(time[6:8]) * 30 * 24 * 60 + int(time[9:11]) * 24 * 60 + int(
                time[12:14]) * 60 + int(time[15:17])
            inf.append(time_cnt)
        except:
            return []
    if mode == 2:
        if key_word in items:
            keyword_cnt = items.index(key_word)
        else:
            keyword_cnt = 999
        inf.append(keyword_cnt)
    return inf


def search(url, mode):
    print('【0/4】start!')
    key_word = ''
    if mode == 0:
        print('按热度：', end= ' ')
    elif mode == 1:
        print('按时间：', end=' ')
    elif mode == 2:
        print('按相关度：', end=' ')
    if url[:4] != 'http':
        print('a word')
        key_word = url
        url = 'https://news.sina.com.cn/'
    else:
        print('a web')
    parser = FirstHTMLParser(url)
    r = Request(url, headers={'User-agent': 'Mozilla 5.10'})
    t = urlopen(r)
    parser.feed(str(t.read(), encoding='utf-8'))
    name = []
    for url in parser.stack:
        name.append(url)
    print('【1/4】first layer finished!')
    if mode == 0:
        lenth = len(parser.stack)
        Markov = [([0] * lenth) for i in range(lenth)]
        Markov = add(Markov, parser.stack, 0, name)
        for i in range(len(name) - 1):
            url = name[i]
            # print(url)
            parser = MyHTMLParser(url, name)
            r = Request(url, headers={'User-agent': 'Mozilla 5.10'})
            t = urlopen(r)
            parser.feed(str(t.read(), encoding='utf-8'))
            Markov = add(Markov, parser.stack, i + 1, name)  # 调用add
        print('【2/4】second layer finished!')
        p = [[0] for i in range(lenth)]
        p[0][0] = 1
        p = numpy.mat(p)
        Markov = numpy.mat(Markov)
        S = Markov.T
        alpha = 0.85
        I = [([1] * lenth) for i in range(lenth)]
        I = numpy.mat(I)

        A = (alpha * S) + ((1 - alpha) / lenth) * I
        distance = 1.0
        while distance > 0.0001:
            p_next = A * p
            distance = 0.0
            for i in range(lenth):
                distance += abs(float(p[i] - p_next[i]))
            p = p_next

        num = []
        for i in range(len(p)):
            num.append((float(p[i]), i))
        num.sort(reverse=True)
        print('【3/4】calculate finished!')
        text_url = []
        for i in range(len(num)):
            urltxt = get_urltxt(name[num[i][1]], key_word, mode)  # 调用get_urltxt
            if len(urltxt) > 0:
                text_url.append(urltxt)
    elif mode == 1:
        text_url = []
        for i in range(len(name)):
            urltxt = get_urltxt(name[i], key_word, mode)  # 调用get_urltxt
            if len(urltxt) > 0:
                text_url.append(urltxt)
        print('【2/4】second layer finished!')
        text_url.sort(key=lambda x: x[-1], reverse=True)
        print('【3/4】calculate finished!')
    elif mode == 2:
        text_url = []
        for i in range(len(name)):
            urltxt = get_urltxt(name[i], key_word, mode)  # 调用get_urltxt
            if len(urltxt) > 0:
                text_url.append(urltxt)
        print('【2/4】second layer finished!')
        text_url.sort(key=lambda x: x[-1])
        print('【3/4】calculate finished!')
    keyword = word_cloud()  # 调用word_cloud
    text_url.append(keyword)
    print('【4/4】wordcloud finished!')
    return text_url


def window():
    root = Tk()  # TK基底
    root.title("GG search")
    root.geometry('1000x500')
    root.resizable(width=True, height=True)
    Example(root)  # 调用Example类


if __name__ == '__main__':
    print('Welcome to GG search!')
    window()
