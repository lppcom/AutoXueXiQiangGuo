# 写在最前
项目地址来源 
https://github.com/kessil/AutoXue  
因原作者不再更新，仅作研究学习用，切勿用于商业用途。
# 使用方法，一定要先读！！
1、配置环境，参考原作者的配置教程，这点非常重要

2、运行setup.cmd,如果安装不上相关组件，用记事本打开，手动安装

3、用户名在default.ini里配置，可以配置多用户，也可以单用户。一定要配置！！



## 免责申明
`AutoXueXiQiangGuo`为本人`Python`学习交流的开源非营利项目，仅作为`Python`学习交流之用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止使用`AutoXue`进行任何盈利活动。对一切非法使用所产生的后果，本人概不负责。
安装：

0. 如果之前添加过环境变量`ADB1.0.40`请确保删除之

1. 安装`JDK`，本文使用JDK1.8
    + 在环境变量中新建`JAVA_HOME`变量，值为JDK安装路径，如`C:\Program Files\Java\jdk1.8.0_05`
    + 新建`CLASSPATH`变量，值为`.;%JAVA_HOME%\lib;%JAVA_HOME%\lib\tools.jar;`
    + `Path`变量中添加：`%JAVA_HOME%\bin和%JAVA_HOME%\jre\bin`
    
2. 安装`SDK`，本文使用SDK r24.4.1
    + 在环境变量中新建`ANDROID_HOME`，值为SDK安装路径，如`C:\Program Files (x86)\Android\android-sdk`
    + 在Path变量中添加项：`%ANDROID_HOME%\platform-tools` 和 `%ANDROID_HOME%\tools`
    + 打开`SDK Manager.exe` 安装对应的工具和包,根据安卓版本进行安装，**Tools**和**Build-tools**别漏
    ![avatar](https://github.com/kessil/AutoXue/raw/dev/image-20200601204634969.png)
    
3. 安装`Appium",推荐通过npm安装，这样可以一键自动学习，无需通过点击启动service
     appium本质是一个nodejs库所以要先安装nodejs，然后使用npm安装。
    3.1nodejs下载地址：https://nodejs.org/zh-cn/download/
    3.2下载zip包解压到自己想放的目录，然后把该目录加入Path环境变量即可。
    3.3运行 npm install -g appium
    3.4使用appinum-doctor确认环境配置无误
        npm install -g appium-doctor
        appium-doctor --android
        
4. 安装一个Android模拟器。

5. 安装`Python3.8

## 使用方法(windows)
双击运行xuexi.exe

