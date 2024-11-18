import os
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='StegoDetectoLive')

    # Select the mode of the proxy
    parser.add_argument('-R', type=str, nargs=1, help='Enable reverse proxy mode. Provide the IP address of the server')
    parser.add_argument('-F', action='store_true', help='Enable forward proxy mode')

    # Configures the behavior
    parser.add_argument('-M', type=int, default=1, help='Minimum number of successful detections before blocking')
    parser.add_argument('-T', action='store_true', help='This will allow all traffic to pass through the proxy. All '
                                                        'image data will be saved to the triage folder with its '
                                                        'respective metadata.')
    
    # Configures the proxy
    parser.add_argument('-P', type=int, default=8080, help='Port number to run the proxy')

    args = parser.parse_args()

    # Update the configuration file if it exists or create a new one
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            config["min_detections"] = args.M
            config["allow_all_traffic_and_save_data"] = args.T
        with open("config.json", "w") as f:
            json.dump(config, f)
    else:
        with open("config.json", "w") as f:
            config = {
                "min_detections": args.M,
                "allow_all_traffic_and_save_data": args.T
            }
            json.dump(config, f)

    if args.R and args.F:
        print("Please select only one mode")
        return

    if args.R:
        command = "mitmdump -p {} -s steganalysis_addon.py --mode reverse:{}".format(args.P, args.R[0])

    if args.F:
        # The command to start the mitmproxy server
        command = "mitmdump -p {} -s steganalysis_addon.py".format(args.P)

    # Run the command in the background
    os.system(command)

if __name__ == '__main__':
    main()