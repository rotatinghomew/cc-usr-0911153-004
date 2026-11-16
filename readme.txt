中国—东盟人工智能标准适配验证台

映射与认证：Repository.register_mapping 维护规格对照和单调修订号，
link_case_mapping 登记案例使用的映射，sign_case 基于当时映射版本和证据
封存签发结论，mapping_impact 可读出影响案例和历史签发。签发记录不能被
后续映射修订覆盖。

可比性分层（economics/comparability.py）：跨市场案例按单位制（相同或存在
登记换算）、规格族映射连通性与桥别名覆盖、豁免口径（豁免率差）、证据充分性
逐对判定为 comparable / not_comparable / insufficient_evidence。平均通过率
只在同一可比层内聚合，另给出 pooled_mean_pass_rate 仅供参照，不能据此下复用
结论；comparability 视图按案例输出 reuse_supported / not_comparable /
insufficient_evidence / revalidation_pending。

修订影响复验（assurance/revision_control.py）：register_mapping 修订别名表时，
只沿 case_mapping_usage 的真实依赖为相关案例挂起复验请求，共同映射在所有关联
市场一致传播，未涉及映射的案例不会被重跑也无法被复验。已签发认证保留旧修订号
与证据并标记 stale=1；存在未完成复验时 sign_case 拒绝新签发。revalidate 关闭
请求并按新修订重估比较，revision 视图给出本修订改变了哪些比较层（pair_changes）、
哪些复验仍未完成（open_case_ids）以及哪些认证已过期。

运行验收：
python3 -m standards_bridge run --fixture fixtures/acceptance.json --database /tmp/standards_bridge.sqlite3 --output /tmp/standards_bridge-output

核验：
python3 -m standards_bridge verify --database /tmp/standards_bridge.sqlite3 --output /tmp/standards_bridge-output

可比性与修订复验命令：
python3 -m standards_bridge comparability --database /tmp/standards_bridge.sqlite3
python3 -m standards_bridge compare --database /tmp/standards_bridge.sqlite3 --left <case-a> --right <case-b>
python3 -m standards_bridge mapping register --database /tmp/standards_bridge.sqlite3 --mapping-id <id> --source <spec> --target <spec> --aliases '{"k":"v"}'
python3 -m standards_bridge mapping impact --database /tmp/standards_bridge.sqlite3 --mapping-id <id>
python3 -m standards_bridge link-case --database /tmp/standards_bridge.sqlite3 --case-id <case> --mapping-id <id>
python3 -m standards_bridge sign-case --database /tmp/standards_bridge.sqlite3 --certification-id <cert> --case-id <case> --mapping-id <id> --evidence '{"accepted":true}'
python3 -m standards_bridge revision --database /tmp/standards_bridge.sqlite3 --mapping-id <id>
python3 -m standards_bridge revalidate --database /tmp/standards_bridge.sqlite3 --mapping-id <id> --case-id <case> --result '{"outcome":"approve"}'

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.profiles.test_specification -v

构建检查：
python3 -m compileall -q standards_bridge tests
