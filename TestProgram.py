import random

actions = ["paper", "rock", "scissors"]

win_conditions = {
        "paper": "rock",
        "scissor": "paper",
        "rock": "scissors"
}

wins = 0
loses = 0
ties = 0

def results(user_input, random_action):
    global wins, loses, ties

    try:
        if user_input.lower() == random_action.lower():
            ties += 1
            return "Draw!"

        if win_conditions[user_input] == random_action:
            wins += 1
            return "You won!"
        else:
            loses += 1
            return "You lost!"
    except KeyError:
        return "Invalid input!"

def main():
    print("Welcome to the Rock, Paper, Scissor Game!")
    print("You can leave if you type 'exit'")

    while True:
        print(f"""Statistics: 
            Wins: {wins}, Loses: {loses}, Ties: {ties}
            """)

        random_choice = random.choice(actions)

        user_choice = input(f"Choose your action, available: {', '.join(actions)}: ").lower()

        if user_choice == "exit":
            break

        print(f"You chose: {user_choice}, computer chose: {random_choice}")
        print(results(user_choice, random_choice))

if __name__ == "__main__":
    main()

