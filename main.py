from game import Game
from player import DummyPlayer, ShowOffPlayer

if __name__ == '__main__':
    game = Game([*[DummyPlayer()] * 3, ShowOffPlayer()])

    game.init()
    game.run()
