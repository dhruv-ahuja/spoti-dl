# current plan is:
# add some basic arguments to the cli to enable some flexibility
# construct a basic controller for the cli
# add some more features

# main should not contain complex app logic
# just be used to run the main functions themselves mostly


from cli import controller


def main():
    c = controller()


if __name__ == "__main__":
    main()
