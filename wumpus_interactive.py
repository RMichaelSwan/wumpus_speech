import random

from wumpushost import ActionResult, WumpusHost

from queue import Queue


class Player:
    def __init__(self, a_seed, map_file):
        self.seed = a_seed
        self.map_file = map_file
        self.decision_history = Queue()
        self.replay_flag = False
        self.host = WumpusHost(a_seed, map_file, show_graphics=False, cheat_graphics=False)

    def play(self):
        return self.host.play(self.status_callback)

    def replay(self):
        if self.decision_history.qsize() <= 0:
            print('Nothing to replay. Exiting.')
        else:
            print('Replaying last game...')
            self.replay_flag = True
            self.host = WumpusHost(self.seed, self.map_file, show_graphics=True, cheat_graphics=True)
            return self.host.play(self.status_callback)
        
    def replay_decision(self):
        decision = input('Review Game? (y or n) ')
        if decision in ['y', 'Y']:
            self.replay()
            return True
        else:
            print(f'Received {decision}. Exiting.')
        return False

    def make_decision(self):
        if self.replay_flag:
            decision = self.decision_history.get_nowait()
            print('Move or Shoot? (m or s) ', decision)
        else:
            decision = input('Move or Shoot? (m or s) ')
            self.decision_history.put_nowait(decision)
        
        if decision in ['m', 'M']:
            self.perform_move()
        elif decision in ['s', 'S']:
            self.perform_shoot()
        else:
            print("That's not an option in this game.")

    def status_callback(self, near_pit, near_bats, near_wumpus, room, exits, entrances):
        if near_pit:
            print('I feel a draft')
        if near_bats:
            print('I hear bats!')
        if near_wumpus:
            print('I smell a wumpus!')
        print('You are in room {}. Tunnels lead to {}.'.format(
            room + 1,
            [x+1 for x in exits]
        ))
        visible = [x + 1 for x in entrances if x not in exits]
        if visible:
            print("You can also see (but cannot get to) {}".format(visible))
        self.make_decision()

    def perform_move(self):
        """Perform a move action."""
        if self.replay_flag:
            new_room = int(self.decision_history.get_nowait())
            print('Where to? ', new_room)
            input("[REPLAY] Press any key to continue...")
        else:
            try:
                new_room = input('Where to? ')
                new_room = int(new_room)
            except ValueError:
                print(f'Invalid input room value: {new_room}. Try again.')
                return
            self.decision_history.put_nowait(new_room)
        new_room -= 1 # rooms are 0-indexed on backend
        
        result, bats_picked_up = self.host.move(new_room)
        if bats_picked_up:
            print('ZAP -- Super Bat snatch! Elsewhereville for you!')
        if result == ActionResult.MET_WUMPUS:
            print('TSK TSK TSK - Wumpus got you!')
        elif result == ActionResult.FELL_IN_PIT:
            print('YYYIIIIEEEE . . . Fell in a pit.')
        elif result == ActionResult.EXHAUSTED:
            print('OOF! You collapse from exhaustion.')
        elif result == ActionResult.NOT_AN_EXIT:
            print("BONK! That's not a possible move.")

    def perform_shoot(self):
        """Perform a shoot action"""
        if self.replay_flag:
            rooms = self.decision_history.get_nowait()
            print('You can shoot up to five rooms, separate rooms with a comma ', rooms)
            input("[REPLAY] Press any key to continue...")
        else:
            rooms = input('You can shoot up to five rooms, separate rooms with a comma ')
            self.decision_history.put_nowait(rooms)

        try: 
            room_list = [int(x) - 1 for x in rooms.split(',')]
        except ValueError:
            print(f'Invalid input room list: {rooms}. Try again.')
            return
        
        result = self.host.shoot(room_list)
        if result == ActionResult.TOO_CROOKED:
            print("Arrows aren't that crooked - try another room")
        elif result == ActionResult.WUMPUS_MISSED:
            print("SWISH! The wumpus didn't like that. He may have moved to a quieter room")
        elif result == ActionResult.WUMPUS_KILLED:
            print("AHA! You got the wumpus!")
        elif result == ActionResult.KILLED_BY_GROGGY_WUMPUS:
            print("CLANG! Missed and a groggy wumpus just ate you!")
        elif result == ActionResult.OUT_OF_ARROWS:
            print("WHIZZ! Oh no! Out of arrows. At night the ice weasels come for you...")
        elif result == ActionResult.SHOT_SELF:
            print("LOOK OUT! Thunk! You shot yourself!")


if __name__ == '__main__':
    # seed = random.randint(0, 1000)
    seed = 921
    player = Player(seed, 'standard.txt')
    print("""
        WELCOME TO 'HUNT THE WUMPUS'

        THE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 TUNNELS LEADING TO OTHER
        ROOMS. THE STANDARD MAP IS A DODECAHEDRON (IF YOU DON'T KNOW WHAT A
        DODECAHEDRON IS, ASK SOMEONE)

        ***
        HAZARDS:

        BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
        IF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)

        SUPER BATS  - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU
        AND TAKES YOU TO SOME OTHER ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)

        WUMPUS:

        THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER FEET AND IS TOO BIG FOR
        A BAT TO LIFT). USUALLY HE IS ASLEEP. TWO THINGS WAKE HIM UP: YOUR ENTERING HIS
        ROOM OR YOUR SHOOTING AN ARROW.

            IF THE WUMPUS WAKES, HE EATS YOU IF YOU ARE THERE, OTHERWISE, HE MOVES (P=0.75)
        ONE ROOM OR STAYS STILL (P=0.25). AFTER THAT, IF HE IS WHERE YOU ARE, HE EATS
        YOU UP (& YOU LOSE!)

        YOU:

        EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW
        MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
        ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.

            EACH ARROW CAN GO FROM 1 TO 5 ROOMS: YOU AIM BY TELLING THE COMPUTER THE ROOMS
        YOU WANT THE ARROW TO GO TO. IF THE ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT
        MOVES AT RANDOM TO THE NEXT ROOM.

            IF THE ARROW HITS THE WUMPUS: YOU WIN.

            IF THE ARROW HITS YOU: YOU LOSE.

            WARNINGS:

        WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OR HAZARD, THE COMPUTER SAYS:

        WUMPUS - 'I SMELL A WUMPUS'

        BAT - 'I HEAR BATS'

        PIT - 'I FEEL A DRAFT'

    ***
    HUNT THE WUMPUS
    """)
    score = player.play()
    player.replay_decision()
    print("Your seed that game was:", player.seed)
    if score:
        print("HEE HEE HEE - The wumpus'll getcha next time!!\nYou got a score of {}".format(score))
    else:
        print("HA HA HA - You lose!")
