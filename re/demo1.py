import re

my_str = "username:cjj,email:2871843852@qq.com"
my_str2 = "121313username:cjj,email:2871843852@qq.com"

info_pattern = re.compile(r"username:(\w*),email:(\d*@.*)")

info_match1 = info_pattern.match(my_str)
info_match2 = info_pattern.match(my_str2)

if info_match1:
    print("info_match1 successfully")
    all_match = info_match1.group(0)
    user_name = info_match1.group(1)
    email = info_match1.group(2)
    print(user_name)
    print(email)
    print(all_match)

if info_match2:
    print("info_match2 successfully")
    all_match = info_match1.group(0)
    user_name = info_match1.group(1)
    email = info_match1.group(2)
    print(user_name)
    print(email)
    print(all_match)

search_match = info_pattern.search(my_str2)
if search_match:
    print("search_match successfully")
    all_match = info_match1.group(0)
    user_name = info_match1.group(1)
    email = info_match1.group(2)
    print(user_name)
    print(email)
    print(all_match)