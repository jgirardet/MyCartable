from mycartable.defaults.configuration import KEEP_UPDATED_CONFIGURATION


def test_layouts():
    for k, v in KEEP_UPDATED_CONFIGURATION["layouts"].items():
        assert k == v["splittype"]

    # test splitindex, dans ordre voulu
    indextemoin = 0
    for k, v in KEEP_UPDATED_CONFIGURATION["layouts"].items():
        assert v["splitindex"] == indextemoin
        indextemoin += 1
