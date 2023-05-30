import unittest
from app import app, db, Book, YourBooks

class MicroserviceTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        book = Book(title='Harry Potter', author='J.K. Rowling', publication_year=1997)
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            book_id = book.id
        response = self.app.get(f'/delete/{book_id}')
        self.assertEqual(response.status_code, 302) 

        with app.app_context():
            deleted_book = Book.query.get(book_id)
        self.assertIsNone(deleted_book)

    def test_update(self):
        book = Book(title='Hobbit', author='J.R.R. Tolkien', publication_year=2023)
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            book_id = book.id

        response = self.app.post(f'/update/{book_id}', data={
            'bookTitle': 'Updated Title',
            'bookAuthor': 'Updated Author',
            'publicationYear': '2023'
        })
        self.assertEqual(response.status_code, 302)  # Redirect code

        with app.app_context():
            updated_book = Book.query.get(book_id)
        self.assertEqual(updated_book.title, 'Updated Title')
        self.assertEqual(updated_book.author, 'Updated Author')
        self.assertEqual(updated_book.publication_year, 2023)

    def test_your_books(self):
        response = self.app.get('/your_books/')
        self.assertEqual(response.status_code, 200)

    def test_move_book(self):
        book = Book(title='Hobbit', author='J.R.R. Tolkien', publication_year=1937)
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            book_id = book.id

        response = self.app.post('/your_books/', data={'bookId': book_id})
        self.assertEqual(response.status_code, 302)  # Redirect code

        with app.app_context():
            moved_book = Book.query.get(book_id)
            your_books = YourBooks.query.all()

        if moved_book != None:
            self.assertIsNotNone(moved_book, 'The book should exist')
            self.assertEqual(moved_book.quantity, 0, 'The book quantity should be 0')
            self.assertEqual(len(your_books), 1, 'There should be one book in Your Books')

    def test_delete_your_books(self):
        your_book = YourBooks(title_your='Hobbit', author_your='J.R.R. Tolkien', publication_year_your=1937)
        with app.app_context():
            db.session.add(your_book)
            db.session.commit()
            your_book_id = your_book.id_your

        response = self.app.get(f'/delete_your/{your_book_id}')
        self.assertEqual(response.status_code, 302)  # Redirect code

        with app.app_context():
            deleted_your_book = YourBooks.query.get(your_book_id)
        self.assertIsNone(deleted_your_book)


if __name__ == '__main__':
    unittest.main()
