from xerxes_node.leaves.pleaf import Medium


logging_level = 'DEBUG' # DEBUG INFO WARNING ERROR
mongo_URI = "mongodb+srv://node:prokopcakovamama@xerxes.57jmr.mongodb.net/alfa?retryWrites=true&w=majority"
use_database = "pri_sajbach"
sample_period = 1
update_period = 60
use_device = "/dev/ttyS0"
used_medium = Medium.WATER
leaves = {
    0x01: "nivelation",
    0x02: "nivelation",
    0x03: "nivelation",
    0x1f: "nivelation"  # also reference
}
reference_leaf_addr = 0x1f