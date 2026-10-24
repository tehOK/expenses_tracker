from accessors import ExpensesManager


def main():

    expense_manager = ExpensesManager()

    COMMANDS = {
        "add": expense_manager.add,
        "list": expense_manager.list_expenses,
        "delete": expense_manager.delete,
        "find": expense_manager.find,
        "report": expense_manager.report,
        "top": expense_manager.top,
    }

    while True:
        try:
            raw = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход")
            break
        if not raw:
            continue
        parts = raw.split(maxsplit=3)
        command = parts[0].lower()
        handler = COMMANDS.get(command)
        if handler:
            handler(parts[1:])
        else:
            print("Неизвестная команда.\nВведите /help для помощи.")


if __name__ == "__main__":
    main()
