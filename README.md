# senz.app.activity.mapping
senz user activities mapping service


### config.py
  主要保存了当前项目的所有的config 信息，其中涉及到数据库信息和一些常用的常量。
  
### util.py
  主要是封装了一些数据库操作，包括从mongdb 中获取用户的traces 信息，从leancloud上查询events信息，保存匹配结果等。
  
### mapper.py
  活动匹配的核心代码
  
### main.py
  测试程序的入口


## 运行此程序需要 安装依赖的包
  pip install -r requirement.txt
  
