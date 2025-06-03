## python库matplotlib使用

### 加载中文字体

- 查看能显示的字体
  ```py
  from matplotlib import pyplot as plt
  import matplotlib
  a=sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist]) 

  for i in a:
        print(i)
  ```
  找到对应的中文字体，通常后面有CN两个标志

- 加载字体
  ```py
  plt.rcParams['font.sans-serif'] = ['AR PL UKai CN']
  ```
  即可.