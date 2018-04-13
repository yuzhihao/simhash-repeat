#### simhash去重

simhash值的存储与检索采用网上开源代码  
修改后代码位置：./lib/simhash_db

其中依赖的simhashx需要自己生成到python库:  
1. 需先安装[`libJudy`](http://judy.sourceforge.net/)  
2. 然后在 ./lib/simhash_deploy 目录下运行：
```
	python setup.py install
```

OK