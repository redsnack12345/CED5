import unittest
from participant import get_participants, kick_participant
from friend import FriendManager

class ManageTests(unittest.TestCase):
    def setUp(self):
        self.room = {'owner_id': 1, 'participants': [1, 2, 3]}
        self.manager = FriendManager([1, 2, 3])

    def test_kick(self):
        self.assertEqual(kick_participant(self.room, 1, 2), 2)
        self.assertEqual(get_participants(self.room), [1, 3])

    def test_permission(self):
        with self.assertRaises(PermissionError):
            kick_participant(self.room, 2, 3)

    def test_owner_and_missing(self):
        for target in (1, 9):
            with self.assertRaises(ValueError):
                kick_participant(self.room, 1, target)
        self.assertEqual(get_participants(self.room), [1, 2, 3])

    def test_friend(self):
        self.manager.add_friend(1, 2)
        self.assertEqual(self.manager.get_friends(2), [1])
        with self.assertRaises(ValueError):
            self.manager.add_friend(2, 1)
        self.manager.remove_friend(2, 1)
        self.assertEqual(self.manager.get_friends(1), [])

    def test_block(self):
        self.manager.add_friend(1, 2)
        self.manager.block_user(1, 2)
        self.assertEqual(self.manager.get_friends(2), [])
        self.assertEqual(self.manager.get_blocked_users(1), [2])
        self.assertEqual(self.manager.get_blocked_users(2), [])
        with self.assertRaises(ValueError):
            self.manager.add_friend(2, 1)
        self.manager.unblock_user(1, 2)
        self.manager.add_friend(2, 1)
        self.assertEqual(self.manager.get_friends(1), [2])

    def test_invalid_users(self):
        for target in (1, 9):
            with self.assertRaises(ValueError):
                self.manager.add_friend(1, target)

if __name__ == '__main__':
    unittest.main(verbosity=2)
