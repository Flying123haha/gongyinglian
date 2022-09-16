db_neo4j为neo4j中的数据
sckg_v1为Django项目
    环境要求：
        neo4j及py2neo：能跑起来就行
        py2pinyin
        django
        python3.7


cd /data1/flying/neo4j-community-4.4.7/bin
./neo4j start
cd /data1/flying/code/aistudy/sckg/sckg_v1
运行Django：
python manage.py runserver 0.0.0.0:8005
