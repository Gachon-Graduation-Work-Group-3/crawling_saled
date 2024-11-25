def find_class(input,tag, cls):
    input_tag = input.find(tag, class_ = cls)
    input = input_tag.text.strip() if input_tag else '정보 없음'

    return input