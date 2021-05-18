from player import Player
from throw import Throw

ANSWER_YES = ["y", "yes"]
ANSWER_NO = ["n", "no"]
ANSWER_ABORT = ["x", "leave", "exit", "abort"]


class UserPlayer(Player):
    def __init__(self, playerId: int = None):
        super().__init__(playerId)

    def getDoubt(self, lastThrow: Throw):
        doubt = self.getInputYesNo(f"Do you trust the previous player that they threw {lastThrow.value}? ")
        return doubt

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw) -> Throw:
        truth = self.getInputYesNo(f"You threw {myThrow.value}. Do you tell the truth? ")
        if truth:
            return myThrow
        else:
            return self.getInputNumber(f"You chose to lie. What result do you tell the other players? ")

    @staticmethod
    def getInputYesNo(self, prompt: str):
        gotAnswer = False
        response: bool = None
        print(prompt, end="")
        while not gotAnswer:
            answ = input().lower()
            if answ in ANSWER_YES:
                gotAnswer = True
                response = True
            elif answ in ANSWER_NO:
                gotAnswer = True
                response = False
            elif answ in ANSWER_ABORT:
                break
            else:
                print(f"Allowed answers are {'/'.join(ANSWER_YES + ANSWER_NO)}. Try again: ", end="")

        return gotAnswer, answ

    @staticmethod
    def getInputNumber(self, prompt: str, allowedAnswers: list = None):
        gotAnswer = False
        answer: int = None
        print(prompt, end="")
        while not gotAnswer:
            answ = input().lower()
            if answ in ANSWER_ABORT:
                break
            try:
                answ = int(answ)
            except ValueError:
                print("That is not a number. Try again: ", end="")
                continue
            if answ in allowedAnswers:
                gotAnswer = True
            else:
                print(
                    f"Answer is not an allowed number. (Allowed numbers are: {', '.join(allowedAnswers)}). Try again: ",
                    end="")
                continue

        return gotAnswer, answ
