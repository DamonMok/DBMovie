from flask import Flask, render_template
from movie import MovieHandel

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    movies = MovieHandel.movie_from_db()
    new = movies[0:6]
    top_rated = movies[6:12]
    hot_comment = movies[12:18]
    context = {"new": new, "top_rated": top_rated, "hot_comment": hot_comment}
    return render_template('index.html', context=context)


if __name__ == '__main__':
    app.run()
