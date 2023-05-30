from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_restful import Resource, Api
import json

app = Flask(__name__)
fa = FontAwesome(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookShop.db'
db = SQLAlchemy(app)
api = Api(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Book {self.id}: {self.title} by {self.author}>'

class YourBooks(db.Model):
    id_your = db.Column(db.Integer, primary_key=True)
    title_your = db.Column(db.String(200), nullable=False)
    author_your = db.Column(db.String(200), nullable=False)
    publication_year_your = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Book {self.id_your}: {self.title_your} by {self.author_your}>'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['bookTitle']
        author = request.form['bookAuthor']
        publication_year = request.form['publicationYear']

        new_book = Book(title=title, author=author, publication_year=publication_year)

        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'Error adding the book to the database: {str(e)}'

    else:
        books = Book.query.order_by(Book.publication_year.desc()).all()
        return render_template('index.html', books=books)


@app.route('/delete/<int:id>')
def delete(id):
    book_to_delete = Book.query.get_or_404(id)

    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue with deleting the book.'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    book = Book.query.get_or_404(id)

    if request.method == 'POST':
        book.title = request.form['bookTitle']
        book.author = request.form['bookAuthor']
        book.publication_year = request.form['publicationYear']

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'Error updating the book: {str(e)}'
    else:
        return render_template('update.html', book=book)


@app.route('/your_books/')
def your_books():
    your_books = YourBooks.query.all()
    return render_template('your_books.html', your_books=your_books)

@app.route('/your_books/', methods=['POST'])
def move_book():
    book_id = request.form['bookId']
    book_to_move = Book.query.get_or_404(book_id)
    try:
        existing_book = YourBooks.query.filter_by(title_your=book_to_move.title).first()
        if existing_book:
            existing_book.quantity += 1
        else:
            new_book_your = YourBooks(
                title_your=book_to_move.title,
                author_your=book_to_move.author,
                publication_year_your=book_to_move.publication_year
            )
            db.session.add(new_book_your)
        book_to_move.quantity -= 1
        if book_to_move.quantity == 0:
            db.session.delete(book_to_move)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'Error moving the book: {str(e)}'

@app.route('/delete_your/<int:id>')
def delete_yourBooks(id):
    book_to_delete_your = YourBooks.query.get_or_404(id)
    try:
        book_to_delete_your.quantity -= 1
        if book_to_delete_your.quantity == 0:
            db.session.delete(book_to_delete_your)
        db.session.commit()
        return redirect('/your_books/')
    except:
        return 'There was an issue with deleting the book.'



class BookResource(Resource):
    def get(self, id=None):
        if id is None:
            books = Book.query.order_by(Book.publication_year.desc()).all()
            return [self.serialize_book(book) for book in books]
        else:
            book = Book.query.get_or_404(id)
            return self.serialize_book(book)

    def post(self):
        title = request.form['bookTitle']
        author = request.form['bookAuthor']
        publication_year = request.form['publicationYear']

        new_book = Book(title=title, author=author, publication_year=publication_year)

        try:
            db.session.add(new_book)
            db.session.commit()
            return {'message': 'Book added successfully'}, 201
        except Exception as e:
            return {'error': f'Error adding the book to the database: {str(e)}'}, 500

    def put(self, id):
        book = Book.query.get_or_404(id)
        book.title = request.form['bookTitle']
        book.author = request.form['bookAuthor']
        book.publication_year = request.form['publicationYear']
        try:
            db.session.commit()
            return {'message': 'Book updated successfully'}
        except Exception as e:
            return {'error': f'Error updating the book: {str(e)}'}, 500

    def delete(self, id):
        book_to_delete = Book.query.get_or_404(id)

        try:
            db.session.delete(book_to_delete)
            db.session.commit()
            return {'message': 'Book deleted successfully'}
        except:
            return {'error': 'There was an issue with deleting the book.'}, 500

    @staticmethod
    def serialize_book(book):
        serialized = book.__dict__.copy()
        serialized.pop('_sa_instance_state', None)
        return serialized

api.add_resource(BookResource, '/books_api', '/books_api/<int:id>')


class BookResourceOfYourBooks(Resource):
    def get(self, id=None):
        if id is None:
            your_books = YourBooks.query.order_by(YourBooks.publication_year_your.desc()).all()
            return [self.serialize_book(book) for book in your_books]
        else:
            your_book = YourBooks.query.get_or_404(id)
            return self.serialize_book(your_book)

    def post(self):
        title_your = request.form['title_your']
        author_your = request.form['author_your']
        publication_year_your = request.form['publication_year_your']

        new_your_book = YourBooks(title_your=title_your, author_your=author_your, publication_year_your=publication_year_your)
        try:
            db.session.add(new_your_book)
            db.session.commit()
            return {'message': 'Book added successfully'}, 201
        except Exception as e:
            return {'error': f'Error adding the book to the database: {str(e)}'}, 500

    def put(self, id):
        book = YourBooks.query.get_or_404(id)
        book.title_your = request.form['title_your']
        book.author_your = request.form['author_your']
        book.publication_year_your = request.form['publication_year_your']
        try:
            db.session.commit()
            return {'message': 'Book updated successfully'}
        except Exception as e:
            return {'error': f'Error updating the book: {str(e)}'}, 500

    def delete(self, id):
        your_book_to_delete = YourBooks.query.get_or_404(id)
        try:
            db.session.delete(your_book_to_delete)
            db.session.commit()
            return {'message': 'Book deleted successfully'}
        except:
            return {'error': 'There was an issue with deleting the book.'}, 500

    @staticmethod
    def serialize_book(book):
        serialized = book.__dict__.copy()
        serialized.pop('_sa_instance_state', None)
        return serialized

api.add_resource(BookResourceOfYourBooks, '/your_books_api/', '/your_books_api/<int:id>')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
