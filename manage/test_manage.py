import unittest
from participant import get_participants, is_participant, kick_participant
from friend import FriendManager

class ManageTests(unittest.TestCase):
    def setUp(self):
        self.users = {1: "김민수", 2: "이지훈", 3: "박서연", 4: "최유진"}
        self.room = {"owner_id": 1, "participants": [1, 2, 3]}
        self.manager = FriendManager(self.users)

    def test_participant_kick_and_membership(self):
        self.assertTrue(is_participant(self.room, 2))
        self.assertEqual(kick_participant(self.room, 1, 2), 2)
        self.assertFalse(is_participant(self.room, 2))
        self.assertEqual(get_participants(self.room), [1, 3])

    def test_kick_permissions(self):
        with self.assertRaises(PermissionError):
            kick_participant(self.room, 2, 3)
        with self.assertRaises(ValueError):
            kick_participant(self.room, 1, 1)

    def test_search_all_users(self):
        self.assertEqual([x["user_id"] for x in self.manager.search_users(1, "서연")], [3])
        self.assertEqual(len(self.manager.search_users(1)), 3)

    def test_room_recommendations_update_after_leave(self):
        self.assertEqual([x["user_id"] for x in self.manager.get_room_recommendations(1, self.room)], [2, 3])
        self.room["participants"].remove(2)
        self.assertEqual([x["user_id"] for x in self.manager.get_room_recommendations(1, self.room)], [3])

    def test_request_accept_is_mutual(self):
        self.assertEqual(self.manager.send_friend_request(1, 2), "pending")
        self.assertEqual(self.manager.get_friends(1), [])
        self.assertEqual(self.manager.get_received_requests(2)[0]["user_id"], 1)
        self.manager.accept_friend_request(2, 1)
        self.assertEqual(self.manager.get_friends(1), [2])
        self.assertEqual(self.manager.get_friends(2), [1])
        self.assertEqual(self.manager.get_sent_requests(1), [])

    def test_reject_deletes_request(self):
        self.manager.send_friend_request(1, 2)
        self.manager.reject_friend_request(2, 1)
        self.assertEqual(self.manager.get_received_requests(2), [])
        self.assertEqual(self.manager.get_sent_requests(1), [])
        self.assertEqual(self.manager.get_friends(1), [])

    def test_cancel_request(self):
        self.manager.send_friend_request(1, 2)
        self.manager.cancel_friend_request(1, 2)
        self.assertEqual(self.manager.get_received_requests(2), [])

    def test_duplicate_and_reverse_request(self):
        self.manager.send_friend_request(1, 2)
        with self.assertRaises(ValueError):
            self.manager.send_friend_request(1, 2)
        self.assertEqual(self.manager.send_friend_request(2, 1), "incoming_request_exists")
        self.manager.accept_friend_request(2, 1)
        self.assertEqual(self.manager.get_friends(1), [2])

    def test_block_removes_pending_and_prevents_request(self):
        self.manager.send_friend_request(1, 2)
        self.manager.block_user(2, 1)
        self.assertEqual(self.manager.get_sent_requests(1), [])
        with self.assertRaises(ValueError):
            self.manager.send_friend_request(1, 2)
        self.manager.unblock_user(2, 1)
        self.manager.send_friend_request(1, 2)

    def test_remove_friend_and_invalid_user(self):
        self.manager.send_friend_request(1, 2)
        self.manager.accept_friend_request(2, 1)
        self.manager.remove_friend(1, 2)
        self.assertEqual(self.manager.get_friends(2), [])
        with self.assertRaises(ValueError):
            self.manager.send_friend_request(1, 99)

if __name__ == "__main__":
    unittest.main(verbosity=2)
