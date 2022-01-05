from techflurry.controller.datasource import TFDataSource


def test_initiate_new_datasource():
    datasource = TFDataSource(topic="test_topic")

    assert isinstance(datasource, TFDataSource)
