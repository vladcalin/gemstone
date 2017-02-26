from gemstone.config.configurable import Configurable


def test_configurable_just_value():
    configurable = Configurable("test")

    configurable.set_value("hello world")

    assert configurable.name == "test"
    assert configurable.get_final_value() == "hello world"


def test_configurable_custom_type():
    configurable = Configurable("test", type=int)
    configurable.set_value("100")
    assert configurable.name == "test"
    assert configurable.get_final_value() == 100

    configurable = Configurable("test", type=float)
    configurable.set_value("3.14")
    assert configurable.get_final_value() == 3.14


def test_configurable_template():
    configurable = Configurable("test", template=lambda x: x.split(","))
    configurable.set_value("1,2,3,4")
    assert configurable.get_final_value() == ["1", "2", "3", "4"]

    configurable = Configurable("test", template=lambda x: [int(i) for i in x.split(",")])
    configurable.set_value("1,2,3,4")
    assert configurable.get_final_value() == [1, 2, 3, 4]

    def sum_between_max_and_min(str_seq):
        items = [int(i) for i in str_seq.split(",")]
        return max(items) + min(items)

    configurable = Configurable("test_complex_template", template=sum_between_max_and_min)
    configurable.set_value("1,2,3,4,5")
    assert configurable.get_final_value() == 6


def test_configurable_mappings():
    mappings = [("1", "one"), ("2", "two"), ("3", "three")]
    configurable = Configurable("test", mappings=mappings)

    configurable.set_value("1")
    assert configurable.get_final_value() == "one"

    configurable.set_value("3")
    assert configurable.get_final_value() == "three"

    configurable.set_value("2")
    assert configurable.get_final_value() == "two"

    configurable.set_value("4")
    assert configurable.get_final_value() == "4"

    configurable.set_value(1)
    assert configurable.get_final_value() == "one"  # because of the default str type


def test_configurable_template_and_mappings():
    mappings = [("1", "one_str"), ("2", "two_str"), ("3", "three_str"),
                (1, "one_int"), (2, "two_int"), (3, "three_int")]
    configurable = Configurable("test", mappings=mappings, type=str, template=lambda x: str(int(x) + 1))
    configurable.set_value(0)
    assert configurable.get_final_value() == "one_str"
    configurable.set_value(-1)
    assert configurable.get_final_value() == "0"  # no mapping applied
    configurable.set_value("2")
    assert configurable.get_final_value() == "three_str"

    configurable = Configurable("test", mappings=mappings, type=int, template=lambda x: x - 1)
    configurable.set_value("1")
    assert configurable.get_final_value() == 0  # 1 - 1
    configurable.set_value("2")
    assert configurable.get_final_value() == "one_int"  # mapping(2 - 1)
    configurable.set_value(4)
    assert configurable.get_final_value() == "three_int"  # mapping(4 - 1)
