import re
import os,random
from collections import OrderedDict
import jieba
import jieba.analyse
from bs4 import BeautifulSoup

class Document(object):
    """docstring for Document."""
    def __init__(self, docid, fullpath, num_words, tags):
        self.docid = docid
        self.fullpath = fullpath
        self.year,self.month,self.name = self.fullpath.replace('static/blogs/','').split('/')
        self.time = self.year + '/' + self.month
        self.link = self.fullpath.replace('static', '') + '/'
        self.tags = tags
        self.num_words = num_words



    def read_html(self):
        f = open(self.fullpath+'.html', 'r', encoding='utf8')
        html = f.read()
        f.close()
        return html

class BlogSearch(object):
    """used to search the blog content

    Args:
        basepath
    Attributes:
        basepath
        documents: store the information of blogs
        paths: map path to docid
        worddoc: store all words, and its documents id
        date_path_dict: map year_month to fullpath
    """
    def __init__(self, basepath, page_size=4):
        self.basepath = basepath
        self.paths = []
        for dirpath,dirnames,filenames in os.walk(self.basepath):
            for file in filenames:
                x = file.split('.')
                if x[1].strip() == 'md':
                    fullpath = os.path.join(dirpath,x[0].strip())
                    self.paths.append(fullpath)
        self.paths = sorted(self.paths)
        self.reverse_paths = sorted(self.paths, reverse=True)

        jieba.analyse.set_stop_words('static/file/search/stop_words.txt')
        self.documents = []
        self.worddoc = {}
        self.tagdict = {}
        self.time_dict = {}
        for path in self.paths:
            self._add_document(path, self.paths.index(path))

        self.total_docs = len(self.paths)
        self.page_size = page_size
        import math
        self.total_pages = int(math.ceil(self.total_docs / self.page_size))
        self.current_page = 1

        self.sorted_tagdict = sorted(self.tagdict.items(), key=lambda d: d[1], reverse=True)

        print('building searching content finished')


    def _add_document(self,fullpath, docid):

        # get full content
        fhtml = open(fullpath+'.html', 'r', encoding='utf8')
        soup = BeautifulSoup(fhtml, 'html.parser')

        content = ''        
        plist = soup.find_all('p')
        for pi in plist:
            content += pi.text

        hlist = soup.find_all('h')
        for hi in hlist:
            content += hi.text

        title = fullpath.split('/')[-1]

        content = re.sub('\W',' ',title + content).lower().replace('__','')
        tags = jieba.analyse.extract_tags(content, topK=30)

        for tag in tags[:15]:
            if tag not in self.tagdict:
                self.tagdict[tag] = 0
            self.tagdict[tag] += (15-tags.index(tag))

        wordlist = jieba.lcut_for_search(content)
        num_words = len(wordlist)
        wordlist = set(wordlist)

        document = Document(docid, fullpath, num_words, tags)
        document.summary = soup.p.text
        self.documents.append(document)
        if document.time not in self.time_dict:
            self.time_dict[document.time] = []
        self.time_dict[document.time].append(document.docid)

        for word in wordlist:
            if word not in self.worddoc:
                self.worddoc[word] = []
            if docid not in self.worddoc[word]:
                self.worddoc[word].append(docid)

    """
    search api
    """
    def search(self,q):
        if q in self.time_dict: # search for year and month, eg q='2018/05'
            return self.time_dict[q]
        result = None
        content = re.sub('\W',' ',q).lower()
        keywords = jieba.analyse.extract_tags(content, topK=3)
        for k in keywords:
            if k in self.worddoc:
                if result == None:
                    result = self.worddoc[k]
                else:
                    result = list(set(result).intersection(set(self.worddoc[k])))
        resultdict = {}
        if result == None:
            return []
        for docid in result:
            resultdict[docid] = 0
            for k in keywords:
                tags = self.documents[docid].tags
                if k in tags:
                    resultdict[docid] += (len(tags) - tags.index(k))
        result = [k for k,v in sorted(resultdict.items(), key=lambda d: d[1], reverse=True)]
        return result

    def get_tags_topk(self,path,k):
        tag = ''
        if path in self.paths:
            docid = self.paths.index(path)
            tag = self.documents[docid].tags[0:k]
        return tag

    def get_path(self,docid):
        if docid < len(self.paths):
            return self.paths[docid]
        return ''

    def get_id(self,year,month,name):
        fullpath = 'static/blogs/' + year + '/' + month + '/' + name
        return self.paths.index(fullpath)

    def get_document(self,year, month, name):
        docid = self.get_id(year,month,name)
        if docid > 0 and docid < self.total_docs:
            return self.documents[docid]
        return None

    def get_page(self, page_index):
        return [self.total_docs-1-i%self.total_docs for i in range(page_index*self.page_size, (page_index+1)*self.page_size)]

    def get_recommend(self, docid):
        document = self.documents[docid]
        recommend = self.search(document.name)
        recommend.remove(docid)
        recommend = list(set(recommend))
        
        for i in range(len(document.tags)):
            if len(recommend) >= 3:
                return recommend
            recommend += self.search(document.tags[i])
            recommend.remove(docid)
            recommend = list(set(recommend))
        
        while len(recommend) < 3:
            x = random.randint(0, len(self.documents))
            if x not in recommend and x != docid:
                recommend.append(x)

        return recommend

bs = BlogSearch('static/blogs/', page_size=4)
# # print(bs.sorted_tagdict)
# print(bs.search('and'))
# print(bs.search('tensorflow'))
