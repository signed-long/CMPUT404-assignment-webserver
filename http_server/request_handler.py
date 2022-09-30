import pathlib
from typing import Tuple, Dict


class RequestHandler():

    root = pathlib.Path('./www')
    allowed_file_types = {".html": True, ".css": True}

    def handle(self, raw_request: bytes) -> str:
        '''
        Handles a request and returns a response to be sent to client.

        parameters
            - raw_request: the request received from our socket server.
        '''
        try:
            # server only handles get requests
            request = raw_request.decode("utf-8").split("/n")[0].split(" ")
            if (request[0] != "GET"):
                raise HttpError(405, "Method Not Allowed")

            # validate and build the file_to_serve path
            file_to_serve = self._get_file_path(request[1])

        except HttpRedirect as e:
            return self._get_response((e.status, e.msg), headers={"Location": e.location})
        except HttpError as e:
            return self._get_response((e.status, e.msg))
        except Exception as e:
            return self._get_response((400, "Bad Request"))

        return self._get_response((200, "Ok"), file_to_serve=file_to_serve)

    def _get_file_path(self, url: str) -> str:
        '''
        Validates and builds the path of the file we are serving.

        parameters
            - url: url given in request
        '''
        url = self._escape_url(url)
        if (url[-1] == "/"):
            url += "index.html"

        path = pathlib.Path("./www" + url)

        # url doesn't end in a file extension or a /
        if (path.suffix == ''):
            # only redirect if the new location exists
            if (pathlib.Path("./www" + url + "/index.html").is_file):
                raise HttpRedirect(301, "Moved Permanently", url + "/")
            else:
                # print("404 invalid path here")
                raise HttpError(404, "Not Found")

        # url is pointing to file under ./www dir
        if (self.root not in path.parents):
            # print("404 invalid path")
            raise HttpError(404, "Not Found")

        # url is pointing to a file with an allowed file extension
        if (not self.allowed_file_types.get(path.suffix)):
            # print("404 invalid file type")
            raise HttpError(404, "Not Found")

        # file exists
        is_file = path.is_file()
        if not is_file:
            # print("404 invalid file: " + str(path))
            raise HttpError(404, "Not Found")

        return path

    def _escape_url(self, url: str) -> str:
        '''
        Substitute escaped charters in request url. 
        List of chars is from here: https://www.w3schools.com/tags/ref_urlencode.ASP

        parameters:
            - url with escaped chars
        '''
        escaping = {' ': '%20', '!': '%21', '"': '%22', '#': '%23', '$': '%24', '%': '%25', '&': '%26', "'": '%27', '(': '%28', ')': '%29', '*': '%2A', '+': '%2B', ',': '%2C', '-': '%2D', '.': '%2E', '/': '%2F', '0': '%30', '1': '%31', '2': '%32', '3': '%33', '4': '%34', '5': '%35', '6': '%36', '7': '%37', '8': '%38', '9': '%39', ':': '%3A', ';': '%3B', '<': '%3C', '=': '%3D', '>': '%3E', '?': '%3F', '@': '%40', 'A': '%41', 'B': '%42', 'C': '%43', 'D': '%44', 'E': '%45', 'F': '%46', 'G': '%47', 'H': '%48', 'I': '%49', 'J': '%4A', 'K': '%4B', 'L': '%4C', 'M': '%4D', 'N': '%4E', 'O': '%4F', 'P': '%50', 'Q': '%51', 'R': '%52', 'S': '%53', 'T': '%54', 'U': '%55', 'V': '%56', 'W': '%57', 'X': '%58', 'Y': '%59', 'Z': '%5A', '[': '%5B', '\\': '%5C', ']': '%5D', '^': '%5E', '_': '%5F', '`': '%60', 'a': '%61', 'b': '%62', 'c': '%63', 'd': '%64', 'e': '%65', 'f': '%66', 'g': '%67', 'h': '%68', 'i': '%69', 'j': '%6A', 'k': '%6B', 'l': '%6C', 'm': '%6D', 'n': '%6E', 'o': '%6F', 'p': '%70', 'q': '%71', 'r': '%72', 's': '%73', 't': '%74', 'u': '%75', 'v': '%76', 'w': '%77', 'x': '%78', 'y': '%79', 'z': '%7A', '{': '%7B', '|': '%7C', '}': '%7D', '~': '%7E', '': '%C2%A0', '€': '%E2%82%AC', '\x81': '%81', '‚': '%E2%80%9A', 'ƒ': '%C6%92', '„': '%E2%80%9E', '…': '%E2%80%A6', '†': '%E2%80%A0', '‡': '%E2%80%A1', 'ˆ': '%CB%86', '‰': '%E2%80%B0', 'Š': '%C5%A0', '‹': '%E2%80%B9', 'Œ': '%C5%92', '\x8d': '%C5%8D', 'Ž': '%C5%BD', '\x8f': '%8F', '\x90': '%C2%90', '‘': '%E2%80%98', '’': '%E2%80%99', '“': '%E2%80%9C', '”': '%E2%80%9D', '•': '%E2%80%A2', '–': '%E2%80%93',
                    '—': '%E2%80%94', '˜': '%CB%9C', '™': '%E2%84', 'š': '%C5%A1', '›': '%E2%80', 'œ': '%C5%93', '\x9d': '%9D', 'ž': '%C5%BE', 'Ÿ': '%C5%B8', '¡': '%C2%A1', '¢': '%C2%A2', '£': '%C2%A3', '¤': '%C2%A4', '¥': '%C2%A5', '¦': '%C2%A6', '§': '%C2%A7', '¨': '%C2%A8', '©': '%C2%A9', 'ª': '%C2%AA', '«': '%C2%AB', '¬': '%C2%AC', '\xad': '%C2%AD', '®': '%C2%AE', '¯': '%C2%AF', '°': '%C2%B0', '±': '%C2%B1', '²': '%C2%B2', '³': '%C2%B3', '´': '%C2%B4', 'µ': '%C2%B5', '¶': '%C2%B6', '·': '%C2%B7', '¸': '%C2%B8', '¹': '%C2%B9', 'º': '%C2%BA', '»': '%C2%BB', '¼': '%C2%BC', '½': '%C2%BD', '¾': '%C2%BE', '¿': '%C2%BF', 'À': '%C3%80', 'Á': '%C3%81', 'Â': '%C3%82', 'Ã': '%C3%83', 'Ä': '%C3%84', 'Å': '%C3%85', 'Æ': '%C3%86', 'Ç': '%C3%87', 'È': '%C3%88', 'É': '%C3%89', 'Ê': '%C3%8A', 'Ë': '%C3%8B', 'Ì': '%C3%8C', 'Í': '%C3%8D', 'Î': '%C3%8E', 'Ï': '%C3%8F', 'Ð': '%C3%90', 'Ñ': '%C3%91', 'Ò': '%C3%92', 'Ó': '%C3%93', 'Ô': '%C3%94', 'Õ': '%C3%95', 'Ö': '%C3%96', '×': '%C3%97', 'Ø': '%C3%98', 'Ù': '%C3%99', 'Ú': '%C3%9A', 'Û': '%C3%9B', 'Ü': '%C3%9C', 'Ý': '%C3%9D', 'Þ': '%C3%9E', 'ß': '%C3%9F', 'à': '%C3%A0', 'á': '%C3%A1', 'â': '%C3%A2', 'ã': '%C3%A3', 'ä': '%C3%A4', 'å': '%C3%A5', 'æ': '%C3%A6', 'ç': '%C3%A7', 'è': '%C3%A8', 'é': '%C3%A9', 'ê': '%C3%AA', 'ë': '%C3%AB', 'ì': '%C3%AC', 'í': '%C3%AD', 'î': '%C3%AE', 'ï': '%C3%AF', 'ð': '%C3%B0', 'ñ': '%C3%B1', 'ò': '%C3%B2', 'ó': '%C3%B3', 'ô': '%C3%B4', 'õ': '%C3%B5', 'ö': '%C3%B6', '÷': '%C3%B7', 'ø': '%C3%B8', 'ù': '%C3%B9', 'ú': '%C3%BA', 'û': '%C3%BB', 'ü': '%C3%BC', 'ý': '%C3%BD', 'þ': '%C3%BE', 'ÿ': '%C3%BF'}
        for k, v in escaping.items():
            if v in url:
                url = url.replace(v, k)

        return url

    def _get_response(self, status: Tuple[int, str], headers: Dict[str, str] = {}, file_to_serve: pathlib.Path = '') -> str:
        '''
        Builds a HTTP/1.1 response to send back to client.

        parameters
            - status: (status code,  status text)
            - headers: headers to include in response
            - file_to_serve: pathlib.Path to the file we want to serve
        '''
        res = f'HTTP/1.1 {str(status[0])} {status[1]}\n'

        for k, v in headers.items():
            res += f'{k}: {v}\n'

        if file_to_serve:
            with open(file_to_serve, "r") as file:
                res += f'Content-Type: text/{file_to_serve.suffix[1:]}\n\n'
                res += file.read()
        res += "\n"

        return res


class HttpError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status = status
        self.msg = msg


class HttpRedirect(HttpError):
    def __init__(self, status, msg, location):
        super().__init__(status, msg)
        self.location = location
