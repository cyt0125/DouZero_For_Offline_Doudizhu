import sys
import random
from collections import Counter
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QMessageBox, QLabel, QComboBox, QGroupBox
)
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from douzero.env.game import GameEnv, InfoSet
from douzero.evaluation.deep_agent import DeepAgent
from douzero.env.env import Env, DummyAgent



# 牌型转换映射
EnvCard2RealCard = {
    3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
    8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'
}

RealCard2EnvCard = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30
}

# 卡牌配置
AllCards = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2', 'X', 'D']
initial_card_counts = {
    '3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4, '9': 4, 'T': 4,
    'J': 4, 'Q': 4, 'K': 4, 'A': 4, '2': 4, 'X': 1, 'D': 1
}


class GameState:
    def __init__(self):
        self.reset()
        # 新增AI相关属性
        self.ai_agent = None  # AI代理
        self.ai_suggestion = []  # AI推荐的出牌
        self.win_rate = 0.0  # 当前胜率
        self.env = None  # 游戏环境
        self.user_position = None  # 新增user_position属性
        self.card_play_model_path_dict = {
            "landlord": "baselines/douzero_WP/landlord.ckpt",
            "landlord_up": "baselines/douzero_WP/landlord_up.ckpt",
            "landlord_down": "baselines/douzero_WP/landlord_down.ckpt"
        }  # 新增card_play_model_path_dict属性
        self.player_hands = {
            "player": [],
            "up": [],  # 新增上家手牌初始化
            "down": []  # 新增下家手牌初始化
        }
        self.bomb_num = 0
        # 确保以下字段存在
        self.played_cards = {
            'landlord': [],
            'landlord_up': [],
            'landlord_down': []
        }
        self.played_counts = {"player": 0, "up": 0, "down": 0}
        self.position_map = {
            # 当地主是玩家（"player"）
            "player": {
                "player": "landlord",  # 玩家是地主
                "up": "landlord_up",  # 上家是农民
                "down": "landlord_down"  # 下家是农民
            },
            # 当地主是上家（"up"）
            "up": {
                "up": "landlord",  # 上家是地主
                "player": "landlord_down",  # 玩家是下家农民
                "down": "landlord_up"  # 下家是上家农民
            },
            # 当地主是下家（"down"）
            "down": {
                "down": "landlord",  # 下家是地主
                "up": "landlord_up",  # 上家是上家农民
                "player": "landlord_down"  # 玩家是下家农民
            }
        }


    def reset(self):
        self.phase = "选牌阶段"
        self.player_hands = {"player": [], "up": [], "down": []}
        self.landlord = ""
        self.history = []
        self.landlord_cards = []
        self.shared_cards = []
        self.current_player = ""
        self.current_leader = ""
        self.player_order = []
        self.last_played = []  # 确保有初始值
        self.played_counts = {"player": 0, "up": 0, "down": 0}
        self.user_position = "landlord"  # 新增默认身份
        self.consecutive_passes = 0  # 连续跳过计数器
        self.must_play = False  # 强制出牌标志
        self.init_ai_agent()

    def init_ai_agent(self):
        """
        初始化AI代理
        """
        try:
            model_paths = {
                "landlord": "baselines/douzero_WP/landlord.ckpt",
                "landlord_up": "baselines/douzero_WP/landlord_up.ckpt",
                "landlord_down": "baselines/douzero_WP/landlord_down.ckpt"
            }
            if self.landlord:
                role = "landlord" if self.landlord == "player" else "landlord_up" if self.landlord == "up" else "landlord_down"
                import os
                if not os.path.exists(model_paths[role]):
                    print(f"模型文件 {model_paths[role]} 不存在")
                    # 移除无效的self参数，改为使用全局父窗口
                    from PyQt5.QtWidgets import QApplication
                    QMessageBox.critical(QApplication.activeWindow(), "错误", f"模型文件 {model_paths[role]} 不存在")
                    return
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"AI模型加载失败: {str(e)}")
            # 同样修改这里的错误提示
            QMessageBox.critical(QApplication.activeWindow(), "错误", f"AI模型加载失败: {str(e)}")

    def create_game_env(self):
        try:
            # 确保地主位置有效
            if self.landlord not in ["player", "up", "down"]:
                raise ValueError(f"无效的地主位置: {self.landlord}")

            # 动态确定玩家的游戏角色
            self.user_position = self.position_map[self.landlord][self.landlord]

            # 初始化游戏环境
            self.env = GameEnv(players={
                'landlord': DummyAgent('landlord'),
                'landlord_up': DummyAgent('landlord_up'),
                'landlord_down': DummyAgent('landlord_down')
            })

            # 初始化AI代理（关键修复：使用动态角色）
            self.ai_agent = DeepAgent(
                self.user_position,
                self.card_play_model_path_dict[self.user_position]
            )

            # 合并地主手牌（确保底牌已合并）
            landlord_hand = self.player_hands[self.landlord]
            if len(landlord_hand) != 20:
                raise ValueError(f"地主手牌应为20张，实际为{len(landlord_hand)}张")

            # 构建 card_play_data
            card_play_data = {
                'landlord': sorted([RealCard2EnvCard[c] for c in landlord_hand]),
                'landlord_up': [0] * 17 if self.landlord != "up" else [],
                'landlord_down': [0] * 17 if self.landlord != "down" else [],
                'three_landlord_cards': sorted([RealCard2EnvCard[c] for c in self.landlord_cards])
            }

            # 初始化游戏环境
            self.env.card_play_init(card_play_data)

        except Exception as e:
            print(f"创建游戏环境时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            raise



    def set_landlord(self, landlord):
        self.landlord = landlord
        try:
            # 确保已正确设置初始手牌
            if not hasattr(self, 'player_hands'):
                self.player_hands = {'player': [], 'up': [], 'down': []}

            # 确保存在有效手牌（原错误中手牌只有3张，说明初始手牌未正确传递）
            if len(self.player_hands[landlord]) != 17:  # 增加初始手牌验证
                raise ValueError(f"初始手牌异常！应为17张，实际{len(self.player_hands[landlord])}张")

            # 合并底牌前先拷贝原始手牌
            original_hand = self.player_hands[landlord].copy()
            valid_cards = [c for c in self.landlord_cards if c in RealCard2EnvCard]

            # 带重复检查的合并
            for card in valid_cards:
                if self.player_hands[landlord].count(card) + original_hand.count(card) > 4:
                    raise ValueError(f"卡牌 {card} 超过最大数量限制")

            self.player_hands[landlord].extend(valid_cards)

            # 排序前验证总数量
            if len(self.player_hands[landlord]) != 20:
                actual = self.player_hands[landlord]
                raise ValueError(f"合并后手牌应为20张，实际{len(actual)}张\n"
                                 f"初始手牌: {original_hand}\n"
                                 f"合并的底牌: {valid_cards}")

            # 使用稳定排序
            self.player_hands[landlord].sort(
                key=lambda x: (RealCard2EnvCard[x], x == '?')
            )

        except Exception as e:
            print(f"[DEBUG] 当前地主手牌: {self.player_hands.get(landlord, [])}")
            print(f"[DEBUG] 地主角色: {landlord}")
            print(f"[DEBUG] 底牌内容: {self.landlord_cards}")
            raise
        # 设置出牌顺序
        if landlord == "player":
            self.player_order = ["player", "down", "up"]
        elif landlord == "up":
            self.player_order = ["up", "player", "down"]
        elif landlord == "down":
            self.player_order = ["down", "up", "player"]
        self.current_player = landlord  # 地主先出牌



    def next_player(self):
        current_index = self.player_order.index(self.current_player)
        next_p = self.player_order[(current_index + 1) % 3]
        self.current_player = next_p  # 更新当前玩家
        print(f"下一个玩家: {self.current_player}")  # 保留调试输出
        return next_p  # 同时返回下一个玩家

    def reset_round(self):
        self.current_player = self.current_leader
        self.last_played = []


class CardSelectionDialog(QDialog):
    def __init__(self, title, max_selection, parent=None, is_play_phase=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(800, 400)
        self.max_selection = max_selection
        self.selected_cards = []
        self.is_play_phase = is_play_phase
        self.card_counts = initial_card_counts.copy() if not is_play_phase else {}
        self.parent = parent

        layout = QVBoxLayout()

        self.hand_label = QLabel("已选牌区" if is_play_phase else "已选手牌")
        self.hand_list = QListWidget()
        self.hand_list.setFixedHeight(100)
        self.hand_list.setFlow(QtWidgets.QListWidget.LeftToRight)
        self.hand_list.itemClicked.connect(self.remove_from_hand)
        layout.addWidget(self.hand_label)
        layout.addWidget(self.hand_list)

        self.card_label = QLabel("可选牌库" if is_play_phase else "可选手牌")
        self.card_list = QListWidget()
        self.card_list.itemClicked.connect(self.add_to_hand)
        layout.addWidget(self.card_label)
        layout.addWidget(self.card_list)

        btn_layout = QHBoxLayout()
        if self.is_play_phase:
            self.pass_button = QPushButton("过")
            # 根据游戏状态设置按钮状态
            if (self.parent.game_state.must_play or
                    (self.parent.game_state.current_player == self.parent.game_state.landlord
                     and not self.parent.game_state.history)):
                self.pass_button.setEnabled(False)
            self.pass_button.clicked.connect(self.pass_clicked)
            btn_layout.addWidget(self.pass_button)

        self.confirm_button = QPushButton("出牌" if is_play_phase else "确定")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.confirm_button)
        btn_layout.addWidget(self.cancel_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.update_card_list()

    def pass_clicked(self):
        self.selected_cards = []
        self.accept()

    def update_card_list(self):
        self.card_list.clear()
        for card, count in self.card_counts.items():
            if count > 0:
                display_text = f"{card} (剩余: {count})" if not self.is_play_phase else f"{card} (可选: {count})"
                item = QListWidgetItem(display_text)
                item.setData(QtCore.Qt.UserRole, card)
                self.card_list.addItem(item)



    def add_to_hand(self, item):
        if self.max_selection > 0 and len(self.selected_cards) >= self.max_selection:
            QMessageBox.warning(self, "提示", f"最多选择{self.max_selection}张!")
            return

        card = item.data(QtCore.Qt.UserRole)
        if self.card_counts.get(card, 0) > 0:
            self.selected_cards.append(card)
            self.hand_list.addItem(QListWidgetItem(card))
            self.card_counts[card] -= 1
            self.update_card_list()
            if self.max_selection > 0 and len(self.selected_cards) == self.max_selection:
                self.confirm_button.setEnabled(True)
            elif self.max_selection == 0:
                self.confirm_button.setEnabled(True)

    def remove_from_hand(self, item):
        card = item.text()
        if card in self.selected_cards:
            self.selected_cards.remove(card)
            self.hand_list.takeItem(self.hand_list.row(item))
            self.card_counts[card] += 1
            self.update_card_list()
            if self.max_selection > 0 and len(self.selected_cards) < self.max_selection:
                self.confirm_button.setEnabled(False)

    def get_selected_cards(self):
        return self.selected_cards


class LandlordSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择地主")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()

        self.combo = QComboBox()
        self.combo.addItem("上家", "up")
        self.combo.addItem("本家", "player")
        self.combo.addItem("下家", "down")
        layout.addWidget(QLabel("请选择地主:"))
        layout.addWidget(self.combo)

        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.clicked.connect(self.accept)
        layout.addWidget(self.confirm_btn)

        self.setLayout(layout)

    def get_landlord(self):
        return self.combo.currentData()



class PlayPhaseWindow(QtWidgets.QMainWindow):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.setup_ui()
        self.turn_label = QLabel()
        self.win_rate_label = QLabel("胜率: 0.0%")  # 添加胜率标签
        central_widget = self.centralWidget()
        central_widget.layout().insertWidget(0, self.turn_label)
        central_widget.layout().insertWidget(1, self.win_rate_label)  # 将胜率标签添加到界面
        self.update_display()



    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        position_layout = QHBoxLayout()

        self.up_group = QGroupBox("上家")
        self.up_label = QLabel()
        up_layout = QVBoxLayout()
        up_layout.addWidget(self.up_label)
        self.up_group.setLayout(up_layout)

        self.player_group = QGroupBox("本家手牌")
        self.hand_list = QListWidget()
        self.hand_list.setFlow(QtWidgets.QListWidget.LeftToRight)
        player_layout = QVBoxLayout()
        player_layout.addWidget(self.hand_list)
        self.player_group.setLayout(player_layout)

        self.down_group = QGroupBox("下家")
        self.down_label = QLabel()
        down_layout = QVBoxLayout()
        down_layout.addWidget(self.down_label)
        self.down_group.setLayout(down_layout)

        position_layout.addWidget(self.up_group)
        position_layout.addWidget(self.player_group)
        position_layout.addWidget(self.down_group)
        layout.addLayout(position_layout)

        info_layout = QHBoxLayout()

        self.landlord_group = QGroupBox("地主信息")
        self.landlord_label = QLabel("地主：未确定")
        landlord_layout = QVBoxLayout()
        landlord_layout.addWidget(self.landlord_label)
        self.landlord_group.setLayout(landlord_layout)

        self.history_group = QGroupBox("出牌历史")
        self.history_list = QListWidget()
        history_layout = QVBoxLayout()
        history_layout.addWidget(self.history_list)
        self.history_group.setLayout(history_layout)

        info_layout.addWidget(self.landlord_group)
        info_layout.addWidget(self.history_group)
        layout.addLayout(info_layout)

        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("出牌")
        self.pass_btn = QPushButton("过")
        self.ai_button = QPushButton("AI推荐")  # 添加AI推荐按钮
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.pass_btn)
        btn_layout.addWidget(self.ai_button)  # 将按钮添加到布局
        layout.addLayout(btn_layout)

        central_widget.setLayout(layout)
        self.play_btn.clicked.connect(self.play_cards)
        self.pass_btn.clicked.connect(self.pass_turn)
        self.ai_button.clicked.connect(self.get_ai_suggestion)  # 绑定点击事件

    def get_ai_suggestion(self):
        try:
            # 修正角色定位逻辑
            role_map = {
                "player": {
                    "player": "landlord",
                    "up": "landlord_up",
                    "down": "landlord_down"
                },
                "up": {
                    "player": "landlord_down",
                    "up": "landlord",
                    "down": "landlord_up"
                },
                "down": {
                    "player": "landlord_up",
                    "up": "landlord_down",
                    "down": "landlord"
                }
            }
            player_role = role_map[self.game_state.landlord][self.game_state.current_player]

            # 转换手牌时添加容错处理
            player_hand = []
            for card in self.game_state.player_hands["player"]:
                try:
                    player_hand.append(RealCard2EnvCard[card])
                except KeyError:
                    print(f"无效牌型被过滤: {card}")
                    continue

            # 初始化InfoSet必须携带的字段
            infoset = InfoSet(player_role)
            infoset.player_hand_cards = player_hand
            infoset.num_cards_left_dict = {
                "landlord": 20 - self.game_state.played_counts.get(self.game_state.landlord, 0),
                "landlord_up": 17 - self.game_state.played_counts.get("up", 0),
                "landlord_down": 17 - self.game_state.played_counts.get("down", 0)
            }
            infoset.last_move = [RealCard2EnvCard[c] for c in self.game_state.last_played if c in RealCard2EnvCard]
            infoset.legal_actions = self.get_legal_actions()
            infoset.bomb_num = self.game_state.bomb_num
            infoset.played_cards = {  # 必须包含的字段
                "landlord": [RealCard2EnvCard[c] for c in self.game_state.played_cards['landlord']],
                "landlord_up": [RealCard2EnvCard[c] for c in self.game_state.played_cards['landlord_up']],
                "landlord_down": [RealCard2EnvCard[c] for c in self.game_state.played_cards['landlord_down']]
            }

            # 调用AI模型
            action, confidence = self.game_state.ai_agent.act(infoset)

            if action is not None:
                suggested_cards = [EnvCard2RealCard.get(int(card), '?') for card in action]
                suggested_cards = [c for c in suggested_cards if c != '?']  # 过滤无效牌
                QMessageBox.information(self, "AI推荐", f"建议出牌: {' '.join(suggested_cards)}")
                self.game_state.ai_suggestion = suggested_cards
            else:
                QMessageBox.warning(self, "错误", "AI未给出有效建议")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"AI推荐失败: {str(e)}")
            print(f"当前玩家: {self.game_state.current_player}, 地主: {self.game_state.landlord}")
            print(f"玩家手牌: {self.game_state.player_hands['player']}")
            print(f"上家手牌: {self.game_state.player_hands['up']}")
            print(f"下家手牌: {self.game_state.player_hands['down']}")
            print(f"底牌: {self.game_state.landlord_cards}")


    def map_card(self, card, mapping_dict):
        try:
            return mapping_dict[card]
        except KeyError:
            print(f"牌型映射错误: 无法映射牌 {card}")
            raise

    def get_player_role(self):
        """获取玩家角色标识"""
        return 'landlord' if self.game_state.landlord == "player" else 'peasant'

    def get_player_position(self):
        """根据当前玩家和地主位置返回正确的游戏角色"""
        landlord = self.game_state.landlord
        current_player = self.game_state.current_player

        # 使用 position_map 动态映射
        try:
            return self.game_state.position_map[landlord][current_player]
        except KeyError:
            raise ValueError(
                f"无效的玩家位置: landlord={landlord}, current_player={current_player}"
            )

    def get_legal_actions(self):
        try:
            if not self.game_state.env:
                self.game_state.create_game_env()

            # 强制更新游戏状态
            self.game_state.env.acting_player_position = self.get_player_position()
            self.game_state.env.get_infoset()
            return self.game_state.env.get_legal_card_play_actions()

        except Exception as e:
            print(f"获取合法动作时出错: {str(e)}")
            return []
    def update_display(self):
        landlord_map = {"up": "上家", "player": "本家", "down": "下家"}
        self.landlord_label.setText(f"地主：{landlord_map.get(self.game_state.landlord, '未确定')}")

        current_player_name = landlord_map.get(self.game_state.current_player, "未知")
        self.turn_label.setText(f"当前轮到：{current_player_name}出牌")

        self.hand_list.clear()
        self.hand_list.addItems(sorted(self.game_state.player_hands["player"]))

        self.up_label.setText(self.get_status_text('up'))
        self.down_label.setText(self.get_status_text('down'))

        self.history_list.clear()
        self.history_list.addItems(self.game_state.history[-10:])

        is_player_turn = (self.game_state.current_player == "player")
        self.play_btn.setEnabled(is_player_turn)
        self.pass_btn.setEnabled(is_player_turn and not self.game_state.must_play)
        self.win_rate_label.setText(f"胜率: {self.game_state.win_rate * 100:.2f}%")  # 更新胜率显示

        if not is_player_turn:
            self.handle_opponent_turn()

    def get_status_text(self, role):
        landlord = self.game_state.landlord
        if role == landlord:
            remaining = 20 - self.game_state.played_counts[role]
            return f"地主剩余需出牌：{remaining}张"
        else:
            if landlord == "player":
                remaining = 17 - self.game_state.played_counts[role]
                return f"农民剩余需出牌：{remaining}张"
            else:
                total = sum(self.game_state.played_counts[p] for p in ["up", "down"] if p != landlord)
                remaining = 17 - total
                return f"农民剩余需出牌：{remaining}张"

    def play_cards(self):
        dialog = CardSelectionDialog("选择要出的牌", 0, self, is_play_phase=True)
        current_hand = self.game_state.player_hands["player"]

        card_counts = Counter(current_hand)
        dialog.card_counts = {k: v for k, v in card_counts.items() if v > 0}
        dialog.update_card_list()

        if dialog.exec_() == QDialog.Accepted:
            selected = dialog.get_selected_cards()
            if not selected:
                QMessageBox.warning(self, "错误", "请选择要出的牌！")
                return
            if not self.validate_play(selected):
                QMessageBox.warning(self, "错误", "无效出牌组合！")
                return

            for card in selected:
                self.game_state.player_hands["player"].remove(card)
            self.game_state.played_counts["player"] += len(selected)

            # 更新胜率
            # infoset = self.get_infoset()  # 获取当前游戏状态
            # self.game_state.calculate_win_rate(infoset)  # 计算胜率

            self.update_game_state(selected, "玩家")

    def validate_play(self, cards):
        # 如果是AI推荐的牌型，直接通过
        if set(cards) == set(self.game_state.ai_suggestion):
            return True

        if not cards:
            return False

         # 新增火箭验证
        if set(cards) == {'X', 'D'}:
            return True


        if len(cards) == 1:
            return True

        if len(cards) == 2:
            return len(set(cards)) == 1 or set(cards) == {'x', 'X'}

        # 重构炸弹验证（4张相同牌）
        if len(cards) == 4:
            if len(set(cards)) == 1:
                return True  # 普通炸弹

        # 改进顺子验证（排除2和大小王）
        if len(cards) >= 5:
            try:
                indexes = sorted([AllCards.index(c) for c in cards])
                # 检查是否连续且不包含2/X/D（索引12及以上）
                if indexes[-1] >= 12 or any(b - a != 1 for a, b in zip(indexes, indexes[1:])):
                    return False
                return True
            except ValueError:
                return False

        # 新增连对验证（例如3344）
        if len(cards) % 2 == 0 and len(cards) >= 4:
            pairs = [cards[i:i + 2] for i in range(0, len(cards), 2)]
            if all(len(set(p)) == 1 for p in pairs):
                indexes = [AllCards.index(p[0]) for p in pairs]
                if indexes[-1] < 12 and all(b - a == 1 for a, b in zip(indexes, indexes[1:])):
                    return True


    def update_game_state(self, cards, player_name):
        if self.check_victory():
            return

        self.game_state.consecutive_passes = 0
        self.game_state.must_play = False
        self.game_state.last_played = cards
        self.game_state.current_leader = self.game_state.current_player
        self.game_state.history.append(f"{player_name}出牌: {' '.join(cards)}")
        self.game_state.current_player = self.game_state.next_player()
        self.process_next_turn()
        # 检查是否为炸弹并更新计数
        if len(cards) == 4 and len(set(cards)) == 1:
            self.game_state.bomb_num += 1

    def check_victory(self):
        landlord = self.game_state.landlord

        if self.game_state.played_counts[landlord] >= 20:
            QMessageBox.information(self, "游戏结束", "地主获胜！")
            return True

        if landlord == "player":
            farmer_total = sum(self.game_state.played_counts[p] for p in ["up", "down"])
        else:
            farmer_total = sum(self.game_state.played_counts[p] for p in ["up", "down"] if p != landlord)

        if farmer_total >= 17:
            QMessageBox.information(self, "游戏结束", "农民获胜！")
            return True

        return False

    def pass_turn(self):
        if not self.game_state.last_played:
            QMessageBox.warning(self, "错误", "首轮必须出牌！")
            return

        self.game_state.consecutive_passes += 1

        if self.game_state.consecutive_passes >= 2:
            next_player = self.game_state.next_player()
            self.game_state.current_leader = next_player
            self.game_state.must_play = True

        self.game_state.history.append("玩家选择过")
        self.game_state.current_player = self.game_state.next_player()
        self.process_next_turn()

    def process_next_turn(self):
        if self.game_state.current_player == self.game_state.current_leader:
            self.game_state.reset_round()
        self.update_display()

    def handle_opponent_turn(self):
        player = self.game_state.current_player
        if player not in ["up", "down"]:
            return

        available_cards = self.game_state.shared_cards.copy()
        possible_cards = Counter(available_cards)
        if self.game_state.landlord == player:
            possible_cards.update(Counter(self.game_state.landlord_cards))

        player_name = {"up": "上家", "down": "下家"}[player]
        dialog = CardSelectionDialog(f"{player_name}出牌", 0, self, is_play_phase=True)
        dialog.card_counts = possible_cards
        dialog.update_card_list()

        if self.game_state.must_play:
            dialog.pass_button.setEnabled(False)

        if dialog.exec_() == QDialog.Accepted:
            selected = dialog.get_selected_cards()

            if not selected:
                if not self.game_state.last_played and player == self.game_state.landlord:
                    QMessageBox.warning(self, "错误", "地主首轮必须出牌！")
                    return self.handle_opponent_turn()

                if self.game_state.must_play:
                    QMessageBox.warning(self, "错误", "必须出牌！")
                    return self.handle_opponent_turn()

                self.game_state.consecutive_passes += 1
                self.game_state.history.append(f"{player_name}选择过")

                if self.game_state.consecutive_passes >= 2:
                    next_player = self.game_state.next_player()
                    self.game_state.current_leader = next_player
                    self.game_state.must_play = True

                self.game_state.current_player = self.game_state.next_player()
                self.process_next_turn()
                return

            if not self.validate_play(selected):
                QMessageBox.warning(self, "错误", "无效出牌组合！")
                return self.handle_opponent_turn()

            for card in selected:
                if card in self.game_state.shared_cards:
                    self.game_state.shared_cards.remove(card)
                else:
                    QMessageBox.warning(self, "错误", f"牌堆中没有这些牌！")
                    return

            self.game_state.played_counts[player] += len(selected)
            self.game_state.last_played = selected
            self.game_state.current_leader = player
            self.game_state.consecutive_passes = 0
            self.game_state.must_play = False
            self.game_state.history.append(f"{player_name}出牌: {' '.join(selected)}")
            self.game_state.current_player = self.game_state.next_player()
            self.process_next_turn()





class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("斗地主")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()

        self.start_btn = QPushButton("开始游戏")
        self.start_btn.clicked.connect(self.start_selection)
        self.hand_label = QLabel("手牌：未选择")
        self.landlord_label = QLabel("底牌：未选择")

        layout.addWidget(self.start_btn)
        layout.addWidget(self.hand_label)
        layout.addWidget(self.landlord_label)
        self.setLayout(layout)

    def start_selection(self):
        total_cards = []
        for card, count in initial_card_counts.items():
            total_cards += [card] * count
        random.shuffle(total_cards)

        hand_dialog = CardSelectionDialog("选择手牌（17张）", 17, self)
        if hand_dialog.exec_() != QDialog.Accepted:
            return
        hand_cards = hand_dialog.get_selected_cards()

        for card in hand_cards:
            total_cards.remove(card)

        remaining_counts = Counter(total_cards)
        landlord_dialog = CardSelectionDialog("选择底牌（3张）", 3, self)
        landlord_dialog.card_counts = remaining_counts
        landlord_dialog.update_card_list()
        if landlord_dialog.exec_() != QDialog.Accepted:
            return
        landlord_cards = landlord_dialog.get_selected_cards()

        for card in landlord_cards:
            total_cards.remove(card)

        # 在选择地主前初始化所有玩家的手牌
        self.game_state.player_hands = {
            "player": hand_cards.copy(),
            "up": [],  # 上家初始手牌应为随机分配的17张
            "down": []  # 下家同理
        }

        # 修复底牌设置逻辑
        self.game_state.landlord_cards = landlord_cards.copy()  # 使用拷贝避免引用问题
        self.game_state.shared_cards = total_cards.copy()

        print(f"[DEBUG] 玩家初始手牌: {hand_cards}")  # 新增调试输出
        print(f"[DEBUG] 底牌内容: {landlord_cards}")

        landlord_selector = LandlordSelectionDialog(self)
        if landlord_selector.exec_() != QDialog.Accepted:
            return
        selected_landlord = landlord_selector.get_landlord()

        # 根据地主位置分配初始手牌（关键修复）
        if selected_landlord != "player":
            # 正确分配AI玩家初始手牌
            remaining_cards = self.game_state.shared_cards.copy()
            self.game_state.player_hands["up"] = remaining_cards[:17]
            self.game_state.player_hands["down"] = remaining_cards[17:34]

        self.game_state.set_landlord(selected_landlord)


        # 初始化AI代理
        self.game_state.init_ai_agent()

        self.game_state.landlord_cards = landlord_cards  # 新增此行
        self.game_state.shared_cards = total_cards

        order_map = {
            "up": ["up", "player", "down"],
            "player": ["player", "down", "up"],
            "down": ["down", "up", "player"]
        }
        self.game_state.player_hands["up"] = sorted(self.game_state.player_hands["up"])
        self.game_state.player_hands["down"] = sorted(self.game_state.player_hands["down"])
        self.game_state.player_order = order_map[selected_landlord]
        self.game_state.current_player = selected_landlord
        self.game_state.current_leader = selected_landlord
        self.game_state.phase = "出牌阶段"
        self.play_window = PlayPhaseWindow(self.game_state)
        self.play_window.show()
        self.hide()






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())