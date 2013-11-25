weixin_pub
==========
运行文件管理：由于不同的控制级别和端口问题，需要自己创建运行文件
1. 外部添加运行文件，这个和git管理一起
2. 命名需要带有weixin_pub和个人信息，为了更好的管理和区分，比如：
lyw_weixin_pub.py
server_weixin_pub.py
test_server_weixin_pub.py
test_weixin_pub.py


配置文件管理：
1. 程序使用的配置文件是setting.py，但是这个文件不和git一起，为的是安全性，防止密码的泄露
2. 由于不同的开发环境和开发人员有自己的配置文件，我们统一把配置文件放在setting文件夹里面，这个配置的文件夹同样不在git管理里面
3. 如果需要部署新的环境，只需要在新的开发环境里面添加一个setting.py文件即可
4. 为了更好的配置，在外部添加一个setting.sample文件，这个就是基本的模板

数据库配置和管理：
1. 配置数据库的文件就是setting.py文件
2. 创建数据库，只需要导入相关的类到create_database.py文件，然后运行即可

包管理：
1. 最好使用相对导入的方式，就是 . 或者 .. 的方式