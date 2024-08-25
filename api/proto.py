import protobuf.gtfs_realtime_pb2 as gtfs


new_message = gtfs.FeedMessage()
with open(r"C:\Users\Daniel\OneDrive - University of Bristol\comp_tings\bods_api\gtfsrt.bin", "rb") as f:
    new_message.ParseFromString(f.read())

print(new_message.entity)