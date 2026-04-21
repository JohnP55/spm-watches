from memorywatch import Datatype

# Add watches here.
# Format is:
# "Name" : {
#     "addresses": {
#         "E": [US0, US1, US2],
#         "P": [EU0, EU1],
#         "J": [JP0, JP1],
#         "K": [KR0]
#     },
#     "datatype": (refer to Datatype enum above)
# }
watches = {
    "GSWF_base_address": {
        "addresses": {
            "E": [0x804e2694, 0x804e3f14, 0x804e4094],
            "P": [0x80525694, 0x80525694],
            "J": [0x804b7994, 0x804b8f94],
            "K": [0x8055cff4]
        },
        "datatype": Datatype.BYTE
    },
    "SequencePosition" : {
        "addresses" : {
            "E": [0x804E2690, 0x804E3F10, 0x804E4090],
            "P": [0x80525690, 0x80525690],
            "J": [0x804B7990, 0x804B8F90],
            "K": [0x8055CFF0]
        },
        "datatype": Datatype.WORD
    }
}
