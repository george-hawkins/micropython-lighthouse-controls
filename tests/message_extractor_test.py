from message_extractor import Extractor


# I tried using `unittest` but this depends on a more sophisticated version of
# `logging` than that found in `../lib`. One can remove `../lib` from `sys.path`
# but there are issues with this and trying to run the unit tests within IntelliJ's
# own test harness. In the end I just moved to using the basic `assert.


class TestHelper:
    def __index__(self):
        self._data = None
        self._i = None

    def _read(self, buf):
        data_len = len(self._data)
        if self._i == data_len:
            return 0
        buf_len = len(buf)
        end = min(self._i + buf_len, data_len)
        buf[0:(end - self._i)] = self._data[self._i:end]
        count = end - self._i
        self._i = end
        return count

    def process(self, extractor, data):
        self._i = 0
        self._data = data
        return extractor.consume(self._read)


helper = TestHelper()
extractor = None


# Use to simply test that extractor can still function even after testing problem cases.
def ok():
    assert "abc" == helper.process(extractor, b"\x02abc\x03")


# Test 1. looks like a valid message but is one byte too long.

extractor = Extractor()
data = b'\x02123456789012345\x03'

assert len(data) == extractor.maxMessageLen + 1

result = helper.process(extractor, data)
assert result == None

ok()

# Test 2. looks like a valid message but is several byte too long.

data = b'\x021234567890123456789\x03'

assert len(data) > extractor.maxMessageLen + 1

result = helper.process(extractor, data)
assert result == None

ok()

# Test 3. only get last message.

result = helper.process(extractor, b'\x021\x03\x0212\x03\x02123\x03')
assert result == "123"

ok()

# Test 4. oversized message followed by two valid messages.

result = helper.process(extractor, b'\x021234567890123456789\x03\x021\x03\x0212\x03')
assert result == "12"

ok()

# Test 5. invalid data followed by a valid message.

result = helper.process(extractor, b'1234567890123456\x021\x03')
assert result == "1"

ok()

# Test 6. message broken into two chunks by transmission.

result = helper.process(extractor, b'\x0212')
assert result == None

result = helper.process(extractor, b'34\x03')
assert result == "1234"

ok()
