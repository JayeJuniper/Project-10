import unittest

from peewee import *

from app import app
from models import Todo


DATABASE = SqliteDatabase(':memory:')


class ApiTestCase(unittest.TestCase):
    '''create tables and instantiate database'''
    def setup (self):
        models = [todo]
        DATABASE.bind(models)
        DATABASE.create_tables(models, safe=True)
        self.todo_resources = [
            {'name': "test1"},
            {'name': "test2"},
            {'name': "test3"}
        ]
        with DATABASE.transaction():
            Todo.insert_many(self.todo_resources).execute()

    def teardown(self):
        with DATABASE:
            DATABASE.drop_tables([todo])


class TestNoTodos(ApiTestCase):
    '''Verify that a HTTP response returns a 404 status status
    when no Todo resources in the TodoList resource [GET]'''
    def setUp(self):
        super().setUp()
        delete_todos = Todo.delete().where(Todo.id >= 1)
        delete_todos.execute()

    def test_no_todo_list_resource(self):
        with app.test_client() as client:
            resp = client.get("api/v1/todos")
        self.assertEqual(resp.status_code, 404)


class TestGetTodoList(ApiTestCase):
    '''Verify that all todo resources are sent back 
    to the client with a 200 status code [GET].'''
    def test_todo_collection_resource(self):
        with app.test_client() as client:
            resp = client.get("/api/v1/todos")
        self.assertEqual(resp.status_code, 200)


class TestTodo(ApiTestCase):
    '''Test Todo Post, Get, Put, and Delete'''
    def setUp(self):
        super().setUp()
        self.app = app.test_client()
        self.app.testing = True
        self.todo_count = Todo.select().count()

    def test_todo_post_success(self):
        '''Test that the client recieves a
         201 status after creating a Todo.'''
        resp = self.app.post("/api/v1/todos", data={"name": "test 1"})
        self.assertEqual(resp.status_code, 201)
        self.assertGreater(Todo.select().count(), self.todo_count)

    def test_todo_get_success(self):
        '''Test that the client recieves a 200 
        status after successfully retrieving data.'''
        resp1 = self.app.post("/api/v1/todos", data={"name": "test 1"})
        resp2 = self.app.get(
            '/api/v1/todos/{}'.format(Todo.get(name='test 1').id)
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('test 1', str(resp1.data))

    def test_todo_get_fail(self):
        '''Test the the client recieves a 404 status 
        when attempting to retrieve an invalid resource.'''
        resp = self.app.get('/api/v1/todos/200')
        self.assertEqual(resp.status_code, 404)

    def test_todo_put_success(self):
        '''Test that the client recieves a 200 
        status when updating a resource.'''
        resp = self.app.put("/api/v1/todos/1", data={"name": "test 2"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('test 2', resp.get_data(as_text=True))

    def test_todo_delete_success(self):
        '''Test that the client recieves a 204 status 
        when successfully deleting a resource.'''
        resp = self.app.delete('/api/v1/todos/1')
        self.assertEqual(resp.status_code, 204)
        self.assertNotIn('test 1', resp.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
