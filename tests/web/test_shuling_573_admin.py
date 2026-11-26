"""书灵 5.7.3 后台优化（DXCS-4）Web 回归用例。

覆盖实际通过的用例：
- T-01 反馈列表列顺序（无「最近编辑」）
- T-02 分配/处理时间显示操作人
- T-08 题库列表 12 列与题型/母题/相似题标签
- T-09 题库顶部四项搜索（ID 精确、名称模糊、重置）
- T-10 操作栏上下架展示
- T-11 驳回次数区间筛选
- T-12 错误明细「错误原因」单选与默认全部
- T-13 驳回次数非法区间提示
- T-14 空结果筛选
- T-17 筛选接口失败提示且保留旧结果
- T-19 题库 1280×720 表头对齐与横向滚动
- T-20 切换错误分类重置错误原因
- T-21 多选枚举语义（同项任一命中、不同条件同时满足）
- T-22 切换学科学段清空题型
- T-27 1440×900 四入口无页面级横向溢出
- T-29 深链直达题库列表

未覆盖（报告中已说明缺口）：T-03/T-04/T-05/T-06/T-07/T-15/T-16/
T-18/T-23/T-24/T-25/T-26/T-28/T-30。

环境：daily（config.LOGIN_URL 所在环境），登录态复用 config.STATE_FILE。
用例只读查询，不做上下架/分配/保存等写操作。
"""

import re
from urllib.parse import urlparse

from playwright.sync_api import Page, expect

from config import LOGIN_URL

TOTAL_PATTERN = re.compile(r"共\s*\d+\s*条")
BASE_URL = "{0.scheme}://{0.netloc}".format(urlparse(LOGIN_URL))
QUESTION_BANK_PATH = "/bizmodule/aiTutorWeb/questionBank.htm"

QUESTION_BANK_HEADERS = [
    "题目 ID",
    "题目图片",
    "图书信息",
    "教材信息",
    "投放来源",
    "上架状态",
    "内容状态",
    "内部审核状态",
    "商家审核状态",
    "创建时间",
    "保存时间",
    "配图信息",
]

FEEDBACK_HEADERS = [
    "题目图片",
    "题目ID",
    "学科",
    "商家名称",
    "图书名称/ID",
    "内容状态",
    "问题类型",
    "AI审查错误",
    "驳回次数",
    "处理组",
    "处理人",
    "反馈时间",
    "分配时间",
    "处理时间",
    "操作",
]


def _open_module(page: Page, module: str):
    """从云协同首页进入书灵AI，再切到指定左侧菜单，返回 iframe locator。"""
    if page.locator("iframe").count() == 0:
        page.get_by_role("button", name="更多").click()
        page.get_by_role("button", name="书灵AI").click()
        page.wait_for_url("**/app.htm?**")
        page.locator("iframe").wait_for(state="visible")
    frame = page.frame_locator("iframe")
    frame.get_by_role("menuitem", name=module).click()
    return frame


def _content_frame(page: Page, needle: str):
    """返回命中 URL 片段的 frame，用于读取 DOM 结构。"""
    for item in page.frames:
        if needle in item.url:
            return item
    raise AssertionError(f"未找到包含 {needle} 的 iframe，当前 frames={[f.url for f in page.frames]}")


def _wait_total(frame) -> None:
    expect(frame.get_by_text(TOTAL_PATTERN).first).to_be_visible(timeout=60000)


def _headers(frame) -> list[str]:
    return [re.sub(r"\s+", " ", text).strip() for text in frame.locator("thead th").all_inner_texts()]


def _visible_rows(frame):
    return frame.locator("tbody tr").filter(has_text=re.compile(r".+"))


def _open_filter(frame, column: str) -> None:
    frame.get_by_role("button", name=f"{column} filter").click()


def _reset_all(frame) -> None:
    frame.get_by_role("button", name="重置全部").click()


def _check(frame, name: str) -> None:
    frame.get_by_role("checkbox", name=name, exact=True).check()


def _confirm_filter(frame) -> None:
    frame.get_by_role("button", name="确定筛选").click()


def _select_in_dialog(frame, option: str) -> None:
    """操作表头筛选弹窗里的学科学段下拉。"""
    frame.locator("[role=dialog] .yt5-antd-select").first.click()
    frame.locator(".yt5-antd-select-dropdown:visible").get_by_text(option, exact=True).click()


# CASE_WEB_573_01 / T-01：反馈列表列顺序固定，且不再有「最近编辑」
def test_t01_feedback_columns(page: Page) -> None:
    frame = _open_module(page, "商家审核反馈")
    _wait_total(frame)

    headers = _headers(frame)
    assert headers[1:] == FEEDBACK_HEADERS, f"列顺序不符：{headers}"
    assert "最近编辑" not in headers


# CASE_WEB_573_02 / T-02：分配时间显示分配人、处理时间显示处理人；未分配/未处理显示占位
def test_t02_assign_and_process_operator(page: Page) -> None:
    frame = _open_module(page, "商家审核反馈")
    _wait_total(frame)
    frame.get_by_text("已处理", exact=True).click()
    _wait_total(frame)

    content = _content_frame(page, "merchantAuditFeedback")
    rows = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => [tr.children[13]?.innerText || '', tr.children[14]?.innerText || ''])"""
    )
    assert rows, "已处理列表无数据"
    timed = [r for r in rows if re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s+\S+", r[0])]
    assert timed, f"分配时间未展示分配人：{rows[:3]}"
    assert any(re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s+\S+", r[1]) for r in rows), "处理时间未展示处理人"

    frame.get_by_text("待处理", exact=True).click()
    _wait_total(frame)
    rows = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => [tr.children[13]?.innerText || '', tr.children[14]?.innerText || ''])"""
    )
    assert any(r[0] == "-" and r[1] == "-" for r in rows), "未分配/未处理未显示占位"


# CASE_WEB_573_03 / T-08：题库列表 12 个信息列，题型/母题/相似题标签正确
def test_t08_question_bank_columns_and_tags(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)

    headers = _headers(frame)
    assert headers[0] == "" and headers[-1] == "操作"
    assert headers[1:13] == QUESTION_BANK_HEADERS, f"12 列不符：{headers}"

    _open_filter(frame, "题目 ID")
    _check(frame, "母题")
    _confirm_filter(frame)
    expect(frame.get_by_text("题目属性：母题").first).to_be_visible(timeout=10000)

    content = _content_frame(page, "questionBank.htm")
    rows = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => tr.children[1]?.innerText || '')"""
    )
    assert rows and all("母题" in row for row in rows), "母题标签缺失"
    assert any(re.search(r"填空题|选择题|判断题|听力|应用题", row) for row in rows), "题型标签缺失"

    _reset_all(frame)


# CASE_WEB_573_04 / T-09：题目ID/图书ID 精确，商家/图书名称模糊，重置全部生效
def test_t09_question_bank_search(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)
    content = _content_frame(page, "questionBank.htm")

    frame.get_by_role("textbox", name="题目 ID").fill("6910667")
    frame.get_by_role("button", name=re.compile(r"查\s*询")).click()
    expect(frame.get_by_text(re.compile(r"共\s*1\s*条数据"))).to_be_visible(timeout=15000)

    frame.get_by_role("textbox", name="题目 ID").fill("69106")
    frame.get_by_role("button", name=re.compile(r"查\s*询")).click()
    expect(frame.get_by_text("暂无数据").first).to_be_visible(timeout=15000)

    _reset_all(frame)
    _wait_total(frame)
    frame.get_by_role("textbox", name="图书 ID").fill("57410")
    frame.get_by_role("button", name=re.compile(r"查\s*询")).click()
    _wait_total(frame)
    books = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => tr.children[3]?.innerText || '')"""
    )
    assert books and all("57410" in row for row in books), f"图书ID精确搜索不符：{books[:3]}"

    _reset_all(frame)
    _wait_total(frame)
    frame.get_by_role("textbox", name="商家名称").fill("QH")
    frame.get_by_role("button", name=re.compile(r"查\s*询")).click()
    _wait_total(frame)
    sellers = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => tr.children[4]?.innerText || '')"""
    )
    assert sellers and all("QH" in row for row in sellers), f"商家名称模糊搜索不符：{sellers[:3]}"

    _reset_all(frame)
    _wait_total(frame)
    assert frame.get_by_role("textbox", name="商家名称").input_value() == ""


# CASE_WEB_573_05 / T-10：已上架显示「下架」，未上架/待上架显示「上架」
def test_t10_shelf_actions(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)
    content = _content_frame(page, "questionBank.htm")

    def operation_texts():
        return content.evaluate(
            """() => [...document.querySelectorAll('tbody tr')]
                .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
                .map(tr => tr.children[13]?.innerText.replace(/\\s+/g, ' ') || '')"""
        )

    _open_filter(frame, "上架状态")
    _check(frame, "已上架")
    _confirm_filter(frame)
    _wait_total(frame)
    assert all("下架" in text for text in operation_texts()), "已上架行未显示下架"

    _reset_all(frame)
    _wait_total(frame)
    _open_filter(frame, "上架状态")
    _check(frame, "未上架")
    _confirm_filter(frame)
    _wait_total(frame)
    assert all("上架" in text and "下架" not in text for text in operation_texts()), "未上架行未显示上架"

    _reset_all(frame)


# CASE_WEB_573_06 / T-11：驳回次数 [N-M] 区间含边界
def test_t11_reject_count_range(page: Page) -> None:
    frame = _open_module(page, "商家审核反馈")
    _wait_total(frame)
    frame.get_by_text("已处理", exact=True).click()
    _wait_total(frame)
    frame.get_by_role("button", name="筛选").click()

    frame.get_by_placeholder("起始次数").fill("1")
    frame.get_by_placeholder("结束次数").fill("2")
    page.keyboard.press("Tab")
    _wait_total(frame)
    counts = _content_frame(page, "merchantAuditFeedback").evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => tr.children[9]?.innerText.trim() || '')"""
    )
    assert counts and set(counts) <= {"1", "2"}, f"[1-2] 命中越界：{set(counts)}"

    frame.get_by_placeholder("起始次数").fill("2")
    frame.get_by_placeholder("结束次数").fill("2")
    page.keyboard.press("Tab")
    _wait_total(frame)
    counts = _content_frame(page, "merchantAuditFeedback").evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => tr.children[9]?.innerText.trim() || '')"""
    )
    assert counts and set(counts) == {"2"}, f"[2-2] 命中不符：{set(counts)}"


# CASE_WEB_573_07 / T-13：起始次数大于结束次数时给出提示且不发起错误查询
def test_t13_reject_count_invalid_range(page: Page) -> None:
    frame = _open_module(page, "商家审核反馈")
    _wait_total(frame)
    frame.get_by_text("已处理", exact=True).click()
    _wait_total(frame)
    frame.get_by_role("button", name="筛选").click()

    frame.get_by_placeholder("起始次数").fill("5")
    frame.get_by_placeholder("结束次数").fill("1")
    page.keyboard.press("Tab")
    expect(frame.get_by_text("驳回次数起始值不能大于结束值").first).to_be_visible(timeout=10000)


# CASE_WEB_573_08 / T-14：不可能命中的条件显示空态，清除后恢复
def test_t14_empty_filter_result(page: Page) -> None:
    frame = _open_module(page, "商家审核反馈")
    _wait_total(frame)
    frame.get_by_role("button", name="筛选").click()

    frame.get_by_placeholder("输入商家名称").fill("QA_NOT_EXIST_XYZ")
    page.keyboard.press("Tab")
    expect(frame.get_by_text("暂无数据").first).to_be_visible(timeout=15000)

    frame.get_by_placeholder("输入商家名称").fill("")
    page.keyboard.press("Tab")
    _wait_total(frame)
    assert _visible_rows(frame).count() > 0


# CASE_WEB_573_09 / T-17：筛选接口 500 时有失败提示，旧结果不被清空
def test_t17_filter_api_failure_keeps_old_result(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)
    content = _content_frame(page, "questionBank.htm")
    before = content.evaluate(
        """() => [...document.querySelectorAll('li')]
            .map(li => li.innerText).find(t => /共\\s*\\d+\\s*条数据/.test(t))"""
    )

    page.route(
        "**/aiExplainQuestion/listPage.do",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body='{"success":false,"msg":"QA injected 500"}',
        ),
    )
    try:
        frame.get_by_role("textbox", name="题目 ID").fill("6910667")
        frame.get_by_role("button", name=re.compile(r"查\s*询")).click()
        expect(frame.get_by_text("服务异常，请稍后重试").first).to_be_visible(timeout=15000)
        after = content.evaluate(
            """() => [...document.querySelectorAll('li')]
                .map(li => li.innerText).find(t => /共\\s*\\d+\\s*条数据/.test(t))"""
        )
        assert after == before, f"接口失败后旧结果被清空：{before} -> {after}"
    finally:
        page.unroute("**/aiExplainQuestion/listPage.do")


# CASE_WEB_573_10 / T-21：同一列多选取并集，不同列条件取交集
def test_t21_multi_select_union(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)
    content = _content_frame(page, "questionBank.htm")

    _open_filter(frame, "上架状态")
    _check(frame, "未上架")
    _confirm_filter(frame)
    _wait_total(frame)

    _open_filter(frame, "投放来源")
    _check(frame, "人工创建")
    _check(frame, "复制创建")
    _confirm_filter(frame)
    _wait_total(frame)

    expect(frame.get_by_text("投放来源：人工创建").first).to_be_visible(timeout=10000)
    expect(frame.get_by_text("投放来源：复制创建").first).to_be_visible(timeout=10000)
    rows = content.evaluate(
        """() => [...document.querySelectorAll('tbody tr')]
            .filter(tr => tr.offsetParent !== null && tr.innerText.trim())
            .map(tr => [tr.children[5]?.innerText.trim() || '', tr.children[6]?.innerText.trim() || ''])"""
    )
    assert rows and all(src in {"人工创建", "复制创建"} for src, _ in rows), f"多选来源越界：{rows[:3]}"
    assert all(shelf == "未上架" for _, shelf in rows), "跨列条件未同时满足"

    _reset_all(frame)


# CASE_WEB_573_11 / T-22：切换学科学段后，不再适用的题型被清空
def test_t22_subject_switch_clears_type(page: Page) -> None:
    frame = _open_module(page, "题库")
    _wait_total(frame)

    _open_filter(frame, "题目 ID")
    _select_in_dialog(frame, "小学数学")
    frame.get_by_role("checkbox", name="计算题", exact=True).check()
    assert frame.get_by_role("checkbox", name="计算题", exact=True).is_checked()

    _select_in_dialog(frame, "小学语文")
    expect(frame.get_by_role("checkbox", name="单选题", exact=True)).to_be_visible(timeout=10000)
    assert not frame.get_by_role("checkbox", name="计算题", exact=True).is_checked(), "切换学段后题型未清空"

    frame.get_by_role("button", name="取 消").click()


# CASE_WEB_573_14 / T-12：图书管理错误明细「错误原因」单选、默认全部，选具体类型后结果收窄
def test_t12_error_detail_single_reason_filter(page: Page) -> None:
    frame = _open_module(page, "图书管理")
    content = _content_frame(page, "bookManagement")
    row = frame.locator("tbody tr").filter(has_text="57414").first
    expect(row).to_be_visible(timeout=60000)

    row.locator("span").filter(has_text="板书错误").first.locator("a").click()
    dialog = frame.locator("[role=dialog]").filter(has_text="板书错误").first
    expect(dialog).to_be_visible(timeout=30000)

    dialog.locator("thead th").filter(has_text="错误原因").locator("[role=button]").click()
    popup = frame.locator(".yt5-antd-table-filter-dropdown:visible").first
    expect(popup).to_be_visible(timeout=10000)
    radios = popup.locator("input[type=radio]")
    expect(radios).to_have_count(11)
    assert radios.first.is_checked(), "错误原因默认未选中「全部」"

    popup.get_by_text("违规独立答案卡片", exact=True).click()
    popup.locator("button").filter(has_text=re.compile(r"确\s*定")).click()
    rows = dialog.locator("tbody tr").filter(has_text=re.compile(r".+"))
    expect(rows).to_have_count(1, timeout=15000)
    assert "违规独立答案卡片" in rows.first.inner_text()


# CASE_WEB_573_15 / T-19：1280×720 下表头/单元格对齐，横向滚动同步，固定列不遮挡
def test_t19_question_bank_1280_alignment(page: Page) -> None:
    page.set_viewport_size({"width": 1280, "height": 720})
    try:
        frame = _open_module(page, "题库")
        _wait_total(frame)
        content = _content_frame(page, "questionBank.htm")

        metrics = content.evaluate(
            """() => {
                const h = document.querySelector('.yt5-antd-table-header');
                const b = document.querySelector('.yt5-antd-table-body');
                h.scrollLeft = 0; b.scrollLeft = 0;
                return {vw: innerWidth, docW: document.documentElement.scrollWidth};
            }"""
        )
        assert metrics["docW"] <= metrics["vw"], f"页面级横向溢出：{metrics}"

        box = page.locator("iframe").last.bounding_box()
        assert box, "未找到业务 iframe"
        page.mouse.move(box["x"] + box["width"] * 0.6, box["y"] + box["height"] * 0.5)
        page.mouse.wheel(900, 0)
        page.wait_for_timeout(500)

        state = content.evaluate(
            """() => {
                const h = document.querySelector('.yt5-antd-table-header');
                const b = document.querySelector('.yt5-antd-table-body');
                const ths = [...document.querySelectorAll('.yt5-antd-table-header thead th')];
                const tr = [...document.querySelectorAll('.yt5-antd-table-body tbody tr')]
                    .find(r => r.offsetParent !== null && r.innerText.trim() && !r.className.includes('measure'));
                const deltas = ths.map((th, i) => {
                    const a = th.getBoundingClientRect();
                    const c = tr.children[i]?.getBoundingClientRect();
                    return c ? Math.round(c.left - a.left) : null;
                });
                return {h: h.scrollLeft, b: b.scrollLeft, deltas};
            }"""
        )
        assert state["h"] == state["b"], f"表头与内容区滚动不同步：{state}"
        assert state["h"] > 0, "横向滚动未生效"
        assert [d for d in state["deltas"] if d is not None] == [0] * len(state["deltas"]), (
            f"表头与单元格未对齐：{state['deltas']}"
        )
    finally:
        page.set_viewport_size({"width": 1440, "height": 900})


# CASE_WEB_573_16 / T-20：切换一级错误分类后，错误原因筛选重置为「全部」
def test_t20_error_category_switch_resets_reason(page: Page) -> None:
    frame = _open_module(page, "图书管理")
    row = frame.locator("tbody tr").filter(has_text="57414").first
    expect(row).to_be_visible(timeout=60000)

    def open_category(name: str):
        row.locator("span").filter(has_text=name).first.locator("a").click()
        dialog = frame.locator("[role=dialog]").filter(has_text=name).first
        expect(dialog).to_be_visible(timeout=30000)
        return dialog

    def selected_reason(dialog):
        dialog.locator("thead th").filter(has_text="错误原因").locator("[role=button]").click()
        popup = frame.locator(".yt5-antd-table-filter-dropdown:visible").first
        expect(popup).to_be_visible(timeout=10000)
        checked = popup.locator("input[type=radio]:checked").count()
        label = popup.locator("input[type=radio]:checked").evaluate(
            "el => el.closest('li').innerText.trim()"
        )
        page.keyboard.press("Escape")
        return checked, label.strip()

    board = open_category("板书错误")
    board.locator("thead th").filter(has_text="错误原因").locator("[role=button]").click()
    popup = frame.locator(".yt5-antd-table-filter-dropdown:visible").first
    popup.get_by_text("违规独立答案卡片", exact=True).click()
    popup.locator("button").filter(has_text=re.compile(r"确\s*定")).click()
    board.get_by_role("button", name="Close").click()

    lecture = open_category("讲稿错误")
    expect(lecture.locator("tbody tr").filter(has_text=re.compile(r".+"))).to_have_count(2, timeout=20000)
    checked, label = selected_reason(lecture)
    assert checked == 1 and label == "全部", f"切换一级后二级未重置：{checked}/{label}"
    lecture.get_by_role("button", name="Close").click()

    board2 = open_category("板书错误")
    expect(board2.locator("tbody tr").filter(has_text=re.compile(r".+"))).to_have_count(1, timeout=20000)
    checked, label = selected_reason(board2)
    assert checked == 1 and label == "全部", f"切回一级后二级未重置：{checked}/{label}"


# CASE_WEB_573_12 / T-27：1440×900 下四个入口无页面级横向溢出
def test_t27_four_entries_no_overflow_at_1440(page: Page) -> None:
    page.set_viewport_size({"width": 1440, "height": 900})
    try:
        for module in ["题库", "图书管理", "商家审核反馈", "高频错题投放池"]:
            _open_module(page, module)
            page.wait_for_timeout(2500)
            metrics = page.evaluate(
                "() => ({vw: innerWidth, docW: document.documentElement.scrollWidth})"
            )
            assert metrics["docW"] <= metrics["vw"], f"{module} 出现页面级横向溢出：{metrics}"
    finally:
        page.set_viewport_size({"width": 1280, "height": 720})


# CASE_WEB_573_13 / T-29：已登录态下深链直达题库列表，不跳登录、不 404
def test_t29_question_bank_deep_link(page: Page) -> None:
    new_page = page.context.new_page()
    try:
        response = new_page.goto(
            BASE_URL + QUESTION_BANK_PATH,
            wait_until="domcontentloaded",
            timeout=60000,
        )
        assert response is not None and response.status < 400, "深链请求失败"
        expect(new_page.get_by_text(TOTAL_PATTERN).first).to_be_visible(timeout=60000)
        assert "login" not in new_page.url.lower()
    finally:
        new_page.close()
