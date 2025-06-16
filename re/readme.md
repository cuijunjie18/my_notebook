# 正则表达式的使用

## 正则表达式常用操作符

|操作符 |	说明 |	实例|
|--|-- |-- |
|. 	|表示任何单个字符（默认除换行符）|| 	 
|[] |	字符集，对单个字符给出取值范围 |	[abc]表示a、b、c，[a-z]表示a到z的单个字符|
|[^] 	|非字符集，对单个字符给出排除范围 |	[^abc]表示非a或非b或非c的单个字符|
|* 	|前一个字符0次或无限次扩展| 	abc*表示ab、abc、abcc、abccc等|
|+ 	|前一个字符1次或无限次扩展 |	abc+表示abc、abcc、abccc等|
|? 	|前一个字符0次或1次扩展 	|abc*表示ab、abc |
|\| |左右表达式任意一个 |	abc\|def表示abc、def |
|{m} |	扩展前一个字符m次 |	ab{2}c表示abbc|
|{m,n} 	|扩展前一个字符m至n次（含n） 	|ab{1,2}c表示abc,abbc|
|^ 	|匹配字符串开头 	|abc且在一个字符串的开头|
|$ 	|匹配字符串结尾 	|abc且在一个字符串的结尾|
|() 	|分组标记，内部只能使用\|操作符 |(abc)表示abc,(abc\|def)表示abc、def|
|\d 	|数字，等价于[0-9]|
|\w 	|单词字符，等价于[A-Za-z0-9_ ]|

## 语法实例

|正则表达式 	|对应字符串|
|-|-|
|P(Y\|YT\|YTH\|YTHO)?N 	|‘PN’、’PYN’、’PYTN’、’PYTHN’、’PYTHON’|
|PYTHON+ 	|‘PYTHON’、’PYTHONN’、’PYTHONNN’……|
|PY[TH]ON 	|‘PYTON’、’PYHON’|
|PY[^TH]?ON |	‘PYON’、’PYaON’、’PYbON’、’PYcON’……|
|PY{:3}ON 	|‘PN’、’PYN’、’PYYN’、’PYYYN’|

## 经典实例

|正则表达式 	|意义|
|-|-|
|\^[A-Za-z]+$ 	|由26个字母组成的字符串|
|\^[A-Za-z0-9]+$ |	由26个字母和数字组成的字符串|
|^-?\d+$ 	|整数形式的字符串|
|^ [1-9]\*[0-9]*$ 	|正整数形式的字符串|
|[1-9]\d{5} 	|中国境内邮政编码，6位|
|[\u4e00-\u9fa5] |	匹配中文字符|
|\d{3}-\d{8}\|\d{4}-\d{7} |	国内电话号码 3位-8位或4位-7位|

## python re库的使用

### re库的核心函数集

|函数 	|说明|
|-|-|
|re.search() 	|从一个字符串中搜索匹配正则表达式的第一个位置，返回match对象|    
|re.match() 	|从一个字符串的开始位置起匹配正则表达式，返回match对象|
|re.findall() 	|搜索字符串，以列表类型返回全部能匹配的子串|
|re.split() 	|将一个字符串按照正则表达式匹配结果进行分割，返回列表类型|
|re.finditer() 	|搜索字符串，返回一个匹配结果的迭代类型，每个迭代元素是match对象|
|re.sub() 	    |在一个字符串中替换所有匹配正则表达式的子串，返回替换后的字符串|

**注意区分search()与match()，其实我一般用search更多**

### 具体使用

- search使用
  ```shell
  import re
  output_text = '```json\n[\n\t{"bbox_2d": [359, 170, 580, 326], "label": "a truck number 14 on a snow bank"}\n]\n```'
  x = re.search('"bbox_2d":',output_text)
  start = x.start()
  end = x.end()
  print(start,end)
  output_text = output_text[end:]
  a = output_text.find("[")
  b = output_text.find("]")
  output_text = output_text[a:b + 1]
  print(output_text)
  x = eval(output_text) # 将字符串当指令使用，eval
  print(type(x),x)
  ```

## 后记

参考文章：https://www.cnblogs.com/huskysir/p/12467491.html