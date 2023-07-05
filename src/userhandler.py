import sys
import select

def input_timeout(prompt, default=True, timeout=10):
    print(f"You have {timeout} seconds to answer next user input.")
    print(prompt)
    inputs = [sys.stdin]
    outputs = []
    user_input = ""
    timer_start = None
    while True:
        readable, _, _ = select.select(inputs, outputs, [], timeout)
        if readable:
            user_input = sys.stdin.readline().strip().lower()
            break
        else:
            print("Time limit exceeded. No input received. Answer accepted as {default}.")
            return default
    if user_input in ['yes', 'y', '']:
        return True
    elif user_input in ['no', 'n']:
        return False
    else:
        return default

# print("Example usage:")
# user_confirmation = input_timeout("Do you want to proceed? [Y/N]: ", default=True, timeout=10)
# print("User confirmation:", user_confirmation)
