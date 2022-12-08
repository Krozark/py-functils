# Built-in
import base64

# Third-party
import magic


def datauri(stream) -> str:  # type: ignore
    data = stream.read()
    detected = magic.detect_from_content(data)
    encoded_base64 = base64.b64encode(data)  # return bytes
    encoded_str = encoded_base64.decode("utf-8")  # return string
    return f"data:{detected.mime_type};base64,{encoded_str}"
