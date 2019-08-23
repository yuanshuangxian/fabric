执行文件  fabfileStart.py  运行前引入fabric模块

配置文件  server.conf

参数说明
            "user":"root",                                   ---服务器账号
            "name":"us1b001_API",                            ---服务器名,自定义
            "target":"/data",                                ---根目录
            "ip":"XX.XX.XXX.XXX",                            ---服务器IP
            "port":22,                                       ---服务器端口
            "password":"Sdkus1b001",                         ---服务器密码
            "jarname":"sdk-server-us-v2.jar",                ---运行jar名
            "server_dir":"server"                            ---项目所在目录API为server ad_exchange为adex_server


该工具重启功能还有问题，暂不使用！！！！！！

上传步骤：

1 在fabric目录下创建项目文件夹,API为server ad_exchange为adex_server,将上传的文件按服务器目录结构拷贝至项目文件夹

2 压缩成server.tar.gz文件就可以运行fabfileStart.py进行上传

3 按提示选择选项： ——上传——选择上传服务器——按Enter继续——按Enter上传至所有实例文件夹