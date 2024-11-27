import pandas as pd

def find_class(input,tag, cls):
    if isvalid(input):
        input_tag = input.find(tag, class_ = cls)
        input = input_tag.text.strip() if input_tag else None
    else:
        input = None
        
    return input


#옵션이름 받아서 확인여부하는 함수
def option_check(soupobject,option_name):
    if isvalid(soupobject.find("a", string=option_name)):
        check = soupobject.find("a", string=option_name).find_parent("label").find_parent("div")
        check = check.find("input", {"type": "checkbox"})
        # .find_parent().find_previous_sibling().get_attribute_list('checked')

        if check.has_attr("checked"):
            return '유'
        else:
            return '무'
        
    else: return '무'
    
    
def isvalid(soupobject):
    return True if soupobject is not None else False


def extract_urls(file_path, col):
    df = pd.read_csv(file_path)
    urls = list(df[col])
    return urls