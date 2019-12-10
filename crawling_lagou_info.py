import json
import requests
import xlwt
import time


# 获取存储职位信息的json对象，遍历获得公司名、福利待遇、工作地点、学历要求、工作类型、发布时间、职位名称、薪资、工作年限
def get_json(url, datas):
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        "Referer": "https://www.lagou.com/jobs/list_python?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    time.sleep(5)
    ses = requests.session()  # 获取session
    ses.headers.update(my_headers)  # 更新
    ses.get(
        "https://www.lagou.com/jobs/list_python?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput="
        )
    content = ses.post(url=url, data=datas)
    result = content.json()
    info = result['content']['positionResult']['result']
    info_list = []
    for job in info:
        information = list(job.values())
        info_list.append(information)
    return info_list


def main():
    page = int(input('请输入你要抓取的页码总数：'))
    kd = input('请输入你要抓取的职位关键字：')
    # city = input('请输入你要抓取的城市：')

    info_result = []
    title = ['岗位id', '城市', '公司全名', '福利待遇', '工作地点', '学历要求', '工作类型', '发布时间', '职位名称', '薪资', '工作年限']
    info_result.append(title)
    for x in range(1, page + 1):
        url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
        datas = {
            'first': 'false',
            'pn': x,
            'kd': kd,
        }
        try:
            info = get_json(url, datas)
            info_result = info_result + info
            print("第{}页正常采集".format(x))
        except Exception as msg:
            print("第{}页采集出现异常".format(x))
            raise msg

        # 创建workbook,即excel
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建表,第二参数用于确认同一个cell单元是否可以重设值
        worksheet = workbook.add_sheet('lagouzp', cell_overwrite_ok=True)
        for i, row in enumerate(info_result):
            # print(row)
            for j, col in enumerate(row):
                # print(col)
                worksheet.write(i, j, col)
        workbook.save('lagouzp.xls')


if __name__ == '__main__':
    main()
