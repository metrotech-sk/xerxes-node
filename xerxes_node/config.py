from xerxes_node.leaves.pleaf import Medium


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
sample_period = 1
update_period = 60
use_device = "/dev/ttyS0"
used_medium = Medium.SILOXANE
leaves = {
    0x01: "nivelation",
    0x02: "nivelation",
    0x03: "nivelation",
    0x05: "nivelation",
    0x06: "nivelation",
    0x15: "nivelation",
    0x18: "nivelation",
    0x1f: "nivelation",
}