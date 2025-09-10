from flask import Flask, render_template, request, redirect , url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"{self.Sno}-{self.title}"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
        # Redirect after POST to avoid duplicate submissions
        return redirect(url_for('home'))

    alltodo = Todo.query.all()
    return render_template('index.html', alltodo=alltodo)


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(Sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(Sno=sno).first()
    if request.method == "POST":
        todo.title = request.form.get('title')
        todo.desc = request.form.get('desc')
        db.session.commit()
        return redirect("/")
    return render_template('update.html', todo=todo)


@app.route("/about")
def about():
    return render_template("about.html")


# New search route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()

    if not query:
        # If query is empty, show all todos
        results = []
    elif query.isdigit():
        # If search query is numeric, search by Sno
        results = Todo.query.filter(Todo.Sno == int(query)).all()
    else:
        # Else, search by title or description
        results = Todo.query.filter(
            or_(
                Todo.title.ilike(f"%{query}%"),
                Todo.desc.ilike(f"%{query}%")
            )
        ).all()

    return render_template("search.html", alltodo=results, query=query)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
