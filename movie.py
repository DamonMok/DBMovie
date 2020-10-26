import ssl
import urllib.request, urllib.error
from bs4 import BeautifulSoup
import xlwt
import sqlite3


class MovieHandel(object):

    def __init__(self):
        # 取消全局ssl证书验证
        ssl._create_default_https_context = ssl._create_unverified_context
        self.base_url = "https://movie.douban.com/top250?start="
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36"
        }
        self.movie_list = []  # 电影信息集合

    def get_data(self):

        for page in range(0, 10):
            current_url = self.base_url + str(page * 25)
            html = self.get_html(current_url)

            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("li > .item"):

                movie = {}  # 电影信息字典
                movie.update({"image_link": item.select_one(".pic>a>img")["src"]})  # 图片链接
                movie.update({"detail_link": item.select_one(".pic>a")["href"]})  # 电影详情链接
                movie.update({"title": item.select(".hd>a>.title")[0].string})  # 标题
                movie.update({"sub_title": " "})  # 副标题
                if len(item.select(".hd>a>.title")) > 1:
                    movie.update({"sub_title": item.select(".hd>a>.title")[1].string})
                movie.update({"other_title": item.select(".hd>a>.other")[0].string})  # 其他标题
                movie.update({"desc": item.select_one(".bd>p").get_text().replace("\n", "").replace(" ", "")})  # 描述
                movie.update({"rating_num": item.select_one(".star>.rating_num").string})  # 评分
                movie.update({"comment_num": item.select(".star>span")[-1].string.replace("人评价", "")})  # 评价数
                movie.update({"inq": " "})  # 简述
                if len(item.select(".bd>.quote>span")) > 0:
                    movie.update({"inq": item.select(".bd>.quote>span")[0].string})

                self.movie_list.append(movie)

    def get_html(self, url):

        request = urllib.request.Request(url=url, headers=self.headers)
        response = None
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print(e.reason, e.code, e.headers, sep="\n")
        except urllib.error.URLError as e:
            print(e.reason)
        else:
            print("Request finished!")

        return response.read().decode("utf-8")

    def save2excel(self):
        """
        保存到Excel
        :return:
        """
        work_book = xlwt.Workbook(encoding="utf-8")
        work_sheet = work_book.add_sheet("movies_data")

        th_list = ["图片", "详情", "标题", "副标题", "其他标题", "描述", "评分数", "评价数", "简述"]
        for i in range(len(th_list)):
            # 写入头标题
            work_sheet.write(0, i, th_list[i])

        for i in range(len(self.movie_list)):
            # 写入电影信息
            movie = self.movie_list[i]

            j = 0
            for key, value in movie.items():
                work_sheet.write(i + 1, j, value)
                j = j + 1

        work_book.save("movies.xls")

    def save2db(self):
        """
        保存到数据库
        :return:
        """
        self.init_db()
        connect = sqlite3.connect("movies.db")
        cursor = connect.cursor()

        # 保存到数据库
        for movie in self.movie_list:
            print(movie)
            cursor.execute('insert into movie (image_link, detail_link, title, sub_title, other_title, desc, rating_num, comment_num, inq) values ("%s", "%s", "%s", "%s","%s", "%s","%s", "%s","%s")' % (movie["image_link"], movie["detail_link"], movie["title"], movie["sub_title"], movie["other_title"], movie["desc"], movie["rating_num"], movie["comment_num"], movie["inq"]))
            connect.commit()

        cursor.close()
        connect.close()

    @staticmethod
    def init_db():
        connect = sqlite3.connect("movies.db")
        cursor = connect.cursor()
        try:
            cursor.execute('''
                            create table movie(
                                id integer primary key autoincrement ,
                                image_link text ,
                                detail_link text ,
                                title varchar ,
                                sub_title varchar ,
                                other_title varchar ,
                                desc text,
                                rating_num varchar ,
                                comment_num varchar ,
                                inq varchar );''')
        except sqlite3.OperationalError as e:
            print(e)
        else:
            connect.commit()
            cursor.close()
            connect.close()
            print("Create table successful!")


if __name__ == '__main__':
    movie_handle = MovieHandel()
    movie_handle.get_data()
    movie_handle.save2excel()  # 保存到Excel
    # movie_handle.save2db()  # 保存到数据库
