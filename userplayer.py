import constants as c
from player import Player
from throw import Throw
from random import Random

ANSWER_YES = ["y", "yes"]
ANSWER_NO = ["n", "no"]
ANSWER_ABORT = ["x", "leave", "exit", "abort"]


class UserPlayer(Player):
    def __init__(self, playerId: int = None) -> None:
        super().__init__(playerId)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: Random) -> bool:
        gotAnsw, trust = self.getInputYesNo(f"Do you trust the previous player that they threw {lastThrow.value}? ")
        return not trust if gotAnsw else None

    def getThrowStated(self, myThrow: Throw, lastThrow: Throw, iMove: int, rng: Random) -> Throw:
        beatsLast = myThrow > lastThrow
        truthPrompt = f"You threw {myThrow.value}, which " + ("doesn't beat" if not beatsLast else "beats") + \
                      f" the previous player, who threw {lastThrow}. Do you tell the truth? "
        gotAnsw, truth = self.getInputYesNo(truthPrompt)
        if not gotAnsw:
            return None
        truthConfirm = False
        if truth and not beatsLast:
            gotAnswer, truthConfirm = self.getInputYesNo("By doing this you will lose this round. Are you sure? ")
            # Keine Antowort bedeutet, dass der Benutzer das Spiel abbrechen möchte. Deshalb wird bestätigt,
            # ein zu niedriges Ergebnis anzugeben, um direkt auszuscheiden
            truthConfirm = truthConfirm or (not gotAnswer)
        if truth and (beatsLast or truthConfirm):
            return myThrow
        else:
            gotAnsw, throwStated = self.getInputNumber(f"You chose to lie. What result do you tell the other players? ",
                                              allowedAnswers=c.THROW_VALUES)
            return Throw(throwStated) if gotAnsw else None

    @staticmethod
    def getInputYesNo(prompt: str) -> tuple[bool, bool]:
        gotAnswer = False
        answ: bool = None
        print(prompt, end="")
        while not gotAnswer:
            inp = input().lower()
            if inp in ANSWER_YES:
                gotAnswer = True
                answ = True
            elif inp in ANSWER_NO:
                gotAnswer = True
                answ = False
            elif inp in ANSWER_ABORT:
                break
            else:
                print(f"Allowed answers are {'/'.join(ANSWER_YES + ANSWER_NO)}. Try again: ", end="")

        return gotAnswer, answ

    @staticmethod
    def getInputNumber(prompt: str, allowedAnswers: list = None) -> tuple[bool, int]:
        gotAnswer = False
        answ: int = None
        print(prompt, end="")
        while not gotAnswer:
            inp = input().lower()
            if inp in ANSWER_ABORT:
                break
            try:
                answ = int(inp)
            except ValueError:
                print("That is not a number. Try again: ", end="")
                continue
            if answ in allowedAnswers:
                gotAnswer = True
            else:
                print(
                    f"Your input {answ} is not an allowed number. (Allowed numbers are: {', '.join([str(a) for a in allowedAnswers])}).\nTry again (\"{ANSWER_ABORT[0]}\" to exit): ",
                    end="")
                continue

        return gotAnswer, answ
