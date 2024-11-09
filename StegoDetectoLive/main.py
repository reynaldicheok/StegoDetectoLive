import os

def main():
    # The command to start the mitmproxy server
    command = "mitmdump -s steganalysis_addon.py"

    # Run the command in the background
    os.system(command)

if __name__ == '__main__':
    main()