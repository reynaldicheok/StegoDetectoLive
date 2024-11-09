from mitmproxy import http


def request(flow: http.HTTPFlow) -> None:
    flow.kill()


def response(flow: http.HTTPFlow) -> None:
    flow.kill()
