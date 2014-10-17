# from django.test import TestCase
# from factories import WarGameFactory, PlayerFactory
# from ..models import WarGame
#
#
# class UserGetWinLossTestCase(TestCase):
#     def setUp(self):
#         self.user = PlayerFactory.create()
#         WarGameFactory.create_batch(2, player=self.user, result=WarGame.WIN)
#         WarGameFactory.create_batch(3, player=self.user, result=WarGame.LOSS)
#
#     def test_get_wins(self):
#         self.assertEqual(self.user.get_results(WarGame.WIN), 2)
#
#     def test_get_losses(self):
#         self.assertEqual(self.user.get_results(WarGame.LOSS), 3)
