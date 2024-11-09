from mitmproxy import http

from StegoDetectoLive.modules.histogram import histogram


def request(flow: http.HTTPFlow) -> None:
    print(flow.request.content)


def response(flow: http.HTTPFlow) -> None:
    isStego = histogram(flow.response.content)
    if isStego:
        print("Steganography detected")
        flow.kill()
    else:
        print("No steganography detected")


