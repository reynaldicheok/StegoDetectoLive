import os

def main():
    # If the images.db file does not exist, generate it
    if not os.path.exists("images.db"):
        os.system("python database_generation.py")

    # The command to start the mitmproxy server
    command = "mitmdump -s steganalysis_addon.py"

    # Run the command in the background
    os.system(command)

if __name__ == '__main__':
    main()