import unittest

from base import BaseTestCase



# class ProjectTests(BaseTestCase):
    
    
#     # Ensure a logged in user can add a new post
#     def test_user_can_post(self):
#         with self.client:
#             self.client.post(
#                 '/login',
#                 data=dict(username="admin", password="admin"),
#                 follow_redirects=True
#             )
#             response = self.client.post(
#                 '/projects/new',
#                 data=dict(title="test project", 
#                           description="test",
#                           category="convergence behaviour"),
#                 follow_redirects=True
#             )
#             self.assertEqual(response.status_code, 200)
#             self.assertIn(b'You successfully added a project.', response.data)


# if __name__ == '__main__':
#     unittest.main()