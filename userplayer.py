from typing import Optional, List, Tuple

import constants as c
from player import Player
from throw import Throw
from random import Random

ANSWER_YES = ["y", "yes"]
ANSWER_NO = ["n", "no"]
ANSWER_ABORT = ["x", "leave", "exit", "abort"]


class UserPlayer(Player):
    def __init__(self, player_id: int = None) -> None:
        super().__init__(player_id)

    def getDoubt(self, lastThrow: Throw, iMove: int, rng: Random) -> Optional[bool]:
        gotAnsw, trust = self.getInputYesNo(f"Do you trust the previous player that they threw {lastThrow.value}?")
        return not trust if gotAnsw else None

    def getThrowStated(self, myThrow: Throw, lastThrow: Optional[Throw], iMove: int, rng: Random) -> Optional[Throw]:
        # Spieler fragen, ob er die Wahrheit sagen will
        if lastThrow is None:
            truthPrompt = f"You threw {myThrow.value} (no predecessor). Will you tell this result to the other players?"
            beatsLast = True  # Has to be True so later checks work
        else:
            beatsLast = myThrow > lastThrow
            truthPrompt = f"You threw {myThrow.value}, which " + ("doesn't beat" if not beatsLast else "beats") + \
                          f" the previous player, who threw {lastThrow}. Do you tell the truth?"
        gotAnsw, truth = self.getInputYesNo(truthPrompt)
        if not gotAnsw:
            return None
        truthConfirm: Optional[bool] = False
        if truth and not beatsLast:
            gotAnswer, truthConfirm = self.getInputYesNo("By doing this you will lose this round. Are you sure?")
            # Keine Antowort bedeutet, dass der Benutzer das Spiel abbrechen möchte. Deshalb wird bestätigt,
            # ein zu niedriges Ergebnis anzugeben, um direkt auszuscheiden
            truthConfirm = truthConfirm or (not gotAnswer)
        if truth and (beatsLast or truthConfirm):
            return myThrow
        else:
            gotAnsw, throwStated = self.getInputNumber(f"You chose to lie. What result do you tell the other players?",
                                              allowedAnswers=c.THROW_VALUES)
            if throwStated is None:
                return None
            else:
                return Throw(throwStated)

    @staticmethod
    def getInputYesNo(prompt: str) -> Tuple[bool, Optional[bool]]:
        """Request a yes/no input from the user and return success and the value of the input.

        The first element of the returned tuple reports the success of the user input.
        The second element containts the answer, with True corresponding to 'Yes'
        and False to 'No'.
        """
        gotAnswer = False
        answ: Optional[bool] = None
        print(prompt, end=" ")
        while not gotAnswer:
            inp = input().lower()
            if inp in ANSWER_YES:
                return True, True
            elif inp in ANSWER_NO:
                return True, False
            elif inp in ANSWER_ABORT:
                break
            else:
                print(f"Allowed answers are {'/'.join(ANSWER_YES + ANSWER_NO)}. Try again: ", end="")

        return gotAnswer, answ

    @staticmethod
    def getInputNumber(prompt: str, allowedAnswers: Optional[List] = None) -> Tuple[bool, Optional[int]]:
        """Request the user to input an integer and return success and the value of the input.

        The first element of the returned tuple reports the success of the user input.
        The second element containts the answer, as an int.
        """
        gotAnswer = False
        answ: Optional[int] = None
        print(prompt, end=" ")
        while not gotAnswer:
            inp = input().lower()
            if inp in ANSWER_ABORT:
                break
            try:
                answ = int(inp)
            except ValueError:
                print("That's not a number. Try again:", end=" ")
                continue
            if allowedAnswers is None:
                return True, answ
            else:
                if answ in allowedAnswers:
                    return True, answ
                else:
                    print(
                        f"Your input {answ} is not an allowed number. (Allowed numbers are: {', '.join([str(a) for a in allowedAnswers])}).\nTry again (\"{ANSWER_ABORT[0]}\" to exit):",
                        end=" ")

        return gotAnswer, answ
