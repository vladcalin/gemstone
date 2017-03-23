from gemstone.config.configurable import Configurable


def test_configurable_just_value():
    configurable = Configurable("test")

    configurable.set_value("hello world")

    assert configurable.name == "test"
    assert configurable.get_final_value() == "hello world"


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
