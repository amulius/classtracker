# from django.test import TestCase
# from factories import PlayerFactory, WarGameFactory
# from ..models import Card, WarGame
#
#
# class CardModelTestCase(TestCase):
#     def setUp(self):
#         self.card = Card.objects.create(suit=Card.CLUB, rank="jack")
#         self.card_higher = Card.objects.create(suit=Card.CLUB, rank="ace")
#
#     def test_get_ranking(self):
#         self.assertEqual(self.card.get_ranking(), 11)
#
#     def test_war_result(self):
#         self.assertEquals(self.card_higher.get_war_result(self.card), 1)
#         self.assertEquals(self.card_higher.get_war_result(self.card_higher), 0)
#         self.assertEquals(self.card.get_war_result(self.card_higher), -1)
#
#
# class PlayerModelTestCase(TestCase):
#     def test_get_ties(self):
#         user = PlayerFactory.create(username='test-user', email='test@test.com', password='password')
#         WarGameFactory.create_batch(4, player=user, result=WarGame.TIE)
#         self.assertEqual(user.get_results(WarGame.TIE), 4)
#
#     def test_get_record_display(self):
#         user = PlayerFactory.create(username='test-user', email='test@test.com', password='password')
#         WarGameFactory.create_batch(2, player=user, result=WarGame.WIN)
#         WarGameFactory.create_batch(3, player=user, result=WarGame.LOSS)
#         WarGameFactory.create_batch(4, player=user, result=WarGame.TIE)
#         self.assertEqual(user.get_record_display(), "2-3-4")
