# tripitaka-simple

基于 tornado 的切栏校对应用（本地版，无云服务存储和任务管理）。

## 安装

1. 安装 Python 3.6 和 pip。

2. 安装本项目的 Python 依赖包：
```
pip install -r requirements.txt
```

3. 将栏切分的 img 和 pos 文件夹复制到 static 目录下，有增加或改动后直接更新即可。

   可运行 `python static/resize-image.py` 缩小页面图和检查切分JSON的正确性。

## 运行

- 在 PyCharm 中选中 app.py 右键点“Debug app”，或在命令行中运行 `python app.py`。

- 在浏览器中打开 [localhost:8001](http://localhost:8001)

## 参考资料

- [Tornado Web应用结构](https://segmentfault.com/a/1190000004240965)
- [Tornado 4.3 文档中文版](https://tornado-zh.readthedocs.io/zh/latest/)
- [前端模板语法](https://tornado-zh.readthedocs.io/zh/latest/guide/templates.html)
