import protobuf.gtfs_realtime_pb2 as gtfs


def inspect_gtfsrt(path: str = "gtfsrt.bin"):
    """Parse and print a GTFS-RT binary file for inspection."""
    new_message = gtfs.FeedMessage()
    with open(path, "rb") as f:
        new_message.ParseFromString(f.read())
    print(new_message.header)
    print(new_message.entity[4])


if __name__ == "__main__":
    inspect_gtfsrt()