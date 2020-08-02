import xml.etree.cElementTree as ET
import re
def pre_ncbi(fullpath, writepath):
    with open(fullpath, 'rb') as file:
        content = file.read().decode("utf-8")
        content = str(content)
        content = re.sub('<sup>.*?</sup>', ' ', content)
        text = ""
        root = ET.fromstring(content)
        num = 1
        for child_of_root in root.iterfind('PubmedArticle/MedlineCitation/Article'):
            text += child_of_root.find('ArticleTitle').text
            text += "\n"
            for i in child_of_root.findall('Abstract/AbstractText'):
                text += i.text
            with open(writepath+str(num), 'wb') as f:
                f.write(text.encode('utf-8'))
            num+=1
            text = ""

pre_ncbi()