import ssl
import urllib.request
from bs4 import BeautifulSoup
import xlwt


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
            html = self.get_html()

            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("li > .item"):

                movie = {}  # 电影信息字典
                movie.update({"image_link": item.select_one(".pic>a>img")["src"]})  # 图片链接
                movie.update({"detail_link": item.select_one(".pic>a")["href"]})  # 电影详情链接
                movie.update({"title": item.select(".hd>a>.title")[0].string})  # 标题
                movie.update({"sub_title": " "})   # 副标题
                if len(item.select(".hd>a>.title")) > 1:
                    movie.update({"sub_title": item.select(".hd>a>.title")[1].string})
                movie.update({"other_title": item.select(".hd>a>.other")[0].string})  # 其他标题
                movie.update({"desc": item.select_one(".bd>p").get_text().replace("\n", "").replace(" ", "")})  # 描述
                movie.update({"rating_num": item.select_one(".star>.rating_num").string})  # 评分
                movie.update({"comment_num": item.select(".star>span")[-1].string.replace("人评价", "")})  # 评价数
                movie.update({"inq": item.select_one(".bd>.quote>span").string})  # 简述

                self.movie_list.append(movie)

    def get_html(self):

        request = urllib.request.Request(url=self.base_url, headers=self.headers)
        response = urllib.request.urlopen(request)

        return response.read().decode("utf-8")

    def save(self):

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
                j = j+1

        work_book.save("movies.xls")


if __name__ == '__main__':
    movie_handle = MovieHandel()
    movie_handle.get_data()
    movie_handle.save()