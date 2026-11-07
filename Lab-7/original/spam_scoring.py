def sender_domain(email):
    return email.split('@')[1].lower()

def first_link(text):
    start = text.index('http')
    end = text.find(' ', start)
    if end == -1:
        end = len(text)
    return text[start:end]

def shout_ratio(text):
    letters = [c for c in text if c.isalpha()]
    upper = [c for c in letters if c.isupper()]
    return len(upper) / len(letters)

def main():
    print("==== Running sender_domain ====")
    user_input = input("Enter a sender email (e.g. offers@Deals.com): ")
    result = sender_domain(user_input)
    print("Sender Domain:", result)

    print("\n==== Running first_link ====")
    user_input = input("Enter a message containing a link: ")
    result = first_link(user_input)
    print("First Link:", result)

    print("\n==== Running shout_ratio ====")
    user_input = input("Enter a message (e.g. FREE prize NOW): ")
    result = shout_ratio(user_input)
    print("Uppercase Ratio:", result)

if __name__ == "__main__":
    main()
