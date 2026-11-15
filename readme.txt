中国—东盟人工智能标准适配验证台

运行验收：
python3 -m standards_bridge run --fixture fixtures/acceptance.json --database /tmp/standards_bridge.sqlite3 --output /tmp/standards_bridge-output

核验：
python3 -m standards_bridge verify --database /tmp/standards_bridge.sqlite3 --output /tmp/standards_bridge-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.profiles.test_specification -v

构建检查：
python3 -m compileall -q standards_bridge tests
