# main should not contain complex app logic
# just be used to run the main functions themselves mostly


from cli import controller


def main():
    controller()


if __name__ == "__main__":
    main()
