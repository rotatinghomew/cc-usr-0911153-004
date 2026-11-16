中国—东盟人工智能标准适配验证台

映射与认证基线：Repository.register_mapping 维护规格对照和单调修订号，
link_case_mapping 登记案例使用的映射，sign_case 基于当时映射版本和证据
封存签发结论，mapping_impact 可读出影响案例和历史签发。签发记录不能被
后续映射修订覆盖。当前未实现统计可比性分层、跨市场映射修订的复验队列、
或将复验结果用于待认证判断，这些仍是新增功能。

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
