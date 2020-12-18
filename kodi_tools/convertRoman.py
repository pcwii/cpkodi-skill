def roman_to_int(input_string):
    """
    :type s: str
    :rtype: int
    """
    result_string = ""
    result_list = []
    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, 'IV': 4, 'IX': 9, 'XL': 40, 'XC': 90,
             'CD': 400, 'CM': 900}
    all_words = input_string.split()
    for each_word in all_words:
        isRoman = all(romanCheck in roman for romanCheck in each_word)
        i = 0
        num = 0
        if isRoman:
            while i < len(each_word):
                if i + 1 < len(each_word) and each_word[i:i + 2] in roman:
                    num += roman[each_word[i:i + 2]]
                    i += 2
                else:
                    num += roman[each_word[i]]
                    i += 1
            result_list.append(str(num))
        else:
            result_list.append(each_word)
    result_string = ' '.join(result_list)
    return result_string

def int_to_Roman(input_num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while input_num > 0:
        for _ in range(input_num // val[i]):
            roman_num += syb[i]
            input_num -= val[i]
        i += 1
    return roman_num
