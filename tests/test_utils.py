REMOTES_LEN_LIMIT = 10
LSST_SITE = "love"


def assert_all_objects_in_list_have_keys(keys, objects):
    """Assert that all objects in a list have the same keys."""
    for obj in objects:
        for key in keys:
            assert key in obj
