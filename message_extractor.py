import logging


_logger = logging.getLogger("message_extractor")


# Messages are arbitrary sequences of characters delimited by STX at the start and ETX
# at the end and with a maximum length (specific as a constructor argument here).
# There's no support for escaping STX and ETX within a message and no support for
# characters that require more than one byte.
class Extractor:
    _STX = 2
    _ETX = 3

    def __init__(self, maxMessageLen=16):
        self.maxMessageLen = maxMessageLen

        bufferLen = maxMessageLen + 1
        buffer = bytearray(bufferLen)

        self._view = memoryview(buffer)
        self._offset = 0

    # `consume` keeps reading data until all currently available data is read.
    # It returns only the last message received, i.e. if you send messages too fast, such
    # that they're arriving quicker than the system's ability to consume them individually
    # then it will discard all but the most recent message.
    def consume(self, readfn):
        finished = False

        while not finished:
            free = len(self._view) - self._offset
            count = readfn(self._view[self._offset : len(self._view)])

            # Break on 0 or None (Stream.readline returns None when no data is available).
            if not count:
                break

            # We're finished when we've clearly hit the end of all currently available data.
            # I.e. we've read less bytes than we had capacity for.
            finished = count < free
            self._offset += count

            # Search backwards in read data for STX. Shift it to 0 position if found.
            start = self._offset - 1
            end = self._offset - count - 1
            if end == -1:
                end = 0
            for i in range(start, end, -1):
                c = self._view[i]
                if c == self._STX:
                    # We discard all but the last message.
                    _logger.warning(
                        "Discarding superseded data {}".format(bytes(self._view[0:i]))
                    )
                    tmp = self._offset - i
                    self._view[0:tmp] = self._view[i : self._offset]
                    self._offset = tmp
                    break

            # The buffer is deliberately one byte longer than the longest valid message.
            # If the buffer is full the message is invalidly long (irrespective of
            # whether the message is otherwise structuraly valid).
            if self._offset == len(self._view):
                _logger.warning(
                    "Discarding oversized data {}".format(bytes(self._view))
                )
                self._offset = 0
            elif self._view[0] != self._STX:
                _logger.warning(
                    "Discarding invalid data {}".format(
                        bytes(self._view[0 : self._offset])
                    )
                )
                self._offset = 0

        if self._offset > 0 and self._view[self._offset - 1] == self._ETX:
            message = str(self._view[1 : (self._offset - 1)], "utf-8")
            self._offset = 0
            # Zero length messages can be used as low-level heartbeats that are always ignored.
            return message if len(message) > 0 else None
        else:
            return None
