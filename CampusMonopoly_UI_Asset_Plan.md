# CampusMonopoly 界面元素与素材清单

## 一、整体视觉风格

- 风格定位：清爽扁平校园风，适合 Web/App/桌面数字原型。
- 视觉关键词：明亮、轻松、宿舍感、校园生活、低压力社交、轻策略。
- 主色建议：校园绿或清爽蓝，用于主按钮、当前位置、积极收益。
- 辅色建议：暖黄色，用于金币、奖励、奖学金、提示高亮。
- 警示色建议：柔和红色，用于支出、破产、罚款、补考。
- 中性色建议：浅灰、白色、深灰，用于卡片底色、文字和分隔线。
- 图标风格：线性图标或轻填充图标，圆角统一，避免复杂写实。
- 卡牌风格：统一卡面模板，通过颜色区分类型。
- 字体建议：中文无衬线字体，标题清晰，说明文字短句化。

## 二、核心界面元素

| 界面 | 需要设计的元素 |
| --- | --- |
| 开始页 | 游戏标题、开始游戏按钮、规则入口、设置入口 |
| 宿舍房间创建页 | 房间名称输入、玩家人数选择、生活费档位选择、确认开局按钮 |
| 玩家设置页 | 玩家头像、玩家昵称、棋子颜色、储蓄目标选择 |
| 主棋盘页 | 校园棋盘、玩家棋子、当前玩家提示、骰子按钮、回合数、公共储备金 |
| 玩家状态栏 | 资金、社交值、理财值、手牌数、状态标记、是否破产 |
| 回合操作面板 | 投骰子、使用行动牌、执行地块操作、结束回合 |
| 手牌区 | 最多 3 张行动牌、可使用状态、不可使用状态、已选择状态 |
| 事件弹窗 | 被动事件标题、事件图标、金额变化、确认按钮 |
| 银行界面 | 当前资金、可存金额、定期存款列表、到期回合、储蓄目标进度 |
| 宿舍共同基金界面 | 基金余额、参与玩家、可用用途、确认支付按钮 |
| 社交互动界面 | 邀请玩家、互助请求、团建参与选择、社交值变化提示 |
| 结算页 | 获胜玩家、剩余资金、储蓄完成情况、社交称号、理财称号 |

## 三、地图与棋盘素材

| 素材 | 设计说明 | 建议格式 | 优先级 |
| --- | --- | --- | --- |
| 校园棋盘底图 | 环形或路线型地图，包含 16 个地块 | PNG/SVG | P0 |
| 地块格子 | 每个地块包含独立图标、名称、颜色标签 | SVG | P0 |
| 玩家棋子 | 2-4 个不同颜色棋子 | SVG/PNG | P0 |
| 骰子 1 点 | 静态骰子图标 | SVG | P0 |
| 骰子 2 点 | 静态骰子图标 | SVG | P0 |
| 骰子 3 点 | 静态骰子图标 | SVG | P0 |
| 骰子 4 点 | 静态骰子图标 | SVG | P0 |
| 骰子 5 点 | 静态骰子图标 | SVG | P0 |
| 骰子 6 点 | 静态骰子图标 | SVG | P0 |
| 移动路径高亮 | 显示玩家本回合移动路线 | SVG/CSS | P1 |
| 当前地块高亮 | 标识玩家落点 | SVG/CSS | P1 |
| 当前玩家光环 | 突出正在行动的玩家 | SVG/CSS | P1 |

## 四、地块图标

| 地块 | 图标方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 教学楼 | 楼房、黑板或书本 | `tile_teaching_building.svg` | P0 |
| 食堂 | 餐盘、筷子或碗 | `tile_canteen.svg` | P0 |
| 图书馆 | 书架或打开的书 | `tile_library.svg` | P0 |
| 超市 | 购物袋或购物车 | `tile_supermarket.svg` | P0 |
| 快递站 | 包裹盒 | `tile_package_station.svg` | P0 |
| 奶茶店 | 奶茶杯 | `tile_milk_tea.svg` | P0 |
| 外卖店 | 外卖袋或餐盒 | `tile_takeout.svg` | P0 |
| 网购点 | 手机购物或快递箱 | `tile_online_shopping.svg` | P0 |
| 电影院 | 电影票或放映机 | `tile_cinema.svg` | P0 |
| 兼职中心 | 工牌或握手 | `tile_part_time_center.svg` | P0 |
| 宿舍 | 床、门牌或宿舍楼 | `tile_dormitory.svg` | P0 |
| 银行 | 银行卡、存钱罐或银行建筑 | `tile_bank.svg` | P0 |
| 考点 | 试卷、笔或准考证 | `tile_exam_site.svg` | P0 |
| 社团广场 | 人群、旗帜或社团摊位 | `tile_club_square.svg` | P0 |
| 心愿墙 | 便签、星星或留言板 | `tile_wish_wall.svg` | P0 |
| 宿舍议事厅 | 圆桌、对话气泡或会议图标 | `tile_dorm_meeting.svg` | P0 |

## 五、行动牌素材

| 行动牌 | 图标方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 发起团建聚会 | 聚会、饮料、多人图标 | `card_action_group_party.png` | P0 |
| 举办生日会 | 蛋糕、礼物 | `card_action_birthday_party.png` | P0 |
| 代取快递跑腿 | 快递盒、奔跑人物 | `card_action_package_runner.png` | P0 |
| 拼单省钱 | 拼单标签、折扣符号 | `card_action_group_discount.png` | P0 |
| 宿舍分摊采购 | 购物袋、多人分摊 | `card_action_shared_purchase.png` | P0 |
| 申请助学金 | 信封、补助金 | `card_action_student_grant.png` | P0 |
| 请客喝奶茶 | 奶茶杯、爱心 | `card_action_treat_milk_tea.png` | P0 |
| 兼职加班 | 工牌、时钟 | `card_action_overtime_job.png` | P0 |
| 集体囤货 | 纸箱、仓储 | `card_action_bulk_stock.png` | P0 |
| 学霸辅导 | 书本、讲解气泡 | `card_action_peer_tutoring.png` | P0 |
| 闲置物品转卖 | 二手标签、循环箭头 | `card_action_secondhand_sale.png` | P0 |
| 宿舍公摊缴费 | 账单、宿舍图标 | `card_action_shared_bill.png` | P0 |
| 禁止 | 禁用符号、拦截手势 | `card_action_forbid.png` | P0 |
| 制定预算 | 计算器、预算表 | `card_action_budget.png` | P0 |
| 室友饭搭子 | 双人餐盘 | `card_action_meal_partner.png` | P0 |
| 二手教材互换 | 两本书、交换箭头 | `card_action_textbook_swap.png` | P0 |

## 六、被动事件素材

| 被动事件 | 图标方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 捡到饭卡 | 饭卡、闪光 | `card_event_found_meal_card.png` | P0 |
| 快递丢失 | 破损包裹 | `card_event_lost_package.png` | P0 |
| 考试挂科补考 | 红叉试卷 | `card_event_exam_resit.png` | P0 |
| 食堂饭菜免单 | 免费餐盘 | `card_event_free_meal.png` | P0 |
| 校园随机抽奖 | 抽奖箱 | `card_event_lucky_draw.png` | P0 |
| 水电费超支 | 水滴、电费账单 | `card_event_utility_overrun.png` | P0 |
| 捡到校园零钱 | 硬币 | `card_event_found_coins.png` | P0 |
| 网购踩雷退货 | 退货箭头、包裹 | `card_event_return_shipping.png` | P0 |
| 图书馆占座被罚 | 座位、罚款标识 | `card_event_library_fine.png` | P0 |
| 兼职额外奖励 | 奖金、工牌 | `card_event_job_bonus.png` | P0 |
| 饭卡遗失补办 | 饭卡、加号 | `card_event_meal_card_replace.png` | P0 |
| 奖学金附加奖励 | 奖章、书本 | `card_event_scholarship_bonus.png` | P0 |
| 室友帮忙代付 | 两人、付款图标 | `card_event_roommate_pay.png` | P0 |
| 校园消费券 | 优惠券 | `card_event_coupon.png` | P0 |
| 社团招新 | 社团摊位、旗帜 | `card_event_club_recruitment.png` | P0 |
| 临时班会 | 通知、讲台 | `card_event_class_meeting.png` | P0 |
| 预算执行成功 | 预算表、对勾 | `card_event_budget_success.png` | P0 |
| 宿舍夜谈 | 聊天气泡、宿舍窗户 | `card_event_dorm_talk.png` | P0 |

## 七、状态与数值图标

| 图标 | 图标方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 资金 | 金币或钱包 | `stat_money.svg` | P0 |
| 社交值 | 双人头像或对话气泡 | `stat_social.svg` | P0 |
| 理财值 | 上升曲线或存钱罐 | `stat_finance.svg` | P0 |
| 行动牌 | 卡牌叠放 | `stat_action_cards.svg` | P0 |
| 共同基金 | 多人存钱罐 | `stat_common_fund.svg` | P1 |
| 储蓄目标 | 靶心或进度条 | `stat_saving_goal.svg` | P1 |
| 父母转账 | 手机转账 | `stat_parent_transfer.svg` | P1 |
| 余额宝收益 | 增长箭头 | `stat_interest_income.svg` | P1 |
| 补考中 | 试卷红叉 | `status_exam_resit.svg` | P1 |
| 预算 | 计算器 | `status_budget.svg` | P1 |
| 孤立 | 灰色单人头像 | `status_isolated.svg` | P1 |
| 学习状态 | 书本星标 | `status_study.svg` | P1 |
| 消费券 | 票券 | `status_coupon.svg` | P1 |
| 拼单省钱 | 折扣标签 | `status_group_discount.svg` | P1 |

## 八、弹窗与反馈元素

| 反馈元素 | 设计方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 收入提示 | 绿色金额上浮 | `ui_income_popup.png` | P1 |
| 支出提示 | 红色金额下降 | `ui_expense_popup.png` | P1 |
| 储蓄完成提示 | 目标达成徽章 | `ui_saving_complete.png` | P1 |
| 社交值提升提示 | 对话气泡加一 | `ui_social_increase.png` | P1 |
| 理财值提升提示 | 曲线加一 | `ui_finance_increase.png` | P1 |
| 行动牌作废提示 | 卡牌灰化 | `ui_card_disabled.png` | P1 |
| 破产提示 | 资金归零、玩家出局 | `ui_bankrupt_popup.png` | P1 |
| 共同基金支付提示 | 基金扣款动画 | `ui_common_fund_pay.png` | P2 |
| 定期存款到期提示 | 本金加利息到账 | `ui_deposit_matured.png` | P2 |
| 回合切换提示 | 当前玩家头像放大或高亮 | `ui_turn_switch.png` | P2 |

## 九、结算页徽章

| 徽章 | 图标方向 | 建议文件名 | 优先级 |
| --- | --- | --- | --- |
| 理财达人 | 存钱罐、皇冠 | `badge_finance_master.svg` | P2 |
| 宿舍核心 | 多人头像、星标 | `badge_dorm_core.svg` | P2 |
| 靠谱室友 | 握手、盾牌 | `badge_reliable_roommate.svg` | P2 |
| 消费达人 | 购物袋 | `badge_spending_expert.svg` | P2 |
| 兼职之星 | 工牌、星星 | `badge_job_star.svg` | P2 |
| 学霸担当 | 书本、奖章 | `badge_study_leader.svg` | P2 |
| 社交新星 | 对话气泡、闪光 | `badge_social_star.svg` | P2 |
| 共赢宿舍 | 宿舍楼、彩带 | `badge_co_win_dorm.svg` | P2 |

## 十、素材格式与命名

- 图标优先使用 SVG。
- 卡牌、棋盘底图、弹窗插画可使用 PNG。
- 命名统一使用英文小写和下划线。
- 地块图标命名示例：`tile_bank.svg`
- 行动牌命名示例：`card_action_budget.png`
- 被动事件命名示例：`card_event_lost_package.png`
- 状态图标命名示例：`status_budget.svg`
- UI 反馈命名示例：`ui_income_popup.png`
- 徽章命名示例：`badge_finance_master.svg`

## 十一、优先级

| 优先级 | 范围 |
| --- | --- |
| P0 | 主棋盘、玩家状态栏、骰子、16 个地块图标、16 张行动牌、18 个被动事件弹窗 |
| P1 | 银行界面、储蓄目标、共同基金、社交互动、状态图标、核心反馈弹窗 |
| P2 | 结算页徽章、动画反馈、额外装饰素材 |

## 十二、P0 素材汇总

- 主棋盘底图 1 个。
- 玩家状态栏组件 1 组。
- 骰子图标 6 个。
- 地块图标 16 个。
- 行动牌卡面 16 张。
- 被动事件卡面 18 张。
- 基础弹窗模板 1 组。
- 玩家棋子 2-4 个。

## 十三、P1 素材汇总

- 银行界面组件 1 组。
- 储蓄目标进度组件 1 组。
- 宿舍共同基金组件 1 组。
- 社交互动组件 1 组。
- 状态与数值图标 14 个。
- 核心反馈弹窗 7 个。

## 十四、P2 素材汇总

- 结算页徽章 8 个。
- 高级反馈动画或插画 3 个。
- 额外装饰素材若干，例如校园云朵、公告栏、课表贴纸、宿舍小物件。
