import protobuf.gtfs_realtime_pb2 as gtfs


new_message = gtfs.FeedMessage()
with open(r"gtfsrt.bin", "rb") as f:
    new_message.ParseFromString(f.read())
print(new_message.header)
print(new_message.entity[4])